# Correction tarification PARTNER - 23/12/2025 18:00

## 🐛 Problème identifié

**Symptôme** : Les enquêtes PARTNER utilisaient la tarification EOS au lieu de la tarification PARTNER combinée.

**Cause** : Dans `backend/services/tarification_service.py`, les méthodes de calcul de tarif utilisaient `TarifClient` (tarif simple par lettre) pour tous les clients non-EOS, au lieu d'utiliser `PartnerTarifResolver` (tarif combiné basé sur les demandes) pour PARTNER.

## ⚙️ Comment ça devrait fonctionner

### Pour EOS
- Tarif basé sur le **code éléments** (A, T, AT, etc.)
- Montant fixe par code

### Pour PARTNER
- Tarif basé sur **lettre + combinaison de demandes**
- Exemple :
  - Lettre `A` + demandes `ADDRESS + EMPLOYER` → tarif combiné spécifique
  - Lettre `B` + demande `BANK` → tarif différent
- Utilise `PartnerTarifResolver.resolve_tarif()` qui :
  1. Récupère les demandes POS du dossier
  2. Construit la clé de combinaison (ex: `ADDRESS+EMPLOYER`)
  3. Cherche une règle exacte (lettre + combinaison)
  4. Sinon, fait la somme des règles unitaires
  5. Retourne le montant calculé

## ✅ Solution appliquée

### Modifications dans `tarification_service.py`

#### 1. Import du PartnerTarifResolver (ligne 11-17)
```python
def get_partner_tarif_resolver():
    """Import lazy de PartnerTarifResolver"""
    try:
        from services.partner_tarif_resolver import PartnerTarifResolver
        return PartnerTarifResolver
    except ImportError:
        return None
```

#### 2. Modification de `_handle_standard_facturation` (ligne 395-460)
Ajout de la détection PARTNER :
```python
# Vérifier si c'est un client PARTNER
client = db.session.get(Client, donnee.client_id)
is_partner = client and client.code == 'PARTNER'

if is_partner:
    # PARTNER : utiliser PartnerTarifResolver (tarif combiné)
    PartnerTarifResolver = get_partner_tarif_resolver()
    if PartnerTarifResolver:
        montant = PartnerTarifResolver.resolve_tarif(
            donnee.client_id,
            donnee.tarif_lettre,
            donnee.id
        )
        # ... appliquer le montant calculé
```

#### 3. Modification de `_handle_positive_contestation` (ligne 315-375)
Même logique pour les contestations positives PARTNER.

### Fichiers modifiés
- `backend/services/tarification_service.py`

## 📊 Impact

### Avant la correction
```
Enquête PARTNER avec lettre A
→ TarifClient cherche lettre A
→ Montant = tarif simple (ex: 10€)
❌ INCORRECT : ignore les demandes combinées
```

### Après la correction
```
Enquête PARTNER avec lettre A + ADDRESS + EMPLOYER
→ PartnerTarifResolver cherche "A + ADDRESS+EMPLOYER"
→ Montant = tarif combiné (ex: 25€)
✅ CORRECT : utilise le tarif combiné configuré
```

## 🧪 Tests à effectuer

### 1. Créer des règles de tarif PARTNER
Dans l'admin PARTNER Tarifs :
- Lettre `A` + `ADDRESS` → 15€
- Lettre `A` + `EMPLOYER` → 20€
- Lettre `A` + `ADDRESS+EMPLOYER` → 30€

### 2. Créer une enquête PARTNER
- Importer un dossier avec `RECHERCHE = "ADRESSE EMPLOYEUR"`
- Lettre de tarif = `A`

### 3. Remplir les données
- Ouvrir la mise à jour
- Remplir une adresse (→ ADDRESS devient POS)
- Remplir un employeur (→ EMPLOYER devient POS)
- Sauvegarder

### 4. Valider l'enquête
- Marquer comme validée
- Vérifier la facturation créée

### 5. Vérifier le montant
**Attendu** :
- `tarif_eos_code` = `A`
- `tarif_eos_montant` = `30.00` (tarif combiné A + ADDRESS+EMPLOYER)
- `resultat_eos_montant` = `30.00`
- `tarif_enqueteur_montant` = `21.00` (70% de 30€)

**Ne PAS avoir** :
- `tarif_eos_montant` = `10.00` (tarif simple EOS)

## 🔍 Diagnostic en cas de problème

### Si le montant est toujours 0 ou 10€

1. **Vérifier que les demandes sont créées** :
```sql
SELECT * FROM partner_case_requests WHERE donnee_id = <ID>;
```
Doit afficher ADDRESS et EMPLOYER avec `status='POS'`

2. **Vérifier que les règles de tarif existent** :
```sql
SELECT * FROM partner_tarif_rules 
WHERE client_id = <PARTNER_CLIENT_ID> 
  AND tarif_lettre = 'A';
```

3. **Vérifier les logs backend** :
Chercher :
```
Résolution tarif: lettre=A, demandes=ADDRESS+EMPLOYER, donnee_id=<ID>
Tarif PARTNER combiné appliqué: 30.00€
```

## 📝 Notes techniques

### Pourquoi un import lazy ?
```python
def get_partner_tarif_resolver():
    from services.partner_tarif_resolver import PartnerTarifResolver
    return PartnerTarifResolver
```

**Raison** : Éviter les imports circulaires. `tarification_service.py` est importé par beaucoup de modules, dont `partner_tarif_resolver.py` pourrait dépendre indirectement.

### Pourquoi 70% pour l'enquêteur ?
```python
facturation.tarif_enqueteur_montant = montant * 0.7
```

**Convention** : L'enquêteur reçoit 70% du montant EOS/PARTNER, comme pour EOS.

### Fallback EOS
Si `PartnerTarifResolver` retourne `None` (pas de règle trouvée), le système utilise quand même `get_tarif_eos` comme fallback pour ne pas bloquer la facturation.

## ⚠️ Actions requises

### 1. Redémarrer le backend
```bash
# Arrêter le backend (Ctrl+C)
# Relancer
DEMARRER_EOS_COMPLET.bat
```

### 2. Recalculer les facturations existantes (optionnel)
Si des enquêtes PARTNER ont déjà été validées avec le mauvais tarif :
```sql
-- Supprimer les anciennes facturations PARTNER
DELETE FROM enquete_facturation 
WHERE donnee_id IN (
    SELECT id FROM donnees WHERE client_id = <PARTNER_CLIENT_ID>
);

-- Elles seront recréées automatiquement au prochain calcul
```

### 3. Tester avec une nouvelle enquête
Suivre les étapes de test ci-dessus.

## 📈 Améliorations futures possibles

1. **Interface de visualisation** : Afficher le détail du calcul de tarif dans l'UI (lettre + demandes + montant)
2. **Historique des tarifs** : Garder une trace des tarifs appliqués même si les règles changent
3. **Alertes** : Notifier si aucun tarif n'est trouvé pour une combinaison donnée

---

**Date** : 23/12/2025 18:00  
**Auteur** : Cursor Agent  
**Version** : 1.0  
**Statut** : ✅ Correction appliquée, backend à redémarrer



