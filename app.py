# -*- coding: utf-8 -*-
"""
Startup Stress-Test TN — Backend Flask
Plateforme de stress-test pour startups tunisiennes
"""

import json
import math
import os
import random
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'tunisian_market.json')

with open(DATA_PATH, 'r', encoding='utf-8') as f:
    MARKET_DATA = json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_float(val, default=0.0):
    """Convertir une valeur en float avec un défaut."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def _clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))


# ===================================================================
# 1) POST /api/simulate — Simulateur de stress-test financier
# ===================================================================
@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        d = request.get_json(force=True)

        panier_moyen       = _safe_float(d.get('panier_moyen', 0))
        cout_produits       = _safe_float(d.get('cout_produits', 0))
        cout_transport      = _safe_float(d.get('cout_transport', 0))
        autres_couts        = _safe_float(d.get('autres_couts', 0))
        charges_fixes       = _safe_float(d.get('charges_fixes', 0))
        commandes_mois      = _safe_float(d.get('commandes_mois', 0))
        livraison_facturee  = _safe_float(d.get('livraison_facturee', 0))

        choc_transport_pct  = _safe_float(d.get('choc_transport_pct', 0))
        choc_demande_pct    = _safe_float(d.get('choc_demande_pct', 0))
        choc_concurrent_pct = _safe_float(d.get('choc_concurrent_pct', 0))
        choc_marge_pct      = _safe_float(d.get('choc_marge_pct', 0))

        # --- Situation de base ---
        marge_unitaire = panier_moyen + livraison_facturee - cout_produits - cout_transport - autres_couts
        resultat_mensuel = commandes_mois * marge_unitaire - charges_fixes

        if marge_unitaire > 0:
            seuil_rentabilite = math.ceil(charges_fixes / marge_unitaire)
        else:
            seuil_rentabilite = None  # impossible

        taux_couverture = (commandes_mois / seuil_rentabilite * 100) if seuil_rentabilite and seuil_rentabilite > 0 else 0

        # --- Application des chocs ---
        cout_transport_choc = cout_transport * (1 + choc_transport_pct / 100)
        commandes_choc      = commandes_mois * (1 - choc_demande_pct / 100)
        panier_choc         = panier_moyen * (1 - choc_concurrent_pct / 100)
        # Le choc marge réduit la marge directement
        reduction_marge     = marge_unitaire * (choc_marge_pct / 100)

        marge_unitaire_choc = (panier_choc + livraison_facturee
                               - cout_produits - cout_transport_choc
                               - autres_couts - reduction_marge)
        resultat_mensuel_choc = commandes_choc * marge_unitaire_choc - charges_fixes

        if marge_unitaire_choc > 0:
            seuil_rentabilite_choc = math.ceil(charges_fixes / marge_unitaire_choc)
        else:
            seuil_rentabilite_choc = None

        taux_couverture_choc = (commandes_choc / seuil_rentabilite_choc * 100) if seuil_rentabilite_choc and seuil_rentabilite_choc > 0 else 0

        # --- Décomposition de l'impact de chaque choc ---
        impact_transport = -commandes_mois * (cout_transport_choc - cout_transport)
        impact_demande   = -(commandes_mois - commandes_choc) * marge_unitaire
        impact_concurrent = -commandes_mois * (panier_moyen - panier_choc)
        impact_marge_red  = -commandes_mois * reduction_marge

        # --- Indicateurs supplémentaires ---
        marge_brute_pct = (marge_unitaire / panier_moyen * 100) if panier_moyen > 0 else 0
        marge_brute_pct_choc = (marge_unitaire_choc / panier_choc * 100) if panier_choc > 0 else 0

        # Mois de trésorerie (combien de mois les charges fixes sont couvertes si 0 ventes)
        tresorerie_mois = resultat_mensuel / charges_fixes if charges_fixes > 0 and resultat_mensuel > 0 else 0

        return jsonify({
            "success": True,
            "avant": {
                "marge_unitaire": round(marge_unitaire, 2),
                "resultat_mensuel": round(resultat_mensuel, 2),
                "seuil_rentabilite": seuil_rentabilite,
                "taux_couverture": round(taux_couverture, 1),
                "marge_brute_pct": round(marge_brute_pct, 1),
                "revenus_mensuels": round(commandes_mois * panier_moyen, 2),
                "couts_variables_totaux": round(commandes_mois * (cout_produits + cout_transport + autres_couts), 2),
                "charges_fixes": round(charges_fixes, 2)
            },
            "apres": {
                "marge_unitaire": round(marge_unitaire_choc, 2),
                "resultat_mensuel": round(resultat_mensuel_choc, 2),
                "seuil_rentabilite": seuil_rentabilite_choc,
                "taux_couverture": round(taux_couverture_choc, 1),
                "marge_brute_pct": round(marge_brute_pct_choc, 1),
                "revenus_mensuels": round(commandes_choc * panier_choc, 2),
                "couts_variables_totaux": round(commandes_choc * (cout_produits + cout_transport_choc + autres_couts), 2),
                "charges_fixes": round(charges_fixes, 2)
            },
            "decomposition_chocs": {
                "impact_transport": round(impact_transport, 2),
                "impact_demande": round(impact_demande, 2),
                "impact_concurrent": round(impact_concurrent, 2),
                "impact_marge": round(impact_marge_red, 2),
                "impact_total": round(impact_transport + impact_demande + impact_concurrent + impact_marge_red, 2)
            },
            "variation_resultat": round(resultat_mensuel_choc - resultat_mensuel, 2),
            "variation_resultat_pct": round((resultat_mensuel_choc - resultat_mensuel) / abs(resultat_mensuel) * 100, 1) if resultat_mensuel != 0 else 0,
            "tresorerie_mois_reserve": round(tresorerie_mois, 1),
            "alerte": _generer_alertes(resultat_mensuel, resultat_mensuel_choc, marge_unitaire_choc, taux_couverture_choc)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _generer_alertes(resultat_avant, resultat_apres, marge_apres, couverture_apres):
    """Génère des alertes contextuelles en français."""
    alertes = []
    if resultat_apres < 0 and resultat_avant >= 0:
        alertes.append({
            "niveau": "critique",
            "message": "⚠️ Votre activité devient déficitaire après les chocs. Revoyez votre structure de coûts."
        })
    if marge_apres <= 0:
        alertes.append({
            "niveau": "critique",
            "message": "🚨 Marge unitaire négative ! Chaque vente vous fait perdre de l'argent."
        })
    if 0 < couverture_apres < 80:
        alertes.append({
            "niveau": "attention",
            "message": "⚡ Taux de couverture du seuil de rentabilité inférieur à 80%. Marge de sécurité faible."
        })
    if resultat_apres < resultat_avant * 0.5 and resultat_avant > 0:
        alertes.append({
            "niveau": "attention",
            "message": "📉 Votre résultat chute de plus de 50% sous stress. Diversifiez vos sources de revenus."
        })
    if not alertes:
        alertes.append({
            "niveau": "info",
            "message": "✅ Votre modèle résiste relativement bien aux chocs simulés."
        })
    return alertes


# ===================================================================
# 2) POST /api/diagnose — Diagnostic startup (5 dimensions)
# ===================================================================
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        d = request.get_json(force=True)
        answers = d.get('answers', {})

        scores = _calculer_scores_diagnostic(answers)
        note_globale = sum(scores.values()) / len(scores) if scores else 0

        forces = [dim for dim, s in scores.items() if s >= 70]
        faiblesses = [dim for dim, s in scores.items() if s < 50]

        grade = _attribuer_grade(note_globale)
        recommandations = _generer_recommandations_diagnostic(scores, answers)

        return jsonify({
            "success": True,
            "scores": scores,
            "note_globale": round(note_globale, 1),
            "grade": grade,
            "forces": forces,
            "faiblesses": faiblesses,
            "recommandations": recommandations,
            "radar_data": [{"dimension": k, "score": v} for k, v in scores.items()]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _calculer_scores_diagnostic(answers):
    """Score chaque dimension 0-100 à partir des réponses."""
    scores = {}

    # --- Marché ---
    marche = 50
    taille = answers.get('taille_marche', 'moyen')
    if taille == 'grand': marche += 20
    elif taille == 'moyen': marche += 10
    elif taille == 'niche': marche += 5
    else: marche -= 10

    if answers.get('marche_valide', False): marche += 15
    if answers.get('clients_existants', False): marche += 10
    croissance = answers.get('croissance_marche', 'stable')
    if croissance == 'forte': marche += 15
    elif croissance == 'moderate': marche += 8
    elif croissance == 'decline': marche -= 15
    concurrence = answers.get('niveau_concurrence', 'moyen')
    if concurrence == 'faible': marche += 10
    elif concurrence == 'fort': marche -= 10
    scores['Marché'] = _clamp(marche)

    # --- Offre Commerciale ---
    offre = 50
    if answers.get('proposition_valeur_claire', False): offre += 15
    if answers.get('avantage_concurrentiel', False): offre += 15
    pricing = answers.get('strategie_prix', 'alignee')
    if pricing == 'premium': offre += 10
    elif pricing == 'low_cost': offre += 5
    elif pricing == 'penetration': offre += 8
    if answers.get('canaux_distribution', False): offre += 10
    if answers.get('marque_identite', False): offre += 5
    taux = _safe_float(answers.get('taux_conversion', 0))
    if taux > 5: offre += 10
    elif taux > 2: offre += 5
    scores['Offre Commerciale'] = _clamp(offre)

    # --- Innovation ---
    innovation = 40
    if answers.get('technologie_proprietary', False): innovation += 20
    if answers.get('brevet_ou_pi', False): innovation += 15
    niveau = answers.get('niveau_innovation', 'incremental')
    if niveau == 'disruptif': innovation += 20
    elif niveau == 'incremental': innovation += 10
    elif niveau == 'me_too': innovation -= 5
    if answers.get('r_et_d_active', False): innovation += 10
    if answers.get('prototype_mvp', False): innovation += 10
    scores['Innovation'] = _clamp(innovation)

    # --- Évolutivité ---
    evolutivite = 45
    modele = answers.get('modele_scalable', 'lineaire')
    if modele == 'plateforme': evolutivite += 25
    elif modele == 'saas': evolutivite += 20
    elif modele == 'marketplace': evolutivite += 18
    elif modele == 'lineaire': evolutivite += 5
    if answers.get('automatisation', False): evolutivite += 10
    if answers.get('expansion_geographique', False): evolutivite += 10
    equipe = _safe_int(answers.get('taille_equipe', 1))
    if equipe >= 5: evolutivite += 10
    elif equipe >= 3: evolutivite += 5
    if answers.get('processus_documentes', False): evolutivite += 5
    scores['Évolutivité'] = _clamp(evolutivite)

    # --- Impact Environnemental ---
    impact = 50
    if answers.get('politique_environnementale', False): impact += 15
    if answers.get('economie_circulaire', False): impact += 15
    if answers.get('empreinte_carbone_mesuree', False): impact += 10
    if answers.get('fournisseurs_locaux', False): impact += 10
    if answers.get('produits_eco', False): impact += 10
    if answers.get('certification_verte', False): impact += 10
    scores['Impact Environnemental'] = _clamp(impact)

    return scores


def _attribuer_grade(note):
    if note >= 85: return {"lettre": "A+", "label": "Excellent", "couleur": "#10b981"}
    if note >= 75: return {"lettre": "A",  "label": "Très Bien", "couleur": "#22c55e"}
    if note >= 65: return {"lettre": "B+", "label": "Bien", "couleur": "#84cc16"}
    if note >= 55: return {"lettre": "B",  "label": "Assez Bien", "couleur": "#eab308"}
    if note >= 45: return {"lettre": "C",  "label": "Passable", "couleur": "#f97316"}
    if note >= 35: return {"lettre": "D",  "label": "Insuffisant", "couleur": "#ef4444"}
    return {"lettre": "F",  "label": "Critique", "couleur": "#dc2626"}


def _generer_recommandations_diagnostic(scores, answers):
    recs = []
    if scores.get('Marché', 0) < 50:
        recs.append({
            "dimension": "Marché",
            "priorite": "haute",
            "conseil": "Validez votre marché avec au moins 50 entretiens clients. Utilisez la méthode Lean Startup pour tester vos hypothèses rapidement.",
            "actions": [
                "Réalisez 50 entretiens de découverte client",
                "Créez une landing page pour mesurer l'intérêt",
                "Analysez la concurrence sur les réseaux sociaux tunisiens"
            ]
        })
    if scores.get('Offre Commerciale', 0) < 50:
        recs.append({
            "dimension": "Offre Commerciale",
            "priorite": "haute",
            "conseil": "Renforcez votre proposition de valeur. Votre offre doit résoudre un problème clair et mesurable.",
            "actions": [
                "Reformulez votre proposition de valeur en une phrase",
                "Identifiez 3 avantages concurrentiels uniques",
                "Testez 3 niveaux de prix différents"
            ]
        })
    if scores.get('Innovation', 0) < 50:
        recs.append({
            "dimension": "Innovation",
            "priorite": "moyenne",
            "conseil": "Différenciez-vous technologiquement. En Tunisie, les solutions qui apportent de l'efficacité via la technologie ont un avantage durable.",
            "actions": [
                "Identifiez une technologie clé qui vous différencie",
                "Protégez votre propriété intellectuelle",
                "Rejoignez un programme Startup Act pour accéder à des ressources R&D"
            ]
        })
    if scores.get('Évolutivité', 0) < 50:
        recs.append({
            "dimension": "Évolutivité",
            "priorite": "moyenne",
            "conseil": "Pensez scalabilité dès le départ. Un modèle SaaS ou marketplace est plus facilement extensible qu'un modèle linéaire.",
            "actions": [
                "Automatisez les processus répétitifs",
                "Documentez vos processus clés",
                "Explorez les modèles de revenus récurrents (abonnement)"
            ]
        })
    if scores.get('Impact Environnemental', 0) < 50:
        recs.append({
            "dimension": "Impact Environnemental",
            "priorite": "basse",
            "conseil": "L'impact environnemental devient un critère pour les investisseurs et les clients. Intégrez-le dans votre stratégie.",
            "actions": [
                "Mesurez votre empreinte carbone",
                "Privilégiez les fournisseurs locaux",
                "Explorez les certifications vertes disponibles en Tunisie"
            ]
        })
    if not recs:
        recs.append({
            "dimension": "Général",
            "priorite": "info",
            "conseil": "Excellent profil ! Concentrez-vous sur l'exécution et la croissance.",
            "actions": [
                "Préparez votre dossier de financement",
                "Développez vos partenariats stratégiques",
                "Planifiez votre expansion géographique"
            ]
        })
    return recs


# ===================================================================
# 3) POST /api/questionnaire — Questionnaire adaptatif
# ===================================================================
QUESTIONNAIRE_TREE = {
    1: {
        "titre": "Votre Projet",
        "questions": [
            {"id": "secteur", "texte": "Dans quel secteur souhaitez-vous entreprendre ?",
             "type": "select",
             "options": [
                 {"value": "livraison", "label": "Livraison & Logistique"},
                 {"value": "ecommerce", "label": "E-Commerce"},
                 {"value": "services", "label": "Services Numériques"},
                 {"value": "foodtech", "label": "Food Tech"},
                 {"value": "edtech", "label": "EdTech"},
                 {"value": "healthtech", "label": "HealthTech"},
                 {"value": "fintech", "label": "FinTech"},
                 {"value": "agritech", "label": "AgriTech"},
                 {"value": "autre", "label": "Autre"}
             ]},
            {"id": "description_projet", "texte": "Décrivez brièvement votre projet en une phrase",
             "type": "text"},
            {"id": "stade_projet", "texte": "À quel stade en êtes-vous ?",
             "type": "select",
             "options": [
                 {"value": "idee", "label": "Juste une idée"},
                 {"value": "mvp", "label": "J'ai un MVP / prototype"},
                 {"value": "lance", "label": "Déjà lancé, premiers clients"},
                 {"value": "croissance", "label": "En croissance, je veux scaler"}
             ]},
            {"id": "localisation", "texte": "Où sera basée votre activité ?",
             "type": "select",
             "options": [
                 {"value": "grand_tunis", "label": "Grand Tunis"},
                 {"value": "sahel", "label": "Sahel (Sousse, Monastir, Mahdia)"},
                 {"value": "sfax", "label": "Sfax"},
                 {"value": "autre_region", "label": "Autre région"},
                 {"value": "national", "label": "National (tout le pays)"},
                 {"value": "international", "label": "International"}
             ]}
        ],
        "step_suivant": 2
    },
    2: {
        "titre": "Marché Cible",
        "questions": [
            {"id": "type_client", "texte": "Quel est votre client cible ?",
             "type": "select",
             "options": [
                 {"value": "b2c", "label": "Particuliers (B2C)"},
                 {"value": "b2b", "label": "Entreprises (B2B)"},
                 {"value": "b2b2c", "label": "Les deux (B2B2C)"},
                 {"value": "b2g", "label": "Gouvernement / Secteur public (B2G)"}
             ]},
            {"id": "tranche_age", "texte": "Quelle tranche d'âge ciblez-vous principalement ?",
             "type": "select",
             "options": [
                 {"value": "18_25", "label": "18-25 ans (Étudiants / Jeunes)"},
                 {"value": "25_35", "label": "25-35 ans (Jeunes professionnels)"},
                 {"value": "35_50", "label": "35-50 ans (Familles / Cadres)"},
                 {"value": "50_plus", "label": "50+ ans (Seniors)"},
                 {"value": "tous", "label": "Toutes les tranches"}
             ],
             "condition": {"field": "type_client", "values": ["b2c", "b2b2c"]}},
            {"id": "taille_entreprise_cible", "texte": "Quelle taille d'entreprise ciblez-vous ?",
             "type": "select",
             "options": [
                 {"value": "tpe", "label": "TPE (< 10 employés)"},
                 {"value": "pme", "label": "PME (10-250 employés)"},
                 {"value": "grande", "label": "Grande entreprise (250+)"},
                 {"value": "toutes", "label": "Toutes tailles"}
             ],
             "condition": {"field": "type_client", "values": ["b2b", "b2b2c"]}},
            {"id": "probleme_resolu", "texte": "Quel problème principal résolvez-vous pour vos clients ?",
             "type": "text"},
            {"id": "concurrence_directe", "texte": "Avez-vous identifié des concurrents directs ?",
             "type": "select",
             "options": [
                 {"value": "aucun", "label": "Aucun concurrent identifié"},
                 {"value": "peu", "label": "1-3 concurrents"},
                 {"value": "beaucoup", "label": "Plus de 3 concurrents"},
                 {"value": "domine", "label": "Marché dominé par un acteur majeur"}
             ]}
        ],
        "step_suivant": 3
    },
    3: {
        "titre": "Modèle Économique",
        "questions": [
            {"id": "modele_revenu", "texte": "Comment comptez-vous générer des revenus ?",
             "type": "multiselect",
             "options": [
                 {"value": "vente_directe", "label": "Vente directe de produits"},
                 {"value": "commission", "label": "Commission sur transactions"},
                 {"value": "abonnement", "label": "Abonnement mensuel/annuel"},
                 {"value": "freemium", "label": "Freemium (gratuit + premium)"},
                 {"value": "publicite", "label": "Publicité"},
                 {"value": "licence", "label": "Licence / SaaS"},
                 {"value": "service", "label": "Facturation à l'acte / service"},
                 {"value": "autre_revenu", "label": "Autre"}
             ]},
            {"id": "panier_moyen_estime", "texte": "Quel est votre panier moyen estimé (en DT) ?",
             "type": "number", "placeholder": "Ex: 50"},
            {"id": "frequence_achat", "texte": "À quelle fréquence vos clients achèteront-ils ?",
             "type": "select",
             "options": [
                 {"value": "quotidien", "label": "Quotidiennement"},
                 {"value": "hebdomadaire", "label": "Chaque semaine"},
                 {"value": "mensuel", "label": "Chaque mois"},
                 {"value": "trimestriel", "label": "Chaque trimestre"},
                 {"value": "annuel", "label": "Une fois par an"},
                 {"value": "ponctuel", "label": "Achat ponctuel / unique"}
             ]},
            {"id": "objectif_clients_an1", "texte": "Combien de clients visez-vous la première année ?",
             "type": "number", "placeholder": "Ex: 500"}
        ],
        "step_suivant": 4
    },
    4: {
        "titre": "Équipe & Ressources",
        "questions": [
            {"id": "taille_equipe_actuelle", "texte": "Combien de personnes composent votre équipe actuellement ?",
             "type": "select",
             "options": [
                 {"value": "solo", "label": "Je suis seul(e)"},
                 {"value": "2_3", "label": "2-3 personnes"},
                 {"value": "4_10", "label": "4-10 personnes"},
                 {"value": "plus_10", "label": "Plus de 10 personnes"}
             ]},
            {"id": "competences_equipe", "texte": "Quelles compétences clés avez-vous dans l'équipe ?",
             "type": "multiselect",
             "options": [
                 {"value": "technique", "label": "Développement / Technique"},
                 {"value": "commercial", "label": "Commercial / Vente"},
                 {"value": "marketing", "label": "Marketing / Communication"},
                 {"value": "finance", "label": "Finance / Gestion"},
                 {"value": "design", "label": "Design / UX"},
                 {"value": "domaine", "label": "Expertise du domaine"},
                 {"value": "juridique", "label": "Juridique / Réglementaire"}
             ]},
            {"id": "experience_entrepreneuriale", "texte": "Avez-vous de l'expérience entrepreneuriale ?",
             "type": "select",
             "options": [
                 {"value": "premiere_fois", "label": "C'est ma première startup"},
                 {"value": "experience", "label": "J'ai déjà créé une entreprise"},
                 {"value": "serie", "label": "Entrepreneur en série (3+)"}
             ]},
            {"id": "temps_consacre", "texte": "Quel temps consacrez-vous au projet ?",
             "type": "select",
             "options": [
                 {"value": "temps_plein", "label": "Temps plein"},
                 {"value": "mi_temps", "label": "Mi-temps (je garde mon emploi)"},
                 {"value": "soir_weekend", "label": "Soirs et weekends uniquement"}
             ]}
        ],
        "step_suivant": 5
    },
    5: {
        "titre": "Financement & Budget",
        "questions": [
            {"id": "budget_initial", "texte": "Quel est votre budget initial disponible (en DT) ?",
             "type": "select",
             "options": [
                 {"value": "moins_5000", "label": "Moins de 5 000 DT"},
                 {"value": "5000_20000", "label": "5 000 - 20 000 DT"},
                 {"value": "20000_50000", "label": "20 000 - 50 000 DT"},
                 {"value": "50000_100000", "label": "50 000 - 100 000 DT"},
                 {"value": "plus_100000", "label": "Plus de 100 000 DT"}
             ]},
            {"id": "source_financement", "texte": "Comment comptez-vous financer votre projet ?",
             "type": "multiselect",
             "options": [
                 {"value": "fonds_propres", "label": "Fonds propres / Épargne"},
                 {"value": "famille", "label": "Famille et amis"},
                 {"value": "pret_bancaire", "label": "Prêt bancaire (BFPME, BTS…)"},
                 {"value": "investisseurs", "label": "Investisseurs / Business Angels"},
                 {"value": "startup_act", "label": "Startup Act / Subventions"},
                 {"value": "crowdfunding", "label": "Crowdfunding"},
                 {"value": "accelerateur", "label": "Accélérateur (Flat6Labs, etc.)"},
                 {"value": "bootstrapping", "label": "Bootstrapping (revenus clients)"}
             ]},
            {"id": "besoin_financement", "texte": "Avez-vous besoin de lever des fonds supplémentaires ?",
             "type": "select",
             "options": [
                 {"value": "non", "label": "Non, mon budget suffit"},
                 {"value": "court_terme", "label": "Oui, dans les 6 prochains mois"},
                 {"value": "moyen_terme", "label": "Oui, dans 6-12 mois"},
                 {"value": "long_terme", "label": "Oui, dans 1-2 ans"}
             ]},
            {"id": "montant_recherche", "texte": "Si oui, combien souhaitez-vous lever (en DT) ?",
             "type": "number", "placeholder": "Ex: 100000",
             "condition": {"field": "besoin_financement", "values": ["court_terme", "moyen_terme", "long_terme"]}}
        ],
        "step_suivant": 6
    },
    6: {
        "titre": "Vision & Objectifs",
        "questions": [
            {"id": "objectif_12_mois", "texte": "Quel est votre objectif principal à 12 mois ?",
             "type": "select",
             "options": [
                 {"value": "valider_marche", "label": "Valider le product-market fit"},
                 {"value": "premiers_revenus", "label": "Générer les premiers revenus"},
                 {"value": "rentabilite", "label": "Atteindre la rentabilité"},
                 {"value": "croissance", "label": "Accélérer la croissance"},
                 {"value": "lever_fonds", "label": "Lever un tour de financement"},
                 {"value": "expansion", "label": "Expansion géographique"}
             ]},
            {"id": "ca_objectif_an1", "texte": "Quel chiffre d'affaires visez-vous la 1ère année (en DT) ?",
             "type": "number", "placeholder": "Ex: 200000"},
            {"id": "differentiation", "texte": "Qu'est-ce qui vous rend unique par rapport à la concurrence ?",
             "type": "text"},
            {"id": "risque_principal", "texte": "Quel est selon vous le principal risque de votre projet ?",
             "type": "select",
             "options": [
                 {"value": "marche", "label": "Pas assez de demande"},
                 {"value": "concurrence", "label": "Concurrence trop forte"},
                 {"value": "financement", "label": "Manque de financement"},
                 {"value": "equipe", "label": "Difficulté à recruter"},
                 {"value": "reglementation", "label": "Obstacles réglementaires"},
                 {"value": "technologie", "label": "Défis techniques"},
                 {"value": "execution", "label": "Capacité d'exécution"}
             ]}
        ],
        "step_suivant": None
    }
}


@app.route('/api/questionnaire', methods=['POST'])
def questionnaire():
    try:
        d = request.get_json(force=True)
        step = _safe_int(d.get('step', 1), 1)
        answers = d.get('answers', {})

        if step not in QUESTIONNAIRE_TREE:
            return jsonify({"success": False, "error": f"Étape {step} inconnue"}), 400

        node = QUESTIONNAIRE_TREE[step]

        # Filtrer les questions conditionnelles
        questions_filtrees = []
        for q in node['questions']:
            cond = q.get('condition')
            if cond:
                field_val = answers.get(cond['field'], '')
                if isinstance(field_val, list):
                    if not any(v in cond['values'] for v in field_val):
                        continue
                elif field_val not in cond['values']:
                    continue
            questions_filtrees.append(q)

        # Adapter les questions en fonction du secteur
        secteur = answers.get('secteur', '')
        for q in questions_filtrees:
            if q['id'] == 'panier_moyen_estime' and secteur in MARKET_DATA.get('secteurs', {}):
                info = MARKET_DATA['secteurs'][secteur]
                q['placeholder'] = f"Moyenne du secteur: {info['panier_moyen']} DT"
                q['hint'] = f"Le panier moyen dans le secteur {info['nom']} est d'environ {info['panier_moyen']} DT"

        total_steps = len(QUESTIONNAIRE_TREE)
        progression = round(step / total_steps * 100)

        return jsonify({
            "success": True,
            "step": step,
            "total_steps": total_steps,
            "progression": progression,
            "titre": node['titre'],
            "questions": questions_filtrees,
            "allQuestions": node['questions'],  # toutes les questions de l'étape (pour détecter les conditions)
            "step_suivant": node['step_suivant'],
            "is_last": node['step_suivant'] is None
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ===================================================================
# 4) POST /api/business-plan — Générer un business plan structuré
# ===================================================================
@app.route('/api/business-plan', methods=['POST'])
def business_plan():
    try:
        d = request.get_json(force=True)
        answers = d.get('answers', {})
        simulation = d.get('simulation', {})

        secteur = answers.get('secteur', 'autre')
        secteur_info = MARKET_DATA.get('secteurs', {}).get(secteur, {})
        secteur_nom = secteur_info.get('nom', secteur.capitalize())

        plan = {
            "titre": f"Business Plan — {answers.get('description_projet', 'Mon Projet')}",
            "date_generation": "Généré automatiquement",
            "sections": []
        }

        # 1. Résumé exécutif
        budget_label = {
            "moins_5000": "moins de 5 000 DT",
            "5000_20000": "5 000 - 20 000 DT",
            "20000_50000": "20 000 - 50 000 DT",
            "50000_100000": "50 000 - 100 000 DT",
            "plus_100000": "plus de 100 000 DT"
        }.get(answers.get('budget_initial', ''), answers.get('budget_initial', 'Non défini'))

        plan["sections"].append({
            "id": "resume_executif",
            "titre": "📋 Résumé Exécutif",
            "contenu": (
                f"Ce projet s'inscrit dans le secteur **{secteur_nom}** en Tunisie. "
                f"{answers.get('description_projet', '')}. "
                f"Le marché cible est constitué de clients **{answers.get('type_client', 'B2C')}** "
                f"dans la région **{answers.get('localisation', 'Grand Tunis')}**. "
                f"Le budget initial est de **{budget_label}** avec un objectif de chiffre d'affaires "
                f"de **{_safe_float(answers.get('ca_objectif_an1', 0)):,.0f} DT** la première année."
            ),
            "points_cles": [
                f"Secteur: {secteur_nom}",
                f"Stade: {answers.get('stade_projet', 'Idée')}",
                f"Budget: {budget_label}",
                f"Objectif CA An 1: {_safe_float(answers.get('ca_objectif_an1', 0)):,.0f} DT"
            ]
        })

        # 2. Analyse de marché
        benchmarks = MARKET_DATA.get('benchmarks_sectoriels', {}).get(secteur, {})
        taille_marche = secteur_info.get('taille_marche_mdt', 'N/A')
        croissance = secteur_info.get('taux_croissance_annuel', 'N/A')

        plan["sections"].append({
            "id": "analyse_marche",
            "titre": "📊 Analyse de Marché",
            "contenu": (
                f"Le marché **{secteur_nom}** en Tunisie représente environ **{taille_marche} millions DT** "
                f"avec un taux de croissance annuel de **{croissance}%**. "
                f"La concurrence est **{secteur_info.get('concurrence', 'moyenne')}** et "
                f"la barrière à l'entrée est **{secteur_info.get('barriere_entree', 'moyenne')}**."
            ),
            "donnees": {
                "taille_marche_mdt": taille_marche,
                "croissance_pct": croissance,
                "concurrence": secteur_info.get('concurrence', 'moyenne'),
                "benchmarks": benchmarks
            },
            "opportunites": [
                f"Pénétration internet en Tunisie: {MARKET_DATA['indicateurs_macro']['penetration_internet_pct']}%",
                f"Pénétration smartphone: {MARKET_DATA['indicateurs_macro']['penetration_smartphone_pct']}%",
                f"Nombre de startups labellisées: {MARKET_DATA['indicateurs_macro']['nombre_startups_labelisees']}"
            ],
            "menaces": [
                f"Taux d'inflation: {MARKET_DATA['indicateurs_macro']['taux_inflation_pct']}%",
                f"Taux de chômage: {MARKET_DATA['indicateurs_macro']['taux_chomage_pct']}%",
                f"Concurrence: {answers.get('concurrence_directe', 'Non évalué')}"
            ]
        })

        # 3. Modèle économique
        modeles_revenu = answers.get('modele_revenu', [])
        if isinstance(modeles_revenu, str):
            modeles_revenu = [modeles_revenu]

        panier = _safe_float(answers.get('panier_moyen_estime', secteur_info.get('panier_moyen', 50)))
        objectif_clients = _safe_int(answers.get('objectif_clients_an1', 500))
        ca_estime = panier * objectif_clients

        plan["sections"].append({
            "id": "modele_economique",
            "titre": "💰 Modèle Économique",
            "contenu": (
                f"Le modèle de revenus repose sur: **{', '.join(modeles_revenu) if modeles_revenu else 'Non défini'}**. "
                f"Avec un panier moyen de **{panier:.0f} DT** et un objectif de **{objectif_clients}** clients "
                f"la première année, le CA estimé est de **{ca_estime:,.0f} DT**."
            ),
            "projections": {
                "panier_moyen_dt": panier,
                "clients_an1": objectif_clients,
                "ca_estime_an1": ca_estime,
                "ca_estime_an2": ca_estime * 1.5,
                "ca_estime_an3": ca_estime * 2.2
            },
            "modeles_revenu": modeles_revenu,
            "frequence_achat": answers.get('frequence_achat', 'mensuel')
        })

        # 4. Projections financières (utiliser simulation si disponible)
        avant = simulation.get('avant', {})
        apres = simulation.get('apres', {})

        plan["sections"].append({
            "id": "projections_financieres",
            "titre": "📈 Projections Financières",
            "contenu": (
                f"Basé sur la simulation de stress-test, le résultat mensuel en conditions normales est de "
                f"**{avant.get('resultat_mensuel', 'N/A')} DT** avec un seuil de rentabilité à "
                f"**{avant.get('seuil_rentabilite', 'N/A')} commandes/mois**."
            ),
            "simulation_avant": avant,
            "simulation_apres": apres,
            "couts_demarrage": _estimer_couts_demarrage(secteur, answers),
            "compte_resultat_previsionnel": {
                "an1": {
                    "ca": ca_estime,
                    "charges_variables": ca_estime * (1 - secteur_info.get('marge_moyenne_pct', 25) / 100),
                    "charges_fixes_annuelles": avant.get('charges_fixes', 3000) * 12,
                    "resultat_net": ca_estime * secteur_info.get('marge_moyenne_pct', 25) / 100 - avant.get('charges_fixes', 3000) * 12
                }
            }
        })

        # 5. Risques et mitigation
        risque_principal = answers.get('risque_principal', 'marche')
        risques = _generer_analyse_risques(risque_principal, secteur, answers)
        plan["sections"].append({
            "id": "risques",
            "titre": "⚠️ Analyse des Risques",
            "contenu": f"Le risque principal identifié est: **{risque_principal}**.",
            "matrice_risques": risques
        })

        # 6. Recommandations et plan d'action
        plan["sections"].append({
            "id": "recommandations",
            "titre": "🎯 Recommandations & Plan d'Action",
            "contenu": "Actions prioritaires pour les 12 prochains mois.",
            "actions": _generer_plan_action(answers, secteur),
            "financements_recommandes": _recommander_financements(answers)
        })

        return jsonify({"success": True, "business_plan": plan})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _estimer_couts_demarrage(secteur, answers):
    couts = MARKET_DATA.get('couts_startup', {})
    creation = couts.get('creation_entreprise', {}).get('suarl', {})
    charges = couts.get('charges_fixes_mensuelles', {})

    return {
        "creation_entreprise": creation.get('frais_creation_dt', 350),
        "equipement_initial": 5000 if secteur in ['foodtech', 'healthtech'] else 2000,
        "marketing_lancement": 3000,
        "fond_roulement_3_mois": (
            charges.get('bureau_coworking', {}).get('min', 150) +
            charges.get('internet_fibre', {}).get('min', 50) +
            charges.get('hebergement_web', {}).get('min', 20)
        ) * 3,
        "total_estime": None  # calculé côté client
    }


def _generer_analyse_risques(risque_principal, secteur, answers):
    risques_map = {
        "marche": {
            "risque": "Risque de marché",
            "probabilite": "moyenne",
            "impact": "élevé",
            "mitigation": "Validez votre marché avec un MVP et 50 entretiens clients avant d'investir massivement."
        },
        "concurrence": {
            "risque": "Concurrence intense",
            "probabilite": "élevée" if MARKET_DATA.get('secteurs', {}).get(secteur, {}).get('concurrence') == 'forte' else "moyenne",
            "impact": "moyen",
            "mitigation": "Différenciez-vous clairement. Ciblez un segment de niche au début."
        },
        "financement": {
            "risque": "Insuffisance de trésorerie",
            "probabilite": "élevée",
            "impact": "critique",
            "mitigation": "Constituez une réserve de 6 mois de charges fixes. Explorez le Startup Act et les SICAR."
        },
        "equipe": {
            "risque": "Difficulté de recrutement",
            "probabilite": "moyenne",
            "impact": "moyen",
            "mitigation": "Rejoignez des communautés tech tunisiennes. Proposez de l'equity pour attirer des talents."
        },
        "reglementation": {
            "risque": "Obstacles réglementaires",
            "probabilite": "moyenne",
            "impact": "élevé",
            "mitigation": "Consultez un avocat spécialisé. Le Startup Act offre des avantages réglementaires significatifs."
        },
        "technologie": {
            "risque": "Défis techniques",
            "probabilite": "moyenne",
            "impact": "moyen",
            "mitigation": "Utilisez des technologies éprouvées. Externalisez les développements non critiques."
        },
        "execution": {
            "risque": "Capacité d'exécution",
            "probabilite": "moyenne",
            "impact": "élevé",
            "mitigation": "Consacrez-vous à temps plein. Priorisez rigoureusement et utilisez la méthode OKR."
        }
    }

    result = []
    # Risque principal en premier
    if risque_principal in risques_map:
        entry = risques_map[risque_principal].copy()
        entry['principal'] = True
        result.append(entry)

    # Ajouter 2-3 risques complémentaires
    for key, val in risques_map.items():
        if key != risque_principal and len(result) < 4:
            entry = val.copy()
            entry['principal'] = False
            result.append(entry)

    return result


def _generer_plan_action(answers, secteur):
    actions = []
    stade = answers.get('stade_projet', 'idee')

    if stade == 'idee':
        actions = [
            {"mois": "Mois 1-2", "action": "Validation du marché", "details": "50 entretiens clients, étude concurrentielle, landing page test"},
            {"mois": "Mois 2-3", "action": "Développement MVP", "details": "Construire un prototype minimal fonctionnel"},
            {"mois": "Mois 3-4", "action": "Tests utilisateurs", "details": "Beta-test avec 20-50 utilisateurs early adopters"},
            {"mois": "Mois 4-6", "action": "Itération produit", "details": "Améliorer le produit selon les retours, préparer le lancement"},
            {"mois": "Mois 6-8", "action": "Lancement commercial", "details": "Marketing digital, réseaux sociaux, premiers clients payants"},
            {"mois": "Mois 8-12", "action": "Croissance", "details": "Optimiser l'acquisition, fidéliser, préparer le scaling"}
        ]
    elif stade == 'mvp':
        actions = [
            {"mois": "Mois 1-2", "action": "Beta-test élargi", "details": "Recruter 100 beta-testeurs, collecter les feedbacks"},
            {"mois": "Mois 2-3", "action": "Product-market fit", "details": "Valider le PMF (40%+ répondraient 'très déçus' sans votre produit)"},
            {"mois": "Mois 3-5", "action": "Go-to-market", "details": "Stratégie d'acquisition, partenariats, contenu"},
            {"mois": "Mois 5-8", "action": "Croissance organique", "details": "SEO, réseaux sociaux, bouche-à-oreille"},
            {"mois": "Mois 8-12", "action": "Monétisation + levée", "details": "Optimiser la conversion, préparer dossier de financement"}
        ]
    elif stade == 'lance':
        actions = [
            {"mois": "Mois 1-3", "action": "Optimisation", "details": "Améliorer les KPIs clés (conversion, rétention, NPS)"},
            {"mois": "Mois 3-6", "action": "Scaling marketing", "details": "Doubler le budget marketing sur les canaux performants"},
            {"mois": "Mois 6-9", "action": "Expansion produit", "details": "Nouvelles features, upsell, cross-sell"},
            {"mois": "Mois 9-12", "action": "Structuration", "details": "Recrutements clés, processus, préparation levée de fonds"}
        ]
    else:
        actions = [
            {"mois": "Mois 1-3", "action": "Levée de fonds", "details": "Préparer le pitch deck, contacter les investisseurs (SICAR, BA)"},
            {"mois": "Mois 3-6", "action": "Scaling équipe", "details": "Recruter les profils clés, structurer les processus"},
            {"mois": "Mois 6-9", "action": "Expansion géographique", "details": "Lancement dans de nouvelles régions / marchés"},
            {"mois": "Mois 9-12", "action": "International", "details": "Étude de marché MENA, adaptation produit"}
        ]

    return actions


def _recommander_financements(answers):
    """Recommander les sources de financement adaptées."""
    financements = MARKET_DATA.get('financement', {})
    recs = []

    budget = answers.get('budget_initial', '')
    stade = answers.get('stade_projet', 'idee')

    # Startup Act pour tous
    recs.append({
        "source": financements.get('startup_act', {}).get('nom', 'Startup Act'),
        "type": "Programme gouvernemental",
        "pertinence": "haute",
        "raison": "Exonérations fiscales et avantages pendant 8 ans"
    })

    if budget in ['moins_5000', '5000_20000']:
        recs.append({
            "source": "BFPME",
            "type": "Prêt bancaire",
            "pertinence": "haute",
            "raison": "Financement adapté aux petits budgets avec taux préférentiel"
        })

    if stade in ['lance', 'croissance']:
        recs.append({
            "source": "SICAR / Business Angels",
            "type": "Capital risque",
            "pertinence": "haute",
            "raison": "Capital et accompagnement pour accélérer la croissance"
        })
        recs.append({
            "source": "Flat6Labs Tunis",
            "type": "Accélérateur",
            "pertinence": "moyenne",
            "raison": "Financement de 30-120K DT + mentorat intensif"
        })

    if stade == 'idee':
        recs.append({
            "source": "Smart Capital",
            "type": "Fonds public",
            "pertinence": "moyenne",
            "raison": "Co-investissement et subventions pour les projets innovants"
        })

    return recs


# ===================================================================
# 5) POST /api/pivot-scenarios — Planificateur de scénarios pivot
# ===================================================================
@app.route('/api/pivot-scenarios', methods=['POST'])
def pivot_scenarios():
    try:
        d = request.get_json(force=True)

        # Paramètres actuels
        panier_moyen   = _safe_float(d.get('panier_moyen', 50))
        cout_produits   = _safe_float(d.get('cout_produits', 20))
        cout_transport  = _safe_float(d.get('cout_transport', 7))
        charges_fixes   = _safe_float(d.get('charges_fixes', 3000))
        commandes_mois  = _safe_float(d.get('commandes_mois', 200))
        marge_pct       = _safe_float(d.get('marge_pct', 25))
        secteur_actuel  = d.get('secteur', 'ecommerce')
        pivot_type      = d.get('pivot_type', 'premium')

        # Calculs actuels
        marge_unitaire_actuel = panier_moyen * marge_pct / 100
        resultat_actuel = commandes_mois * marge_unitaire_actuel - charges_fixes
        ca_actuel = commandes_mois * panier_moyen

        # Scénarios de pivot
        pivots = {
            "premium": {
                "nom": "Montée en gamme (Premium)",
                "description": "Augmenter les prix et la qualité, cibler une clientèle plus aisée",
                "facteur_prix": 1.6,
                "facteur_volume": 0.6,
                "facteur_marge": 1.3,
                "facteur_charges": 1.2,
                "risque": "moyen",
                "delai_transition_mois": 4,
                "actions": [
                    "Repositionner la marque avec un branding premium",
                    "Améliorer la qualité du produit/service",
                    "Réduire le volume, augmenter la valeur",
                    "Cibler les quartiers aisés (La Marsa, Lac, Carthage)"
                ]
            },
            "volume": {
                "nom": "Stratégie volume (Low-cost)",
                "description": "Baisser les prix pour capturer un maximum de parts de marché",
                "facteur_prix": 0.65,
                "facteur_volume": 2.0,
                "facteur_marge": 0.7,
                "facteur_charges": 1.4,
                "risque": "élevé",
                "delai_transition_mois": 3,
                "actions": [
                    "Optimiser la chaîne d'approvisionnement",
                    "Automatiser les processus",
                    "Marketing de masse (Facebook, TikTok)",
                    "Négocier des prix fournisseurs en volume"
                ]
            },
            "niche": {
                "nom": "Spécialisation niche",
                "description": "Se concentrer sur un segment très spécifique mal desservi",
                "facteur_prix": 1.2,
                "facteur_volume": 0.5,
                "facteur_marge": 1.5,
                "facteur_charges": 0.8,
                "risque": "faible",
                "delai_transition_mois": 2,
                "actions": [
                    "Identifier le sous-segment le plus rentable",
                    "Devenir l'expert reconnu de cette niche",
                    "Créer du contenu ultra-ciblé",
                    "Développer des partenariats avec des influenceurs de niche"
                ]
            },
            "b2b": {
                "nom": "Pivot B2B",
                "description": "Passer du B2C au B2B (ou inversement) pour des contrats plus stables",
                "facteur_prix": 2.5,
                "facteur_volume": 0.3,
                "facteur_marge": 1.2,
                "facteur_charges": 1.1,
                "risque": "moyen",
                "delai_transition_mois": 6,
                "actions": [
                    "Adapter l'offre aux besoins des entreprises",
                    "Recruter un commercial B2B",
                    "Développer un pipeline de prospection",
                    "Créer des cas d'usage et témoignages clients"
                ]
            },
            "plateforme": {
                "nom": "Pivot plateforme / marketplace",
                "description": "Devenir une plateforme connectant offre et demande, prenant une commission",
                "facteur_prix": 0.8,
                "facteur_volume": 3.0,
                "facteur_marge": 0.5,
                "facteur_charges": 1.5,
                "risque": "élevé",
                "delai_transition_mois": 8,
                "actions": [
                    "Développer la plateforme technique (double interface)",
                    "Résoudre le problème de la poule et l'œuf (offre/demande)",
                    "Lancer dans une zone géographique limitée",
                    "Subventionner un côté du marché pour amorcer"
                ]
            },
            "abonnement": {
                "nom": "Modèle abonnement / récurrent",
                "description": "Transformer les ventes ponctuelles en revenus récurrents mensuels",
                "facteur_prix": 0.4,
                "facteur_volume": 1.5,
                "facteur_marge": 1.1,
                "facteur_charges": 1.05,
                "risque": "faible",
                "delai_transition_mois": 3,
                "actions": [
                    "Créer des formules d'abonnement avec paliers",
                    "Offrir un mois gratuit pour convertir",
                    "Développer la rétention (programme fidélité)",
                    "Automatiser le renouvellement et la facturation"
                ]
            }
        }

        pivot = pivots.get(pivot_type, pivots['premium'])

        # Calculs du scénario pivot
        panier_pivot = panier_moyen * pivot['facteur_prix']
        commandes_pivot = commandes_mois * pivot['facteur_volume']
        marge_pct_pivot = marge_pct * pivot['facteur_marge']
        charges_pivot = charges_fixes * pivot['facteur_charges']

        marge_unitaire_pivot = panier_pivot * marge_pct_pivot / 100
        resultat_pivot = commandes_pivot * marge_unitaire_pivot - charges_pivot
        ca_pivot = commandes_pivot * panier_pivot

        seuil_actuel = math.ceil(charges_fixes / marge_unitaire_actuel) if marge_unitaire_actuel > 0 else None
        seuil_pivot = math.ceil(charges_pivot / marge_unitaire_pivot) if marge_unitaire_pivot > 0 else None

        return jsonify({
            "success": True,
            "scenario_actuel": {
                "panier_moyen": round(panier_moyen, 2),
                "commandes_mois": round(commandes_mois),
                "marge_pct": round(marge_pct, 1),
                "ca_mensuel": round(ca_actuel, 2),
                "resultat_mensuel": round(resultat_actuel, 2),
                "seuil_rentabilite": seuil_actuel,
                "charges_fixes": round(charges_fixes, 2)
            },
            "scenario_pivot": {
                "nom": pivot['nom'],
                "description": pivot['description'],
                "panier_moyen": round(panier_pivot, 2),
                "commandes_mois": round(commandes_pivot),
                "marge_pct": round(marge_pct_pivot, 1),
                "ca_mensuel": round(ca_pivot, 2),
                "resultat_mensuel": round(resultat_pivot, 2),
                "seuil_rentabilite": seuil_pivot,
                "charges_fixes": round(charges_pivot, 2),
                "risque": pivot['risque'],
                "delai_transition_mois": pivot['delai_transition_mois'],
                "actions_requises": pivot['actions']
            },
            "comparaison": {
                "variation_ca": round(ca_pivot - ca_actuel, 2),
                "variation_ca_pct": round((ca_pivot - ca_actuel) / ca_actuel * 100, 1) if ca_actuel > 0 else 0,
                "variation_resultat": round(resultat_pivot - resultat_actuel, 2),
                "variation_resultat_pct": round((resultat_pivot - resultat_actuel) / abs(resultat_actuel) * 100, 1) if resultat_actuel != 0 else 0,
                "recommendation": _recommander_pivot(resultat_actuel, resultat_pivot, pivot)
            },
            "pivots_disponibles": [
                {"value": k, "label": v['nom'], "risque": v['risque']}
                for k, v in pivots.items()
            ]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _recommander_pivot(resultat_actuel, resultat_pivot, pivot):
    if resultat_pivot > resultat_actuel * 1.3:
        return {
            "verdict": "recommandé",
            "emoji": "✅",
            "texte": f"Ce pivot {pivot['nom']} améliorerait significativement votre résultat. Le risque est {pivot['risque']} avec un délai de transition de {pivot['delai_transition_mois']} mois."
        }
    elif resultat_pivot > resultat_actuel:
        return {
            "verdict": "à considérer",
            "emoji": "🤔",
            "texte": f"Le pivot apporte une amélioration modeste. Évaluez si le risque ({pivot['risque']}) et l'effort de transition ({pivot['delai_transition_mois']} mois) en valent la peine."
        }
    else:
        return {
            "verdict": "déconseillé",
            "emoji": "⚠️",
            "texte": f"Ce pivot réduirait votre résultat. Votre modèle actuel semble plus performant. Explorez d'autres types de pivot."
        }


# ===================================================================
# 6) POST /api/persona-simulator — Simulation de personas clients
# ===================================================================
@app.route('/api/persona-simulator', methods=['POST'])
def persona_simulator():
    try:
        d = request.get_json(force=True)
        secteur = d.get('secteur', 'ecommerce')
        type_produit = d.get('type_produit', 'Produit général')
        prix_range = d.get('prix_range', 'moyen')  # bas, moyen, haut

        personas_base = MARKET_DATA.get('personas_types', {})
        secteur_info = MARKET_DATA.get('secteurs', {}).get(secteur, {})

        # Sélectionner les personas pertinents selon le secteur et le prix
        personas_pertinents = _selectionner_personas(secteur, prix_range, personas_base)

        personas_generes = []
        prenoms_m = ["Ahmed", "Mohamed", "Youssef", "Amine", "Khaled", "Nizar", "Slim", "Rami"]
        prenoms_f = ["Amira", "Sara", "Ines", "Mariem", "Fatma", "Nour", "Rim", "Yasmine"]

        for i, (type_persona, base) in enumerate(personas_pertinents):
            is_femme = i % 2 == 1
            prenom = random.choice(prenoms_f if is_femme else prenoms_m)
            age = random.randint(base['age_range'][0], base['age_range'][1])

            persona = {
                "id": i + 1,
                "nom": prenom,
                "age": age,
                "type": type_persona,
                "profil": _generer_profil_persona(type_persona, age, is_femme),
                "demographiques": {
                    "age": age,
                    "genre": "Femme" if is_femme else "Homme",
                    "localisation": _localisation_persona(base['localisation']),
                    "revenu_mensuel_dt": base['revenu_moyen_dt'],
                    "situation": _situation_persona(type_persona, age)
                },
                "comportements": {
                    "canaux_preferes": base['canaux_preferes'],
                    "comportement_achat": base['comportement_achat'],
                    "frequence_achat": _frequence_par_type(type_persona, secteur),
                    "panier_moyen_estime_dt": _panier_persona(base['revenu_moyen_dt'], prix_range),
                    "sensibilite_prix": base['sensibilite_prix'],
                    "moment_achat": _moment_achat(type_persona)
                },
                "pain_points": _pain_points_persona(type_persona, secteur),
                "motivations": _motivations_persona(type_persona, secteur),
                "willingness_to_pay": {
                    "max_dt": _wtpay(base['revenu_moyen_dt'], prix_range, base['sensibilite_prix']),
                    "facteurs_decision": _facteurs_decision(type_persona, base['sensibilite_prix'])
                },
                "scenario_utilisation": _scenario_utilisation(type_persona, secteur, type_produit)
            }
            personas_generes.append(persona)

        return jsonify({
            "success": True,
            "personas": personas_generes,
            "secteur": secteur_info.get('nom', secteur),
            "conseil_ciblage": _conseil_ciblage(personas_generes, secteur)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _selectionner_personas(secteur, prix_range, personas_base):
    """Sélectionner les personas les plus pertinents."""
    mapping = {
        'livraison': ['jeune_professionnel', 'famille', 'etudiant', 'entrepreneur'],
        'ecommerce': ['jeune_professionnel', 'etudiant', 'famille', 'senior'],
        'services': ['entrepreneur', 'jeune_professionnel', 'famille'],
        'foodtech': ['etudiant', 'jeune_professionnel', 'famille', 'entrepreneur'],
        'edtech': ['etudiant', 'jeune_professionnel', 'famille'],
        'healthtech': ['senior', 'famille', 'jeune_professionnel'],
        'fintech': ['jeune_professionnel', 'entrepreneur', 'etudiant'],
        'agritech': ['entrepreneur', 'famille']
    }
    types = mapping.get(secteur, ['jeune_professionnel', 'famille', 'etudiant', 'entrepreneur'])
    # Prendre 3-4 personas
    types = types[:4]
    return [(t, personas_base.get(t, personas_base['jeune_professionnel'])) for t in types if t in personas_base]


def _generer_profil_persona(type_p, age, is_femme):
    profils = {
        'etudiant': f"Étudiant{'e' if is_femme else ''} en informatique à l'Université de Tunis, passionné{'e' if is_femme else ''} de technologie",
        'jeune_professionnel': f"Cadre dans une entreprise tech au Lac 2, actif{'ve' if is_femme else ''} sur les réseaux sociaux",
        'famille': f"Parent de 2 enfants, travaille dans le secteur privé, habite dans la banlieue de Tunis",
        'entrepreneur': f"Fondateur{'rice' if is_femme else ''} d'une PME, toujours à la recherche de solutions pour optimiser son activité",
        'senior': f"Retraité{'e' if is_femme else ''}, résident{'e' if is_femme else ''} à Sousse, utilise un smartphone mais préfère la simplicité"
    }
    return profils.get(type_p, f"Professionnel{'le' if is_femme else ''} actif{'ve' if is_femme else ''} en Tunisie")


def _localisation_persona(loc_type):
    locs = {
        'urbain': random.choice(["Tunis Centre", "La Marsa", "Lac 2", "Ariana", "Sousse"]),
        'urbain_periurbain': random.choice(["Manouba", "Ben Arous", "Hammam Sousse", "Monastir"]),
    }
    return locs.get(loc_type, random.choice(["Tunis", "Sousse", "Sfax"]))


def _situation_persona(type_p, age):
    sits = {
        'etudiant': "Célibataire, vit chez ses parents ou en colocation",
        'jeune_professionnel': "Célibataire ou en couple, premier appartement" if age < 30 else "En couple, locataire",
        'famille': "Marié(e), 2-3 enfants, propriétaire",
        'entrepreneur': "En couple, mobilité professionnelle élevée",
        'senior': "Marié(e), enfants adultes, propriétaire"
    }
    return sits.get(type_p, "Actif")


def _frequence_par_type(type_p, secteur):
    freqs = {
        ('etudiant', 'foodtech'): "3-4 fois par semaine",
        ('etudiant', 'ecommerce'): "2-3 fois par mois",
        ('jeune_professionnel', 'livraison'): "5+ fois par semaine",
        ('jeune_professionnel', 'foodtech'): "quotidien",
        ('famille', 'ecommerce'): "2 fois par mois",
        ('famille', 'foodtech'): "1-2 fois par semaine",
        ('entrepreneur', 'services'): "hebdomadaire",
        ('senior', 'healthtech'): "mensuel",
    }
    return freqs.get((type_p, secteur), "mensuel")


def _panier_persona(revenu, prix_range):
    factors = {'bas': 0.02, 'moyen': 0.04, 'haut': 0.08}
    return round(revenu * factors.get(prix_range, 0.04))


def _moment_achat(type_p):
    moments = {
        'etudiant': "Soir (20h-23h), weekend",
        'jeune_professionnel': "Pause déjeuner, soir après le travail",
        'famille': "Weekend, mercredi soir",
        'entrepreneur': "Heures de bureau (9h-18h)",
        'senior': "Matin (9h-12h), début d'après-midi"
    }
    return moments.get(type_p, "Variable")


def _pain_points_persona(type_p, secteur):
    points = {
        'etudiant': [
            "Budget très limité, chaque dinar compte",
            "Méfiance envers les paiements en ligne",
            "Délais de livraison trop longs",
            "Manque de choix adaptés aux petits budgets"
        ],
        'jeune_professionnel': [
            "Manque de temps pour comparer les offres",
            "Qualité de service inconsistante",
            "Difficulté à trouver des services premium en Tunisie",
            "Frustration avec les interfaces mal conçues"
        ],
        'famille': [
            "Préoccupation prix/qualité",
            "Peur des arnaques en ligne",
            "Besoin de fiabilité et de suivi",
            "Peu de solutions adaptées aux familles"
        ],
        'entrepreneur': [
            "Solutions existantes pas adaptées au marché tunisien",
            "Manque de fournisseurs fiables",
            "Lenteur administrative",
            "Coûts élevés des solutions internationales"
        ],
        'senior': [
            "Complexité des interfaces numériques",
            "Besoin d'accompagnement humain",
            "Méfiance envers la technologie",
            "Accessibilité limitée"
        ]
    }
    return points.get(type_p, ["Besoin non satisfait", "Prix élevé", "Manque de qualité"])


def _motivations_persona(type_p, secteur):
    motivations = {
        'etudiant': ["Prix bas et promotions", "Nouveauté et tendances", "Recommandations d'amis", "Facilité d'utilisation mobile"],
        'jeune_professionnel': ["Gain de temps", "Qualité supérieure", "Expérience utilisateur fluide", "Marque et réputation"],
        'famille': ["Bon rapport qualité-prix", "Sécurité et fiabilité", "Avis d'autres familles", "Praticité"],
        'entrepreneur': ["ROI mesurable", "Efficacité opérationnelle", "Support réactif", "Intégration facile"],
        'senior': ["Simplicité d'utilisation", "Contact humain disponible", "Confiance et sécurité", "Proximité locale"]
    }
    return motivations.get(type_p, ["Qualité", "Prix", "Service"])


def _wtpay(revenu, prix_range, sensibilite):
    base = revenu * {'bas': 0.03, 'moyen': 0.06, 'haut': 0.12}.get(prix_range, 0.06)
    factor = {'très élevée': 0.6, 'élevée': 0.8, 'moyenne': 1.0, 'faible': 1.3}.get(sensibilite, 1.0)
    return round(base * factor)


def _facteurs_decision(type_p, sensibilite):
    if sensibilite in ['très élevée', 'élevée']:
        return ["Prix d'abord", "Promotions / remises", "Comparaison des offres", "Avis clients"]
    elif type_p == 'entrepreneur':
        return ["ROI démontré", "Témoignages professionnels", "Support technique", "Facilité d'intégration"]
    else:
        return ["Qualité perçue", "Réputation de la marque", "Recommandations", "Expérience utilisateur"]


def _scenario_utilisation(type_p, secteur, produit):
    scenarios = {
        ('etudiant', 'foodtech'): f"Commande {produit} depuis le campus entre les cours via l'app mobile, paye en espèces à la livraison.",
        ('jeune_professionnel', 'ecommerce'): f"Browse {produit} pendant la pause déjeuner, commande depuis le bureau, utilise le paiement par carte.",
        ('famille', 'livraison'): f"Commande des {produit} le weekend pour toute la famille, vérifie le suivi de livraison sur WhatsApp.",
        ('entrepreneur', 'services'): f"Cherche {produit} pour optimiser son entreprise, compare 3 solutions, demande une démo avant de décider.",
        ('senior', 'healthtech'): f"Son fils l'aide à s'inscrire. Utilise {produit} mensuellement avec un rappel SMS.",
    }
    key = (type_p, secteur)
    return scenarios.get(key, f"Découvre {produit} via les réseaux sociaux et effectue un premier achat pour tester.")


def _conseil_ciblage(personas, secteur):
    """Générer des conseils de ciblage basés sur les personas."""
    sensibilites = [p['comportements']['sensibilite_prix'] for p in personas]
    canaux = set()
    for p in personas:
        canaux.update(p['comportements']['canaux_preferes'])

    return {
        "persona_prioritaire": personas[0]['type'] if personas else "jeune_professionnel",
        "canaux_recommandes": list(canaux)[:4],
        "strategie_prix": "Proposez des formules accessibles avec des options premium" if 'très élevée' in sensibilites else "Misez sur la valeur perçue plutôt que sur les prix bas",
        "conseil": f"Commencez par cibler les {personas[0]['type'].replace('_', ' ')}s dans le Grand Tunis, puis élargissez."
    }


# ===================================================================
# 7) POST /api/ai-advice — Conseils expert (rule-based)
# ===================================================================
@app.route('/api/ai-advice', methods=['POST'])
def ai_advice():
    try:
        d = request.get_json(force=True)

        secteur = d.get('secteur', 'autre')
        stade = d.get('stade', 'idee')
        budget = d.get('budget', 'moyen')
        type_client = d.get('type_client', 'b2c')
        marge_pct = _safe_float(d.get('marge_pct', 25))
        resultat_mensuel = _safe_float(d.get('resultat_mensuel', 0))
        commandes = _safe_float(d.get('commandes_mois', 0))
        concurrence = d.get('concurrence', 'moyen')
        risque = d.get('risque_principal', '')
        modele_revenu = d.get('modele_revenu', [])
        if isinstance(modele_revenu, str):
            modele_revenu = [modele_revenu]

        # Chiffres réels du simulateur (optionnels)
        panier_moyen = _safe_float(d.get('panier_moyen', 0))
        cout_transport = _safe_float(d.get('cout_transport', 0))
        charges_fixes = _safe_float(d.get('charges_fixes', 0))
        seuil_rentabilite = d.get('seuil_rentabilite')
        variation_pct = _safe_float(d.get('variation_resultat_pct', 0))
        contexte_chiffres = d.get('contexte_chiffres', [])
        question_posee = d.get('question_posee', '')
        description_projet = d.get('description_projet', '')

        # Contexte financier enrichi transmis aux fonctions conseil
        ctx = {
            'panier_moyen': panier_moyen,
            'cout_transport': cout_transport,
            'charges_fixes': charges_fixes,
            'seuil_rentabilite': seuil_rentabilite,
            'variation_pct': variation_pct,
            'resultat_mensuel': resultat_mensuel,
            'commandes': commandes,
            'marge_pct': marge_pct,
            'question': question_posee,
            'description': description_projet,
        }

        # Traitement conversationnel intelligent si une question est posée
        if question_posee:
            q = question_posee.strip().lower()
            greetings = ['bonjour', 'salut', 'salam', 'hello', 'coucou', 'bonsoir', 'hey', 'bjr', 'slm', 'slt', 'assalamou', 'ahla', 'aslema']
            
            # 1. Salutations simples
            if any(q == g or (q.startswith(g) and len(q.split()) <= 3) for g in greetings):
                return jsonify({
                    "success": True,
                    "type": "conversation",
                    "reponse": "Bonjour ! 👋 Je suis votre copilote IA pour votre startup en Tunisie.\n\nJe peux analyser la viabilité de votre projet, optimiser vos coûts ou vous guider sur les financements tunisiens.\n\nQue souhaitez-vous explorer ?",
                    "suggestions": [
                        "Mon transport coûte trop cher, que faire ?",
                        "Comment financer mon projet en Tunisie ?",
                        "Comment optimiser mes marges et mon prix ?",
                        "Analyser la viabilité de mon projet"
                    ]
                })

            # 2. Questions thématiques ciblées (on renvoie uniquement le conseil pertinent sans le dump complet)
            if any(w in q for w in ['transport', 'livraison', 'logistique', 'livrer']):
                ct = _conseil_transport(cout_transport or 8, panier_moyen or 89, marge_pct, charges_fixes)
                return jsonify({
                    "success": True,
                    "type": "reponse_ciblee",
                    "reponse": "Voici mes recommandations spécifiques pour optimiser votre logistique et réduire vos frais de livraison en Tunisie :",
                    "conseils": {"transport": ct},
                    "suggestions": ["Comment financer mon projet en Tunisie ?", "Optimiser mes prix", "Analyser tout mon projet"]
                })

            if any(w in q for w in ['financ', 'argent', 'startup act', 'subvention', 'investiss', 'bfpme', 'fonds', 'capital', 'aide']):
                cf = _conseil_financement(stade, budget, secteur)
                return jsonify({
                    "success": True,
                    "type": "reponse_ciblee",
                    "reponse": "Voici les meilleures opportunités de financement pour votre projet en Tunisie :",
                    "conseils": {"financement": cf},
                    "suggestions": ["Mon transport coûte trop cher, que faire ?", "Comment optimiser mon prix ?", "Analyser tout mon projet"]
                })

            if any(w in q for w in ['prix', 'marge', 'rentab', 'tarif', 'cher', 'coût', 'cout']):
                cp = _conseil_prix(marge_pct, concurrence, type_client, secteur, ctx)
                return jsonify({
                    "success": True,
                    "type": "reponse_ciblee",
                    "reponse": "Voici mon analyse de votre pricing et de votre structure de marge :",
                    "conseils": {"strategie_prix": cp},
                    "suggestions": ["Comment financer mon projet en Tunisie ?", "Comment réduire le transport ?", "Analyser tout mon projet"]
                })

            if any(w in q for w in ['concurren', 'différenc', 'differenc', 'concurrent']):
                cm = _conseil_entree_marche(secteur, stade, type_client, concurrence)
                return jsonify({
                    "success": True,
                    "type": "reponse_ciblee",
                    "reponse": "Face à la concurrence sur le marché tunisien, voici les leviers prioritaires :",
                    "conseils": {"strategie_entree_marche": cm},
                    "suggestions": ["Stratégie marketing recommandée", "Optimiser mes prix", "Analyser tout mon projet"]
                })

            if any(w in q for w in ['market', 'client', 'vent', 'pub', 'acquisit', 'canal', 'canaux', 'attirer']):
                cmk = _conseil_marketing(secteur, type_client, stade, budget)
                return jsonify({
                    "success": True,
                    "type": "reponse_ciblee",
                    "reponse": "Voici les canaux d'acquisition les plus performants en Tunisie pour votre cible :",
                    "conseils": {"marketing": cmk},
                    "suggestions": ["Comment optimiser mon prix ?", "Comment financer mon projet ?", "Analyser tout mon projet"]
                })

        # 3. Diagnostic complet (quand demandé explicitement ou sans question ciblée)
        conseils = {
            "strategie_entree_marche": _conseil_entree_marche(secteur, stade, type_client, concurrence),
            "strategie_prix": _conseil_prix(marge_pct, concurrence, type_client, secteur, ctx),
            "strategie_croissance": _conseil_croissance(stade, resultat_mensuel, commandes, secteur, ctx),
            "mitigation_risques": _conseil_risques(risque, secteur, stade, budget, ctx),
            "financement": _conseil_financement(stade, budget, secteur),
            "marketing": _conseil_marketing(secteur, type_client, stade, budget)
        }

        # Conseil transport si question sur coût transport
        if question_posee and any(w in question_posee.lower() for w in ['transport', 'livraison']) and cout_transport > 0:
            conseils["transport"] = _conseil_transport(cout_transport, panier_moyen, marge_pct, charges_fixes)

        # Score de confiance (rule-based)
        score_global = _calculer_score_confiance(marge_pct, resultat_mensuel, concurrence, stade)

        return jsonify({
            "success": True,
            "type": "analyse_complete",
            "conseils": conseils,
            "score_confiance": score_global,
            "resume": _resume_conseil(conseils, score_global),
            "contexte_financier": contexte_chiffres
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _conseil_entree_marche(secteur, stade, type_client, concurrence):
    strategies = []
    secteur_info = MARKET_DATA.get('secteurs', {}).get(secteur, {})

    if concurrence in ['fort', 'forte', 'domine']:
        strategies.append({
            "titre": "Différenciation par la niche",
            "priorite": "haute",
            "description": "Dans un marché concurrentiel, ciblez un micro-segment mal desservi. En Tunisie, les segments régionaux (hors Grand Tunis) sont souvent sous-exploités.",
            "actions": [
                "Identifiez 3 sous-segments de votre marché",
                "Testez votre offre dans une ville secondaire (Sousse, Sfax)",
                "Développez un avantage compétitif unique (service, prix, rapidité)"
            ]
        })
    else:
        strategies.append({
            "titre": "Avantage du premier entrant",
            "priorite": "haute",
            "description": f"La concurrence est {concurrence} dans le secteur {secteur_info.get('nom', secteur)}. Profitez-en pour établir votre marque rapidement.",
            "actions": [
                "Lancez rapidement un MVP pour capturer le marché",
                "Investissez dans le contenu et le SEO pour être la référence",
                "Créez des partenariats exclusifs avec les acteurs clés"
            ]
        })

    if type_client in ['b2b', 'b2b2c']:
        strategies.append({
            "titre": "Approche commerciale B2B",
            "priorite": "moyenne",
            "description": "Le B2B en Tunisie fonctionne beaucoup par réseau et confiance personnelle.",
            "actions": [
                "Participez aux événements et salons professionnels tunisiens",
                "Obtenez 3-5 clients pilotes avec des conditions préférentielles",
                "Collectez des témoignages et études de cas"
            ]
        })

    if stade == 'idee':
        strategies.append({
            "titre": "Validation avant lancement",
            "priorite": "critique",
            "description": "Ne construisez rien avant d'avoir validé la demande. 42% des startups échouent car il n'y a pas de besoin réel.",
            "actions": [
                "Créez une landing page et mesurez l'intérêt (objectif: 10% conversion)",
                "Réalisez 50 entretiens de découverte client",
                "Pré-vendez avant de construire (commandes ou lettres d'intention)"
            ]
        })

    return strategies


def _conseil_prix(marge_pct, concurrence, type_client, secteur, ctx=None):
    conseils = []
    ctx = ctx or {}
    panier = ctx.get('panier_moyen', 0)
    seuil = ctx.get('seuil_rentabilite')
    commandes = ctx.get('commandes', 0)

    # Libellé panier si disponible
    panier_txt = f" (panier moyen : {panier:.0f} DT)" if panier > 0 else ""

    if marge_pct < 15:
        seuil_txt = f" Votre seuil de rentabilité est de {seuil} commandes/mois." if seuil else ""
        conseils.append({
            "titre": "Marge trop faible — Urgence pricing",
            "priorite": "critique",
            "description": f"Votre marge de {marge_pct:.0f}%{panier_txt} est dangereusement basse.{seuil_txt} En Tunisie, avec l'inflation à ~8%, vous risquez de perdre de l'argent rapidement.",
            "actions": [
                "Augmentez vos prix de 10-20% (testez d'abord sur un segment)",
                "Réduisez les coûts : négociez avec les fournisseurs",
                "Ajoutez des services premium à marge élevée",
                "Envisagez de supprimer les produits/services à marge négative"
            ]
        })
    elif marge_pct < 25:
        seuil_txt = f" À {commandes:.0f} commandes/mois actuelles, votre seuil de {seuil} cmd/mois est {'atteint ✅' if seuil and commandes >= seuil else 'pas encore atteint ⚠️'}." if seuil and commandes > 0 else ""
        conseils.append({
            "titre": "Optimisation des marges",
            "priorite": "moyenne",
            "description": f"Votre marge de {marge_pct:.0f}%{panier_txt} est correcte mais peut être améliorée. Visez 30%+ pour avoir un coussin de sécurité.{seuil_txt}",
            "actions": [
                "Identifiez les 20% de produits qui génèrent 80% de la marge",
                "Créez des bundles pour augmenter le panier moyen",
                "Explorez les modèles d'abonnement pour des revenus récurrents"
            ]
        })
    else:
        seuil_txt = f" Votre seuil de rentabilité ({seuil} cmd/mois) est bien couvert à {commandes:.0f} cmd/mois actuelles." if seuil and commandes > 0 else ""
        conseils.append({
            "titre": "Bonne marge — Capitaliser",
            "priorite": "info",
            "description": f"Votre marge de {marge_pct:.0f}%{panier_txt} est saine.{seuil_txt} Investissez dans la croissance tout en la maintenant.",
            "actions": [
                "Réinvestissez 20-30% des marges en marketing",
                "Développez des produits complémentaires",
                "Envisagez une stratégie de prix psychologiques (99 DT vs 100 DT)"
            ]
        })

    return conseils


def _conseil_croissance(stade, resultat, commandes, secteur, ctx=None):
    conseils = []
    ctx = ctx or {}
    variation_pct = ctx.get('variation_pct', 0)
    charges_fixes = ctx.get('charges_fixes', 0)

    # Libellés avec vrais chiffres
    res_txt = f"{resultat:,.0f} DT/mois".replace(',', ' ') if resultat != 0 else None
    choc_txt = f" (variation sous stress : {variation_pct:+.0f}%)" if variation_pct != 0 else ""

    if stade in ['idee', 'mvp']:
        conseils.append({
            "titre": "Phase de traction initiale",
            "priorite": "haute",
            "description": "Votre priorité n°1 est d'atteindre le product-market fit. Ne scalez pas tant que ce n'est pas validé.",
            "actions": [
                "Mesurez le Sean Ellis test (40%+ seraient 'très déçus' sans vous)",
                "Visez 100 clients actifs et satisfaits avant de scaler",
                "Itérez rapidement sur le produit (cycles de 2 semaines)",
                "Collectez du feedback qualitatif systématiquement"
            ]
        })
    elif resultat > 0:
        desc = f"Vous êtes rentable ({res_txt}).{choc_txt} C'est le moment d'accélérer en investissant dans les canaux qui fonctionnent." if res_txt else f"Vous êtes rentable.{choc_txt} C'est le moment d'accélérer."
        conseils.append({
            "titre": "Accélération de la croissance",
            "priorite": "haute",
            "description": desc,
            "actions": [
                "Doublez le budget sur votre canal d'acquisition le plus rentable",
                "Lancez un programme de parrainage (très efficace en Tunisie)",
                "Développez des partenariats stratégiques dans votre secteur",
                "Recrutez un profil commercial/marketing senior"
            ]
        })
    else:
        charge_txt = f" (charges fixes : {charges_fixes:,.0f} DT/mois)".replace(',', ' ') if charges_fixes > 0 else ""
        desc = f"Résultat mensuel : {res_txt}.{choc_txt}{charge_txt} Concentrez-vous sur la réduction des coûts et l'optimisation avant de croître." if res_txt else f"Vous n'êtes pas encore rentable.{choc_txt} Concentrez-vous sur la réduction des coûts."
        conseils.append({
            "titre": "Atteindre la rentabilité d'abord",
            "priorite": "critique",
            "description": desc,
            "actions": [
                "Identifiez et supprimez les coûts non essentiels",
                "Augmentez les prix ou réduisez le scope de l'offre",
                "Concentrez-vous sur vos 20% de clients les plus rentables",
                "Réduisez le burn rate pour gagner du temps"
            ]
        })

    # Canaux de croissance spécifiques Tunisie
    conseils.append({
        "titre": "Canaux de croissance en Tunisie",
        "priorite": "moyenne",
        "description": "Les canaux les plus efficaces en Tunisie pour votre stade.",
        "actions": [
            "Facebook Ads (90%+ de pénétration chez les 18-45 ans)",
            "Instagram pour le contenu visuel et lifestyle",
            "Bouche-à-oreille et groupes Facebook communautaires",
            "Influenceurs tunisiens (micro-influenceurs: 1000-10K abonnés)",
            "Google Ads pour capturer la demande existante"
        ]
    })

    return conseils


def _conseil_risques(risque, secteur, stade, budget, ctx=None):
    conseils = []
    ctx = ctx or {}
    charges_fixes = ctx.get('charges_fixes', 0)
    reserve_txt = f"{charges_fixes * 6:,.0f} DT".replace(',', ' ') if charges_fixes > 0 else "6 mois de charges"

    mitigation_map = {
        "marche": {
            "titre": "Risque marché — Plan de mitigation",
            "priorite": "haute",
            "description": "Le risque de marché est le plus courant (42% des échecs). Validez avant d'investir.",
            "actions": [
                "Minimum 50 entretiens clients avant tout développement",
                "Lancez une campagne de pré-vente / crowdfunding",
                "Testez avec un MVP minimal (< 30 jours de développement)",
                "Mesurez le taux de rétention dès les premiers clients"
            ]
        },
        "financement": {
            "titre": "Risque financement — Plan de survie",
            "priorite": "critique",
            "description": f"Le manque de trésorerie tue 29% des startups. Constituez une réserve de {reserve_txt} minimum.",
            "actions": [
                f"Réserve cible : {reserve_txt} (6 mois de charges fixes)",
                "Demandez le label Startup Act (bourse de 1000 DT/mois)",
                "Contactez la BFPME pour un prêt à taux préférentiel",
                "Explorez le bootstrapping: générez des revenus dès le jour 1",
                "Préparez un 'Plan B' en cas de trésorerie critique"
            ]
        },
        "concurrence": {
            "titre": "Risque concurrence — Différenciation",
            "priorite": "haute",
            "description": "Si la concurrence est votre principal risque, vous devez être clairement différent.",
            "actions": [
                "Identifiez votre USP (Unique Selling Proposition) incontournable",
                "Ciblez un segment que la concurrence ignore",
                "Construisez une communauté fidèle autour de votre marque",
                "Innovez sur le service client (c'est souvent le maillon faible en Tunisie)"
            ]
        },
        "equipe": {
            "titre": "Risque équipe — Renforcement",
            "priorite": "moyenne",
            "description": "Le talent technique est rare et cher en Tunisie. Anticipez.",
            "actions": [
                "Proposez de l'equity/stock options pour attirer les meilleurs",
                "Recrutez dans les universités (INSAT, SUP'COM, ENIS)",
                "Rejoignez des communautés tech (Tunisia JS, GDG Tunis)",
                "Externalisez les tâches non critiques (freelances)"
            ]
        }
    }

    if risque in mitigation_map:
        conseils.append(mitigation_map[risque])
    else:
        conseils.append({
            "titre": "Gestion des risques globale",
            "priorite": "moyenne",
            "description": "Anticipez les principaux risques de votre projet.",
            "actions": [
                "Identifiez vos 3 risques majeurs et créez un plan B pour chacun",
                "Constituez une réserve de trésorerie de 6 mois",
                "Diversifiez vos sources de revenus et vos fournisseurs",
                "Rejoignez un incubateur pour bénéficier de mentorat"
            ]
        })

    return conseils


def _conseil_transport(cout_transport, panier_moyen, marge_pct, charges_fixes):
    """Conseil spécifique coût transport quand l'utilisateur pose une question là-dessus."""
    conseils = []
    pct_panier = (cout_transport / panier_moyen * 100) if panier_moyen > 0 else 0
    conseil_base = {
        "titre": "Réduire le coût de transport",
        "priorite": "haute" if pct_panier > 15 else "moyenne",
        "description": f"Votre coût de transport est de {cout_transport:.1f} DT/commande, soit {pct_panier:.1f}% de votre panier moyen ({panier_moyen:.0f} DT). {'C\'est trop élevé — cela compresse votre marge directement.' if pct_panier > 15 else 'Niveau acceptable, mais optimisable.'}",
        "actions": [
            "Négociez un tarif dégressif avec votre prestataire logistique (Topnet, Aramex TN, etc.)",
            "Regroupez les commandes par zone géographique pour réduire les trajets",
            f"Facturez la livraison au client si vous ne le faites pas déjà (ex: +{min(cout_transport, 7):.0f} DT/commande)",
            "Testez un modèle de livraison click-and-collect pour réduire les coûts de 40-60%",
            "Évaluez la possibilité d'un partenariat avec d'autres startups pour mutualiser la logistique"
        ]
    }
    conseils.append(conseil_base)
    return conseils


