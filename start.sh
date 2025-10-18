#!/bin/bash

# Script de lancement pour KodeKloud Progress Tracker
# Ce script crée l'environnement virtuel si nécessaire et lance l'application

echo "🚀 KodeKloud Progress Tracker - Script de lancement"
echo "=================================================="

# Fermer toutes les instances Streamlit existantes
echo "🛑 Fermeture des instances Streamlit existantes..."
pkill -f streamlit 2>/dev/null || true
sleep 2  # Attendre que les processus se terminent
echo "✅ Instances Streamlit fermées"

# Vérifier si l'environnement virtuel existe
if [ ! -d "env" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv env
    if [ $? -ne 0 ]; then
        echo "❌ Erreur lors de la création de l'environnement virtuel"
        exit 1
    fi
    echo "✅ Environnement virtuel créé avec succès"
else
    echo "✅ Environnement virtuel trouvé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source env/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'activation de l'environnement virtuel"
    exit 1
fi
echo "✅ Environnement virtuel activé"

# Installer/mettre à jour les dépendances
echo "📚 Installation des dépendances..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
echo "✅ Dépendances installées"

# Lancer l'application Streamlit
echo "🎯 Lancement de l'application Streamlit..."
echo "=================================================="
echo "📱 L'application sera accessible sur :"
echo "   - Local: http://localhost:8501"
echo "   - Réseau: http://$(hostname -I | awk '{print $1}'):8501"
echo "=================================================="
echo "Appuyez sur Ctrl+C pour arrêter l'application"
echo ""

streamlit run app.py --server.headless true --server.port 8501