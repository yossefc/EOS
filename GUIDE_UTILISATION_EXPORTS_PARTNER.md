# Guide d'utilisation - Exports PARTNER

## 🎯 Vue d'ensemble

Les exports PARTNER sont intégrés directement dans l'onglet **"Export des résultats"** de l'application EOS. Cette interface unique permet de gérer à la fois les exports EOS et PARTNER.

## 📍 Accès à l'interface

1. Ouvrir l'application EOS
2. Cliquer sur l'onglet **"Export des résultats"**
3. L'interface affiche deux sections distinctes :
   - 🔵 **Export EOS** (en haut)
   - 🟣 **Export PARTNER** (en bas)

## 🚨 Indicateurs visuels

### Badges rouges animés
Des **badges rouges avec animation** s'affichent automatiquement lorsque des dossiers sont prêts à exporter :

- **Export EOS** : Badge à côté du titre "Export EOS"
  ```
  Export EOS  [5 enquêtes] ← Badge rouge animé
  ```

- **Export PARTNER** : Badges sur chaque catégorie
  ```
  📋 Enquêtes Positives [12] ← Badge rouge
  📋 Enquêtes Négatives [3]  ← Badge rouge
  📋 Contestations Positives [7] ← Badge rouge
  📋 Contestations Négatives [2] ← Badge rouge
  ```

### Bouton "Actualiser"
Cliquez sur le bouton **"Actualiser"** en haut à droite pour rafraîchir les compteurs en temps réel.

## 📤 Exports EOS

### Comment exporter ?

1. Les enquêtes EOS validées apparaissent dans le tableau
2. Vérifier le nombre d'enquêtes (affiché dans le badge rouge)
3. Cliquer sur **"Exporter EOS (X)"** où X = nombre d'enquêtes
4. Confirmer l'export dans la popup
5. Le fichier `.txt` est téléchargé automatiquement

### Format du fichier
- **Nom** : `XXXExp_AAAAMMJJ.txt` (XXX = code prestataire)
- **Format** : Texte longueur fixe (encodage CP1252)
- **Contenu** : Toutes les enquêtes validées au format EOS FRANCE

### Après l'export
- Les enquêtes sont **archivées** automatiquement
- Elles disparaissent du tableau
- Le fichier est disponible dans l'onglet **"Archives"**

## 📤 Exports PARTNER

### Types d'exports disponibles

#### 1. 📋 Enquêtes Positives (2 formats)

**Bouton Word (.docx)**
- Génère un rapport détaillé avec :
  - Titre : "Rapport positif du DD/MM/YYYY no X"
  - Référence : DATE_ENVOI/BATCH_TOTAL TARIF
  - Identité complète
  - Sections conditionnelles (employeur, adresse, téléphone, etc.)
- **Usage** : Pour envoi client ou archivage

**Bouton Excel (.xls)**
- Génère un tableau avec 64 colonnes :
  - Données d'import (NUM, NOM, PRENOM, dates, etc.)
  - Résultats enquêteur (adresses, téléphones, montants)
  - Informations banque et employeur
- **Usage** : Pour traitement dans Excel ou import

#### 2. 📋 Enquêtes Négatives (1 format)

**Bouton Excel (.xls)**
- Tableau 5 colonnes : nom, prenom, reference, dossier, memo
- Liste simplifiée des enquêtes sans résultat
- **Usage** : Suivi des échecs

#### 3. 📋 Contestations Positives (1 format)

**Bouton Word (.docx)**
- Rapport similaire aux enquêtes positives
- Titre : "Rapport contestation positif du DD/MM/YYYY no X"
- Mention "URGENT" si applicable
- **Usage** : Réponse aux contestations avec résultat

#### 4. 📋 Contestations Négatives (1 format)

**Bouton Excel (.xls)**
- Tableau 5 colonnes avec memo = "NEGATIF"
- Colonne prenom = "TRES URGENT" si urgence
- **Usage** : Suivi des contestations sans résultat

### Comment exporter ?

1. **Vérifier les badges** : Les nombres indiquent les dossiers prêts
2. **Choisir le format** : Cliquer sur le bouton Word ou Excel souhaité
3. **Attendre** : Le bouton affiche "Export..." pendant la génération
4. **Téléchargement** : Le fichier se télécharge automatiquement

### Exemples de noms de fichiers
```
export_partner_enquetes_pos_word_2025-12-17_143025.docx
export_partner_enquetes_pos_excel_2025-12-17_143030.xls
export_partner_enquetes_neg_2025-12-17_143035.xls
export_partner_contest_pos_2025-12-17_143040.docx
export_partner_contest_neg_2025-12-17_143045.xls
```

### Après l'export
- Les dossiers exportés sont **archivés** (statut = 'archivee')
- Ils ne réapparaîtront plus dans les compteurs
- Les badges se mettent à jour automatiquement
- Les fichiers sont enregistrés dans l'onglet **"Archives"**

## 🔄 Workflow recommandé

### Pour PARTNER - Export complet

Si vous avez des enquêtes positives, exportez dans l'ordre :

1. **Word des positives** (pour le client)
2. **Excel des positives** (pour votre archivage)
3. **Excel des négatives** (si applicable)

