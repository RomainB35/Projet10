import json
import pandas as pd
import numpy as np

# --- Variables globales pour cache ---
clicks_df = None
articles_df = None
neighbors_df = None

CLICKS_URL = "https://oc-projet10.s3.fr-par.scw.cloud/exports/all_clicks.csv"
ARTICLES_URL = "https://oc-projet10.s3.fr-par.scw.cloud/exports/articles_pca.csv"
NEIGHBORS_URL = "https://oc-projet10.s3.fr-par.scw.cloud/exports/top5_neighbors_faiss.csv"


def load_data():
    """Charge les CSV dans des variables globales si ce n'est pas déjà fait."""
    global clicks_df, articles_df, neighbors_df
    if clicks_df is None or articles_df is None or neighbors_df is None:
        print("Chargement des CSV depuis S3…")
        clicks_df = pd.read_csv(CLICKS_URL)
        articles_df = pd.read_csv(ARTICLES_URL)
        neighbors_df = pd.read_csv(NEIGHBORS_URL)
    return clicks_df, articles_df, neighbors_df


def handle(event, context):
    try:
        # --- Récupérer les données (avec cache) ---
        clicks_df, articles_df, neighbors_df = load_data()

        # --- Lecture du body JSON ---
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body or "{}")

        user_id = int(body.get("user_id", -1))
        if user_id == -1:
            return {"statusCode": 400, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Paramètre 'user_id' manquant."})}

        # --- Vérification utilisateur ---
        if user_id not in clicks_df["user_id"].unique():
            return {"statusCode": 404, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"L'utilisateur {user_id} n'existe pas."})}

        # --- Articles lus ---
        user_clicks = clicks_df[clicks_df["user_id"] == user_id].copy()
        user_clicks = user_clicks.merge(
            articles_df[["article_id", "created_at_ts"]],
            left_on="click_article_id",
            right_on="article_id",
            how="left"
        )
        user_articles = user_clicks["click_article_id"].unique()
        if len(user_articles) == 0:
            return {"statusCode": 404, "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Aucun article trouvé pour l'utilisateur."})}

        # --- Article le plus récent et le moins récent ---
        most_recent_article_id = int(user_clicks.loc[user_clicks["created_at_ts"].idxmax(), "click_article_id"])
        least_recent_article_id = int(user_clicks.loc[user_clicks["created_at_ts"].idxmin(), "click_article_id"])

        # --- Article moyen ---
        pca_cols = [c for c in articles_df.columns if c.startswith("pca_")]
        user_vecs = articles_df.loc[articles_df["article_id"].isin(user_articles), pca_cols].values
        if user_vecs.shape[0] > 0:
            user_profile_vec = np.mean(user_vecs, axis=0)
        else:
            user_profile_vec = None

        # --- Récupérer les voisins FAISS ---
        def get_faiss_neighbors(article_id, exclude_ids=None):
            row = neighbors_df[neighbors_df["article_id"] == article_id]
            if row.empty:
                return {"neighbors": [], "distances": []}
            neighbors = row[[f"neighbor_{i}" for i in range(1, 6)]].values.flatten().tolist()
            distances = row[[f"distance_{i}" for i in range(1, 6)]].values.flatten().tolist()
            if exclude_ids:
                filtered = [(nid, d) for nid, d in zip(neighbors, distances) if nid not in exclude_ids]
                if filtered:
                    neighbors, distances = zip(*filtered)
                    return {"neighbors": list(neighbors), "distances": list(distances)}
                else:
                    return {"neighbors": [], "distances": []}
            return {"neighbors": neighbors, "distances": distances}

        # --- Recommandations pour l'article le plus récent et le moins récent ---
        recent_recos = get_faiss_neighbors(most_recent_article_id, exclude_ids=[most_recent_article_id])
        oldest_recos = get_faiss_neighbors(least_recent_article_id, exclude_ids=[least_recent_article_id])

        # --- Recommandations pour le vecteur moyen ---
        if user_profile_vec is not None:
            X = articles_df[pca_cols].values
            all_article_ids = articles_df["article_id"].values
            dists = np.linalg.norm(X - user_profile_vec, axis=1)
            mask = ~np.isin(all_article_ids, user_articles)
            closest_idx = np.argsort(dists[mask])[:5]
            profile_recos = {
                "neighbors": all_article_ids[mask][closest_idx].tolist(),
                "distances": dists[mask][closest_idx].tolist()
            }
        else:
            profile_recos = {"neighbors": [], "distances": []}

        # --- Construction JSON final ---
        result = {
            "user_id": user_id,
            "most_recent_article": {
                "article_id": most_recent_article_id,
                **recent_recos
            },
            "least_recent_article": {
                "article_id": least_recent_article_id,
                **oldest_recos
            },
            "user_profile_mean": profile_recos
        }

        return {"statusCode": 200, "headers": {"Content-Type": "application/json"},
                "body": json.dumps(result, ensure_ascii=False)}

    except Exception as e:
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})}


