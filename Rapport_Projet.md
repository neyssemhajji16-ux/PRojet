# Startup Stress-Test TN

## Simulateur de Résistance des Startups

---

**Matière :** Management de l'Innovation

**Description :** Plateforme web intelligente permettant aux entrepreneurs tunisiens de tester la résistance financière et stratégique de leur projet de startup avant son lancement, à travers des simulations de stress, des diagnostics multi-dimensionnels et des recommandations contextualisées au marché tunisien.

---

## 1. Introduction

La Tunisie connaît une dynamique entrepreneuriale croissante, portée par une jeunesse diplômée, un écosystème de soutien en développement (BFPME, CDC, SICAR, Startup Act 2018) et une volonté politique de diversifier l'économie. Pourtant, le taux d'échec des startups tunisiennes reste élevé : selon les estimations, plus de 70 % des jeunes entreprises ne franchissent pas le cap des trois premières années.

**Le problème** : les entrepreneurs tunisiens disposent de peu d'outils accessibles pour évaluer objectivement la viabilité de leur idée avant de se lancer. Les ressources existantes — business plans statiques, conseils génériques, formations théoriques — ne permettent pas de simuler l'impact concret de décisions critiques (hausse des coûts de transport, baisse de la demande, pression concurrentielle).

**Notre solution** : *Startup Stress-Test TN* est une plateforme web qui permet de **tester ses décisions avant de les prendre**. En simulant des chocs financiers réalistes et en fournissant un diagnostic multi-dimensionnel, l'outil transforme l'intuition entrepreneuriale en analyse chiffrée, contextualisée aux réalités du marché tunisien.

---

## 2. Problématique

Les entrepreneurs tunisiens font face à plusieurs défis structurels :

- **Manque de données locales** : les outils existants (calculateurs en ligne, templates de business plan) utilisent des données occidentales inadaptées au contexte tunisien — coûts en euros, marges de marchés matures, comportements de consommation différents.
- **Absence de simulation dynamique** : un business plan classique est un document statique. Il ne permet pas de répondre à la question « *que se passe-t-il si mes coûts de transport augmentent de 25 % ?* ».
- **Conseils génériques** : les incubateurs et programmes d'accompagnement fournissent des recommandations standardisées, rarement calibrées sur les spécificités sectorielles tunisiennes (livraison, food tech, e-commerce local).
- **Complexité des outils professionnels** : les logiciels de modélisation financière (Excel avancé, outils SaaS) sont soit trop complexes, soit payants, soit inadaptés aux micro-entreprises.

**Le fossé à combler** : il n'existe pas d'outil simple, gratuit et contextualisé qui permette à un entrepreneur tunisien de **stress-tester** son idée — c'est-à-dire de mesurer sa résistance face à des scénarios défavorables réalistes, en utilisant des données du marché tunisien.

---

## 3. Solution Proposée

**Startup Stress-Test TN** est une plateforme web interactive qui offre un parcours complet d'évaluation entrepreneuriale :

1. **Collecte intelligente** : un questionnaire adaptatif identifie le profil du projet (secteur, marché cible, modèle de revenus, équipe, besoins de financement).
2. **Simulation de stress** : le cœur de la plateforme — l'entrepreneur ajuste des paramètres de choc (transport, demande, concurrence, marges) et visualise en temps réel l'impact sur sa rentabilité.
3. **Diagnostic stratégique** : une évaluation sur 5 axes fournit une vision globale des forces et faiblesses du projet.
4. **Aide à la décision** : des scénarios de pivot, des personas clients, un business plan structuré et des conseils stratégiques complètent l'analyse.

**L'innovation clé** : contrairement aux outils de conseil qui disent « *faites ceci* », Startup Stress-Test TN dit « *voici ce qui se passe si vous faites ceci* ». L'entrepreneur reste décideur, mais il décide en connaissance de cause.

---

## 4. Architecture Technique

### Stack technologique

| Couche | Technologie | Justification |
|--------|------------|---------------|
| Backend | Python Flask | Léger, rapide à déployer, idéal pour les API REST |
| Frontend | HTML/CSS/JS (Vanilla) | Aucune dépendance framework, chargement rapide |
| Visualisation | Chart.js v4 | Graphiques interactifs et responsifs |
| Données | JSON statique | Données de référence tunisiennes embarquées |

### Architecture applicative

