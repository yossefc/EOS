# 💰 Calcul des Gains Enquêteur PARTNER - Explications

## 🎯 Problème Actuel

Le système actuel de tarification enquêteur basé sur des **codes** (A, AT, ATB, etc.) **n'est PAS adapté** à PARTNER.

### Pourquoi ?

| Client | Système de Tarification Client | Système Tarif Enquêteur | Problème |
|--------|-------------------------------|------------------------|----------|
| **EOS** | Code → Montant (ex: AT = 15,40€) | Code → Montant | ✅ Compatible |
| **PARTNER** | **Lettre** → Montant (ex: W = 20€) | Code → Montant | ❌ **Incompatible** |

**PARTNER utilise des LETTRES (W, X, Y, Z)**, pas des codes d'éléments (A, AT, ATB).

## 🔄 Comment ça Fonctionne Actuellement

### Pour EOS (✅ Fonctionne)

```
1. Enquête confirmée avec code "AT"
2. Système cherche TarifEOS pour "AT" → 15,40€
3. Système cherche TarifEnqueteur pour "AT" → 11,00€
4. Facturation créée :
   - Prix client EOS : 15,40€
   - Gain enquêteur : 11,00€
   - Marge admin : 4,40€
```

### Pour PARTNER (❌ Ne fonctionne pas correctement)

```
1. Enquête PARTNER confirmée avec lettre "W"
2. Système cherche TarifClient pour "W" → 20,00€ ✅
3. Système cherche TarifEnqueteur pour "W" → ❌ N'EXISTE PAS
4. Problème : pas de tarif enquêteur trouvé !
```

## 🛠️ Solution : Deux Approches

### Approche 1 : Pourcentage (Recommandé)

**Principe :** Les enquêteurs PARTNER reçoivent un **pourcentage fixe** du montant facturé au client.

**Exemple :**
- Client PARTNER paie 20€ (lettre W)
- Enquêteur reçoit **60%** = 12€
- Admin garde **40%** = 8€

**Avantages :**
- ✅ Simple à gérer
- ✅ S'adapte automatiquement aux tarifs PARTNER
- ✅ Pas besoin de créer des tarifs pour chaque lettre

**Implémentation :**
```python
# Dans TarificationService
if client.code == "PARTNER":
    prix_client = TarifClient.get_montant_pour_lettre(lettre)  # Ex: 20€
    pourcentage_enqueteur = 0.60  # 60% configurable
    montant_enqueteur = prix_client * pourcentage_enqueteur
```

### Approche 2 : Mapping Lettre → Montant Enquêteur

**Principe :** Créer des tarifs enquêteur pour chaque lettre PARTNER.

**Exemple :**
| Lettre | Prix Client | Prix Enquêteur |
|--------|-------------|----------------|
| W | 20€ | 12€ |
| X | 25€ | 15€ |
| Y | 30€ | 18€ |
| Z | 35€ | 21€ |

**Inconvénients :**
- ❌ Nécessite de créer manuellement les tarifs pour W, X, Y, Z
- ❌ Pas intuitif (les lettres ne correspondent pas à des éléments retrouvés)
- ❌ Maintenance complexe (si tarif client change, faut changer tarif enquêteur)

## ✅ Implémentation Recommandée : Pourcentage Configurable

### 1. Ajouter un Champ `pourcentage_enqueteur` dans `Client`

```python
# backend/models/client.py
class Client(db.Model):
    # ... champs existants ...
    pourcentage_enqueteur = db.Column(db.Numeric(5, 2), default=60.00)  # 60% par défaut
```

### 2. Modifier `TarificationService.get_tarif_enqueteur`

```python
def get_tarif_enqueteur(self, donnee: Donnee, client: Client, montant_eos: float) -> dict:
    """
    Calcule le montant à payer à l'enquêteur
    
    - Pour EOS : utilise TarifEnqueteur (code → montant)
    - Pour PARTNER : applique pourcentage_enqueteur sur montant facturé client
    """
    
    if client.code == "PARTNER":
        # Pour PARTNER : pourcentage du montant client
        lettre_tarif = donnee.lettre_tarif  # Ex: W
        
        # Obtenir le montant facturé au client PARTNER
        montant_client = self.partner_tarif_resolver.get_montant_for_lettre(
            client_id=client.id,
            lettre=lettre_tarif
        )
        
        # Appliquer le pourcentage configuré
        pourcentage = float(client.pourcentage_enqueteur or 60.00) / 100
        montant_enqueteur = montant_client * pourcentage
        
        return {
            'code': lettre_tarif,
            'description': f'Tarif PARTNER {lettre_tarif} ({client.pourcentage_enqueteur}%)',
            'montant': montant_enqueteur
        }
    
    else:
        # Pour EOS : logique actuelle (TarifEnqueteur par code)
        code = donnee.elementsRetrouves or 'A'
        enqueteur_id = donnee.enqueteurId
        
        # Chercher tarif spécifique enquêteur puis tarif par défaut
        tarif = TarifEnqueteur.query.filter_by(
            code=code,
            enqueteur_id=enqueteur_id,
            actif=True
        ).first()
        
        if not tarif:
            tarif = TarifEnqueteur.query.filter_by(
                code=code,
                enqueteur_id=None,
                actif=True
            ).first()
        
        if not tarif:
            raise ValueError(f"Aucun tarif enquêteur trouvé pour le code {code}")
        
        return {
            'code': tarif.code,
            'description': tarif.description,
            'montant': float(tarif.montant)
        }
```

