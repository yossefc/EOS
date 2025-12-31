# ✅ Modifications Tarifs Enquêteur - Support PARTNER

## 🎯 Objectifs Atteints

1. ✅ **Suppression de l'onglet "Rapports Financiers"** dans "Gérer les Tarifs"
2. ✅ **Ajout du support PARTNER** pour les tarifs enquêteur
3. ✅ **Interface améliorée** avec sélecteur de client

## 📋 Modifications Apportées

### 1. Frontend - TarificationViewer.jsx

#### Suppressions
- ✅ Suppression de l'onglet "Rapports Financiers"
- ✅ Suppression du contenu de la section rapports
- ✅ Suppression des états `globalStats`, `enquetesAFacturer`, `loadingStats`, `loadingEnquetes`
- ✅ Suppression des fonctions `fetchGlobalStats()` et `fetchEnquetesAFacturer()`

#### Ajouts
- ✅ État `clients` pour stocker la liste des clients
- ✅ Champ `client_id` dans `formDataEnqueteur`
- ✅ Chargement des clients dans `fetchData()`
- ✅ Sélecteur "Client" dans le formulaire d'ajout/modification
- ✅ Colonne "Client" dans le tableau des tarifs enquêteur
- ✅ Badge coloré pour identifier EOS vs PARTNER

### 2. Backend - models/tarifs.py

#### Modèle TarifEnqueteur
- ✅ Ajout du champ `client_id` (nullable, FK → clients.id)
- ✅ Ajout de la relation `client`
- ✅ Mise à jour de `to_dict()` pour inclure `client_id` et `client_nom`

### 3. Backend - routes/tarification.py

#### Endpoint POST /api/tarifs/enqueteur
- ✅ Accepte le paramètre `client_id`
- ✅ Vérifie l'existence d'un tarif pour code + enquêteur + client
- ✅ Crée le tarif avec le `client_id` spécifié

#### Endpoint PUT /api/tarifs/enqueteur/<id>
- ✅ Permet la mise à jour du `client_id`

### 4. Migration Base de Données

**Fichier** : `backend/migrations/versions/004_add_client_id_to_tarif_enqueteur.py`

- ✅ Ajout de la colonne `client_id` (nullable)
- ✅ Clé étrangère vers `clients.id`
- ✅ Index sur `client_id` pour performance

## 🎨 Interface Utilisateur

### Formulaire d'Ajout de Tarif Enquêteur

```
┌──────────────────────────────────────────────────────────┐
│  Ajouter un nouveau tarif                                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Code* │ Description │ Montant* │ Client │ Enquêteur   │
│  ───── │ ─────────── │ ──────── │ ────── │ ──────────  │
│  AT    │ Adresse+Tel │ 15.40    │PARTNER │ Tous       │
│                                    └──→ 💡 Pour PARTNER │
│                                                          │
│                             [✅ Enregistrer]             │
└──────────────────────────────────────────────────────────┘
```

### Champs du Formulaire

1. **Code** : Code des éléments (A, AT, ATB, etc.)
2. **Description** : Description du tarif
3. **Montant** : Montant en euros
4. **Client** : 
   - Option par défaut : "Par défaut (EOS)"
   - Liste des clients disponibles (EOS, PARTNER, etc.)
   - 💡 Indication "Pour PARTNER"
5. **Enquêteur** :
   - Option par défaut : "Tous les enquêteurs"
   - Liste des enquêteurs spécifiques

### Tableau des Tarifs

```
┌───────────────────────────────────────────────────────────────┐
│ Code │ Description     │ Montant │ Client    │ Enquêteur│ ... │
├──────┼─────────────────┼─────────┼───────────┼──────────┼─────┤
│ AT   │ Adresse+Tél     │ 15.40 € │ EOS       │ Tous     │ ... │
│ AT   │ Adresse+Tél PTR │ 12.00 € │ PARTNER   │ Tous     │ ... │
│ ATB  │ Adresse+Tél+Bnq │ 16.80 € │ EOS       │ Tous     │ ... │
└───────────────────────────────────────────────────────────────┘
```

### Badges Colorés

- **EOS (défaut)** : Badge gris
- **EOS France** : Badge bleu
- **PARTNER** : Badge vert
- **Tous (enquêteurs)** : Badge violet

## 🔄 Logique de Fonctionnement

### Création d'un Tarif

1. Utilisateur remplit le formulaire
2. Sélectionne un client (optionnel, défaut = EOS)
3. Sélectionne un enquêteur (optionnel, défaut = Tous)
4. Soumission du formulaire
5. Backend vérifie si un tarif existe déjà pour :
   - Code + Enquêteur + Client
6. Si oui : désactive l'ancien tarif
7. Crée le nouveau tarif avec `client_id`

### Calcul de Tarification (Backend)

