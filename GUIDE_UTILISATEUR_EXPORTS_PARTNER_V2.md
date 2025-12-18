# Guide Utilisateur - Exports PARTNER v2
**Version** : 2.0  
**Date** : 17 décembre 2025

---

## 📖 Vue d'Ensemble

Cette mise à jour améliore l'export des enquêtes PARTNER positives et simplifie l'interface de saisie.

### 🆕 Nouveautés

1. **Export Word** : Format restructuré avec 2 sections distinctes (1 page par enquête)
2. **Export Excel** : Champs NJF, date de naissance et proximité complétés
3. **Interface de saisie** : Mémos simplifiés et renommés pour PARTNER

---

## 📝 Saisie des Données PARTNER

### Écran "Mise à jour" - Nouveaux Libellés

Lors de la mise à jour d'une enquête PARTNER, vous verrez maintenant **3 champs mémo** au lieu de 5 :

#### 1. **Memo adresse / téléphone**
- **Utilisation** : Informations complémentaires sur l'adresse ou le téléphone
- **Exemples** :
  - "Habite au 2ème étage, porte droite"
  - "N° de portable : 06 12 34 56 78"
  - "Adresse confirmée par la mairie"
  - "Téléphone non attribué"

#### 2. **Memo employeur**
- **Utilisation** : Informations complémentaires sur l'employeur
- **Exemples** :
  - "Travaille à temps partiel"
  - "En arrêt maladie"
  - "Démission prévue fin du mois"
  - "CDI depuis 2020"

#### 3. **Proximité (commentaires détaillés)**
- **Utilisation** : Informations sur la proximité et méthode de confirmation
- **Exemples** :
  - "Confirmé en Proximité"
  - "Confirmé par la mairie"
  - "Confirmé par le voisin du palier"
  - "Information obtenue auprès de l'employeur"
  - "Recherche effectuée auprès du service de l'état civil"
- **Important** : Ce champ sera affiché en priorité dans l'export Word

### 📌 Conseils de Saisie

| Champ | À Remplir Si... | Limite |
|-------|-----------------|--------|
| Memo adresse / téléphone | Vous avez des précisions sur l'adresse ou le téléphone | 64 caractères |
| Memo employeur | Vous avez des informations sur l'employeur | 64 caractères |
| Proximité | Vous devez expliquer comment vous avez obtenu l'information | 1000 caractères |

---

## 📤 Export Word - Enquêtes Positives

### Nouveau Format (1 page par enquête)

Chaque enquête exportée occupe **exactement 1 page** dans le document Word.

#### Structure de la Page

```
┌─────────────────────────────────────────────┐
│ Rapport positif du 17/12/2025 no 1         │
│ 17.12/10 A                                  │
│                                             │
│ ─── DONNÉES IMPORTÉES ───                   │
│ Dossier: DUPONT Jean NO 12345               │
│ NJF: MARTIN                                 │
│ Né(e) le 15/03/1980 à Paris                │
│ Date envoi: 17/12/2025                      │
│ Date butoir: 31/12/2025                     │
│ Tarif: A                                    │
│ Adresse importée:                           │
│   15 Rue de la République                   │
│   Appartement 3B                            │
│   75001 Paris                               │
│ Tél: 01 23 45 67 89                        │
│ Instructions: Vérifier adresse actuelle     │
│ Recherche: A T                              │
│                                             │
│ ─── RÉSULTATS ENQUÊTE ───                   │
│ Proximité: Confirmé par la mairie           │
│ NOUVELLE ADRESSE:                           │
│   22 Avenue des Champs                      │
│   75008 Paris                               │
│ Tél: 06 12 34 56 78                        │
│ Memo: Habite au 2ème étage                 │
└─────────────────────────────────────────────┘
[SAUT DE PAGE]
```

### Sections du Document

#### 📋 Section 1 : DONNÉES IMPORTÉES
Contient toutes les informations fournies lors de l'import :
- Identité complète (nom, prénom, n° dossier, NJF)
- Date de naissance et lieu
- Dates (envoi, butoir) et tarif
- Adresse importée
- Téléphone importé
- Instructions spécifiques
- Éléments recherchés

