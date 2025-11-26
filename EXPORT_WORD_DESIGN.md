# 📄 Export Word avec Design Professionnel

## 🎯 Fonctionnalité

L'export génère maintenant un **fichier Word (.docx)** avec un design professionnel :
- ✅ **Une enquête par page**
- ✅ **Design moderne et structuré**
- ✅ **Tableau de données formaté**
- ✅ **Sections bien organisées**

## 📋 Structure du Document Word

### Pour Chaque Enquête :

#### 1. **Titre Principal** (Centré, Bleu Foncé, 18pt)
```
Enquête n°123 – DUPONT Jean
```

#### 2. **Sous-titre** (Gris Foncé, 12pt)
```
Date : 23/11/2024 | Enquêteur : Marie MARTIN | Statut : Positif
```

#### 3. **Tableau des Données** (2 colonnes)
- **En-tête** : Fond bleu (#4472C4), texte blanc, gras
- **Colonnes** : "Champ" | "Valeur"
- **Contenu** :
  - Informations de base (N° Dossier, Référence, Type)
  - État civil (Nom, Prénom, Date/Lieu de naissance)
  - Adresse d'origine
  - Résultat de l'enquête
  - Adresse trouvée (si disponible)
  - Contact (téléphones)
  - Employeur (si disponible)
  - Banque (si disponible)
  - Décès (si applicable)

#### 4. **Section Notes / Commentaires**
- Titre en bleu foncé (14pt)
- Contenu des notes personnelles et commentaires

#### 5. **Saut de Page**
- Chaque enquête commence sur une nouvelle page

## 🎨 Design et Couleurs

### Palette de Couleurs
- **Bleu foncé** : `RGB(0, 51, 102)` - Titres
- **Bleu clair** : `#4472C4` - En-tête tableau
- **Gris foncé** : `RGB(64, 64, 64)` - Sous-titres
- **Blanc** : `RGB(255, 255, 255)` - Texte en-tête

### Polices
- **Principale** : Calibri 11pt
- **Titres** : Calibri 18pt (gras)
- **Sous-titres** : Calibri 12pt
- **Notes** : Calibri 14pt (titres de section)
- **Tableau** : Calibri 10-11pt

### Espacements
- Après titre principal : 12pt
- Après sous-titre : 18pt
- Avant section notes : 12pt
- Après section notes : 12pt

## 📁 Format du Fichier

### Nom du Fichier
```
Export_Enquetes_YYYYMMDD_HHMMSS.docx
```

**Exemple** : `Export_Enquetes_20241123_143022.docx`

### Type MIME
```
application/vnd.openxmlformats-officedocument.wordprocessingml.document
```

## 🔧 Utilisation

### Depuis l'Onglet "Export des Résultats"

1. Sélectionnez les enquêtes à exporter
2. Cliquez sur **"Exporter en Word"**
3. Le fichier `.docx` se télécharge automatiquement
4. Ouvrez le fichier avec Microsoft Word, LibreOffice, ou Google Docs

### Exemple de Requête

**POST** `/api/export-enquetes`

```json
{
  "enquetes": [
    { "id": 123 },
    { "id": 124 },
    { "id": 125 }
  ]
}
```

**Réponse** : Fichier Word binaire

## 📊 Contenu du Tableau

### Champs Exportés

#### Informations de Base
- N° Dossier
- Référence
- Type de demande (Enquête / Contestation)

#### État Civil
- Nom
- Prénom
- Date de naissance (format DD/MM/YYYY)
- Lieu de naissance

#### Adresse d'Origine
- Adresse
- Code postal
- Ville
- Téléphone

#### Résultats
- Code résultat (avec label : Positif, Négatif, etc.)
- Éléments retrouvés

#### Adresse Trouvée (si disponible)
- Adresse 1, 2, 3
- Code postal
- Ville
- Pays

#### Contact (si disponible)
- Téléphone personnel
- Téléphone chez employeur

#### Employeur (si disponible)
- Nom employeur
- Téléphone employeur
- Adresse employeur
- Ville employeur

#### Banque (si disponible)
- Banque de domiciliation
- Guichet
- Titulaire du compte
- Code banque
- Code guichet

#### Décès (si applicable)
- Date de décès
- N° acte de décès
- Lieu de décès

## 🔍 Codes Résultat

| Code | Label |
|------|-------|
| P | Positif |
| N | Négatif |
| H | Confirmé |
| Z | Annulé (agence) |
| I | Intraitable |
| Y | Annulé (EOS) |
| (vide) | En attente |

## 💡 Avantages du Format Word

### ✅ Avantages
- **Éditable** : Possibilité de modifier le contenu après export
- **Professionnel** : Design soigné et structuré
- **Portable** : Compatible avec tous les logiciels de traitement de texte
- **Imprimable** : Mise en page optimisée pour l'impression
- **Partageable** : Format standard reconnu partout

### 📝 Cas d'Usage
- Rapports clients
- Archives physiques
- Présentations
- Documentation officielle
- Envoi par email

## 🛠️ Dépendances

### Backend
```
python-docx==1.1.0
```

### Installation
```bash
cd D:/EOS/backend
pip install python-docx
```

## 🧪 Tests

### Test 1 : Export Simple
1. Sélectionner 1 enquête
2. Cliquer sur "Exporter"
3. Vérifier que le fichier `.docx` se télécharge
4. Ouvrir le fichier
5. Vérifier le design et le contenu

### Test 2 : Export Multiple
1. Sélectionner 3-5 enquêtes
2. Cliquer sur "Exporter"
3. Ouvrir le fichier
4. Vérifier qu'il y a bien une page par enquête
5. Vérifier les sauts de page

### Test 3 : Données Complètes
1. Sélectionner une enquête avec toutes les données remplies
2. Exporter
3. Vérifier que tous les champs sont présents dans le tableau

### Test 4 : Données Partielles
1. Sélectionner une enquête avec peu de données
2. Exporter
3. Vérifier que seuls les champs disponibles sont affichés

## 📞 Support

### Problèmes Courants

#### Le fichier ne se télécharge pas
- Vérifier la console du navigateur (F12)
- Vérifier les logs backend (`app.log`)
- Vérifier que `python-docx` est installé

#### Le fichier est corrompu
- Vérifier la version de `python-docx`
- Vérifier les logs d'erreur backend

#### Le design ne s'affiche pas correctement
- Ouvrir avec Microsoft Word ou LibreOffice
- Certains lecteurs PDF ne supportent pas tous les styles

---

**Date de création** : 23 novembre 2024
**Version** : 2.0 (Export Word avec Design)


