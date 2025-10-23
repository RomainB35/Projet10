import os
import streamlit as st
import requests
import json
import time

# --- Configuration de la page ---
st.set_page_config(page_title="📰 Système de recommandation", layout="centered")

# --- Panneau latéral (sidebar) ---
st.sidebar.title("⚙️ Configuration")
mode = st.sidebar.radio("Mode de calcul :", ["Calcul live", "Calcul offline"], index=0)
st.sidebar.markdown("---")

if mode == "Calcul live":
    FUNCTION_URL = "https://nsaffectionateptolemkgzvz10w-fct-agitated-chatterjee.functions.fnc.fr-par.scw.cloud"
    TOKEN = os.environ.get("SCW_TOKEN_1")
else:
    FUNCTION_URL = "https://nsaffectionateptolemkgzvz10w-fct-serene-maxwell.functions.fnc.fr-par.scw.cloud"
    TOKEN = os.environ.get("SCW_TOKEN_2")

# --- Affichage du mode actif ---
st.sidebar.write(f"🔗 **Endpoint sélectionné :**")
st.sidebar.code(FUNCTION_URL, language="text")

# --- Vérification du token ---
if not TOKEN:
    st.sidebar.error(f"🚨 Le token d'API n'est pas configuré pour le mode **{mode}**.")
    st.sidebar.info("Définis `SCW_TOKEN_1` ou `SCW_TOKEN_2` dans les variables d'environnement.")
    st.stop()

# --- Interface principale ---
st.title("📰 Système de recommandation d’articles")
st.write("Obtenez des recommandations personnalisées basées sur les articles consultés et leurs caractéristiques. Saisissez un identifiant utilisateur entre 0 et 322896:")

user_id = st.text_input("Identifiant utilisateur :", "15")

# --- Bouton principal ---
if st.button("Obtenir mes recommandations"):
    payload = {"user_id": int(user_id)}
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": TOKEN
    }

    with st.spinner("⏳ Récupération des recommandations..."):
        start_time = time.time()
        try:
            response = requests.post(FUNCTION_URL, headers=headers, json=payload, timeout=120)
            elapsed = time.time() - start_time
            st.info(f"⏱️ Temps de réponse : {elapsed:.2f} secondes")

            if response.status_code == 200:
                data = response.json()
                st.success(f"Recommandations générées pour l’utilisateur **{data.get('user_id', user_id)}**")

                # ============================
                # 🔝 SECTION : Résumé Top 5
                # ============================
                st.header("⭐ Les 5 articles recommandés")

                top_articles = []

                if mode == "Calcul live":
                    # ✅ Utilisation des recommandations basées sur la distance euclidienne
                    recent = data.get("most_recent_article", {})
                    oldest = data.get("least_recent_article", {})
                    profile = data.get("user_profile_mean", {})

                    if "recommendations_euclidean" in recent:
                        top_articles.extend([a["article_id"] for a in recent["recommendations_euclidean"][:2]])
                    if "recommendations_euclidean" in oldest:
                        top_articles.extend([a["article_id"] for a in oldest["recommendations_euclidean"][:1]])
                    if "recommendations_euclidean" in profile:
                        top_articles.extend([a["article_id"] for a in profile["recommendations_euclidean"][:2]])

                else:
                    # Récupération des recos offline (inchangé)
                    recent = data.get("most_recent_article", {})
                    oldest = data.get("least_recent_article", {})
                    profile = data.get("user_profile_mean", {})

                    top_articles.extend(recent.get("neighbors", [])[:2])
                    top_articles.extend(oldest.get("neighbors", [])[:1])
                    top_articles.extend(profile.get("neighbors", [])[:2])

                if top_articles:
                    for i, a in enumerate(top_articles, 1):
                        st.write(f"{i}. 📰 Article {a}")
                else:
                    st.warning("Aucune recommandation disponible pour construire le Top 5.")

                st.markdown("---")

                # ============================
                # 🔍 Détails des recommandations
                # ============================

                # ----------------------------
                # MODE LIVE
                # ----------------------------
                if mode == "Calcul live":
                    st.subheader("🆕 Article le plus récent")
                    if recent:
                        st.markdown(f"**Article source :** {recent.get('article_id')}")
                        st.write("**Top 5 - Similarité cosinus :**")
                        for rec in recent.get("recommendations_cosine", []):
                            st.write(f"📰 {rec['article_id']} — score {rec['score']:.3f}")
                        st.write("**Top 5 - Distance euclidienne :**")
                        for rec in recent.get("recommendations_euclidean", []):
                            st.write(f"📰 {rec['article_id']} — distance {rec['score']:.3f}")

                    st.subheader("📜 Article le moins récent")
                    if oldest:
                        st.markdown(f"**Article source :** {oldest.get('article_id')}")
                        st.write("**Top 5 - Similarité cosinus :**")
                        for rec in oldest.get("recommendations_cosine", []):
                            st.write(f"📰 {rec['article_id']} — score {rec['score']:.3f}")
                        st.write("**Top 5 - Distance euclidienne :**")
                        for rec in oldest.get("recommendations_euclidean", []):
                            st.write(f"📰 {rec['article_id']} — distance {rec['score']:.3f}")

                    st.subheader("📊 Profil moyen utilisateur")
                    if profile:
                        st.write("**Top 5 - Similarité cosinus :**")
                        for rec in profile.get("recommendations_cosine", []):
                            st.write(f"📰 {rec['article_id']} — score {rec['score']:.3f}")
                        st.write("**Top 5 - Distance euclidienne :**")
                        for rec in profile.get("recommendations_euclidean", []):
                            st.write(f"📰 {rec['article_id']} — distance {rec['score']:.3f}")

                # ----------------------------
                # MODE OFFLINE
                # ----------------------------
                else:
                    st.subheader("🆕 Article le plus récent")
                    if recent:
                        st.markdown(f"**Article source :** {recent.get('article_id')}")
                        st.write("**Top 5 - Distance euclidienne :**")
                        for n, d in zip(recent.get("neighbors", []), recent.get("distances", [])):
                            st.write(f"📰 {n} — distance {d:.3f}")

                    st.subheader("📜 Article le moins récent")
                    if oldest:
                        st.markdown(f"**Article source :** {oldest.get('article_id')}")
                        st.write("**Top 5 - Distance euclidienne :**")
                        for n, d in zip(oldest.get("neighbors", []), oldest.get("distances", [])):
                            st.write(f"📰 {n} — distance {d:.3f}")

                    st.subheader("📊 Profil moyen utilisateur")
                    if profile:
                        st.write("**Top 5 - Distance euclidienne :**")
                        for n, d in zip(profile.get("neighbors", []), profile.get("distances", [])):
                            st.write(f"📰 {n} — distance {d:.3f}")

            else:
                st.error(f"Erreur {response.status_code} : {response.text}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Le serveur a mis trop de temps à répondre.")
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur réseau : {e}")

