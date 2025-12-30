# AUDIT COMPLET - SYSTÈME TARIFICATION/PAIEMENTS EOS vs PARTNER

Date: 24 décembre 2025
Objectif: Affichage séparé EOS/PARTNER + montants stables après confirmation

---

## ✅ ÉTAPE 0 — COMPOSANTS EXISTANTS (LOCALISÉS ET ANALYSÉS)

### Backend - Modèles

#### 📄 `backend/models/tarifs.py` (lignes 86-143)
**Modèle `EnqueteFacturation`**
- ✅ **DÉJÀ FAIT** : `client_id` présent (ligne 95) avec relation vers `Client` (ligne 119)
- ✅ **DÉJÀ FAIT** : Contrainte unique `uq_enquete_facturation_donnee` sur `(donnee_id, donnee_enqueteur_id)` (ligne 123)
- ✅ Champs présents :
  - `tarif_eos_code`, `tarif_eos_montant`, `resultat_eos_montant` (prix client)
  - `tarif_enqueteur_code`, `tarif_enqueteur_montant`, `resultat_enqueteur_montant` (gain enquêteur)
  - `paye`, `date_paiement`, `reference_paiement` (statut paiement)
  - `created_at`, `updated_at` (timestamps)
- ✅ Relations : `donnee`, `donnee_enqueteur`, `client`

**Autres modèles tarifs :**
- `TarifEOS` : tarifs client EOS
- `TarifEnqueteur` : rémunération enquêteurs
- `TarifClient` : tarifs clients autres qu'EOS (PARTNER)

### Backend - Services

#### 📄 `backend/services/tarification_service.py`

**`TarificationService.get_tarif_eos()` (lignes 25-73)**
- ✅ **DÉJÀ FAIT** : Détection client EOS vs autres (ligne 36)
- ✅ Utilise `TarifClient` pour clients non-EOS (lignes 38-51)
- ✅ Utilise `TarifEOS` pour client EOS (lignes 61-66)

**`TarificationService.calculate_tarif_for_enquete()` (lignes 110-180)**
- ✅ Point d'entrée principal pour calcul tarification
- ✅ Appelle `_get_or_create_facturation()` (ligne 158)
- ✅ Gère contestations via `_handle_contestation_facturation()` (ligne 162)
- ✅ Gère cas standard via `_handle_standard_facturation()` (ligne 165)

**`TarificationService._get_or_create_facturation()` (lignes 183-206)**
- ✅ **DÉJÀ FAIT** : Inclut `client_id` lors de la création (ligne 194)
- ✅ Évite doublons grâce à contrainte unique

**`TarificationService.get_enqueteur_earnings()` (lignes 690-773)**
- ✅ **DÉJÀ FAIT** : Accepte paramètre `client_id` optionnel
- ✅ Filtre par client si fourni

### Backend - API Endpoints

#### 📄 `backend/routes/paiement.py`

**`/api/paiement/stats/periodes` (lignes 380-479)**
- ✅ **DÉJÀ FAIT** : Accepte `client_id` optionnel (ligne 386)
- ✅ Filtre toutes les requêtes par client_id (lignes 428-431, 446-447, 465-466)

**`/api/paiement/enqueteurs-a-payer` (lignes 18-61)**
- ⚠️ **À VÉRIFIER** : Ne semble pas filtrer par client_id

#### 📄 `backend/routes/tarification.py`

**`/api/tarification/stats/global` (lignes 542-620)**
- ✅ **DÉJÀ FAIT** : Accepte `client_id` optionnel (ligne 549)
- ✅ Filtre toutes les stats par client_id (lignes 555-578, 598-599)

**`/api/facturation/enqueteur/<id>` (lignes 483-514)**
- ✅ **DÉJÀ FAIT** : Passe `client_id` à `TarificationService.get_enqueteur_earnings()`

#### 📄 `backend/routes/enquetes.py`

**`/api/enquetes/confirm` (lignes 168-230)**
- ❌ **PROBLÈME CRITIQUE** : N'appelle PAS `TarificationService.calculate_tarif_for_enquete()`
- Marque seulement l'enquête comme validée dans `EnqueteTerminee`
- **CONSÉQUENCE** : Pas de calcul/persistance des montants à la confirmation

#### 📄 `backend/routes/validation.py`

