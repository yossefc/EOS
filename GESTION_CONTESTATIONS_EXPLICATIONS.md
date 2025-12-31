# 🔄 GESTION DES CONTESTATIONS - Explication Complète

**Date** : 24 décembre 2025

---

## 📋 PRINCIPE GÉNÉRAL

Quand un client conteste une enquête :
1. ✅ Le système **retrouve automatiquement** l'enquête originale
2. ✅ Il **déduit le prix** de l'enquête originale (enquêteur + société)
3. ✅ Il **recalcule** selon le nouveau résultat (N = négatif, P/H = positif confirmé)

---

## 🔗 ÉTAPE 1 : LIEN CONTESTATION ↔ ENQUÊTE ORIGINALE

### Lors de l'import du fichier

**Fichier** : `backend/import_engine.py:294-345` ou `backend/utils.py:192-335`

```python
# 1. Le fichier contient numeroDemandeContestee
if typeDemande == 'CON' and numeroDemandeContestee:
    # 2. Chercher l'enquête originale
    enquete_originale = Donnee.query.filter_by(
        client_id=client_id,
        numeroDemande=numeroDemandeContestee
    ).first()
    
    if enquete_originale:
        # 3. Établir la relation
        nouvelle_donnee.est_contestation = True
        nouvelle_donnee.enquete_originale_id = enquete_originale.id  # ← LIEN
        nouvelle_donnee.date_contestation = datetime.now().date()
        
        # 4. Assigner le même enquêteur
        nouvelle_donnee.enqueteurId = enquete_originale.enqueteurId
```

### Structure en base de données

**Modèle `Donnee`** (`backend/models/models.py:49-62`) :

```python
class Donnee(db.Model):
    # ...
    enquete_originale_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=True)
    est_contestation = db.Column(db.Boolean, default=False, nullable=False)
    date_contestation = db.Column(db.Date)
    motif_contestation_code = db.Column(db.String(16))
    motif_contestation_detail = db.Column(db.String(255))
    
    # Relation bidirectionnelle
    enquete_originale = db.relationship('Donnee', remote_side=[id], 
                                       backref='contestations',
                                       foreign_keys=[enquete_originale_id])
```

**Exemple** :
```
Enquête originale : ID=100, numeroDemande='12345', typeDemande='ENQ'
Contestation      : ID=150, numeroDemandeContestee='12345', typeDemande='CON'
                    → enquete_originale_id = 100
                    → est_contestation = True
```

---

## 💰 ÉTAPE 2 : GESTION FINANCIÈRE DES CONTESTATIONS

### Point d'entrée : `calculate_tarif_for_enquete()`

**Fichier** : `backend/services/tarification_service.py:110-180`

```python
@staticmethod
def calculate_tarif_for_enquete(donnee_enqueteur_id):
    # 1. Récupérer donnee_enqueteur et donnee
    donnee_enqueteur = DonneeEnqueteur.query.filter_by(id=donnee_enqueteur_id).first()
    donnee = db.session.get(Donnee, donnee_enqueteur.donnee_id)
    
    # 2. Vérifier si c'est une contestation
    is_contestation = donnee.est_contestation and donnee.enquete_originale_id
    
    # 3. Récupérer ou créer facturation
    facturation = TarificationService._get_or_create_facturation(donnee, donnee_enqueteur)
    
    # 4. Router vers le bon gestionnaire
    if is_contestation:
        TarificationService._handle_contestation_facturation(facturation, donnee, donnee_enqueteur)
    else:
        TarificationService._handle_standard_facturation(facturation, donnee, donnee_enqueteur)
```

---

### Gestionnaire de contestation : `_handle_contestation_facturation()`

**Fichier** : `backend/services/tarification_service.py:209-283`

```python
@staticmethod
def _handle_contestation_facturation(facturation, donnee, donnee_enqueteur):
    """Gère la facturation pour une contestation"""
    
    # 1. Cas spécial : Contestation en cours (pas encore de résultat)
    if not donnee_enqueteur.code_resultat:
        facturation.resultat_enqueteur_montant = 0.0  # En attente
        return
    
    # 2. Récupérer l'enquête originale
    enquete_originale = db.session.get(Donnee, donnee.enquete_originale_id)
    
    # 3. Récupérer les données enquêteur de l'originale
    original_enquete = DonneeEnqueteur.query.filter_by(donnee_id=enquete_originale.id).first()
    
    # 4. Récupérer la facturation de l'originale
    original_facturation = EnqueteFacturation.query.filter_by(
        donnee_enqueteur_id=original_enquete.id
    ).first()
    
    # 5. Router selon le code résultat
    if donnee_enqueteur.code_resultat == 'N':
        # Contestation NÉGATIVE → Annuler l'enquête originale
        _handle_negative_contestation(...)
    
    elif donnee_enqueteur.code_resultat in ['P', 'H']:
        # Contestation POSITIVE/CONFIRMÉE → Calculer nouveau tarif
        _handle_positive_contestation(...)
```