def _conseil_financement(stade, budget, secteur):
    conseils = []
    fin_data = MARKET_DATA.get('financement', {})

    if stade in ['idee', 'mvp']:
        conseils.append({
            "titre": "Financement early-stage en Tunisie",
            "priorite": "haute",
            "description": "Au stade idée/MVP, privilégiez le bootstrapping et les subventions. Les investisseurs veulent voir de la traction.",
            "sources": [
                {"nom": "Startup Act", "montant": "Bourse 1000 DT/mois + exonérations", "accessibilite": "haute"},
                {"nom": "Smart Capital", "montant": "Jusqu'à 100 000 DT", "accessibilite": "moyenne"},
                {"nom": "Flat6Labs Tunis", "montant": "30 000 - 120 000 DT", "accessibilite": "compétitif"},
                {"nom": "BFPME", "montant": "10 000 - 500 000 DT", "accessibilite": "moyenne"}
            ]
        })
    else:
        conseils.append({
            "titre": "Financement de croissance",
            "priorite": "haute",
            "description": "Avec de la traction, vous pouvez accéder à du capital risque et des prêts plus importants.",
            "sources": [
                {"nom": "SICAR", "montant": "100 000 - 5 000 000 DT", "accessibilite": "nécessite traction"},
                {"nom": "CDC", "montant": "50 000 - 2 000 000 DT", "accessibilite": "projet structurant"},
                {"nom": "AfricInvest", "montant": "1 000 000+ DT", "accessibilite": "série A+"},
                {"nom": "BIAT Capital", "montant": "500 000 - 10 000 000 DT", "accessibilite": "PME en croissance"}
            ]
        })

    return conseils


