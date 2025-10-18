# KodeKloud Progress Tracker

Application Streamlit pour suivre votre progression dans les parcours KodeKloud (SRE, DevOps, Cloud, MLOps).

## 🚀 Lancement rapide

Pour lancer l'application, utilisez simplement le script `start.sh` :

```bash
./start.sh
```

Ce script va automatiquement :
- Créer l'environnement virtuel `env` s'il n'existe pas
- Activer l'environnement virtuel
- Installer les dépendances depuis `requirements.txt`
- Lancer l'application Streamlit sur le port 8501

## 📱 Accès à l'application

Une fois lancée, l'application sera accessible sur :
- **Local :** http://localhost:8501
- **Réseau :** http://[votre-ip]:8501

## 🛠️ Installation manuelle (optionnel)

Si vous préférez l'installation manuelle :

1. Créer l'environnement virtuel Python 3.12 :
```bash
python3 -m venv env
```

2. Activer l'environnement virtuel :
```bash
source env/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Lancer l'application :
```bash
streamlit run app.py --server.headless true --server.port 8501
```

## 📋 Fonctionnalités

- **Dashboard global** avec métriques de progression et graphiques
- **Suivi détaillé** par parcours avec checkboxes et commentaires
- **Liens directs** vers tous les cours KodeKloud
- **Export des données** de progression (.progress.json)
- **Analyse des cours communs** entre parcours

## 📚 Parcours disponibles

- **SRE** : 14 cours - Site Reliability Engineer
- **DevOps** : 22 cours - DevOps Engineer (avec 6 cours IAC supplémentaires)
- **Cloud** : 29 cours - Cloud Engineer
- **MLOps** : 14 cours - AI/MLOps Engineer

**Total : 76 cours** avec liens directs vers KodeKloud

## 📁 Structure des fichiers

- `app.py` - Application Streamlit principale
- `start.sh` - Script de lancement automatisé
- `requirements.txt` - Dépendances Python
- `*.json` - Données des parcours (sre.json, devops.json, cloud.json, mlops.json)
- `.progress.json` - Sauvegarde de votre progression (généré automatiquement)
- `README.md` - Ce fichier de documentation

## 🎯 Interface utilisateur

L'application dispose de 3 onglets principaux :
1. **📋 Sommaire** - Dashboard avec métriques globales et graphiques
2. **📚 Parcours & Progression** - Suivi détaillé par parcours avec checkboxes
3. **🔗 Cours Communs** - Analyse transversale des cours partagés

## 💾 Sauvegarde automatique

Votre progression est automatiquement sauvegardée dans le fichier `.progress.json` à chaque modification.
```

Emplacement attendu des fichiers markdown: `../markdown/` (relatif au dossier `kodekloud_tracker`). L'application tentera d'extraire automatiquement les noms de cours depuis les fichiers Markdown et te permettra de cocher les tâches et sauvegarder localement.

Améliorations possibles:
- parsing plus fin des sections "PATH #" et des listes de cours
- affichage UI plus riche (tableaux, filtres par durée)
- synchronisation cloud (Google Drive / Git)
- export/import CSV

Si tu veux, j'ajoute des fonctionnalités (ex: filtrage par durée, export CSV, interface pour réordonner les tâches).

Améliorations possibles:
- parsing plus fin des sections "PATH #" et des listes de cours
- affichage UI plus riche (tableaux, filtres par durée)
- synchronisation cloud (Google Drive / Git)
- export/import CSV

Si tu veux, j'ajoute des fonctionnalités (ex: filtrage par durée, export CSV, interface pour réordonner les tâches).