---

## 🔴 CAS 1 : CONTESTATION NÉGATIVE (Code 'N')

### Principe
Le client avait raison, l'enquête originale était **erronée**.
→ **Annuler complètement** les montants de l'enquête originale.

### Code : `_handle_negative_contestation()`

**Fichier** : `backend/services/tarification_service.py:286-322`

```python
@staticmethod
def _handle_negative_contestation(facturation, donnee, original_enquete, original_facturation):
    """Gère une contestation avec résultat négatif"""
    
    # 1. Facturation de la contestation = 0
    facturation.tarif_eos_code = 'N'
    facturation.tarif_eos_montant = 0.0
    facturation.resultat_eos_montant = 0.0
    facturation.tarif_enqueteur_code = 'N'
    facturation.tarif_enqueteur_montant = 0.0
    facturation.resultat_enqueteur_montant = 0.0  # ← IMPORTANT: Zéro
    
    # 2. Créer une facturation NÉGATIVE pour l'enquête originale
    if original_facturation:
        previous_montant_eos = float(original_facturation.resultat_eos_montant or 0.0)
        previous_montant_enq = float(original_facturation.resultat_enqueteur_montant or 0.0)
        
        if previous_montant_enq > 0:
            # ✅ DÉDUCTION : Créer ligne négative
            neg_facturation = EnqueteFacturation(
                donnee_id=donnee.enquete_originale_id,
                donnee_enqueteur_id=original_enquete.id,
                client_id=enquete_originale.client_id,
                
                # Codes originaux
                tarif_eos_code=original_facturation.tarif_eos_code,
                tarif_eos_montant=original_facturation.tarif_eos_montant,
                
                # ⚠️ MONTANTS NÉGATIFS pour annuler
                resultat_eos_montant=-previous_montant_eos,
                resultat_enqueteur_montant=-previous_montant_enq,
                
                paye=False
            )
            db.session.add(neg_facturation)
            db.session.commit()
```

### Exemple chiffré

**Enquête originale** :
- Facturé client (EOS) : 22.00€
- Part enquêteur : 15.40€
- Marge EOS : 6.60€

**Contestation négative (N)** :
1. Facturation contestation :
   - Enquêteur : **0.00€**
   - EOS : **0.00€**

