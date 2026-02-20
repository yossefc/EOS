# 🔧 Correction : Historique Contestation PARTNER

## 📋 Problème Identifié

Lors de la consultation de l'historique d'une contestation (ex: JACOB VANILLE), **aucune donnée n'était affichée** et le numéro de dossier était manquant.

### Cause Root

Le frontend (`HistoryModal.jsx`) détecte si la donnée est une contestation et appelle une API spéciale :

```javascript
if (isContestation) {
    response = await fetch(`${API_URL}/api/historique-enquete/${donnee.numeroDossier}`);
}
```

**Mais cette route n'existait pas dans le backend !** ❌

Le frontend appelait également deux autres routes manquantes :
- `/api/archives-enquetes/<donnee_id>`
- `/api/archives-enqueteurs/<donnee_id>`
- `/api/donnees-complete/<donnee_id>`

## ✅ Solution Implémentée

J'ai ajouté **4 nouvelles routes** dans `backend/app.py` :

### 1. `/api/historique-enquete/<numero_dossier>` (GET)

```python
@app.route('/api/historique-enquete/<string:numero_dossier>', methods=['GET'])
def get_historique_enquete_par_numero(numero_dossier):
```

**Fonctionnalités :**
- Cherche une enquête/contestation par son `numeroDossier`
- Retourne l'historique complet JSON
- Retourne les contestations liées (si c'est une enquête originale)
- Retourne l'enquête originale + son historique (si c'est une contestation)
- Retourne les modifications enquêteur
- Retourne toutes les métadonnées (dates, motifs, statut)

**Réponse type :**
```json
{
  "success": true,
  "data": {
    "historique": [...],
    "contestations": [...],
    "enquete_originale": {
      "id": 123,
      "numeroDossier": "EOS0001",
      "nom": "DOE",
      "prenom": "John",
      "historique": [...]
    },
    "modifications": [...],
    "est_contestation": true,
    "numero_dossier": "EOS0002-CON",
    "type_demande": "CON",
    "motif_contestation_code": "A01",
    "motif_contestation_detail": "Adresse incorrecte",
    ...
  }
}
```

### 2. `/api/archives-enquetes/<donnee_id>` (GET)

Récupère tous les snapshots archivés d'une enquête depuis `EnqueteArchive`.

### 3. `/api/archives-enqueteurs/<donnee_id>` (GET)

Récupère tous les snapshots des données enquêteur depuis les archives.

### 4. `/api/donnees-complete/<donnee_id>` (GET)

Récupère une donnée complète avec :
- Données enquêteur
- Informations enquêteur
- Informations client
- Enquête originale (si contestation)

## 🧪 Comment Tester

### 1. Redémarrer le serveur backend

```powershell
cd d:\EOS\backend
python app.py
```

### 2. Tester l'API manuellement

Dans un navigateur ou avec curl :

```
http://localhost:5000/api/historique-enquete/[NUMERO_DOSSIER]
```

Par exemple pour JACOB VANILLE, remplacez `[NUMERO_DOSSIER]` par son numéro.

### 3. Tester dans l'interface

1. Ouvrez l'interface EOS
2. Trouvez une contestation (ex: JACOB VANILLE)
3. Cliquez sur le bouton "Historique"
4. Vérifiez que :
   - ✅ Les données s'affichent
   - ✅ Le numéro de dossier apparaît
   - ✅ L'enquête originale est visible
   - ✅ Les motifs de contestation sont affichés
   - ✅ L'historique JSON est présent

## 📊 Architecture de l'Historique

```
┌─────────────────────────────────────────────────────────┐
│                    CONTESTATION                         │
│                  (JACOB VANILLE)                        │
│                                                         │
│  numeroDossier: "EOS0002-CON"                          │
│  est_contestation: true                                │
│  enquete_originale_id: 123                             │
│  motif_contestation_code: "A01"                        │
│  historique: [                                         │
│    {                                                   │
│      date: "2026-01-15 10:30:00",                     │
│      type: "creation",                                │
│      details: "Contestation de l'enquête EOS0001"     │
│    }                                                   │
│  ]                                                     │
└──────────────┬──────────────────────────────────────────┘
               │
               │ enquete_originale_id
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│                ENQUÊTE ORIGINALE                        │
│                                                         │
│  id: 123                                               │
│  numeroDossier: "EOS0001"                              │
│  nom: "DOE"                                            │
│  prenom: "John"                                        │
│  historique: [                                         │
│    {                                                   │
│      date: "2026-01-10 09:00:00",                     │
│      type: "creation",                                │
│      details: "Enquête créée"                         │
│    },                                                  │
│    {                                                   │
│      date: "2026-01-15 10:30:00",                     │
│      type: "contestation",                            │
│      details: "Contestation reçue: EOS0002-CON"       │
│    }                                                   │
│  ]                                                     │
└─────────────────────────────────────────────────────────┘
```

## 🔍 Points Clés

1. **Double historique** : Lors de l'import d'une contestation, un événement est ajouté dans l'historique de :
   - La contestation elle-même : `"Contestation de l'enquête X"`
   - L'enquête originale : `"Contestation reçue: Y. Motif: Z"`

2. **Recherche intelligente** : La route cherche l'enquête originale par :
   - `numeroDossier` exact
   - `numeroDemande` si pas trouvé
   - Fallback : Nom/Prénom/Date de naissance avec scoring

3. **API duale** : Le frontend utilise 2 stratégies :
   - Contestations : `/api/historique-enquete/<numeroDossier>`
   - Autres : `/api/donnees/<id>/historique`

## 📝 Fichiers Modifiés

- ✅ `backend/app.py` : Ajout de 4 nouvelles routes
  - `get_historique_enquete_par_numero()`
  - `get_archives_enquetes()`
  - `get_archives_enqueteurs()`
  - `get_donnee_complete()`

## 🎯 Résultat Attendu

Après le redémarrage du serveur :

1. Le bouton "Historique" sur une contestation affiche maintenant :
   - ✅ Numéro de dossier de la contestation
   - ✅ Type de demande (CON)
   - ✅ Dates de création/modification
   - ✅ Motifs de contestation (code + libellé)
   - ✅ Lien vers l'enquête originale
   - ✅ Historique JSON complet
   - ✅ Archives (si disponibles)

2. Les mises à jour enquêteur s'affichent correctement

3. Plus d'erreur de connexion API dans la console

---

**Date de correction :** 17 février 2026  
**Testé sur :** JACOB VANILLE (contestation PARTNER)