#### 🔍 Section 2 : RÉSULTATS ENQUÊTE
Contient les informations collectées par l'enquêteur :
- **Proximité** (affiché en premier si rempli)
- Employeur (si trouvé)
- Nouvelle adresse ou confirmation
- Téléphone résultat
- Informations bancaires (si trouvées)
- Mémos complémentaires

### 📏 Optimisations

- **Marges réduites** : Pour tenir sur 1 page
- **Textes tronqués** : Les champs trop longs sont coupés à :
  - Instructions : 500 caractères
  - Proximité : 300 caractères
  - Mémos : 200 caractères
- **Police adaptée** : Tailles réduites pour maximiser l'espace

---

## 📊 Export Excel - Enquêtes Positives

### Colonnes Complétées

#### NJF (Nom de Jeune Fille)
- **Position** : Colonne 7
- **Source** : Champ "Nom patronymique" de l'import
- **Exemple** : Si Madame DUPONT (née MARTIN), la colonne NJF contiendra "MARTIN"

#### Date de Naissance
- **Colonnes** : 8 (JOUR), 9 (MOIS), 10 (ANNEE NAISSANCE)
- **Format** : Valeurs numériques séparées
- **Exemple** : Pour le 15/03/1980
  - JOUR = 15
  - MOIS = 3
  - ANNEE NAISSANCE = 1980

#### Proximité
- **Position** : Colonne 35
- **Source** : Champ "Proximité (commentaires détaillés)" de la saisie
- **Exemple** : "Confirmé par la mairie"

### 📋 Colonnes Complètes (64 colonnes)

| # | Colonne | Exemple |
|---|---------|---------|
| 1 | NUM | 12345 |
| 2 | DATE BUTOIR | 31/12/2025 |
| 3 | DATE ENVOI | 17/12/2025 |
| 4 | TARIF | A |
| 5 | NOM | DUPONT |
| 6 | PRENOM | Jean |
| **7** | **NJF** | **MARTIN** |
| **8** | **JOUR** | **15** |
| **9** | **MOIS** | **3** |
| **10** | **ANNEE NAISSANCE** | **1980** |
| ... | ... | ... |
| **35** | **Proximite** | **Confirmé par la mairie** |
| ... | ... | ... |

---

## 🎯 Workflow Complet

### 1. Import des Données
```
┌─────────────────────────────────┐
│ Import fichier PARTNER          │
│ • Nom, prénom, NJF              │
│ • Date de naissance             │
│ • Adresse, téléphone            │
│ • Instructions, recherche       │
└─────────────────────────────────┘
         ↓
```

### 2. Assignation et Traitement
```
┌─────────────────────────────────┐
│ Assignation à un enquêteur      │
│ • Enquêteur effectue recherche  │
│ • Mise à jour des résultats     │
│ • Saisie de la proximité        │
└─────────────────────────────────┘
         ↓
```

### 3. Validation
```
┌─────────────────────────────────┐
│ Validation de l'enquête         │
│ • Vérification des données      │
│ • Statut : Validée              │
└─────────────────────────────────┘
         ↓
```

### 4. Export
```
┌─────────────────────────────────┐
│ Onglet "Export des résultats"   │
│ Section PARTNER                 │
│ • Clic sur "Export Word + Excel"│
│ • Téléchargement du ZIP         │
└─────────────────────────────────┘
         ↓
┌─────────────────────────────────┐
│ Fichiers générés                │
│ • cr_17_12_2025_14_30_25.docx  │
│ • cr_17_12_2025_14_30_25.xls   │
└─────────────────────────────────┘
         ↓
```

### 5. Archivage Automatique
```
┌─────────────────────────────────┐
│ Enquêtes archivées              │
│ • Statut : Archivée             │
│ • Visible dans l'onglet Archives│
└─────────────────────────────────┘
```

---

## ✅ Bonnes Pratiques

### 📝 Saisie

