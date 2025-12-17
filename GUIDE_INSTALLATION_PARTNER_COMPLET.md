# Guide d'installation des améliorations PARTNER

## Vue d'ensemble

Ce guide décrit l'installation des nouvelles fonctionnalités PARTNER qui permettent :

1. **Affichage de RECHERCHE** dans le header de la mise à jour
2. **Affichage de INSTRUCTIONS** en haut de la mise à jour (encadré visible)
3. **Onglet Naissance** pour saisir la date et le lieu de naissance retrouvés
4. **Suppression des validations** bloquantes pour PARTNER (saisie libre)
5. **Champ INSTRUCTIONS** importé depuis Excel

## Prérequis

- ✅ PARTNER doit être installé (anciennement CLIENT_X)
- ✅ PostgreSQL en cours d'exécution
- ✅ Backend et frontend fonctionnels

## Installation automatique

### Méthode rapide (recommandée)

```batch
INSTALLER_PARTNER_COMPLET.bat
```

Ce script effectue automatiquement :
1. Ajout de la colonne `instructions` dans la table `donnees`
2. Ajout du mapping `INSTRUCTIONS` au profil d'import PARTNER
3. Vérification de l'installation

### Installation manuelle

Si vous préférez installer étape par étape :

#### Étape 1 : Ajouter la colonne instructions

```batch
AJOUTER_INSTRUCTIONS_PARTNER.bat
```

Ou manuellement :

```batch
cd backend
call venv\Scripts\activate.bat
set "DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
python ajouter_instructions_partner.py
```

#### Étape 2 : Mettre à jour les mappings

```batch
METTRE_A_JOUR_PARTNER_MAPPINGS.bat
```

Ou manuellement :

```batch
python backend\scripts\add_instructions_mapping.py
```

## Vérification

### 1. Vérifier la colonne instructions

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'donnees' AND column_name = 'instructions';
```

Résultat attendu :
```
column_name  | data_type
-------------|----------
instructions | text
```

### 2. Vérifier le mapping

```sql
SELECT internal_field, column_name 
FROM import_field_mappings 
WHERE internal_field = 'instructions';
```

Résultat attendu :
```
internal_field | column_name
---------------|-------------
instructions   | INSTRUCTIONS
```

## Fichiers Excel PARTNER

### Format attendu

Votre fichier Excel PARTNER doit maintenant contenir une colonne **INSTRUCTIONS** :

| NUM | NOM | PRENOM | ... | RECHERCHE | INSTRUCTIONS |
|-----|-----|--------|-----|-----------|--------------|
| 001 | DUPONT | Jean | ... | ADRESSE | Vérifier l'adresse actuelle |
| 002 | MARTIN | Marie | ... | TELEPHONE | Appeler entre 9h et 12h |

### Exemple

```
RECHERCHE: ADRESSE + TELEPHONE
INSTRUCTIONS: Personne difficile à joindre. Essayer le matin uniquement.
```

## Utilisation

### 1. Import

Lors de l'import d'un fichier PARTNER :
- La colonne `RECHERCHE` est importée dans le champ `recherche`
- La colonne `INSTRUCTIONS` est importée dans le champ `instructions`
- Les deux champs sont automatiquement nettoyés (trim)

### 2. Mise à jour (UpdateModal)

#### Header
- **RECHERCHE** s'affiche sous les informations principales du dossier
- Titre : "Éléments demandés"
- Visible uniquement si le champ est rempli

#### Bloc INSTRUCTIONS
- S'affiche en haut du contenu, avant les onglets
- Encadré orange avec icône d'alerte
- Très visible pour attirer l'attention
- Visible uniquement si le champ est rempli

#### Onglet Naissance (nouveau)
- Visible uniquement pour PARTNER
- Permet de saisir :
  - Jour (1-31)
  - Mois (1-12)
  - Année (YYYY)
  - Lieu de naissance (texte libre)
- Les données sont envoyées à l'API lors de l'enregistrement

#### Validations
- **PARTNER** : Aucune validation bloquante
  - Pas d'obligation d'adresse si "A" est sélectionné
  - Pas d'obligation de téléphone si "T" est sélectionné
  - Saisie libre des éléments retrouvés
  - Enregistrement possible même avec des champs vides

- **EOS** : Validations strictes conservées
  - Toutes les règles existantes continuent de s'appliquer
  - Aucun changement de comportement

## Composants créés

### Frontend

1. **PartnerHeader.jsx**
   - Affiche RECHERCHE dans le header
   - Composant réutilisable

2. **PartnerInstructions** (dans PartnerHeader.jsx)
   - Affiche INSTRUCTIONS en encadré orange
   - Visible uniquement si rempli

3. **PartnerNaissanceTab.jsx**
   - Onglet complet pour la saisie de la date et du lieu de naissance
   - Interface claire avec champs séparés (jour/mois/année)

### Backend

1. **ajouter_instructions_partner.py**
   - Script de migration pour ajouter la colonne `instructions`
   - Idempotent (peut être exécuté plusieurs fois)

2. **add_instructions_mapping.py**
   - Ajoute le mapping INSTRUCTIONS au profil PARTNER
   - Idempotent

## Modifications apportées

### Modèles (backend/models/models.py)

```python
# Champ ajouté
instructions = db.Column(db.Text, nullable=True)