```
┌─────────────────────────────────────────────────┐
│                   NAVIGATEUR                     │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ index.html│  │ style.css│  │   app.js     │  │
│  │ (SPA)     │  │          │  │ + Chart.js   │  │
│  └─────┬─────┘  └──────────┘  └──────┬───────┘  │
│        │           API REST           │          │
│        └──────────────┬───────────────┘          │
└───────────────────────┼──────────────────────────┘
                        │ HTTP (JSON)
┌───────────────────────┼──────────────────────────┐
│                  FLASK (app.py)                   │
│  ┌────────────┐ ┌──────────┐ ┌────────────────┐  │
│  │ /api/      │ │ Moteur   │ │ Système expert │  │
│  │ simulate   │ │ de calcul│ │ (règles)       │  │
│  │ diagnose   │ │          │ │                │  │
│  │ questionnaire│         │ │                │  │
│  │ business-plan│         │ │                │  │
│  │ pivot-scenarios│       │ │                │  │
│  │ persona-simulator│    │ │                │  │
│  │ ai-advice  │ │          │ │                │  │
│  │ startup-   │ │          │ │                │  │
│  │ suggestions│ │          │ │                │  │
│  └────────────┘ └────┬─────┘ └────────────────┘  │
│                      │                            │
│         ┌────────────┴────────────┐               │
│         │ tunisian_market.json    │               │
│         │ (données de référence)  │               │
│         └─────────────────────────┘               │
└───────────────────────────────────────────────────┘
```

### Décisions de conception clés

- **IA basée sur des règles** : le système expert fonctionne par arbres de décision et scoring pondéré, sans appel à des API externes (OpenAI, etc.). Cela garantit un fonctionnement 100 % hors ligne, sans coût récurrent et avec des réponses déterministes et vérifiables.
- **Approche local-first** : toutes les données restent sur la machine de l'utilisateur. Aucune donnée entrepreneuriale sensible n'est transmise à des serveurs tiers.
- **Application mono-page (SPA)** : navigation par onglets sans rechargement de page, offrant une expérience fluide et réactive.

---

## 5. Fonctionnalités Développées

### 5.1 Questionnaire Adaptatif

Un formulaire intelligent qui s'adapte aux réponses de l'utilisateur. Le parcours suit un arbre de décision : selon le secteur choisi (livraison, e-commerce, food tech, edtech, etc.), les questions suivantes se spécialisent — un projet de livraison sera interrogé sur ses coûts de transport et zones de couverture, tandis qu'un projet edtech sera interrogé sur ses contenus et certifications. Les thèmes couverts incluent : secteur d'activité, marché cible, modèle de revenus, équipe, besoins de financement et concurrence.

### 5.2 Simulateur de Stress Financier

**Fonctionnalité centrale de la plateforme.** L'utilisateur saisit ses paramètres financiers (panier moyen, coûts, charges fixes, nombre de commandes) puis applique des chocs via des curseurs interactifs :

- **Choc transport** : hausse en pourcentage du coût de transport
- **Choc demande** : baisse en pourcentage du nombre de commandes
- **Choc concurrent** : pression sur les prix (baisse du panier moyen)
- **Choc marge** : compression des marges (hausse des coûts produits)

Les résultats s'affichent en temps réel : résultat mensuel avant/après choc, seuil de rentabilité, ratio de couverture, et décomposition de l'impact de chaque choc. Des graphiques Chart.js visualisent instantanément les variations.

### 5.3 Diagnostic Multi-dimensionnel

Une évaluation sur 5 axes notés de 0 à 100 :

- **Marché** : taille, croissance, accessibilité du marché visé
- **Offre Commerciale** : compétitivité du produit/service, positionnement prix
- **Innovation** : degré de nouveauté, barrières à l'entrée technologiques
- **Évolutivité** : potentiel de passage à l'échelle, reproductibilité
- **Impact Environnemental** : durabilité, responsabilité sociale

Le diagnostic produit une note globale, identifie les forces et faiblesses, et fournit des recommandations ciblées par dimension.

### 5.4 Scénarios de Pivot

L'utilisateur peut comparer sa stratégie actuelle avec des pivots alternatifs (changement de segment, de modèle de revenus, d'offre). Pour chaque scénario, la plateforme recalcule les projections financières et affiche un comparatif côte à côte.

### 5.5 Personas Client

À partir du secteur, du type de produit et de la fourchette de prix, le système génère 3 à 4 profils clients réalistes incluant : données démographiques, comportements d'achat, points de douleur et disposition à payer. Ces personas sont calibrées sur les habitudes de consommation tunisiennes.

### 5.6 Générateur de Business Plan

Un business plan structuré est généré automatiquement à partir des données collectées (questionnaire + résultats de simulation). Les sections incluent : résumé exécutif, analyse de marché, modèle économique, projections financières, analyse des risques et recommandations.

### 5.7 Conseils IA

Un système expert basé sur des règles fournit des conseils stratégiques catégorisés : stratégie d'entrée sur le marché, politique de prix, leviers de croissance et mitigation des risques. Les recommandations sont déclenchées par des seuils et combinaisons de paramètres (par exemple : marge < 15 % → recommandation de renégocier les fournisseurs).

### 5.8 Suggestions de Startup

