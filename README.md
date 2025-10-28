#  MVP de recommandation d’articles

Ce dépôt contient le code et les outils pour le **premier MVP** d'une application de recommandation d'articles.

---

## 📌 Contexte

Dans cette première version de l’application :

- L’utilisateur reçoit une **sélection de cinq articles** recommandés.
- Je n'ai pas encore de données réelles utilisateurs ; j'utilise donc les données publiques **https://www.kaggle.com/datasets/gspmoreira/news-portal-user-interactions-by-globocom#clicks_sample.csv¶** pour développer et tester le système de recommandation.
- Le MVP se concentre sur la **fonctionnalité critique** : proposer une recommandation de 5 articles pour un utilisateur donné rapidement.
- L’architecture doit être pensée pour intégrer facilement **de nouveaux utilisateurs et de nouveaux articles** à l’avenir.

---

## 📂 Structure complète du dépôt


```
Projet10/
├── notebooks/
│   └── Projet10-Data-Analysis.ipynb
├── S3_storage/
│   ├── README
│   └── copy_files_to_S3_Scaleway.bash
├── functions/
│   ├── README
│   ├── deploy_functions.bash
│   └── zips/
│       ├── function_compute_offline_cache.zip
│       └── function_compute_online_cache.zip
└── docker/
    ├── docker-compose.yml
    ├── streamlit/
    │   ├── Dockerfile
    │   ├── app.py
    │   └── requirements.txt
    └── traefik/
        ├── Dockerfile
        ├── dynamic_conf.yml
        ├── letsencrypt/
        │   └── acme.json
        └── traefik.yml

```

---

## ⚙️ Fonctionnalités principales

- **Calcul des recommandations**
  - Offline : pré-calcul des articles les plus proches pour chaque article connus.
  - Online : calcul à la demande pour un utilisateur donné.
- **Interface utilisateur**
  - Affichage des **5 articles recommandés** pour l’utilisateur sélectionné.
- **Stockage et gestion des données**
  - Upload automatisé sur un bucket S3 via un script aws cli.
- **Déploiement des fonctions**
  - Déploiement automatisé via un script scw cli.

---

## 🏛️ Architecture actuelle

![Schéma de l'architecture actuelle](architecture/Architecture_actuelle.drawio.png)

1. **Les données applicatives** sur les articles et les utilisateurs sont traitées (voir notebook) puis déposées (voir répertoire `S3_Storage`) sur un **bucket S3 Scaleway**.

2. **Deux Serverless functions** sont déployées sur Scaleway :  

   - **Fonction compute "live"** :
     - Prend en entrée un `user_id`
     - Charge les données brutes des articles et des utilisateurs
     - Trouve les articles consultés par l'utilisateur
     - Identifie l'article le plus récent et le plus ancien consulté par l'utilisateur
     - Calcule l'embedding de l'article moyen (vecteur moyen)
     - Trouve les 5 articles les plus proches (en utilisant les distances **cosine** et **euclidienne**) de :  
       - l'article le plus récent consulté par l'utilisateur
       - l'article le plus ancien consulté par l'utilisateur
       - l'article moyen

   - **Fonction compute "offline"** :
     - Prend en entrée un `user_id`
     - Charge les données brutes des articles, des utilisateurs **et un fichier CSV contenant pour chaque article les 5 articles les plus proches** (distance euclidienne calculée à partir des embeddings de la fonction "live")
     - Trouve les articles consultés par l'utilisateur
     - Identifie l'article le plus récent et le plus ancien consulté par l'utilisateur
     - Calcule l'embedding de l'article moyen (vecteur moyen)
     - Utilise le CSV pour obtenir les 5 articles les plus proches de l'article le plus récent et du plus ancien consulté
     - Calcule les 5 articles les plus proches de l'article moyen

3. **Application Streamlit de démonstration** (déployée sur un VPS Hostinger) :
   - Prend en entrée un `user_id`
   - Propose un **mode de calcul live** et un **mode de calcul offline**, en faisant appel séparément aux deux fonctions ci-dessus
   - Fournit une **recommandation de 5 articles** :
     - Les 2 articles les plus proches de l'article le plus récent consulté par l'utilisateur
     - Les 2 articles les plus proches de l'article moyen
     - L'article le plus proche de l'article le plus ancien consulté par l'utilisateur


---

---

## 📈 Architecture cible

- Prise en compte de **nouveaux utilisateurs** et **nouveaux articles** :
  - Nécessité d'ajouter une fonction pour mettre à jour les données sur le bucket S3
    - Pour le mode online: le système recalculera les recommandations sans modifier l’architecture globale.
    - Pour le mode offline: il faut ajouter une fonction qui met à jour le fichier qui contient les 5 articles les plus proches pour tous les articles.

---

## 💡 Remarques

- Les fichiers volumineux sont stockés sur **S3 Scaleway**, et non directement dans Git.

