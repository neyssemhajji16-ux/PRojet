# 🚀 Startup Stress-Test TN — Simulateur de Résistance des Startups

> **Projet Universitaire — Management de l'Innovation**  
> Une plateforme intelligente tout-en-un pour tester la viabilité d'une idée entrepreneuriale face aux réalités économiques du marché tunisien avant son lancement.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?style=flat&logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/Status-Projet%20Acad%C3%A9mique-success)](#)

---

## 🎯 Vision & Problématique

En Tunisie, plus de 70 % des nouvelles startups rencontrent des difficultés critiques au cours des 24 premiers mois, principalement en raison de chocs imprévus (hausse des coûts logistiques, baisse de la demande, trésorerie insuffisante).

**Notre proposition d'innovation :**  
Passer d'un outil de simple conseil passif à un **simulateur de résistance actif** qui stresse le modèle économique par des chocs réels (carburant, pouvoir d'achat, concurrence) et propose des décisions correctives (**Pivots stratégiques**, **Recommandations IA**, **Personas clients**).

---

## 🌟 Fonctionnalités Clés

1. ⚡ **Stress-Test Financier Interactif** : Sliders en temps réel simulant l'impact d'une hausse du transport et d'une chute de la demande sur la marge unitaire et le seuil de rentabilité (Cas Okkis & Entreprise personnalisée).
2. 📊 **Graphiques & Visualisations** : Courbes de point mort, décomposition des charges et marges de sécurité propulsées par Chart.js.
3. 🧭 **Diagnostic IA Multidimensionnel** : Évaluation radar sur 5 axes (Marché, Évolutivité, Tech/Innovation, Équipe, Environnement/RSE).
4. 📝 **Questionnaire Adaptatif (Adaptive Intake)** : Enquête dynamique en 6 étapes calculant la viabilité de l'idée.
5. 👥 **Simulateur de Personas Tunisiens** : Génération automatique des profils clients locaux (sensibilité au prix, comportements d'achat).
6. 🔄 **Planificateur de Scénarios de Pivot** : 6 modèles alternatifs (Abonnement, B2B, Hubs de quartier, Volume, etc.).
7. 📑 **Générateur de Business Plan & Canvas** : Génération automatique de la matrice BMC prête à imprimer / exporter en PDF.
8. 💡 **Boîte à Idées & Recommandations IA** : Opportunités par secteur en Tunisie (AgriTech, HealthTech, EdTech, FinTech...).

---

## 📁 Architecture du Projet

```text
Projet_Rouis/
├── app.py                  # Backend Flask (API REST & Moteur de calcul)
├── requirements.txt        # Dépendances Python (flask, flask-cors)
├── start.bat               # Lanceur automatique 1-clic pour Windows
├── Rapport_Projet.md       # Rapport complet du projet (Management de l'Innovation)
├── .gitignore              # Fichiers à exclure de git
├── data/
│   └── tunisian_market.json # Données économiques tunisiennes (BCT, INTIGO, salaires, secteurs)
└── static/                 # Frontend Web SPA
    ├── index.html          # Interface utilisateur complète (9 vues)
    ├── css/
    │   └── style.css       # Design moderne & humain (Palette Corail & Turquoise)
    └── js/
        └── app.js          # Logique interactive, requêtes API et graphiques
```

---

## 💻 Guide de Démarrage Rapide (Pour tester la plateforme)

### Prérequis
* [Python 3.9+](https://www.python.org/downloads/) installé avec la case **"Add Python to PATH"** cochée.
* [Git](https://git-scm.com/) installé.

---

### Option A : Lancement ultra-rapide (Windows 1-Clic) ⚡
1. Double-cliquez simplement sur **`start.bat`**.
2. Il installe automatiquement les dépendances et lance l'application.
3. Ouvrez votre navigateur sur **`http://localhost:5000`**.

---

### Option B : Lancement manuel en ligne de commande

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_NOM_UTILISATEUR/startup-stress-test-tn.git

# 2. Accéder au dossier
cd startup-stress-test-tn

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
python app.py
```

Ouvrez ensuite votre navigateur sur :  
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Cas de Test Recommandé

Pour une démonstration complète, testez le scénario **« Mazraa Connect »** (AgriTech bio en circuit court) :
1. Allez dans **Questionnaire** et remplissez les données de base d'un e-commerce agricole.
2. Allez dans **Stress-Test** et testez une hausse de **+2 DT** du transport et **-20 %** de demande.
3. Observez l'alerte de déficit et le passage du seuil de rentabilité de 267 à 337 commandes.
4. Rendez-vous dans **Scénarios de Pivot** pour adopter le modèle **« Box par Abonnement »**.
5. Téléchargez la synthèse dans **Business Plan**.

---

## 👥 Équipe & Remerciements

Projet réalisé dans le cadre du module **Management de l'Innovation**.  
*Données de marché basées sur les publications de la Banque Centrale de Tunisie (BCT), l'INS et les tarifs logistiques publics.*
