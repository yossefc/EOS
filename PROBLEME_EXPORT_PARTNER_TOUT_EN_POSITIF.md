# 🔍 Diagnostic : Toutes les enquêtes Partner vont dans "Enquêtes Positives"

**Date**: 22 janvier 2026  
**Problème**: Quand on valide des enquêtes ou contestations Partner (positives ou négatives), elles apparaissent toutes dans "Enquêtes Positives"

---

## 📋 Analyse du Code

Le système d'export Partner est bien configuré avec 4 types d'exports différents :

### Routes d'export (backend/routes/partner_export.py)

```python
# Enquêtes Positives (code_resultat P, H)
/api/partner/exports/enquetes/positives/both

# Enquêtes Négatives (code_resultat N, I)  
/api/partner/exports/enquetes/negatives/both

# Contestations Positives (est_contestation=True, code_resultat P, H)
/api/partner/exports/contestations/positives/both

# Contestations Négatives (est_contestation=True, code_resultat N, I)
/api/partner/exports/contestations/negatives/both
```

---

## 🎯 Causes Possibles

### Cause 1 : Code résultat manquant ou incorrect

**Symptôme** : Les enquêtes validées n'ont pas de `code_resultat` dans la table `donnees_enqueteur`

**Vérification SQL** :
```sql
-- Voir les enquêtes Partner validées sans code résultat
SELECT d.id, d.numeroDossier, d.nom, d.statut_validation, 
       de.code_resultat, d.est_contestation, d.exported
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
LEFT JOIN clients c ON d.client_id = c.id
WHERE c.code = 'PARTNER'
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
ORDER BY d.est_contestation, de.code_resultat;
```

**Solution** : Les enquêtes doivent avoir un `code_resultat` dans `donnees_enqueteur` :
- `P` ou `H` = Positif
- `N` ou `I` = Négatif

---

### Cause 2 : Flag `est_contestation` non défini

**Symptôme** : Les contestations ne sont pas marquées comme telles

**Vérification SQL** :
```sql
-- Voir les contestations potentielles non marquées
SELECT d.id, d.numeroDossier, d.nom, d.typeDemande, 
       d.est_contestation, d.enquete_originale_id
FROM donnees d
LEFT JOIN clients c ON d.client_id = c.id
WHERE c.code = 'PARTNER'
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND (d.typeDemande = 'CON' OR d.enquete_originale_id IS NOT NULL)
  AND d.est_contestation = FALSE;
```

**Solution** : Corriger le flag pour les contestations :
```sql
UPDATE donnees
SET est_contestation = TRUE
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND statut_validation = 'validee'
  AND exported = FALSE
  AND (typeDemande = 'CON' OR enquete_originale_id IS NOT NULL)
  AND est_contestation = FALSE;
```

---

### Cause 3 : Problème lors de la validation

**Symptôme** : Le code résultat n'est pas sauvegardé lors de la validation

**Fichier** : `backend/routes/validation.py` ou `backend/routes/validation_v2.py`

**Vérifier** que lors de la validation, le code résultat est bien sauvegardé :

```python
# Exemple de validation correcte
donnee_enqueteur.code_resultat = 'P'  # ou 'H', 'N', 'I'
donnee.statut_validation = 'validee'
db.session.commit()
```

---

## 🔧 Solution Étape par Étape

### Étape 1 : Lancer le diagnostic

```bash
cd d:\EOS

# Remplacer VotreMdp par votre mot de passe PostgreSQL
$env:DATABASE_URL="postgresql+psycopg2://postgres:VotreMdp@localhost:5432/eos_db"

python backend/diagnostic_partner_exports.py
```

Le script affichera :
- Nombre d'enquêtes par catégorie
- Enquêtes sans code résultat
- Contestations mal marquées
- Autres problèmes potentiels

---

### Étape 2 : Corriger les données

**2.1 - Corriger les codes résultats manquants**

Si des enquêtes n'ont pas de `donnees_enqueteur`, les créer :

```sql
-- Créer les entrées manquantes dans donnees_enqueteur
INSERT INTO donnees_enqueteur (donnee_id, code_resultat)
SELECT d.id, 'N'  -- Mettre N par défaut, à ajuster manuellement
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
LEFT JOIN clients c ON d.client_id = c.id
WHERE c.code = 'PARTNER'
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
  AND de.id IS NULL;
```

**2.2 - Corriger le flag est_contestation**

```sql
-- Marquer les contestations correctement
UPDATE donnees
SET est_contestation = TRUE
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND statut_validation = 'validee'
  AND exported = FALSE
  AND (typeDemande = 'CON' OR enquete_originale_id IS NOT NULL)
  AND est_contestation = FALSE;
```

---

### Étape 3 : Vérifier dans l'interface

1. Ouvrir l'application : http://localhost:5173
2. Aller dans **Export**
3. Vérifier la section **Export PARTNER**
4. Les statistiques doivent montrer :
   - ✅ Enquêtes Positives : X
   - ✅ Enquêtes Négatives : Y
   - ✅ Contestations Positives : Z
   - ✅ Contestations Négatives : W

---

## 📊 Requête SQL Complète de Vérification

```sql
-- Statistiques complètes des enquêtes Partner à exporter
WITH partner_id AS (
    SELECT id FROM clients WHERE code = 'PARTNER'
)
SELECT 
    CASE 
        WHEN d.est_contestation THEN 'Contestation'
        ELSE 'Enquête'
    END AS type_enquete,
    CASE 
        WHEN de.code_resultat IN ('P', 'H') THEN 'Positive'
        WHEN de.code_resultat IN ('N', 'I') THEN 'Négative'
        ELSE 'Autre (' || COALESCE(de.code_resultat, 'NULL') || ')'
    END AS resultat,
    COUNT(*) AS nombre
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM partner_id)
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
GROUP BY type_enquete, resultat
ORDER BY type_enquete, resultat;
```

---

## ✅ Résultat Attendu

Après correction, la requête SQL devrait montrer :

| type_enquete   | resultat  | nombre |
|----------------|-----------|--------|
| Contestation   | Négative  | X      |
| Contestation   | Positive  | Y      |
| Enquête        | Négative  | Z      |
| Enquête        | Positive  | W      |

---

## 🆘 Si le Problème Persiste

1. Vérifier les logs du backend pour les erreurs lors de l'export
2. Vérifier que les routes d'export sont bien enregistrées dans `backend/app.py`
3. Vérifier la console du navigateur pour les erreurs JavaScript
4. Consulter `backend/routes/partner_export.py` lignes 902-975 (fonction `get_export_stats`)

---

## 📝 Notes Importantes

- Le `code_resultat` DOIT être défini pour que les enquêtes soient exportées
- Le flag `est_contestation` DOIT être `TRUE` pour les contestations
- Le `typeDemande` devrait être `CON` pour les contestations
- Les statistiques dans l'interface se mettent à jour automatiquement toutes les 30 secondes

---

**Dernière mise à jour** : 22 janvier 2026

