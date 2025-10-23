#  MVP de recommandation d’articles

Ce dépôt contient le code et les outils pour le **premier MVP** d'une application de recommandation d'articles.

---

## 📌 Contexte

Dans cette première version de l’application :

- L’utilisateur reçoit une **sélection de cinq articles** recommandés.
- Nous n’avons pas encore de données réelles utilisateurs ; nous utilisons donc des **données publiques https://www.kaggle.com/datasets/gspmoreira/news-portal-user-interactions-by-globocom#clicks_sample.csv¶** pour développer et tester le système de recommandation.
- Le MVP se concentre sur la **fonctionnalité critique** : proposer des recommandations personnalisées rapidement.
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

## 📈 Architecture cible

- Système **modulaire et serverless** pour faciliter la scalabilité.
- Prise en compte de **nouveaux utilisateurs** et **nouveaux articles** :
 - Nécessité d'ajouter une fonction pour mettre à jour les données sur le bucket S3
    - Pour le mode online: le système recalculera les recommandations sans modifier l’architecture globale.
    - Pour le mode offline: il faut ajouter une fonction qui met à jour le fichier qui contient les 5 articles les plus proches pour tous les articles.

---

## 💡 Remarques

- Les fichiers volumineux sont stockés sur **S3 Scaleway**, et non directement dans Git.