**`/api/enquete/valider/<int:enquete_id>` (lignes 65-120)**
- ❌ **PROBLÈME CRITIQUE** : N'appelle PAS `TarificationService.calculate_tarif_for_enquete()`
- Change seulement `statut_validation` à 'confirmee' ou 'refusee'
- **CONSÉQUENCE** : Pas de calcul/persistance des montants à la validation

#### 📄 `backend/routes/validation_v2.py`

**`/api/enquetes/<int:enquete_id>/valider` (lignes 16-66)**
- ❌ **PROBLÈME CRITIQUE** : N'appelle PAS `TarificationService.calculate_tarif_for_enquete()`
- Change seulement `statut_validation` de 'confirmee' à 'validee'
- **CONSÉQUENCE** : Pas de calcul/persistance des montants

### Frontend - Composants

#### 📄 `frontend/src/components/FinancialReports.jsx`

**`fetchAllData()` (lignes 44-90)**
- ❌ **PROBLÈME** : Ne passe PAS `client_id` aux API
  - Ligne 51 : `/api/paiement/stats/periodes` sans `client_id`
  - Ligne 58 : `/api/tarification/stats/global` sans `client_id`
- **CONSÉQUENCE** : Affiche les stats mélangées de TOUS les clients
- ⚠️ Stats par tarif et enquêteur sont MOCKÉES (lignes 65-82)

#### 📄 `frontend/src/components/EarningsViewer.jsx`

**`fetchEarnings()` (lignes 40-65)**
- ❌ **PROBLÈME** : Ne passe PAS `client_id` à l'API
  - Ligne 45 : `/api/facturation/enqueteur/${enqueteurId}` sans `client_id`
- **CONSÉQUENCE** : Affiche les gains de l'enquêteur pour TOUS les clients mélangés

#### 📄 `frontend/src/components/PaiementManager.jsx`
- À analyser pour vérifier le filtrage client

---

## 🔴 PROBLÈMES IDENTIFIÉS

### Problème #1 : CALCUL NON DÉCLENCHÉ À LA CONFIRMATION ⚠️⚠️⚠️
**Criticité : CRITIQUE**

Les 3 endpoints de confirmation/validation n'appellent PAS le service de tarification :
- `/api/enquetes/confirm`
- `/api/enquete/valider/<int:enquete_id>`
- `/api/enquetes/<int:enquete_id>/valider`

**Impact :**
- Les montants ne sont PAS calculés ni persistés lors de la confirmation
- Les rapports financiers ne peuvent pas afficher de données correctes
- Impossible de savoir "combien j'ai gagné" pour une enquête confirmée

**Solution requise :**
Ajouter dans chaque endpoint de confirmation (après commit du statut) :
```python
# Récupérer le DonneeEnqueteur
donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=enquete_id).first()
if donnee_enqueteur:
    # Calculer et persister la facturation
    from services.tarification_service import TarificationService
    facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
    if facturation:
        logger.info(f"Facturation créée: EOS={facturation.resultat_eos_montant}€, Enquêteur={facturation.resultat_enqueteur_montant}€")
```

### Problème #2 : FRONTEND NE FILTRE PAS PAR CLIENT
**Criticité : HAUTE**

Les composants frontend appellent les API sans passer `client_id` :
- `FinancialReports.jsx` : stats globales et périodiques sans filtre
- `EarningsViewer.jsx` : gains enquêteur sans filtre

**Impact :**
- Admin voit les stats mélangées EOS + PARTNER
- Impossible de distinguer "combien EOS a gagné" vs "combien PARTNER a gagné"
- Impossible de calculer la marge par client

**Solution requise :**
1. Ajouter un sélecteur client dans les composants
2. Passer `client_id` dans les appels API : `?client_id=1`
3. Afficher des totaux séparés ou un tableau comparatif

### Problème #3 : RÈGLE DE RECALCUL NON DÉFINIE
**Criticité : MOYENNE**

Aucune règle n'empêche la modification des montants après paiement.

**Impact :**
- Un admin pourrait changer un tarif et recalculer une enquête déjà payée
- Perte de traçabilité
- Désynchronisation des paiements

**Solution requise :**
Dans `_get_or_create_facturation()`, ajouter :
```python
if facturation and facturation.paye:
    logger.warning(f"Facturation {facturation.id} déjà payée, recalcul interdit")
    return facturation  # Ne pas recalculer
```

---

## ✅ PLAN DE CORRECTION

### PHASE 1 : FIX CRITIQUE - Calcul à la confirmation (30 min)

**Fichiers à modifier :**
1. `backend/routes/enquetes.py` (ligne 206, après commit)
2. `backend/routes/validation.py` (ligne 107, après commit)
3. `backend/routes/validation_v2.py` (ligne 62, après commit)

**Code à ajouter :**
```python
# Calculer et persister la facturation
donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=enquete_id).first()
if donnee_enqueteur:
    from services.tarification_service import TarificationService
    try:
        facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
        if facturation:
            logger.info(f"✅ Facturation créée pour enquête {enquete_id}: "
                       f"Client={facturation.resultat_eos_montant}€, "
                       f"Enquêteur={facturation.resultat_enqueteur_montant}€")
        else:
            logger.warning(f"⚠️ Aucune facturation créée pour enquête {enquete_id}")
    except Exception as e:
        logger.error(f"❌ Erreur calcul facturation pour enquête {enquete_id}: {e}")
        # Ne pas bloquer la confirmation si le calcul échoue
```

### PHASE 2 : FIX FILTRAGE FRONTEND - Sélecteur client (45 min)

#### 2.1 Modifier `FinancialReports.jsx`

**Ajouter état client :**
```javascript
const [selectedClient, setSelectedClient] = useState('all'); // 'all', 'EOS', 'PARTNER'
const [clients, setClients] = useState([]);
```

**Charger la liste des clients :**
```javascript
useEffect(() => {
    const fetchClients = async () => {
        const res = await axios.get(`${API_URL}/api/clients`);
        if (res.data.success) {
            setClients(res.data.data);
        }
    };
    fetchClients();
}, []);
```

**Modifier les appels API :**
```javascript
// Ligne 51 - Stats périodes
const clientParam = selectedClient !== 'all' ? `&client_id=${selectedClient}` : '';
const periodRes = await axios.get(
    `${API_URL}/api/paiement/stats/periodes?mois=${periodCount}${clientParam}`
);

// Ligne 58 - Stats globales
const globalRes = await axios.get(
    `${API_URL}/api/tarification/stats/global${selectedClient !== 'all' ? `?client_id=${selectedClient}` : ''}`
);
```

**Ajouter sélecteur dans l'UI :**
```jsx
<div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-2">
        Client
    </label>
    <select
        value={selectedClient}
        onChange={(e) => setSelectedClient(e.target.value)}
        className="px-4 py-2 border rounded-lg"
    >
        <option value="all">Tous les clients</option>
        {clients.map(c => (
            <option key={c.id} value={c.id}>{c.nom}</option>
        ))}
    </select>
</div>
```

#### 2.2 Modifier `EarningsViewer.jsx`

Même logique : ajouter `client_id` optionnel et passer dans l'URL :
```javascript
// Ligne 45
let url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}`;
if (clientId) {
    url += `?client_id=${clientId}`;
} else if (!viewAll) {
    url += `?month=${month}&year=${year}`;
} else if (viewAll && clientId) {
    url += `?client_id=${clientId}`;
}
```

### PHASE 3 : PROTECTION CONTRE RECALCUL APRÈS PAIEMENT (15 min)

**Fichier :** `backend/services/tarification_service.py`

**Dans `_get_or_create_facturation()` (après ligne 185) :**
```python
facturation = EnqueteFacturation.query.filter_by(
    donnee_enqueteur_id=donnee_enqueteur.id
).first()

if facturation:
    # ✅ PROTECTION : Ne pas recalculer si déjà payé
    if facturation.paye:
        logger.warning(f"⚠️ Facturation {facturation.id} déjà payée le {facturation.date_paiement}, recalcul bloqué")
        return facturation
    else:
        logger.info(f"🔄 Facturation {facturation.id} non payée, recalcul autorisé")
```

### PHASE 4 : TESTS ET VALIDATION (30 min)

#### Test 1 : Confirmation déclenche calcul
1. Créer une nouvelle enquête
2. Assigner à un enquêteur
3. Enquêteur soumet résultat
4. Admin confirme
5. ✅ Vérifier qu'une ligne apparaît dans `enquete_facturation` avec les bons montants

#### Test 2 : Filtrage par client fonctionne
1. Avoir des enquêtes EOS et PARTNER confirmées
2. Ouvrir `FinancialReports`
3. Sélectionner "EOS" → doit afficher uniquement stats EOS
4. Sélectionner "PARTNER" → doit afficher uniquement stats PARTNER
5. Sélectionner "Tous" → doit afficher le total

#### Test 3 : Protection paiement fonctionne
1. Confirmer une enquête → facturation créée
2. Marquer comme payée
3. Modifier un tarif
4. Re-confirmer l'enquête
5. ✅ Les montants ne doivent PAS changer

#### Test 4 : Contestations gérées correctement
1. Créer enquête positive → confirmer → montants positifs
2. Créer contestation négative → confirmer → montants négatifs (déduction)
3. Créer contestation positive → confirmer → montants positifs (nouveaux)
4. ✅ Vérifier que les 3 facturations ont le bon `client_id`

---

## 📊 RÉSULTAT ATTENDU

### Pour l'Admin - Vue Financière

**Onglet "Rapports financiers" avec sélecteur client :**

| Indicateur | Tous | EOS | PARTNER |
|------------|------|-----|---------|
| Total facturé client | 45 000 € | 30 000 € | 15 000 € |
| Total versé enquêteurs | 31 500 € | 21 000 € | 10 500 € |
| Marge | 13 500 € (30%) | 9 000 € (30%) | 4 500 € (30%) |
| Enquêtes traitées | 450 | 300 | 150 |

**Graphiques séparés :**
- Évolution mensuelle par client
- Répartition des tarifs par client
- Top enquêteurs par client

### Pour l'Admin - Vue Paiements

**Liste enquêteurs avec filtres :**
- Enquêteur | Client | Nb enquêtes | À payer | Payé | Reste
- Dupont | EOS | 25 | 550 € | 0 € | 550 €
- Dupont | PARTNER | 10 | 220 € | 0 € | 220 €
- Martin | EOS | 42 | 0 € | 924 € | 0 €

### Pour l'Enquêteur - Vue Gains

**Mes gains (avec filtre client optionnel) :**
- Total gagné (tous clients) : 1 240 €
- Total gagné EOS : 850 €
- Total gagné PARTNER : 390 €
- Payé : 600 €
- Reste à payer : 640 €

---

## 🎯 PRIORITÉS

1. **CRITIQUE** : Ajouter appel `calculate_tarif_for_enquete()` dans endpoints validation
2. **HAUTE** : Ajouter sélecteur client dans `FinancialReports.jsx`
3. **HAUTE** : Ajouter filtre client dans `EarningsViewer.jsx`
4. **MOYENNE** : Protéger contre recalcul après paiement
5. **BASSE** : Tests automatisés

---

## 📝 FICHIERS À CRÉER/MODIFIER

### À MODIFIER (Backend)
- [ ] `backend/routes/enquetes.py` (ligne ~206)
- [ ] `backend/routes/validation.py` (ligne ~107)
- [ ] `backend/routes/validation_v2.py` (ligne ~62)
- [ ] `backend/services/tarification_service.py` (ligne ~185, protection paiement)

### À MODIFIER (Frontend)
- [ ] `frontend/src/components/FinancialReports.jsx` (sélecteur + API calls)
- [ ] `frontend/src/components/EarningsViewer.jsx` (filtre client)

### À CRÉER (Tests)
- [ ] `backend/tests/test_tarification_confirmation.py`
- [ ] `backend/tests/test_filtrage_client.py`
- [ ] `backend/tests/test_protection_paiement.py`

---

## ✅ CE QUI EST DÉJÀ EN PLACE (BRAVO !)

1. ✅ Modèle `EnqueteFacturation` avec `client_id` et contrainte unique
2. ✅ `TarificationService` détecte EOS vs PARTNER et utilise les bons tarifs
3. ✅ API `/api/paiement/stats/periodes` accepte `client_id`
4. ✅ API `/api/tarification/stats/global` accepte `client_id`
5. ✅ Service `get_enqueteur_earnings()` filtre par `client_id`
6. ✅ Relations SQL correctes entre tables
7. ✅ Gestion des contestations (positives/négatives)

**Estimation temps total : 2h (avec tests)**