1. **Remplir la proximité systématiquement**
   - C'est le champ le plus important
   - Il apparaît en premier dans l'export Word
   - Utilisez le champ long (1000 caractères)

2. **Séparer les informations**
   - Adresse/téléphone → Memo adresse / téléphone
   - Employeur → Memo employeur
   - Méthode de confirmation → Proximité

3. **Être précis et concis**
   - Instructions : max 500 car. dans l'export
   - Proximité : max 300 car. dans l'export
   - Mémos : max 200 car. dans l'export

### 📤 Export

1. **Vérifier avant d'exporter**
   - Toutes les enquêtes sont validées
   - La proximité est remplie
   - Les informations sont complètes

2. **Contrôler après export**
   - Ouvrir les fichiers Word et Excel
   - Vérifier que chaque enquête est sur 1 page (Word)
   - Vérifier que les colonnes sont complètes (Excel)

3. **Ne pas ré-exporter**
   - Les enquêtes exportées sont automatiquement archivées
   - Elles disparaissent de la liste d'export
   - Consultez l'onglet "Archives" pour l'historique

---

## ❓ FAQ

### Q1 : Pourquoi je ne vois que 3 champs mémo ?
**R** : Pour PARTNER, l'interface est simplifiée. Seuls les mémos utiles sont affichés (adresse/téléphone, employeur, proximité). Les enquêtes EOS conservent les 5 mémos.

### Q2 : Où saisir les informations de proximité ?
**R** : Dans le champ "Proximité (commentaires détaillés)" qui remplace l'ancien "Commentaires détaillés". C'est le champ le plus important pour PARTNER.

### Q3 : Que signifie "CONFIRMATION ADRESSE" vs "NOUVELLE ADRESSE" ?
**R** : 
- **CONFIRMATION ADRESSE** : L'adresse saisie est identique à l'adresse importée
- **NOUVELLE ADRESSE** : L'adresse saisie est différente de l'adresse importée

### Q4 : Pourquoi les textes sont-ils tronqués dans le Word ?
**R** : Pour garantir que chaque enquête tient sur 1 page. Les textes trop longs sont coupés avec "..." à la fin.

### Q5 : Comment voir les enquêtes exportées ?
**R** : Allez dans l'onglet "Archives". Vous y trouverez l'historique de tous les exports avec les dates et le nombre d'enquêtes.

### Q6 : Puis-je modifier une enquête après export ?
**R** : Non, une fois exportée, l'enquête est archivée et ne peut plus être modifiée. Assurez-vous que tout est correct avant d'exporter.

### Q7 : Le format EOS a-t-il changé ?
**R** : Non, absolument aucun changement pour EOS. Tous les formats, mémos et exports EOS restent identiques.

---

## 🆘 Dépannage

### Problème : Le champ NJF est vide dans l'Excel
**Solution** : Le NJF doit être renseigné lors de l'import. Si le champ "Nom patronymique" n'est pas rempli à l'import, la colonne NJF restera vide.

### Problème : La proximité n'apparaît pas dans le Word
**Solution** : Vérifiez que vous avez bien rempli le champ "Proximité (commentaires détaillés)" et non un autre champ mémo.

### Problème : L'enquête fait plus d'1 page dans le Word
**Solution** : C'est rare mais peut arriver si vous avez beaucoup de données. Les textes longs (instructions, mémos) sont normalement tronqués automatiquement.

### Problème : Je ne vois pas les mémos simplifiés
**Solution** : Vérifiez que vous êtes bien sur une enquête PARTNER. Pour EOS, tous les mémos sont affichés (comportement normal).

---

## 📞 Assistance

Si vous rencontrez un problème non couvert par ce guide :

1. **Vérifier les logs** : `backend/app.log`
2. **Vérifier la console** : Appuyez sur F12 dans le navigateur
3. **Redémarrer l'application** : `DEMARRER_EOS_COMPLET.bat`

---

**Dernière mise à jour** : 17/12/2025  
**Version du guide** : 2.0  
**Compatible avec** : EOS PARTNER v2.0+

