# Correction erreur 404 DonneeEnqueteur - 23/12/2025 18:55

## 🐛 Problème identifié

**Symptôme** : Erreur 404 lors de l'ouverture du modal de mise à jour PARTNER.

**Erreur console** :
```
GET http://localhost:5000/api/donnees-enqueteur/398 404 (NOT FOUND)
AxiosError: Request failed with status code 404
```

## 🔍 Diagnostic

### Cause racine

Pour les **nouveaux dossiers PARTNER**, il n'y a pas de `DonneeEnqueteur` créé automatiquement lors de l'import. Le `DonneeEnqueteur` n'était créé que lorsque l'enquêteur commençait à remplir les données.

**Conséquence** : Impossible d'ouvrir le modal de mise à jour pour un dossier PARTNER qui n'a jamais été modifié.

### Comportement attendu

Pour PARTNER :
- ✅ Le modal doit s'ouvrir **même si aucun `DonneeEnqueteur` n'existe**
- ✅ Créer automatiquement un `DonneeEnqueteur` vide à la première ouverture
- ✅ Permettre de remplir les données immédiatement

Pour EOS :
- ✅ Garder le comportement actuel (erreur 404 si pas de `DonneeEnqueteur`)

## ✅ Solution appliquée

### Modification de la route GET `/api/donnees-enqueteur/<int:donnee_id>`

**Avant** :
```python
def get_donnee_enqueteur(donnee_id):
    donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
    
    if not donnee_enqueteur:
        return jsonify({
            'success': False, 
            'error': 'Aucune donnée enquêteur trouvée'
        }), 404
    
    return jsonify({'success': True, 'data': donnee_enqueteur.to_dict()})
```

**Après** :
```python
def get_donnee_enqueteur(donnee_id):
    donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=donnee_id).first()
    
    if not donnee_enqueteur:
        # Récupérer le dossier
        donnee = db.session.get(Donnee, donnee_id)
        if donnee:
            client = db.session.get(Client, donnee.client_id)
            is_partner = client and client.code == 'PARTNER'
            
            if is_partner:
                # PARTNER : créer automatiquement un DonneeEnqueteur vide
                donnee_enqueteur = DonneeEnqueteur(
                    donnee_id=donnee_id,
                    client_id=donnee.client_id
                )
                db.session.add(donnee_enqueteur)
                db.session.commit()
                logger.info(f"DonneeEnqueteur créé auto pour PARTNER {donnee_id}")
            else:
                # EOS : retourner 404 (comportement normal)
                return jsonify({'success': False, 'error': '...'}), 404
    
    return jsonify({'success': True, 'data': donnee_enqueteur.to_dict()})
```

### Fichiers modifiés
- `backend/app.py` (route `get_donnee_enqueteur`, lignes 555-591)

## 🎯 Comportement après correction

### Pour PARTNER
1. **Ouverture du modal** → GET `/api/donnees-enqueteur/398`
2. **Aucun `DonneeEnqueteur` trouvé** → Le backend le crée automatiquement
3. **Retour 200 OK** avec un objet vide :
```json
{
  "success": true,
  "data": {
    "id": 123,
    "donnee_id": 398,
    "client_id": 11,
    "code_resultat": null,
    "adresse1": null,
    ...
  }
}
```
4. **Modal s'ouvre** et l'utilisateur peut remplir les données

### Pour EOS
- ✅ Comportement inchangé
- ❌ Si pas de `DonneeEnqueteur` → erreur 404 (normal)

## 🧪 Tests de validation

### 1. Tester avec un nouveau dossier PARTNER
```sql
-- Vérifier qu'il n'a pas de DonneeEnqueteur
SELECT * FROM donnee_enqueteur WHERE donnee_id = 398;
-- Résultat : 0 ligne

-- Ouvrir le modal dans l'UI
-- → Le modal doit s'ouvrir sans erreur

-- Vérifier qu'un DonneeEnqueteur a été créé
SELECT * FROM donnee_enqueteur WHERE donnee_id = 398;
-- Résultat : 1 ligne (créée automatiquement)
```

### 2. Tester avec un dossier EOS sans DonneeEnqueteur
- ✅ Doit retourner 404 (comportement normal EOS)

### 3. Vérifier les logs backend
```
DonneeEnqueteur créé automatiquement pour dossier PARTNER 398
```

## 📊 Impact

| Situation | Avant | Après |
|-----------|-------|-------|
| PARTNER sans DonneeEnqueteur | ❌ Erreur 404 | ✅ Créé auto, modal s'ouvre |
| PARTNER avec DonneeEnqueteur | ✅ OK | ✅ OK (inchangé) |
| EOS sans DonneeEnqueteur | ❌ Erreur 404 | ❌ Erreur 404 (inchangé) |
| EOS avec DonneeEnqueteur | ✅ OK | ✅ OK (inchangé) |

## 🔄 Actions requises

### 1. Redémarrer le backend (obligatoire)
```bash
# Arrêter le backend (Ctrl+C)
# Relancer
DEMARRER_EOS_COMPLET.bat
```

### 2. Tester avec un dossier PARTNER
1. Ouvrir un dossier PARTNER qui n'a jamais été modifié
2. ✅ Le modal doit s'ouvrir sans erreur 404
3. ✅ Tous les onglets doivent être accessibles
4. ✅ Les demandes doivent s'afficher dans l'en-tête et l'onglet "Données"

### 3. Rafraîchir le navigateur après redémarrage backend
```
Ctrl + F5
```

## 💡 Pourquoi cette approche ?

### Alternative 1 : Créer lors de l'import ❌
**Problème** : Ajoute des données inutiles pour tous les dossiers

### Alternative 2 : Gérer côté frontend ❌
**Problème** : Complexifie le code frontend, duplique la logique

### ✅ Solution choisie : Création lazy côté backend
**Avantages** :
- Simple et transparent
- Ne crée que quand nécessaire
- Pas de changement frontend
- Spécifique à PARTNER (EOS non affecté)

## 🎓 Leçon apprise

Pour les systèmes multi-clients avec des workflows différents, prévoir la **création automatique des enregistrements liés** pour éviter les 404 inattendus.

## 🔗 Corrections liées

Cette correction fait partie d'une série de corrections du 23/12/2025 :
1. Naissance non sauvegardée ✅
2. Recalcul automatique ✅
3. TypeError boolean ✅
4. Taille tarif_code ✅
5. Tarif PARTNER ✅
6. Duplication RECHERCHE ✅
7. PartnerHeader undefined ✅
8. Endpoint API incorrect ✅
9. **404 DonneeEnqueteur** ✅ ← Cette correction

---

**Date** : 23/12/2025 18:55  
**Auteur** : Cursor Agent  
**Type** : Correction backend  
**Statut** : ✅ Appliqué (redémarrage backend requis)