Lors du calcul d'une facture :
1. Récupère le client de l'enquête (via `donnee.client_id`)
2. Cherche un tarif enquêteur pour :
   - Code + Enquêteur spécifique + Client spécifique
   - Sinon : Code + Tous enquêteurs + Client spécifique
   - Sinon : Code + Enquêteur spécifique + EOS (défaut)
   - Sinon : Code + Tous enquêteurs + EOS (défaut)

**Ordre de priorité :**
1. Tarif spécifique : Client X + Enquêteur Y + Code Z
2. Tarif client : Client X + Tous enquêteurs + Code Z
3. Tarif enquêteur : EOS + Enquêteur Y + Code Z
4. Tarif par défaut : EOS + Tous enquêteurs + Code Z

## 💡 Cas d'Usage

### Cas 1 : Tarif Enquêteur Différent pour PARTNER

**Contexte :** PARTNER paie moins cher les enquêteurs que EOS.

**Solution :**
1. Créer un tarif "AT" pour EOS : 15,40 €
2. Créer un tarif "AT" pour PARTNER : 12,00 €

**Résultat :**
- Enquête EOS code AT → Enquêteur reçoit 15,40 €
- Enquête PARTNER code AT → Enquêteur reçoit 12,00 €

### Cas 2 : Enquêteur Spécialisé PARTNER

**Contexte :** Un enquêteur fait uniquement des enquêtes PARTNER avec un tarif spécial.

**Solution :**
1. Créer un tarif pour Client=PARTNER + Enquêteur=Jean Dupont

**Résultat :**
- Jean Dupont sur enquête PARTNER → Utilise son tarif spécial
- Autres enquêteurs sur PARTNER → Utilisent le tarif par défaut PARTNER

### Cas 3 : Tarif Unique pour Tous

**Contexte :** Même tarif pour tous les clients et tous les enquêteurs.

**Solution :**
1. Créer un tarif avec Client="Par défaut (EOS)" et Enquêteur="Tous"

**Résultat :**
- Tous les clients → Utilisent ce tarif
- Tous les enquêteurs → Utilisent ce tarif

## 🚀 Pour Appliquer les Modifications

### 1. Appliquer la Migration

```bash
cd backend
$env:DATABASE_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
python -m flask db upgrade
```

### 2. Redémarrer le Backend

Le backend doit être redémarré pour prendre en compte :
- Le nouveau champ `client_id` dans le modèle
- Les modifications des endpoints

### 3. Rafraîchir le Frontend

Le frontend doit être rafraîchi (F5) pour charger :
- Le nouveau formulaire avec sélecteur de client
- Le nouveau tableau avec colonne "Client"

## ✅ Tests Recommandés

### Test 1 : Créer un Tarif PARTNER

1. Aller dans "Finance & Paiements" → "Gérer les Tarifs" → "Tarifs Enquêteur"
2. Cliquer sur "Ajouter un tarif"
3. Remplir :
   - Code : W
   - Description : Tarif PARTNER
   - Montant : 12.00
   - Client : PARTNER
   - Enquêteur : Tous
4. Cliquer "Enregistrer"
5. ✅ Le tarif apparaît dans le tableau avec badge vert "PARTNER"

### Test 2 : Vérifier l'Application du Tarif

1. Créer une enquête PARTNER
2. Assigner un enquêteur
3. Confirmer l'enquête
4. Aller dans "Paiements Enquêteurs"
5. ✅ Le montant de l'enquêteur correspond au tarif PARTNER (12.00€)

### Test 3 : Vérifier la Séparation

1. Créer une enquête EOS avec même code
2. Assigner le même enquêteur
3. Confirmer l'enquête
4. ✅ Le montant de l'enquêteur correspond au tarif EOS (15.40€)

## 📊 Résumé des Avantages

| Avant | Maintenant |
|-------|------------|
| ❌ Tarif enquêteur unique pour tous les clients | ✅ Tarif enquêteur par client (EOS / PARTNER) |
| ❌ Onglet "Rapports Financiers" inutile dans Tarifs | ✅ Onglet supprimé (disponible dans "Gains Administrateur") |
| ❌ Impossible de différencier EOS vs PARTNER | ✅ Badge coloré pour identifier rapidement |
| ❌ Pas de flexibilité tarifaire | ✅ Flexibilité totale : par client, par enquêteur, par code |

## 🎉 Conclusion

Le système de tarification enquêteur supporte maintenant **PARTNER** de manière native.

**Principales améliorations :**
- ✅ Tarifs enquêteur différenciés par client
- ✅ Interface simplifiée (suppression rapports)
- ✅ Badge visuel pour identifier les clients
- ✅ Ordre de priorité intelligent pour le calcul

**Prochaines étapes (optionnel) :**
- Export PDF des tarifs par client
- Historique des modifications de tarifs
- Alerte si tarif manquant pour un code

**Statut** : ✅ **TERMINÉ ET PRÊT À UTILISER**