def _conseil_marketing(secteur, type_client, stade, budget):
    conseils = []

    budget_map = {
        'moins_5000': 'très limité',
        '5000_20000': 'limité',
        '20000_50000': 'modéré',
        '50000_100000': 'confortable',
        'plus_100000': 'important'
    }
    budget_label = budget_map.get(budget, 'modéré')

    if budget in ['moins_5000', '5000_20000']:
        conseils.append({
            "titre": "Marketing à budget limité",
            "priorite": "haute",
            "description": f"Avec un budget {budget_label}, misez sur le marketing organique et le bouche-à-oreille.",
            "actions": [
                "Créez du contenu de valeur sur Facebook et Instagram (0 DT)",
                "Rejoignez et animez des groupes Facebook communautaires",
                "Lancez un programme de parrainage (récompense: réduction)",
                "Faites du marketing de guérilla local",
                "Utilisez WhatsApp Business pour le service client"
            ],
            "budget_recommande_mensuel_dt": 200
        })
    else:
        conseils.append({
            "titre": "Stratégie marketing multi-canal",
            "priorite": "haute",
            "description": f"Budget {budget_label}: combinez paid et organic pour un maximum d'impact.",
            "actions": [
                "Facebook/Instagram Ads: 40% du budget marketing",
                "Google Ads (Search): 25% du budget",
                "Contenu/SEO: 20% du budget",
                "Influenceurs tunisiens: 15% du budget",
                "Mesurez le CAC par canal et réallouez mensuellement"
            ],
            "budget_recommande_mensuel_dt": 1500
        })

    return conseils


