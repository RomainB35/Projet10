#  MVP de recommandation d’articles

Ce dépôt contient le code et les outils pour le **premier MVP** d'une application de recommandation d'articles

---

## 📌 Contexte

Dans cette première version de l’application :

- L’utilisateur reçoit une **sélection de cinq articles** recommandés.
- Nous n’avons pas encore de données réelles utilisateurs ; nous utilisons donc des **données publiques** pour développer et tester le système de recommandation.
- Le MVP se concentre sur la **fonctionnalité critique** : proposer des recommandations personnalisées rapidement.
- L’architecture est pensée pour intégrer facilement **de nouveaux utilisateurs et de nouveaux articles** à l’avenir.

---

## 📂 Structure complète du dépôt

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

---

## ⚙️ Fonctionnalités principales

- **Calcul des recommandations**
  - Offline : pré-calcul des articles les plus proches pour chaque article connus.
  - Online : calcul à la demande pour un utilisateur donné.
- **Interface utilisateur**
  - Affichage des **5 articles recommandés** pour l’utilisateur sélectionné.
- **Stockage et gestion des données**
  - Upload automatique sur un bucket S3 via script.

---

## 📈 Architecture cible

- Système **modulaire et serverless** pour faciliter la scalabilité.
- Prise en compte de **nouveaux utilisateurs** et **nouveaux articles** : le système recalculera les recommandations sans modifier l’architecture globale.

---

## 💡 Remarques

- Les fichiers volumineux sont stockés sur **S3 Scaleway**, et non directement dans Git.
- Le projet est conçu comme un **MVP**, avec des **extensions futures possibles** pour la production.

