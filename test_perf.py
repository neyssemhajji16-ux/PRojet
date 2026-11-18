# -*- coding: utf-8 -*-
import urllib.request, json, time

BASE = 'http://localhost:5000'

def test(label, url, data=None):
    start = time.time()
    try:
        if data:
            req = urllib.request.Request(
                url,
                json.dumps(data).encode('utf-8'),
                {'Content-Type': 'application/json'},
                method='POST'
            )
        else:
            req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as r:
            body = json.loads(r.read())
            elapsed = round((time.time() - start) * 1000)
            ok = body.get('success', True)
            status = 'OK  ' if ok else 'FAIL'
            print(f'  [{status}] {label} — {elapsed}ms')
            return ok, elapsed, body
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        print(f'  [ERR ] {label} — {elapsed}ms — {e}')
        return False, elapsed, {}

print()
print('====== Startup Stress-Test TN — Tests de performance ======')
print()

# 1. Homepage
start = time.time()
try:
    with urllib.request.urlopen(f'{BASE}/', timeout=5) as r:
        size = len(r.read())
        ms = round((time.time() - start) * 1000)
        print(f'  [OK  ] GET / (home) — {ms}ms — {size} bytes')
except Exception as e:
    print(f'  [ERR ] GET / — {e}')

# 2. Market data
ok, ms, body = test('GET /api/market-data', f'{BASE}/api/market-data')
if ok:
    nb = len(body.get('data', {}).get('secteurs', {}))
    print(f'         {nb} secteurs charges')

# 3. Simulate baseline
ok, ms, body = test('POST /api/simulate (baseline)', f'{BASE}/api/simulate', data={
    'panier_moyen': 89, 'cout_produits': 45, 'cout_transport': 8,
    'autres_couts': 5, 'charges_fixes': 3000, 'commandes_mois': 200,
    'livraison_facturee': 0, 'choc_transport_pct': 0, 'choc_demande_pct': 0,
    'choc_concurrent_pct': 0, 'choc_marge_pct': 0
})
if ok:
    r = body['avant']['resultat_mensuel']
    s = body['avant']['seuil_rentabilite']
    print(f'         Resultat: {r} DT | Seuil: {s} cmd')

# 4. Simulate full stress
ok, ms, body = test('POST /api/simulate (stress x4)', f'{BASE}/api/simulate', data={
    'panier_moyen': 89, 'cout_produits': 45, 'cout_transport': 8,
    'autres_couts': 5, 'charges_fixes': 3000, 'commandes_mois': 200,
    'livraison_facturee': 0, 'choc_transport_pct': 20, 'choc_demande_pct': 30,
    'choc_concurrent_pct': 10, 'choc_marge_pct': 10
})
if ok:
    r2 = body['apres']['resultat_mensuel']
    alerte = body['alerte'][0]['niveau']
    print(f'         Apres chocs: {r2} DT | Alerte: {alerte}')

# 5. Questionnaire step 1
ok, ms, body = test('POST /api/questionnaire (step 1)', f'{BASE}/api/questionnaire', data={
    'step': 1, 'answers': {}
})
if ok:
    print(f'         {len(body["questions"])} questions | next: step {body["step_suivant"]}')

# 6. Questionnaire step 3 conditionnel
ok, ms, _ = test('POST /api/questionnaire (step 3 B2C livraison)', f'{BASE}/api/questionnaire', data={
    'step': 3, 'answers': {'secteur': 'livraison', 'type_client': 'b2c'}
})

# 7. Diagnostic
ok, ms, body = test('POST /api/diagnose', f'{BASE}/api/diagnose', data={'answers': {
    'taille_marche': 'grand', 'marche_valide': True, 'clients_existants': True,
    'croissance_marche': 'forte', 'niveau_concurrence': 'moyen',
    'proposition_valeur_claire': True, 'avantage_concurrentiel': True,
    'niveau_innovation': 'incremental', 'prototype_mvp': True,
    'modele_scalable': 'saas', 'fournisseurs_locaux': True
}})
if ok:
    score = body['note_globale']
    grade = body['grade']['lettre']
    print(f'         Score: {score}/100 — Grade: {grade}')