def _calculer_score_confiance(marge, resultat, concurrence, stade):
    score = 50

    if marge > 40: score += 15
    elif marge > 25: score += 10
    elif marge > 15: score += 5
    elif marge < 10: score -= 15

    if resultat > 5000: score += 15
    elif resultat > 0: score += 10
    elif resultat > -1000: score -= 5
    else: score -= 15

    conc_scores = {'faible': 10, 'moyen': 0, 'moyenne': 0, 'fort': -10, 'forte': -10, 'domine': -15}
    score += conc_scores.get(concurrence, 0)

    stade_scores = {'croissance': 15, 'lance': 10, 'mvp': 5, 'idee': 0}
    score += stade_scores.get(stade, 0)

    score = _clamp(score, 10, 95)

    if score >= 75:
        label = "Confiance élevée"
        emoji = "🟢"
    elif score >= 50:
        label = "Confiance modérée"
        emoji = "🟡"
    else:
        label = "Confiance faible"
        emoji = "🔴"

    return {"score": score, "label": label, "emoji": emoji}


def _resume_conseil(conseils, score):
    points_cles = []
    for categorie, items in conseils.items():
        if isinstance(items, list) and items:
            for item in items:
                if item.get('priorite') in ['critique', 'haute']:
                    points_cles.append(item['titre'])
    return {
        "score": score,
        "points_cles": points_cles[:5],
        "message": "Votre projet a du potentiel ! Concentrez-vous sur les actions prioritaires identifiées." if score['score'] >= 50 else "Attention, plusieurs points critiques nécessitent votre attention immédiate."
    }


