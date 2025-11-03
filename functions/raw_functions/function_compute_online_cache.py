import json
import pandas as pd
import numpy as np

# --- Variables globales pour cache ---
clicks_df = None
articles_df = None

CLICKS_URL = "https://oc-projet10.s3.fr-par.scw.cloud/exports/all_clicks.csv"
ARTICLES_URL = "https://oc-projet10.s3.fr-par.scw.cloud/exports/articles_pca.csv"

def load_data():
    """Charge les CSV depuis S3 si ce n'est pas déjà fait"""
    global clicks_df, articles_df
    if clicks_df is None or articles_df is None:
        print("Chargement des CSV depuis S3…")
        clicks_df = pd.read_csv(CLICKS_URL)
        articles_df = pd.read_csv(ARTICLES_URL)
    return clicks_df, articles_df

def handle(event, context):
    try:
        # --- Récupérer les données avec cache ---
        clicks_df, articles_df = load_data()

        # --- Lecture du body JSON ---
        body = event.get("body", {})
        if isinstance(body, str):
            body = json.loads(body or "{}")

        user_id = int(body.get("user_id", -1))
        if user_id == -1:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Paramètre 'user_id' manquant."}),
            }

        # --- Vérifier l'utilisateur ---
        if user_id not in clicks_df["user_id"].unique():
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"L'utilisateur {user_id} n'existe pas dans les clics."}),
            }

        # --- Colonnes PCA ---
        pca_cols = [c for c in articles_df.columns if c.startswith("pca_")]

        # --- Articles lus ---
        user_clicks = clicks_df[clicks_df["user_id"] == user_id].copy()
        user_clicks = user_clicks.merge(
            articles_df[["article_id", "created_at_ts"]],
            left_on="click_article_id",
            right_on="article_id",
            how="left"
        )

        if user_clicks.empty:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Aucun article trouvé pour l'utilisateur {user_id}."}),
            }

        # --- Identifier article le plus récent et le moins récent ---
        most_recent_article_id = int(user_clicks.loc[user_clicks["created_at_ts"].idxmax(), "click_article_id"])
        least_recent_article_id = int(user_clicks.loc[user_clicks["created_at_ts"].idxmin(), "click_article_id"])

        # --- Fonction générique pour calculer recommandations ---
        def compute_recommendations(target_vec, exclude_ids):
            X = articles_df[pca_cols].values

            # Similarité cosinus
            dot = np.dot(target_vec, X.T)
            norm_target = np.linalg.norm(target_vec)
            norm_X = np.linalg.norm(X, axis=1)
            sims = (dot / (norm_target * norm_X)).flatten()

            # Distance euclidienne
            dists = np.linalg.norm(X - target_vec, axis=1)

            # Filtrer les articles déjà lus
            mask = ~articles_df["article_id"].isin(exclude_ids)

            # Top 5 Cosine
            reco_cos = articles_df.loc[mask].copy()
            reco_cos["score"] = sims[mask]
            top_cos = reco_cos.sort_values("score", ascending=False).head(5)[["article_id", "score"]]

            # Top 5 Euclidienne
            reco_euc = articles_df.loc[mask].copy()
            reco_euc["score"] = dists[mask]
            top_euc = reco_euc.sort_values("score", ascending=True).head(5)[["article_id", "score"]]

            return {
                "recommendations_cosine": top_cos.to_dict(orient="records"),
                "recommendations_euclidean": top_euc.to_dict(orient="records"),
            }

        # --- Article le plus récent ---
        recent_vec = articles_df.loc[articles_df["article_id"] == most_recent_article_id, pca_cols].values
        recos_recent = compute_recommendations(recent_vec, exclude_ids=[most_recent_article_id])

        # --- Article le moins récent ---
        oldest_vec = articles_df.loc[articles_df["article_id"] == least_recent_article_id, pca_cols].values
        recos_oldest = compute_recommendations(oldest_vec, exclude_ids=[least_recent_article_id])

        # --- Profil moyen de l'utilisateur ---
        user_articles = user_clicks["click_article_id"].unique()
        user_vecs = articles_df.loc[articles_df["article_id"].isin(user_articles), pca_cols].values
        if user_vecs.shape[0] > 0:
            user_profile_vec = np.mean(user_vecs, axis=0).reshape(1, -1)
            recos_profile = compute_recommendations(user_profile_vec, exclude_ids=user_articles)
        else:
            recos_profile = {"error": "Aucun vecteur utilisateur disponible."}

        # --- Résultat final ---
        result = {
            "user_id": user_id,
            "most_recent_article": {
                "article_id": most_recent_article_id,
                **recos_recent
            },
            "least_recent_article": {
                "article_id": least_recent_article_id,
                **recos_oldest
            },
            "user_profile_mean": recos_profile
        }

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result, ensure_ascii=False),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }

