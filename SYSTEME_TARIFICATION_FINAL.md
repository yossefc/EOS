# 📊 Système de Tarification/Paiements/Rapports Financiers - Documentation Complète

## 🎯 Objectifs Fonctionnels Atteints

### 1. Vue Administrateur Séparée EOS vs PARTNER ✅
- **Rapports Financiers** : Sélecteur de client permettant de filtrer par EOS, PARTNER ou tous les clients
- **Statistiques Globales** : Affichage séparé des montants par client
  - Total EOS (prix client)
  - Total versé enquêteurs EOS
  - Marge EOS
  - Total PARTNER (prix client)
  - Total versé enquêteurs PARTNER
  - Marge PARTNER

### 2. Vue Par Enquêteur (Par Client et Global) ✅
- **EarningsViewer** : Filtre client pour voir les gains par client
  - `total_gagne` : Total des montants calculés
  - `total_paye` : Total des montants déjà payés
  - `reste_a_payer` : Montants en attente de paiement
- Historique des 6 derniers mois filtrable par client

### 3. Persistance des Montants Après Confirmation ✅
- Les montants sont calculés **UNE SEULE FOIS** lors de la confirmation
- Stockés dans la table `enquete_facturation` avec :
  - `resultat_eos_montant` : Prix client
  - `resultat_enqueteur_montant` : Gain enquêteur
  - `client_id` : Traçabilité du client
  - `tarif_eos_code` / `tarif_enqueteur_code` : Codes tarifs appliqués
- **Protection** : Impossible de recalculer une facturation déjà payée

## 🏗️ Architecture Technique

### Backend

#### 1. Modèles (`backend/models/tarifs.py`)
```python
class EnqueteFacturation:
    - donnee_id (FK → donnees)
    - donnee_enqueteur_id (FK → donnees_enqueteur)
    - client_id (FK → clients) ✅ AJOUTÉ
    - resultat_eos_montant (prix client)
    - resultat_enqueteur_montant (gain enquêteur)
    - paye (boolean)
    - date_paiement
    - reference_paiement
    - created_at / updated_at
    
    Contraintes:
    - UNIQUE(donnee_id, donnee_enqueteur_id) ✅ Empêche les doublons
    - INDEX sur client_id ✅ Performance
```

#### 2. Service de Tarification (`backend/services/tarification_service.py`)

**Fonction Principale : `calculate_tarif_for_enquete(donnee_enqueteur_id)`**

Logique :
1. Récupère la donnée et l'enquêteur
2. Détecte le client (EOS vs PARTNER)
3. Calcule le prix client :
   - **EOS** : Via `TarifEOS` (codes A, AT, ATB, etc.)
   - **PARTNER** : Via `TarifClient` (mapping lettres → montants)
4. Calcule le gain enquêteur (ex: 70% ou règle spécifique)
5. Crée ou met à jour `EnqueteFacturation`
6. **Protection** : Si déjà payé, refuse le recalcul

**Points d'Appel :**
- `/api/enquetes/confirm` (ligne 198-218 de `enquetes.py`) ✅
- `/api/enquete/valider/<id>` (ligne 95-107 de `validation.py`) ✅
- `/api/enquetes/<id>/valider` (ligne 52-62 de `validation_v2.py`) ✅
- Assignation d'enquêteur si code résultat = 'P' ou 'H' (`app.py` ligne 986-991)

#### 3. API Endpoints

**Statistiques Globales** (`backend/routes/tarification.py`)
```python
GET /api/tarification/stats/global?client_id=<id>
```
Retourne :
- `total_eos` : Somme des prix clients
- `total_enqueteurs` : Somme des gains enquêteurs
- `enquetes_traitees` : Nombre d'enquêtes
- `enquetes_positives` : Nombre de résultats positifs

**Statistiques Par Période** (`backend/routes/paiement.py`)
```python
GET /api/paiement/stats/periodes?mois=12&client_id=<id>
```
Retourne pour chaque mois :
- `montant_facture` : Total facturé
- `montant_enqueteurs` : Total enquêteurs
- `montant_paye` : Total payé
- `marge` : Différence

**Gains Enquêteur** (`backend/routes/tarification.py`)
```python
GET /api/facturation/enqueteur/<id>?month=<m>&year=<y>&client_id=<cid>
```
Retourne :
- `total_gagne` : Total des facturations
- `total_paye` : Montants payés
- `total_a_payer` : Reste à payer
- `facturations[]` : Liste détaillée

**Enquêteurs À Payer** (`backend/routes/paiement.py`)
```python
GET /api/paiement/enqueteurs-a-payer?client_id=<id>
```
Liste des enquêteurs avec montants impayés

### Frontend

#### 1. Rapports Financiers (`frontend/src/components/FinancialReports.jsx`)

**Ajouts :**
- État `selectedClientId` pour filtrer par client
- Sélecteur dropdown "Tous les clients / EOS / PARTNER"
- Appels API avec paramètre `client_id`
- Affichage séparé des statistiques par client

**Utilisation :**
```jsx
<select onChange={(e) => setSelectedClientId(e.target.value)}>
  <option value="">Tous les clients</option>
  {clients.map(client => (
    <option value={client.id}>{client.nom}</option>
  ))}
</select>
```

#### 2. Vue Gains Enquêteur (`frontend/src/components/EarningsViewer.jsx`)

**Ajouts :**
- État `selectedClientId` pour filtrer par client
- Sélecteur dropdown dans les filtres
- Appels API avec paramètre `client_id`
- Historique des 6 derniers mois filtré par client

**Utilisation :**
```jsx
// Dans les filtres
{clients.length > 1 && (
  <select onChange={(e) => setSelectedClientId(e.target.value)}>
    <option value="">Tous</option>
    {clients.map(client => (
      <option value={client.id}>{client.nom}</option>
    ))}
  </select>
)}
```

## 🔒 Règles de Gestion

### 1. Calcul de Tarification
- **Déclenchement** : Lors de la confirmation de l'enquête (statut → 'confirmee' ou 'validee')
- **Fréquence** : Une seule fois par enquête (sauf si non payée)
- **Stockage** : Table `enquete_facturation` avec tous les détails

### 2. Recalcul Autorisé
- ✅ **OUI** : Si facturation existe mais `paye = False`
- ❌ **NON** : Si facturation existe et `paye = True`
- **Audit** : Les timestamps `created_at` et `updated_at` permettent de tracer les modifications

### 3. Contestations
- Gérées par la logique existante dans `TarificationService`
- Création de facturations négatives pour déductions
- Création de facturations positives pour confirmations
- Toutes liées au `client_id` de l'enquête originale

## 🧪 Tests et Validation

### Script de Test (`backend/test_tarification_system.py`)

**Ce que le script teste :**
1. ✅ Présence des clients EOS et PARTNER
2. ✅ Présence des tarifs (EOS et PARTNER)
3. ✅ Création de 4 dossiers de test (2 EOS, 2 PARTNER)
4. ✅ Calcul correct des tarifications
5. ✅ Persistance en base de données
6. ✅ Contrainte unique (pas de doublons)
7. ✅ Protection contre recalcul après paiement
8. ✅ Séparation des statistiques par client

**Exécution :**
```bash
cd backend
python test_tarification_system.py
```

**Résultat Attendu :**
```
✅ Tous les tests sont passés avec succès !

📋 Résumé:
  - Clients testés: EOS (1) et PARTNER (2)
  - Dossiers créés: 4 (2 EOS, 2 PARTNER)
  - Facturations créées: 4
  - Contrainte unique: ✅
  - Protection paiement: ✅
  - Séparation stats: ✅
```

## 📝 Migration Base de Données

### Changements Appliqués
1. **Ajout colonne `client_id`** à `enquete_facturation`
2. **Clé étrangère** vers `clients(id)`
3. **Index** sur `client_id` pour performance
4. **Contrainte unique** sur `(donnee_id, donnee_enqueteur_id)`

### Script SQL Appliqué (`backend/fix_add_client_id_v2.sql`)
```sql
-- Ajout de client_id
ALTER TABLE enquete_facturation ADD COLUMN client_id INTEGER;

-- Population depuis donnees
UPDATE enquete_facturation ef
SET client_id = d.client_id
FROM donnees d
WHERE ef.donnee_id = d.id;

-- Contrainte NOT NULL
ALTER TABLE enquete_facturation ALTER COLUMN client_id SET NOT NULL;

-- Clé étrangère
ALTER TABLE enquete_facturation 
ADD CONSTRAINT fk_enquete_facturation_client_id 
FOREIGN KEY (client_id) REFERENCES clients(id);

-- Index
CREATE INDEX ix_enquete_facturation_client_id ON enquete_facturation(client_id);

-- Contrainte unique
ALTER TABLE enquete_facturation 
ADD CONSTRAINT uq_enquete_facturation_donnee 
UNIQUE (donnee_id, donnee_enqueteur_id);
```

## ✅ Critères d'Acceptation

### 1. Montants Corrects Après Confirmation ✅
- Les montants affichés correspondent EXACTEMENT à la tarification (EOS ou PARTNER)
- Pas de différence entre les écrans (source unique : `enquete_facturation`)

### 2. Rapports Filtrables Par Client ✅
- Sélecteur de client dans `FinancialReports.jsx`
- Sélecteur de client dans `EarningsViewer.jsx`
- API endpoints supportent le paramètre `client_id`

### 3. Montants Stables ✅
- Une fois calculés, les montants ne changent pas "selon l'écran"
- Protection contre recalcul après paiement
- Contrainte unique empêche les doublons

### 4. Aucune Régression EOS ✅
- Tous les changements sont conditionnés ou rétrocompatibles
- Logique EOS existante préservée
- Ajout de filtres optionnels (pas obligatoires)

## 🚀 Utilisation

### Pour l'Administrateur

1. **Voir les rapports financiers globaux**
   - Aller dans l'onglet "Rapports Financiers"
   - Sélectionner "Tous les clients" pour vue globale
   - Sélectionner "EOS" ou "PARTNER" pour vue spécifique

2. **Voir les gains d'un enquêteur**
   - Aller dans l'onglet "Paiements"
   - Cliquer sur un enquêteur
   - Utiliser le filtre "Client" pour voir par client ou global

3. **Marquer des paiements**
   - Aller dans l'onglet "Paiements"
   - Sélectionner les facturations à payer
   - Cliquer sur "Marquer comme payé"
   - ⚠️ Une fois payé, le montant ne peut plus être modifié

### Pour le Développeur

1. **Ajouter un nouveau client**
   - Créer le client dans la table `clients`
   - Créer les tarifs dans `tarif_client` (si PARTNER)
   - Les enquêtes de ce client seront automatiquement filtrées

2. **Modifier un tarif**
   - Modifier dans `tarif_eos` ou `tarif_client`
   - Les nouvelles confirmations utiliseront le nouveau tarif
   - Les anciennes facturations (non payées) peuvent être recalculées manuellement

3. **Déboguer une facturation**
   - Vérifier `enquete_facturation.client_id`
   - Vérifier `enquete_facturation.paye`
   - Vérifier `enquete_facturation.created_at` et `updated_at`
   - Logs dans `TarificationService.calculate_tarif_for_enquete`

## 📊 Schéma de Flux

```
┌─────────────────────────────────────────────────────────────┐
│  1. CONFIRMATION D'ENQUÊTE                                  │
│     (Admin clique "Confirmer")                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. ENDPOINT API                                            │
│     /api/enquetes/confirm                                   │
│     /api/enquete/valider/<id>                              │
│     /api/enquetes/<id>/valider                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. CALCUL TARIFICATION                                     │
│     TarificationService.calculate_tarif_for_enquete()       │
│                                                             │
│     • Détecte client (EOS vs PARTNER)                      │
│     • Calcule prix client                                   │
│     • Calcule gain enquêteur                                │
│     • Vérifie si déjà payé (protection)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. PERSISTANCE                                             │
│     INSERT/UPDATE enquete_facturation                       │
│                                                             │
│     • donnee_id                                             │
│     • donnee_enqueteur_id                                   │
│     • client_id ✅                                          │
│     • resultat_eos_montant (prix client)                   │
│     • resultat_enqueteur_montant (gain)                    │
│     • paye = False                                          │
│     • created_at = NOW()                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  5. AFFICHAGE                                               │
│                                                             │
│     ┌──────────────────┐    ┌──────────────────┐          │
│     │ FinancialReports │    │ EarningsViewer   │          │
│     │                  │    │                  │          │
│     │ • Filtre client  │    │ • Filtre client  │          │
│     │ • Stats globales │    │ • Gains enquêteur│          │
│     └──────────────────┘    └──────────────────┘          │
│                                                             │
│     Source unique: enquete_facturation ✅                   │
│     Pas de recalcul à l'affichage ✅                       │
└─────────────────────────────────────────────────────────────┘
```

## 🎉 Conclusion

Le système de tarification/paiements/rapports financiers est maintenant :
- ✅ **Stable** : Montants calculés une fois et persistés
- ✅ **Séparé** : Filtrage EOS vs PARTNER fonctionnel
- ✅ **Protégé** : Impossible de modifier après paiement
- ✅ **Traçable** : `client_id` sur toutes les facturations
- ✅ **Testé** : Script de validation complet
- ✅ **Rétrocompatible** : Aucune régression EOS

**Prochaines Étapes Possibles :**
1. Ajouter des rapports PDF exportables par client
2. Ajouter un historique des modifications de tarifs
3. Ajouter des notifications automatiques pour les paiements
4. Ajouter un dashboard de comparaison EOS vs PARTNER