# ===================================================================
# 8) POST /api/startup-suggestions — Suggestions d'idées startup
# ===================================================================
@app.route('/api/startup-suggestions', methods=['POST'])
def startup_suggestions():
    try:
        d = request.get_json(force=True)
        domain = d.get('domain', 'ecommerce')
        budget_range = d.get('budget_range', 'moyen')
        skills = d.get('skills', [])
        if isinstance(skills, str):
            skills = [skills]

        # Mapper le budget
        budget_limits = {
            'tres_petit': (0, 10000),
            'petit': (10000, 30000),
            'moyen': (30000, 60000),
            'grand': (60000, 100000),
            'tres_grand': (100000, 500000)
        }
        budget_min, budget_max = budget_limits.get(budget_range, (30000, 60000))

        # Chercher les idées dans les données
        ideas_pool = MARKET_DATA.get('startup_ideas', {})
        matched_ideas = []

        # D'abord les idées du domaine demandé
        if domain in ideas_pool:
            for idea in ideas_pool[domain]:
                score = _scorer_idea(idea, budget_min, budget_max, skills)
                idea_copy = idea.copy()
                idea_copy['score_matching'] = score
                idea_copy['secteur'] = domain
                matched_ideas.append(idea_copy)

        # Puis les idées des domaines adjacents
        adjacents = {
            'livraison': ['ecommerce', 'foodtech'],
            'ecommerce': ['livraison', 'services'],
            'services': ['ecommerce', 'fintech'],
            'foodtech': ['livraison', 'ecommerce'],
            'edtech': ['services'],
            'healthtech': ['services'],
            'fintech': ['services', 'ecommerce'],
            'agritech': ['ecommerce', 'livraison']
        }

        for adj_domain in adjacents.get(domain, []):
            if adj_domain in ideas_pool:
                for idea in ideas_pool[adj_domain]:
                    score = _scorer_idea(idea, budget_min, budget_max, skills)
                    idea_copy = idea.copy()
                    idea_copy['score_matching'] = score * 0.8  # pénalité domaine adjacent
                    idea_copy['secteur'] = adj_domain
                    matched_ideas.append(idea_copy)

        # Trier par score et prendre les 5 meilleures
        matched_ideas.sort(key=lambda x: x['score_matching'], reverse=True)
        top_ideas = matched_ideas[:5]

        # Enrichir chaque idée
        suggestions = []
        for idea in top_ideas:
            secteur_data = MARKET_DATA.get('secteurs', {}).get(idea['secteur'], {})
            suggestions.append({
                "nom": idea['nom'],
                "description": idea['description'],
                "secteur": secteur_data.get('nom', idea['secteur']),
                "investissement_initial_dt": idea['investissement_initial_dt'],
                "revenus_mensuels_estimes_dt": idea['revenus_mensuels_estimes_dt'],
                "risque": idea['risque'],
                "opportunite": idea['opportunite'],
                "competences_requises": idea.get('competences', []),
                "score_matching": round(idea['score_matching']),
                "roi_estime_mois": round(idea['investissement_initial_dt'] / idea['revenus_mensuels_estimes_dt']) if idea['revenus_mensuels_estimes_dt'] > 0 else None,
                "marche": {
                    "taille_mdt": secteur_data.get('taille_marche_mdt', 'N/A'),
                    "croissance_pct": secteur_data.get('taux_croissance_annuel', 'N/A'),
                    "concurrence": secteur_data.get('concurrence', 'N/A')
                },
                "prochaines_etapes": _prochaines_etapes(idea['risque'], idea['investissement_initial_dt']),
                "dans_budget": budget_min <= idea['investissement_initial_dt'] <= budget_max
            })

        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "filtres": {
                "domain": domain,
                "budget_range": budget_range,
                "budget_dt": f"{budget_min:,} - {budget_max:,} DT",
                "skills": skills
            },
            "domains_disponibles": [
                {"value": k, "label": v.get('nom', k)}
                for k, v in MARKET_DATA.get('secteurs', {}).items()
            ]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


