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

1. Les données applicatives sur les articles et les utilisateurs sont traitées (voir notebook) puis déposées (voir répertoire S3_Storage) sur un bucket S3 Scaleway.

2. Deux Serverless functions sont déployées sur Scaleway
  - Une fonction compute "live" qui:
    -  prend en entrée un user_id
    -  charge les données brutes des articles et des utilisateurs 
    -  trouve les articles consultés par l'utilisateur
    -  trouve l'article le plus récent et le plus ancien consulté par l'utilisateur
    -  calcule l'embedding de l'article moyen (vecteur moyen)
    -  trouve les 5 articles les plus proches (en utilisant les distances cosine et euclidienne) de 
        - l'article le plus récent consulté par l'utilisateur
        - l'article le plus ancien consulté par l'utilisateur
        - l'article moyen
  - Une fonction compute "offline" qui:
    - prend en entrée un user_id
    - charge les données brutes des articles , des utilisateurs **ET un fichier csv qui contient pour chaque articles les 5 articles les plus proches (distance euclidienne calculée à partir des embedding en 1.)**
    -  trouve les articles consultés par l'utilisateur
    -  trouve l'article le plus récent et le plus ancien consulté par l'utilisateur
    -  calcule l'embedding de l'article moyen (vecteur moyen)
    -  utilise le csv cité précédement pour obtenir les 5 articles les plus proches de l'article plus récent et du plus ancien consulté par l'utilisateur
    -  calcule les 5 articles les plus proches de l'article moyen

 3. Sur un VPS Hostinger, je déploie une application Streamlit de démonstration qui prend en entrée un user_id, propose un mode de calcul live et un mode de calcul offline en faisant appel séparément aux deux fonctions suscités et propose une recommandation de 5 articles:

        - les 2 articles les plus proches de l'article le plus récent consulté par l'utilisateur
        - les 2 articles les plus proches de l'article moyen
        - l'article le plus proche de l'article le plus ancien consulté par l'utilisateur


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