À partir d'un domaine d'intérêt, d'un budget et de compétences, le système propose 3 à 5 idées de startup avec description, coûts estimés, opportunité de marché et niveau de risque, le tout contextualisé au marché tunisien.

---

## 6. Données et Références Tunisiennes

La pertinence de l'outil repose sur l'intégration de données locales réelles :

| Source | Données utilisées |
|--------|-------------------|
| **TikTak PRO (Okkis)** | Paniers moyens livraison (~89 DT), volumes de commandes, coûts opérationnels des plateformes de livraison tunisiennes |
| **INTIGO** | Tarifs de transport et logistique : coûts par zone, grilles tarifaires de livraison urbaine et inter-villes |
| **BCT (Banque Centrale de Tunisie)** | Données de paiement, taux de change, indicateurs macro-économiques, statistiques sur les transactions digitales |
| **Benchmarks sectoriels** | Marges moyennes par secteur (livraison, e-commerce, services, food tech, edtech, healthtech), coûts de démarrage types |
| **Sources de financement** | BFPME, CDC, SICAR, programmes Startup Act |

**Pourquoi les données locales sont essentielles** : un simulateur utilisant des benchmarks européens ou américains donnerait des résultats trompeurs. Les coûts de transport, les paniers moyens, les charges sociales et les habitudes de consommation en Tunisie sont fondamentalement différents. Un panier moyen de 89 DT dans la livraison tunisienne n'a rien à voir avec les 25-35 € européens. L'ancrage local est ce qui rend les simulations actionables.

---

## 7. Méthode de Calcul

### Marge unitaire

$$
\text{Marge unitaire} = \text{Panier moyen} + \text{Livraison facturée} - \text{Coût produits} - \text{Coût transport} - \text{Autres coûts}
$$

### Résultat mensuel

$$
\text{Résultat mensuel} = \text{Commandes} \times \text{Marge unitaire} - \text{Charges fixes}
$$

### Seuil de rentabilité

$$
\text{Seuil de rentabilité} = \left\lceil \frac{\text{Charges fixes}}{\text{Marge unitaire}} \right\rceil \quad (\text{si marge unitaire} > 0)
$$

Le seuil indique le nombre minimum de commandes nécessaires pour couvrir les charges fixes.

### Décomposition des chocs

Chaque choc est appliqué indépendamment puis combiné pour mesurer l'impact total :

- **Choc transport** : `coût_transport_après = coût_transport × (1 + choc_transport_pct / 100)`
- **Choc demande** : `commandes_après = commandes × (1 - choc_demande_pct / 100)`
- **Choc concurrent** : `panier_moyen_après = panier_moyen × (1 - choc_concurrent_pct / 100)`
- **Choc marge** : `coût_produits_après = coût_produits × (1 + choc_marge_pct / 100)`

Le résultat après choc est recalculé avec les paramètres modifiés. La décomposition permet d'identifier quel facteur contribue le plus à la dégradation du résultat.

### Scoring diagnostique

Chaque dimension est évaluée par un ensemble de questions pondérées. Le score final par axe est :

$$
\text{Score}_{\text{axe}} = \frac{\sum_{i} w_i \times r_i}{\sum_{i} w_i} \times 100
$$

où $w_i$ est le poids de la question $i$ et $r_i$ la réponse normalisée (0 à 1).

La note globale est la moyenne pondérée des 5 axes.

---

## 8. Cas de Démonstration

### Scénario : Plateforme de livraison type Okkis

**Paramètres de départ :**

| Paramètre | Valeur |
|-----------|--------|
| Panier moyen | 89 DT |
| Coût transport | 8 DT |
| Coût produits | 60 DT |
| Charges fixes | 5 000 DT/mois |
| Commandes/mois | 500 |

**Résultat initial :**

- Marge unitaire = 89 - 60 - 8 = **21 DT**
- Résultat mensuel = 500 × 21 - 5 000 = **+5 500 DT/mois**

**Application des chocs :**

| Choc | Paramètre |
|------|-----------|
| Transport | +2 DT (hausse de 25 %) |
| Demande | -7,96 % (baisse de commandes) |

**Résultat après choc :**

- Nouveau coût transport = 10 DT
- Nouvelles commandes = 500 × (1 - 0,0796) ≈ 460
- Nouvelle marge unitaire = 89 - 60 - 10 = **19 DT**
- Nouveau résultat = 460 × 19 - 5 000 = 8 740 - 5 000 = **+3 740 DT/mois**

Dans un scénario plus sévère (charges fixes plus élevées, marges plus serrées), le résultat peut basculer de **+2 000 DT/mois** à **-720 DT/mois**, démontrant la fragilité du modèle face à des chocs combinés.

**Seuil de rentabilité :**

$$
\text{Seuil} = \left\lceil \frac{5\,000}{19} \right\rceil = 264 \text{ commandes}
$$