def _scorer_idea(idea, budget_min, budget_max, skills):
    score = 50

    invest = idea.get('investissement_initial_dt', 50000)
    if budget_min <= invest <= budget_max:
        score += 30
    elif invest < budget_min:
        score += 15
    elif invest <= budget_max * 1.5:
        score += 5
    else:
        score -= 20

    # Matching compétences
    idea_skills = idea.get('competences', [])
    if skills and idea_skills:
        matches = len(set(s.lower() for s in skills) & set(s.lower() for s in idea_skills))
        score += matches * 10

    # Risque
    risk_scores = {'faible': 15, 'moyen': 5, 'élevé': -5}
    score += risk_scores.get(idea.get('risque', 'moyen'), 0)

    # ROI
    revenus = idea.get('revenus_mensuels_estimes_dt', 0)
    if revenus > 0 and invest > 0:
        roi_mois = invest / revenus
        if roi_mois < 6: score += 15
        elif roi_mois < 12: score += 10
        elif roi_mois < 18: score += 5

    return _clamp(score, 0, 100)


def _prochaines_etapes(risque, investissement):
    etapes = [
        "Étudier le marché et la concurrence en Tunisie",
        "Valider l'idée avec 30 clients potentiels",
        "Créer un MVP minimal en 30 jours"
    ]
    if investissement > 50000:
        etapes.append("Préparer un dossier BFPME ou Startup Act")
    if risque == 'élevé':
        etapes.append("Constituer une réserve de trésorerie de 6 mois")
        etapes.append("Trouver un co-fondateur avec expertise complémentaire")
    etapes.append("Lancer et itérer rapidement")
    return etapes


# ===================================================================
# API Données du marché
# ===================================================================
@app.route('/api/market-data', methods=['GET'])
def market_data_api():
    return jsonify({"success": True, "data": MARKET_DATA})


# ===================================================================
# Servir le frontend
# ===================================================================
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# ===================================================================
# Point d'entrée
# ===================================================================
if __name__ == '__main__':
    # Créer le dossier static s'il n'existe pas
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
    print("=" * 50)
    print("  Startup Stress-Test TN — Serveur Backend")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