### 3. Interface Admin pour Configurer le Pourcentage

**Dans l'interface "Gestion Clients" :**

```jsx
<div>
  <label>Pourcentage Enquêteur (%)</label>
  <input
    type="number"
    value={client.pourcentage_enqueteur}
    min="0"
    max="100"
    step="0.01"
    className="border p-2 rounded"
  />
  <p className="text-xs text-gray-500">
    Montant versé à l'enquêteur en % du prix facturé au client
  </p>
</div>
```

**Exemple d'utilisation :**
- Client EOS : pourcentage_enqueteur = NULL (utilise tarifs classiques)
- Client PARTNER : pourcentage_enqueteur = 60.00 (enquêteur reçoit 60%)

## 📊 Exemple Complet : Calcul PARTNER

### Scénario

1. **Client :** PARTNER (pourcentage_enqueteur = 60%)
2. **Enquête :** Lettre W
3. **Tarif PARTNER lettre W :** 20,00€
4. **Enquêteur :** Jean Dupont

### Calcul Automatique

```python
# 1. Récupérer le montant facturé au client
montant_client = TarifClient.get(client_id=PARTNER, lettre='W')
# → 20,00€

# 2. Calculer le gain enquêteur
pourcentage = 60.00 / 100  # = 0.60
montant_enqueteur = 20.00 * 0.60
# → 12,00€

# 3. Calculer la marge admin
marge = 20.00 - 12.00
# → 8,00€
```

### Résultat dans EnqueteFacturation

```
{
  "donnee_id": 123,
  "client_id": 2,  // PARTNER
  "tarif_eos_code": "W",
  "tarif_eos_montant": 20.00,       // Prix facturé au client
  "resultat_eos_montant": 20.00,
  "tarif_enqueteur_code": "W",
  "tarif_enqueteur_montant": 12.00,  // 60% de 20€
  "resultat_enqueteur_montant": 12.00,
  "paye": false
}
```

## 🎯 Avantages de cette Approche

| Critère | Solution Pourcentage | Solution Mapping Manuel |
|---------|---------------------|------------------------|
| **Simplicité** | ✅ Très simple | ❌ Complexe |
| **Maintenance** | ✅ Automatique | ❌ Manuelle |
| **Flexibilité** | ✅ Configurable par client | ⚠️ Fixe |
| **Évolutivité** | ✅ Nouveaux tarifs PARTNER auto | ❌ Doit créer manuellement |
| **Cohérence** | ✅ Toujours correct | ⚠️ Risque désynchronisation |

## 🚀 Mise en Place Recommandée

### Étape 1 : Migration Base de Données

```sql
-- Ajouter le champ pourcentage_enqueteur à la table clients
ALTER TABLE clients ADD COLUMN pourcentage_enqueteur NUMERIC(5, 2) DEFAULT 60.00;

-- Définir 60% pour PARTNER
UPDATE clients SET pourcentage_enqueteur = 60.00 WHERE code = 'PARTNER';

-- Laisser NULL pour EOS (utilise tarifs classiques)
UPDATE clients SET pourcentage_enqueteur = NULL WHERE code = 'EOS';
```

### Étape 2 : Modifier TarificationService

Implémenter la logique décrite ci-dessus dans `get_tarif_enqueteur()`.

### Étape 3 : Ajouter l'Interface Admin

Dans "Gestion Clients" :
- Champ "Pourcentage Enquêteur"
- Info-bulle explicative
- Validation (0-100%)

### Étape 4 : Tester

1. Créer une enquête PARTNER avec lettre W (tarif 20€)
2. Confirmer l'enquête
3. Vérifier :
   - Prix client = 20€
   - Gain enquêteur = 12€ (60%)
   - Marge = 8€

## 💡 Alternative Mixte (Optionnel)

Permettre **à la fois** :
- Pourcentage par défaut (60%)
- Override manuel pour cas spéciaux

**Logique :**
```python
# 1. Chercher un TarifEnqueteur spécifique pour cette lettre + client PARTNER
tarif_special = TarifEnqueteur.query.filter_by(
    code=lettre,
    client_id=PARTNER_ID,
    actif=True
).first()

if tarif_special:
    # Utiliser le tarif manuel
    return tarif_special.montant
else:
    # Utiliser le pourcentage par défaut
    return montant_client * (client.pourcentage_enqueteur / 100)
```

**Cas d'usage :**
- Lettre W : 60% automatique (12€ sur 20€)
- Lettre X : tarif spécial 18€ (au lieu de 60% de 25€ = 15€)

## ✅ Conclusion

**Recommandation finale :** Utiliser le **système de pourcentage** pour PARTNER.

**Pourquoi ?**
- Simple à comprendre et maintenir
- Évite la duplication de configuration
- S'adapte automatiquement aux changements de tarifs client
- Transparent pour l'utilisateur

**Prochaine étape :** Implémentation de `pourcentage_enqueteur` dans le modèle `Client` et adaptation de `TarificationService`.