Avec des charges fixes plus élevées et des marges compressées, ce seuil peut atteindre **1 000 commandes**, un volume difficile à maintenir pour une jeune plateforme.

**Analyse** : ce cas illustre la vulnérabilité des plateformes de livraison tunisiennes — un secteur à marges fines où une combinaison de hausse des coûts logistiques et de baisse de la demande peut rapidement transformer un projet rentable en gouffre financier. L'outil permet de quantifier précisément cette sensibilité et d'identifier les leviers d'action (renégocier les tarifs transport, augmenter le panier moyen, réduire les charges fixes).

---

## 9. Valeur Ajoutée et Innovation

### Du conseil à l'expérimentation

Les outils traditionnels d'accompagnement entrepreneurial sont **prescriptifs** : ils disent quoi faire. Startup Stress-Test TN est **exploratoire** : il permet de tester des hypothèses et d'en observer les conséquences. Cette approche s'inscrit dans la logique du **Design Thinking** — prototyper, tester, itérer — appliquée non pas au produit, mais au modèle économique lui-même.

### Visualisation en temps réel

Les graphiques interactifs (Chart.js) permettent une compréhension immédiate de l'impact des décisions. L'entrepreneur voit ses courbes bouger en temps réel lorsqu'il déplace un curseur — une expérience bien plus parlante qu'un tableau Excel.

### Contextualisation tunisienne

L'outil n'est pas une adaptation superficielle d'un produit occidental. Les données, les secteurs, les fourchettes de prix, les sources de financement et les défis logistiques sont spécifiquement tunisiens. Un entrepreneur à Tunis ou Sfax retrouve ses réalités dans les simulations.

### Analyse multi-dimensionnelle

Le diagnostic sur 5 axes évite le piège de l'analyse purement financière. Un projet peut être financièrement viable mais manquer d'innovation ou d'évolutivité — le diagnostic le révèle.

### Lien avec le Design Thinking

La plateforme incarne les principes du Design Thinking appliqués à l'entrepreneuriat :

- **Empathie** : le questionnaire adaptatif comprend le contexte de l'entrepreneur
- **Définition** : le diagnostic identifie les problèmes clés
- **Idéation** : les scénarios de pivot et suggestions de startup ouvrent des alternatives
- **Prototypage** : la simulation financière est un « prototype » du modèle économique
- **Test** : le stress-test *est* le test, avant le test réel du marché

---

## 10. Conclusion

### Réalisations

Startup Stress-Test TN réalise la promesse d'un outil d'aide à la décision entrepreneuriale accessible, contextualisé et interactif. La plateforme intègre 8 fonctionnalités complémentaires — du questionnaire adaptatif au générateur de business plan — dans une interface web fluide et moderne, sans dépendance à des services externes payants.

### Améliorations futures

- **Support vocal** : intégration de la reconnaissance vocale pour une saisie plus naturelle, notamment en dialecte tunisien
- **IA générative** : remplacement progressif du système de règles par des modèles d'IA (LLM) pour des conseils plus nuancés et personnalisés
- **Application mobile** : portage vers une application native pour un accès hors connexion
- **Données temps réel** : connexion aux API de la BCT et des plateformes de paiement pour des benchmarks actualisés automatiquement
- **Communauté** : espace de partage anonymisé où les entrepreneurs peuvent comparer leurs simulations

### Impact sur l'écosystème

En rendant l'analyse de viabilité accessible à tout entrepreneur tunisien — sans coût, sans complexité, sans données occidentales inadaptées — Startup Stress-Test TN contribue à réduire le taux d'échec des startups en Tunisie. Chaque simulation est un échec évité, chaque diagnostic est une faiblesse identifiée à temps, chaque stress-test est une décision prise en connaissance de cause.

---

## Références

1. **Banque Centrale de Tunisie (BCT)** — Rapports annuels sur les paiements et l'inclusion financière, statistiques monétaires et bancaires. [https://www.bct.gov.tn](https://www.bct.gov.tn)

2. **INTIGO** — Grille tarifaire des services de transport et logistique en Tunisie. [https://www.intigo.tn](https://www.intigo.tn)

3. **TikTak PRO / Okkis** — Données opérationnelles et benchmarks des plateformes de livraison tunisiennes.

4. **Startup Act Tunisie (2018)** — Loi n° 2018-20 relative aux startups, cadre réglementaire et incitatif pour l'entrepreneuriat innovant.

5. **Brown, T. (2008)** — *Design Thinking*, Harvard Business Review. Méthodologie d'innovation centrée sur l'humain appliquée à la conception de la plateforme.

6. **BFPME** — Banque de Financement des Petites et Moyennes Entreprises, programmes de financement pour les startups tunisiennes.

7. **INS (Institut National de la Statistique)** — Données démographiques et économiques tunisiennes utilisées pour la calibration des personas et benchmarks.