### Pour les contestations

1. **Word des contestations positives** (réponses au client)
2. **Excel des contestations négatives** (suivi interne)

## ⚠️ Points d'attention

### Boutons désactivés
Un bouton est grisé (désactivé) si :
- Aucun dossier n'est prêt pour ce type d'export (badge = 0)
- Un export est déjà en cours pour ce type

### Messages d'erreur
En cas d'erreur, un message rouge s'affiche en haut de la page :
- **"Aucune enquête à exporter"** : Tous les dossiers sont déjà exportés
- **"Client PARTNER non trouvé"** : Configuration manquante (contacter l'administrateur)
- **Autre erreur** : Réessayer ou contacter le support

### Messages de succès
Un message vert confirme le succès :
```
✓ Export PARTNER "Enquêtes Positives Word" créé avec succès !
```

## 📊 Suivi des exports

### Consulter l'historique

1. Aller dans l'onglet **"Archives"**
2. Tous les exports (EOS et PARTNER) sont listés
3. Colonnes affichées :
   - Nom du fichier
   - Nombre d'enquêtes
   - Taille du fichier
   - Date de création
   - Utilisateur
4. Bouton **"Télécharger"** pour ré-obtenir un fichier

### Rechercher un export

Utiliser la barre de recherche en haut pour filtrer par :
- Nom de fichier
- Date
- Utilisateur

## 🛠️ Dépannage

### Les badges n'affichent pas de dossiers

**Causes possibles :**
- Aucun dossier validé pour PARTNER
- Les dossiers sont déjà exportés
- Statut de validation incorrect

**Solution :**
1. Vérifier dans l'onglet **"Données"** que des enquêtes PARTNER sont en statut "validée"
2. Vérifier que le code résultat est bien renseigné (P, H, N, ou I)
3. Cliquer sur **"Actualiser"** pour rafraîchir les compteurs

### Export ne se déclenche pas

**Solution :**
1. Vérifier votre connexion Internet
2. Vérifier que le backend est démarré
3. Consulter la console du navigateur (F12) pour voir les erreurs
4. Rafraîchir la page complète (Ctrl+R ou Cmd+R)

### Fichier téléchargé corrompu

**Causes possibles :**
- Erreur pendant la génération
- Extension incorrecte (.xls vs .xlsx)

**Solution :**
1. Ré-exporter le fichier
2. Si problème persiste, vérifier les logs backend
3. Vérifier que xlwt est bien installé : `pip list | grep xlwt`

### Erreur "exported = False"

Cette erreur signifie qu'un dossier a déjà été exporté.

**Solution :**
- Les dossiers déjà exportés ne peuvent pas être ré-exportés
- Pour forcer un ré-export, modifier manuellement le statut en base :
  ```sql
  UPDATE donnees SET exported = FALSE WHERE id = XXX;
  ```

## 📈 Statistiques

### Nombre de dossiers par type

L'interface affiche en temps réel :
- **EOS** : X enquête(s) - Affiché dans le badge + tableau
- **PARTNER** : 
  - Enquêtes positives : X
  - Enquêtes négatives : X
  - Contestations positives : X
  - Contestations négatives : X
  - **Total** : Badge global "X dossiers"

### Performance

- Exports Word : ~1-2 secondes pour 100 dossiers
- Exports Excel : ~2-3 secondes pour 100 dossiers
- Les gros volumes (>500 dossiers) peuvent prendre plus de temps

## 💡 Conseils d'utilisation

### Fréquence d'export

**Recommandé :**
- Exporter quotidiennement ou hebdomadairement
- Ne pas laisser s'accumuler trop de dossiers (>1000)

### Organisation des fichiers

**Suggestion :**
- Créer un dossier par mois : `Exports_2025-12/`
- Sous-dossiers : `EOS/`, `PARTNER/`
- Renommer les fichiers si besoin avec des infos supplémentaires

### Backup

- Les fichiers exportés sont stockés dans `backend/exports/archives/`
- **Important** : Faire une sauvegarde régulière de ce dossier
- Les archives en base de données permettent de retrouver les métadonnées

## 📞 Support

En cas de problème persistant :

1. **Logs backend** : Consulter `backend/app.log`
2. **Console navigateur** : Ouvrir avec F12 et regarder l'onglet "Console"
3. **Vérifier la configuration** :
   - Client PARTNER existe dans la base
   - Dépendance xlwt installée (`pip install xlwt`)
   - Serveurs backend et frontend démarrés

4. **Contacter l'administrateur** avec :
   - Message d'erreur exact
   - Copie d'écran
   - Logs pertinents

## ✅ Checklist de validation

Avant de clôturer une session d'export :

- [ ] Tous les badges sont à 0 (tous les dossiers exportés)
- [ ] Les fichiers sont bien téléchargés et lisibles
- [ ] Les archives sont visibles dans l'onglet "Archives"
- [ ] Les dossiers exportés ont disparu de la liste "validée"
- [ ] Backup des fichiers effectué
- [ ] Documents transmis au client ou archivés

---

**Version du guide** : 1.0 (Décembre 2025)
**Compatibilité** : Application EOS avec module PARTNER installé

