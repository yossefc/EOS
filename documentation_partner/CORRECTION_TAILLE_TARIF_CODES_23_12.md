# Correction taille des champs tarif_code - 23/12/2025 17:52

## 🐛 Problème identifié

Erreur lors de la sauvegarde des enquêtes PARTNER :
```
StringDataRightTruncation: value too long for type character varying(10)
```

**Cause** : Les champs `tarif_eos_code` et `tarif_enqueteur_code` dans la table `enquete_facturation` étaient limités à **10 caractères**.

Pour PARTNER, le système essayait d'enregistrer des textes complets comme :
- `"Confirmé par téléphone"` (23 caractères)
- Autres confirmations longues

## ✅ Solution appliquée

### Migration 012 : Augmentation de la taille des colonnes

**Fichier** : `backend/migrations/versions/012_augmenter_taille_tarif_codes.py`

**Modifications** :
```sql
ALTER TABLE enquete_facturation 
ALTER COLUMN tarif_eos_code TYPE VARCHAR(100);

ALTER TABLE enquete_facturation 
ALTER COLUMN tarif_enqueteur_code TYPE VARCHAR(100);
```

**Résultat** :
- `tarif_eos_code` : VARCHAR(10) → VARCHAR(100)
- `tarif_enqueteur_code` : VARCHAR(10) → VARCHAR(100)

Ces champs peuvent maintenant accepter des textes jusqu'à 100 caractères.

## 📋 Test de validation

1. Ouvrir la mise à jour d'une enquête PARTNER
2. Remplir les champs (naissance, banque, etc.)
3. Sauvegarder
4. **Résultat attendu** : Aucune erreur, données sauvegardées correctement

## 🔄 Actions requises

**IMPORTANT** : Redémarrer le backend pour que les changements prennent effet :
1. Arrêter le backend (Ctrl+C dans le terminal backend)
2. Relancer `DEMARRER_EOS_COMPLET.bat`

## 📊 Impact

- **EOS** : Aucun impact (les codes EOS restent courts)
- **PARTNER** : Peut maintenant enregistrer des confirmations longues
- **Base de données** : Migration appliquée avec succès

## 📝 Historique des corrections liées

1. Bug boolean (TypeError) → Correction des méthodes `PartnerRequestCalculator`
2. **Taille des champs tarif_code** → Augmentation à VARCHAR(100)

---
*Cette correction fait suite à la série de corrections du 23/12/2025 pour finaliser le système PARTNER.*



