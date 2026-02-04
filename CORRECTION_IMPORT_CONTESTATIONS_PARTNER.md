# ✅ Correction Import Contestations Partner

**Date** : 22 janvier 2026  
**Problème** : Les contestations importées avaient `est_contestation = FALSE` au lieu de `TRUE`

---

## 🐛 Problème Identifié

Lors de l'import de fichiers de contestation Partner :
- Le `typeDemande` était bien détecté comme `'CON'`
- **MAIS** le flag `est_contestation` restait à `FALSE`
- Résultat : Les contestations allaient dans "Enquêtes Positives/Négatives" au lieu de "Contestations Positives/Négatives"

---

## ✅ Corrections Apportées

### Fichier : `backend/import_engine.py`

#### 1. Forcer `est_contestation = TRUE` pour toutes les contestations

**Ligne 508-513** : Ajout de la définition explicite du flag

```python
# Traiter les contestations
if record.get('typeDemande') == 'CON':
    # IMPORTANT : Marquer TOUJOURS comme contestation si typeDemande = CON
    nouvelle_donnee.est_contestation = True
    nouvelle_donnee.typeDemande = 'CON'
    self._handle_contestation(nouvelle_donnee, record, client_id)
```

#### 2. Amélioration de la détection automatique

**Ligne 435-448** : Forcer aussi le `typeDemande` dans le record lors de la détection

```python
# Critère 1: Nom de fichier contient CONTESTATION
if self.filename and 'CONTESTATION' in self.filename.upper():
    type_demande = 'CON'
    record['typeDemande'] = 'CON'  # Forcer dans le record
    logger.info(f"✅ Détection CON via Nom Fichier: {self.filename}")
# Critère 2: Le champ instructions/motif est rempli
elif record.get('instructions') or record.get('motif'):
    type_demande = 'CON'
    record['typeDemande'] = 'CON'  # Forcer dans le record
    logger.info("✅ Détection CON via présence de Motif/Instructions")
```

---

## 🔧 Correction des Données Existantes

### Pour les contestations déjà importées avec le bug

```sql
-- Vérifier combien sont concernées
SELECT COUNT(*) 
FROM donnees 
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND "typeDemande" = 'CON' 
  AND est_contestation = FALSE;

-- Corriger
UPDATE donnees 
SET est_contestation = TRUE 
WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND "typeDemande" = 'CON' 
  AND est_contestation = FALSE;
```

---

## 📊 Vérification Après Correction

### Requête SQL pour vérifier la répartition

```sql
SELECT 
    CASE 
        WHEN d.est_contestation THEN 'Contestation'
        ELSE 'Enquête'
    END AS type,
    CASE 
        WHEN de.code_resultat IN ('P', 'H') THEN 'Positive'
        WHEN de.code_resultat IN ('N', 'I') THEN 'Négative'
        ELSE 'Autre'
    END AS resultat,
    COUNT(*) AS nombre
FROM donnees d
LEFT JOIN donnees_enqueteur de ON d.id = de.donnee_id
WHERE d.client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
  AND d.statut_validation = 'validee'
  AND d.exported = FALSE
GROUP BY type, resultat
ORDER BY type, resultat;
```

**Résultat attendu :**
```
type         | resultat | nombre
-------------|----------|--------
Contestation | Négative | X
Contestation | Positive | Y
Enquête      | Négative | Z
Enquête      | Positive | W
```

---

## 🧪 Test

1. **Importer un nouveau fichier de contestation** contenant "CONTESTATION" dans le nom
2. **Vérifier dans les logs** : devrait afficher `✅ Détection CON via Nom Fichier`
3. **Vérifier en SQL** :
   ```sql
   SELECT id, "numeroDossier", nom, "typeDemande", est_contestation 
   FROM donnees 
   WHERE client_id = (SELECT id FROM clients WHERE code = 'PARTNER')
   ORDER BY id DESC LIMIT 10;
   ```
4. **Vérifier dans l'interface** : Les contestations doivent apparaître dans "Contestations Positives" ou "Contestations Négatives"

---

## 📝 Notes

- Cette correction affecte **uniquement** les imports Partner et CLIENT_X
- Les contestations existantes doivent être corrigées manuellement via SQL
- Après correction, redémarrer le backend pour appliquer les changements

---

**Dernière mise à jour** : 22 janvier 2026