# Ajouté au to_dict()
'instructions': self.instructions,
```

### Import Engine (backend/import_engine.py)

```python
# Dans create_donnee_from_record
instructions=record.get('instructions', '').strip() if record.get('instructions') else None,
```

### UpdateModal (frontend/src/components/UpdateModal.jsx)

- Import des nouveaux composants
- Feature flag `isPartner`
- Fonction `getTabsForClient()` pour onglets dynamiques
- Validation conditionnelle (aucune pour PARTNER)
- Affichage de RECHERCHE et INSTRUCTIONS
- Onglet Naissance

## Tests

### Test manuel - PARTNER

1. **Import**
   - Importer un fichier Excel avec colonnes RECHERCHE et INSTRUCTIONS
   - Vérifier que les données sont bien importées

2. **Affichage**
   - Ouvrir un dossier PARTNER
   - Vérifier que RECHERCHE s'affiche dans le header
   - Vérifier que INSTRUCTIONS s'affiche en haut (si rempli)

3. **Onglet Naissance**
   - Vérifier que l'onglet "Naissance" est visible
   - Saisir une date et un lieu
   - Enregistrer
   - Recharger : vérifier que les données sont persistées

4. **Validations**
   - Sélectionner "AT" dans éléments retrouvés
   - Laisser l'adresse et le téléphone vides
   - Enregistrer : doit fonctionner sans erreur

### Test manuel - EOS

1. **Validations**
   - Ouvrir un dossier EOS
   - Sélectionner "AT" dans éléments retrouvés
   - Laisser l'adresse vide
   - Enregistrer : doit afficher une erreur (comportement normal)

2. **Onglet Naissance**
   - Vérifier que l'onglet "Naissance" n'est PAS visible pour EOS

## Dépannage

### La colonne instructions n'existe pas

```
ERROR: column "instructions" does not exist
```

**Solution** : Exécuter `AJOUTER_INSTRUCTIONS_PARTNER.bat`

### Le mapping INSTRUCTIONS n'existe pas

Les données ne sont pas importées depuis la colonne INSTRUCTIONS.

**Solution** : Exécuter `METTRE_A_JOUR_PARTNER_MAPPINGS.bat`

### L'onglet Naissance n'apparaît pas

**Vérification** :
1. Le client est-il bien "PARTNER" (pas "CLIENT_X") ?
2. Le frontend a-t-il été redémarré ?

**Solution** :
```batch
cd frontend
npm run dev
```

### RECHERCHE ou INSTRUCTIONS ne s'affichent pas

**Vérification** :
1. Les champs sont-ils remplis dans la base de données ?
2. Le frontend a-t-il été redémarré ?

**Solution** : Vérifier dans la base :
```sql
SELECT recherche, instructions FROM donnees WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER') LIMIT 5;
```

## Rollback

Si vous devez annuler l'installation :

### Supprimer la colonne instructions

```sql
ALTER TABLE donnees DROP COLUMN IF EXISTS instructions;
```

### Supprimer le mapping

```sql
DELETE FROM import_field_mappings WHERE internal_field = 'instructions';
```

### Restaurer UpdateModal.jsx

```bash
git checkout frontend/src/components/UpdateModal.jsx
```

## Support

En cas de problème :

1. Vérifier les logs du backend : `backend/logs/app.log`
2. Vérifier la console du navigateur (F12)
3. Vérifier que PostgreSQL est en cours d'exécution
4. Vérifier que le client est bien "PARTNER" (pas "CLIENT_X")

## Résumé des commandes

```batch
# Installation complète
INSTALLER_PARTNER_COMPLET.bat

# Vérification
psql -U eos_user -d eos_db -c "\d donnees" | findstr instructions

# Redémarrage du frontend
cd frontend
npm run dev

# Redémarrage du backend
cd backend
call venv\Scripts\activate.bat
python app.py
```

## Prochaines étapes

Une fois l'installation terminée :

1. ✅ Redémarrer le frontend
2. ✅ Importer un fichier PARTNER avec INSTRUCTIONS
3. ✅ Tester la mise à jour d'un dossier PARTNER
4. ✅ Vérifier que EOS fonctionne toujours normalement
5. ✅ Former les utilisateurs aux nouvelles fonctionnalités

---

**Date de création** : 17 décembre 2025  
**Version** : 1.0  
**Auteur** : Assistant IA