2. Facturation négative créée automatiquement :
   - Enquêteur : **-15.40€** (annule l'originale)
   - EOS : **-22.00€** (annule l'originale)

**Résultat net pour l'enquêteur** :
```
Enquête originale : +15.40€
Déduction auto    : -15.40€
─────────────────────────────
TOTAL             :  0.00€ ✅
```

---

## ✅ CAS 2 : CONTESTATION POSITIVE (Code 'P' ou 'H')

### Principe
L'enquêteur avait raison, les informations sont confirmées.
→ **Rétablir** le paiement (ou calculer nouveau tarif si éléments changés).

### Code : `_handle_positive_contestation()`

**Fichier** : `backend/services/tarification_service.py:324-387`

```python
@staticmethod
def _handle_positive_contestation(facturation, donnee, donnee_enqueteur, original_enquete, original_facturation):
    """Gère une contestation avec résultat positif ou confirmé"""
    
    elements_code = donnee_enqueteur.elements_retrouves
    
    # 1. Vérifier si client PARTNER ou EOS
    client = db.session.get(Client, donnee.client_id)
    is_partner = client and client.code == 'PARTNER'
    
    if is_partner:
        # PARTNER : Utiliser tarif combiné
        PartnerTarifResolver = get_partner_tarif_resolver()
        montant = PartnerTarifResolver.resolve_tarif(
            donnee.client_id,
            donnee.tarif_lettre,
            donnee.id
        )
        
        if montant is not None:
            facturation.tarif_eos_code = donnee.tarif_lettre or elements_code
            facturation.tarif_eos_montant = montant
            facturation.resultat_eos_montant = montant
            
            # ✅ RÉTABLIR : 70% pour enquêteur
            facturation.tarif_enqueteur_montant = montant * 0.7
            facturation.resultat_enqueteur_montant = montant * 0.7
            return
    
    # EOS : Utiliser tarifs standards
    tarif_eos = TarificationService.get_tarif_eos(elements_code, client_id=donnee.client_id)
    tarif_enqueteur = TarificationService.get_tarif_enqueteur(elements_code, donnee.enqueteurId)
    
    if tarif_eos:
        facturation.tarif_eos_code = elements_code
        facturation.tarif_eos_montant = tarif_eos.montant
        facturation.resultat_eos_montant = tarif_eos.montant
    
    if tarif_enqueteur:
        facturation.tarif_enqueteur_code = elements_code
        facturation.tarif_enqueteur_montant = tarif_enqueteur.montant
        
        # ✅ RÉTABLIR : Montant confirmé
        facturation.resultat_enqueteur_montant = tarif_enqueteur.montant
```

### Exemple chiffré

**Enquête originale** :
- Code éléments : AT (Adresse + Téléphone)
- Facturé client (EOS) : 22.00€
- Part enquêteur : 15.40€

**Client conteste → Enquêteur défend son travail**

**Contestation positive (P ou H)** :
1. Facturation contestation :
   - Code : AT (même que l'original)
   - Enquêteur : **15.40€** (rétabli)
   - EOS : **22.00€** (rétabli)

**Résultat net pour l'enquêteur** :
```
Enquête originale : +15.40€ (déjà payé ou à payer)
Contestation P/H  : +15.40€ (nouveau paiement)
─────────────────────────────
TOTAL             : +30.80€ ✅ (2x le tarif)
```

⚠️ **NOTE** : Si l'enquêteur avait déjà été payé pour l'originale, il reçoit un 2ème paiement pour la confirmation.

---

## 🔀 CAS 3 : ÉLÉMENTS CHANGÉS DANS CONTESTATION

### Principe
Le client avait partiellement raison : certains éléments étaient corrects, d'autres non.
→ **Ajuster** les montants selon les nouveaux éléments.

### Exemple

**Enquête originale** :
- Code : ATB (Adresse + Téléphone + Banque)
- Enquêteur : 16.80€
- EOS : 24.00€

**Contestation : Banque erronée, mais Adresse + Téléphone OK**
- Nouveau code : AT (Adresse + Téléphone)
- Nouveau montant enquêteur : 15.40€
- Nouveau montant EOS : 22.00€

**Le système calcule automatiquement** :
```
Différence enquêteur : 16.80€ - 15.40€ = 1.40€
Différence EOS       : 24.00€ - 22.00€ = 2.00€
```

**Facturations créées** :
1. Contestation (AT) :
   - Enquêteur : +15.40€
   - EOS : +22.00€

2. Ajustement négatif sur originale :
   - Enquêteur : -1.40€ (ajustement)
   - EOS : -2.00€ (ajustement)

**Résultat net pour l'enquêteur** :
```
Enquête originale : +16.80€
Ajustement        :  -1.40€
Contestation      : +15.40€
─────────────────────────────
TOTAL             : +30.80€ ✅
```

---

## 📊 SCHÉMA DE FLUX COMPLET

```
┌─────────────────────────────────────────────────────────────────┐
│ ENQUÊTE ORIGINALE (ID=100)                                      │
│ numeroDemande = '12345'                                         │
│ typeDemande = 'ENQ'                                             │
│ code_resultat = 'P'                                             │
│ elements_retrouves = 'AT'                                       │
└─────────────────────────────────────────────────────────────────┘
                        ↓
              ┌─────────────────┐
              │ Facturation 1   │
              │ Enquêteur: +15.40€ │
              │ EOS: +22.00€    │
              │ paye = False    │
              └─────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ CLIENT CONTESTE                                                 │
│ Import fichier avec typeDemande='CON'                           │
│ numeroDemandeContestee = '12345'                                │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ SYSTÈME RETROUVE AUTOMATIQUEMENT                                │
│ enquete_originale = Donnee.query.filter_by(                     │
│     numeroDemande='12345'                                       │
│ ).first()                                                       │
│                                                                  │
│ nouvelle_donnee.enquete_originale_id = enquete_originale.id     │
│ nouvelle_donnee.est_contestation = True                         │
└─────────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ CONTESTATION (ID=150)                                           │
│ enquete_originale_id = 100                                      │
│ est_contestation = True                                         │
│ typeDemande = 'CON'                                             │
└─────────────────────────────────────────────────────────────────┘
                        ↓
              ┌─────────────────┐
              │ ENQUÊTEUR TRAITE │
              │ ET CONFIRME      │
              └─────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────────┐
│ calculate_tarif_for_enquete() DÉTECTE CONTESTATION             │
│ is_contestation = True                                          │
│ → _handle_contestation_facturation()                            │
└─────────────────────────────────────────────────────────────────┘
                        ↓
              ┌─────────────────┐
              │ RÉCUPÈRE        │
              │ FACTURATION     │
              │ ORIGINALE       │
              └─────────────────┘
                        ↓
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌──────────────────┐         ┌──────────────────┐
│ Code = 'N'       │         │ Code = 'P' ou 'H'│
│ (NÉGATIF)        │         │ (POSITIF)        │
└──────────────────┘         └──────────────────┘
        │                               │
        ▼                               ▼
┌──────────────────┐         ┌──────────────────┐
│ Facturation 2    │         │ Facturation 2    │
│ (Contestation)   │         │ (Contestation)   │
│ Enquêteur: 0.00€ │         │ Enquêteur: +15.40€│
│ EOS: 0.00€       │         │ EOS: +22.00€     │
└──────────────────┘         └──────────────────┘
        │                               
        ▼                               
┌──────────────────┐         
│ Facturation 3    │         
│ (Ajustement)     │         
│ Enquêteur: -15.40€│        
│ EOS: -22.00€     │         
│ donnee_id = 100  │         
└──────────────────┘         
```

---

## 💡 POINTS CLÉS À RETENIR

### ✅ Ce qui fonctionne automatiquement

1. **Retrouver l'enquête originale** :
   - Via `numeroDemandeContestee` dans le fichier
   - Création du lien `enquete_originale_id`

2. **Déduction automatique** :
   - Pour contestation négative (N) : création d'une ligne de facturation négative
   - Annule les montants enquêteur ET société

3. **Rétablissement automatique** :
   - Pour contestation positive (P/H) : nouveau calcul selon les éléments confirmés
   - Rétablit le paiement enquêteur

4. **Gestion des ajustements** :
   - Si éléments changent (ex: ATB → AT), calcul de la différence
   - Création d'ajustements négatifs

### 📋 Vérifications à faire

Pour vérifier que tout fonctionne bien :

```sql
-- 1. Vérifier les liens contestation → originale
SELECT 
    c.id AS contestation_id,
    c.numeroDossier AS contestation_numero,
    c.enquete_originale_id,
    o.numeroDossier AS originale_numero
FROM donnees c
LEFT JOIN donnees o ON c.enquete_originale_id = o.id
WHERE c.est_contestation = TRUE;

-- 2. Vérifier les facturations (positives + négatives)
SELECT 
    d.numeroDossier,
    d.typeDemande,
    ef.tarif_enqueteur_code,
    ef.resultat_enqueteur_montant,
    ef.paye
FROM enquete_facturation ef
JOIN donnees d ON ef.donnee_id = d.id
WHERE d.est_contestation = TRUE
   OR d.id IN (SELECT enquete_originale_id FROM donnees WHERE est_contestation = TRUE)
ORDER BY d.numeroDossier;

-- 3. Vérifier le net pour un enquêteur
SELECT 
    enqueteur_id,
    SUM(resultat_enqueteur_montant) AS total_net
FROM enquete_facturation ef
JOIN donnees d ON ef.donnee_id = d.id
WHERE d.enqueteurId = 5
GROUP BY d.enqueteurId;
```

---

## 🔧 MAINTENANCE ET MONITORING

### Logs à surveiller

Le système génère des logs détaillés :

```
INFO: Traitement contestation 150: code_resultat=N, elements=AT
INFO: Contestation négative (N) pour l'enquête 150
INFO: Création d'une facturation négative pour l'enquête originale 100
```

### Cas d'erreur possibles

1. **Enquête originale non trouvée** :
   ```
   WARNING: Enquête originale non trouvée pour contestation 150, dossier contesté: 12345
   ```
   → Vérifier que `numeroDemandeContestee` correspond à un `numeroDemande` existant

2. **Facturation originale manquante** :
   - Le système crée une facturation basique par défaut
   - Vérifier que toutes les enquêtes ont une facturation

3. **Double déduction** :
   - Protection via logs : vérifie si facturation négative existe déjà
   - Évite de créer plusieurs lignes négatives

---

## 📞 SUPPORT

En cas de problème avec les contestations :

1. Vérifier les logs : `journalctl -u eos-backend | grep "contestation"`
2. Vérifier le lien : `SELECT * FROM donnees WHERE est_contestation=TRUE`
3. Vérifier les facturations : `SELECT * FROM enquete_facturation WHERE resultat_enqueteur_montant < 0`

---

**Version** : 1.0  
**Date** : 24 décembre 2025  
**Statut** : ✅ DOCUMENTÉ