# 8. Business Plan
ok, ms, body = test('POST /api/business-plan', f'{BASE}/api/business-plan', data={
    'answers': {
        'secteur': 'livraison', 'description_projet': 'Test livraison agricole',
        'type_client': 'b2c', 'localisation': 'grand_tunis',
        'budget_initial': '20000_50000', 'ca_objectif_an1': 200000,
        'panier_moyen_estime': 89, 'objectif_clients_an1': 500
    },
    'simulation': {}
})
if ok:
    nb_sections = len(body.get('plan', {}).get('sections', []))
    print(f'         {nb_sections} sections generees')

# 9. Pivot scenarios
ok, ms, _ = test('POST /api/pivot-scenarios (premium)', f'{BASE}/api/pivot-scenarios', data={
    'panier_moyen': 89, 'cout_produits': 45, 'cout_transport': 8,
    'charges_fixes': 3000, 'commandes_mois': 200, 'marge_pct': 25,
    'secteur': 'livraison', 'pivot_type': 'premium'
})

# 10. Persona simulator
ok, ms, body = test('POST /api/persona-simulator', f'{BASE}/api/persona-simulator', data={
    'secteur': 'livraison', 'type_produit': 'Livraison agricole locale', 'prix_range': 'moyen'
})
if ok:
    print(f'         {len(body["personas"])} personas generees')

# 11. AI Advice
ok, ms, _ = test('POST /api/ai-advice', f'{BASE}/api/ai-advice', data={
    'question': 'Comment ameliorer ma marge?',
    'contexte': {'secteur': 'livraison', 'score_diagnostic': 65}
})

# 12. Load test: 50 requetes simulate
print()
print('  [LOAD] Test de charge — 50 requetes /api/simulate...')
times = []
payload = json.dumps({
    'panier_moyen': 89, 'cout_produits': 45, 'cout_transport': 8,
    'autres_couts': 5, 'charges_fixes': 3000, 'commandes_mois': 200,
    'livraison_facturee': 0, 'choc_transport_pct': 20, 'choc_demande_pct': 30,
    'choc_concurrent_pct': 10, 'choc_marge_pct': 10
}).encode('utf-8')

errors = 0
for i in range(50):
    s = time.time()
    try:
        req = urllib.request.Request(
            f'{BASE}/api/simulate', payload,
            {'Content-Type': 'application/json'}, method='POST'
        )
        urllib.request.urlopen(req, timeout=5).read()
        times.append(round((time.time() - s) * 1000))
    except Exception:
        errors += 1
        times.append(9999)

mn = min(times)
avg = round(sum(times) / len(times))
mx = max(times)
all_fast = 'OUI' if mx < 500 else 'NON'
print(f'  [OK  ] 50 requetes terminees — min:{mn}ms | moy:{avg}ms | max:{mx}ms | erreurs:{errors}')
print(f'         Toutes sous 500ms: {all_fast}')

# 13. Load test: 20 requetes diagnose
print()
print('  [LOAD] Test de charge — 20 requetes /api/diagnose...')
times2 = []
payload2 = json.dumps({'answers': {
    'taille_marche': 'grand', 'marche_valide': True, 'croissance_marche': 'forte',
    'niveau_concurrence': 'moyen', 'proposition_valeur_claire': True,
    'niveau_innovation': 'disruptif', 'prototype_mvp': True, 'modele_scalable': 'saas'
}}).encode('utf-8')

for i in range(20):
    s = time.time()
    try:
        req = urllib.request.Request(
            f'{BASE}/api/diagnose', payload2,
            {'Content-Type': 'application/json'}, method='POST'
        )
        urllib.request.urlopen(req, timeout=5).read()
        times2.append(round((time.time() - s) * 1000))
    except Exception:
        times2.append(9999)

print(f'  [OK  ] 20 requetes — min:{min(times2)}ms | moy:{round(sum(times2)/len(times2))}ms | max:{max(times2)}ms')

print()
print('====== Bilan ======')
all_endpoints = [mn, min(times2)]
print(f'  Latence globale: {round(sum(all_endpoints)/len(all_endpoints))}ms moyenne')
print(f'  Statut: {"Excellent" if avg < 20 else "Bon" if avg < 100 else "Acceptable"}')
print()
print('====== Tests termines ======')
print()
