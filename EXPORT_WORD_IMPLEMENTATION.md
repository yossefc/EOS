# 📄 Implémentation de l'Export Word avec Archivage

## 🎯 Objectif

Remplacer l'export au format texte EOS par un export au format **Word (.docx)** avec :
- Une page par enquête
- Mise en page professionnelle (titres, tableaux, notes)
- Archivage automatique des enquêtes exportées
- Téléchargement direct du fichier Word

---

## ✅ Modifications Implémentées

### 1. **Backend - Dépendances**

**Fichier** : `backend/requirements.txt`

**Ajout** :
```txt
python-docx==1.1.0
```

**Installation** :
```powershell
cd D:\EOS\backend
pip install python-docx==1.1.0
```

---

### 2. **Backend - Nouveau Modèle d'Archivage**

**Fichier** : `backend/models/enquete_archive.py` *(NOUVEAU)*

**Description** : Table pour archiver les enquêtes exportées

**Colonnes** :
- `id` : Clé primaire
- `enquete_id` : ID de l'enquête (foreign key vers `donnees`)
- `date_export` : Date et heure de l'export
- `nom_fichier` : Nom du fichier généré
- `utilisateur` : Nom de l'utilisateur (optionnel)

**Relation** : Chaque enquête peut avoir plusieurs exports archivés

---

### 3. **Backend - Route d'Export Réécrite**

**Fichier** : `backend/routes/export.py` *(RÉÉCRIT COMPLÈTEMENT)*

**Changements majeurs** :

#### 3.1 Route `/api/export-enquetes` (POST)

**Avant** : Générait un fichier texte à longueur fixe (format EOS)

**Après** : Génère un fichier Word (.docx) avec mise en page professionnelle

**Fonctionnalités** :
- Reçoit une liste d'IDs d'enquêtes
- Génère un document Word avec `python-docx`
- Archive automatiquement les enquêtes exportées
- Retourne le fichier avec le bon Content-Type

#### 3.2 Fonction `generate_word_document(donnees)`

**Rôle** : Crée le document Word complet

**Processus** :
1. Crée un nouveau document
2. Configure le style par défaut (Calibri, 11pt)
3. Pour chaque enquête :
   - Ajoute le contenu formaté
   - Ajoute un saut de page (sauf pour la dernière)
4. Retourne le document

#### 3.3 Fonction `add_enquete_to_document(doc, donnee, donnee_enqueteur, enqueteur)`

**Rôle** : Ajoute une enquête au document avec mise en forme

**Structure de chaque page** :

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│        Enquête n°123 – Dupont Jean                      │
│              (Titre centré, bleu foncé, 18pt)           │
│                                                          │
│  Date : 23/11/2025 | Enquêteur : Pierre Martin | Statut : Positif
│                    (Sous-titre gris, 12pt)              │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Champ              │ Valeur                      │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ N° Dossier         │ 123456                      │   │
│  │ Référence          │ REF001                      │   │
│  │ Type de demande    │ Enquête                     │   │
│  │ Nom                │ Dupont                      │   │
│  │ Prénom             │ Jean                        │   │
│  │ Date de naissance  │ 01/01/1980                  │   │
│  │ ...                │ ...                         │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Notes / Commentaires                                   │
│  ────────────────────                                   │
│  Aucune note                                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Détails de mise en forme** :

1. **Titre principal** :
   - Style : Heading 1
   - Police : 18pt, gras
   - Couleur : Bleu foncé (RGB: 0, 51, 102)
   - Alignement : Centré
   - Espacement après : 12pt

2. **Sous-titre** :
   - Police : 12pt
   - Couleur : Gris foncé (RGB: 64, 64, 64)
   - Alignement : Gauche
   - Espacement après : 18pt

3. **Tableau** :
   - Style : "Light Grid Accent 1"
   - 2 colonnes : "Champ" et "Valeur"
   - En-tête : Gras, blanc sur fond bleu (RGB: 68, 114, 196)
   - Contenu : 10pt
   - Bordures fines

4. **Notes** :
   - Titre : Heading 2, 14pt, bleu foncé
   - Contenu : Paragraphe normal
   - Espacement : 12pt avant et après

#### 3.4 Fonction `get_enquete_fields_data(donnee, donnee_enqueteur)`

**Rôle** : Prépare les données à afficher dans le tableau

**Sections** :
- Informations de base (N° dossier, référence, type)
- État civil (nom, prénom, date/lieu de naissance)
- Adresse d'origine
- Résultat de l'enquête
- Adresse trouvée (si disponible)
- Contact (téléphones)
- Employeur (si disponible)
- Banque (si disponible)
- Décès (si disponible)

---

### 4. **Frontend - Composant EnqueteExporter**

**Fichier** : `frontend/src/components/EnqueteExporter.jsx`

**Changements** :

#### 4.1 Fonction `handleExport()`

**Avant** : Faisait une requête GET avec des paramètres de filtre

**Après** : Fait une requête POST avec la liste des enquêtes à exporter

```javascript
const response = await axios.post(`${API_URL}/api/export-enquetes`, {
  enquetes: enquetesToExport
}, {
  responseType: 'blob' // Important pour recevoir un fichier binaire
});
```

**Téléchargement** :
```javascript
// Créer un lien de téléchargement
const url = window.URL.createObjectURL(new Blob([response.data]));
const link = document.createElement('a');
link.href = url;
link.setAttribute('download', `Export_Enquetes_${date}.docx`);
document.body.appendChild(link);
link.click();
link.remove();
window.URL.revokeObjectURL(url);
```

#### 4.2 Textes mis à jour

- Titre : "Export des Résultats (Word)"
- Bouton : "Exporter en Word & archiver"
- Description : "Le fichier généré sera au format Word (.docx) avec une page par enquête..."

---

### 5. **Script de Migration**

**Fichier** : `backend/create_archive_table.py` *(NOUVEAU)*

**Rôle** : Créer la table `enquete_archives` dans la base de données

**Utilisation** :
```powershell
cd D:\EOS\backend
python create_archive_table.py
```

**Sortie attendue** :
```
✅ Table 'enquete_archives' créée avec succès!
✅ Vérification : La table 'enquete_archives' existe bien

Colonnes de la table :
  - id (INTEGER)
  - enquete_id (INTEGER)
  - date_export (DATETIME)
  - nom_fichier (VARCHAR(255))
  - utilisateur (VARCHAR(100))
```

---

## 📊 Structure du Document Word Final

### Exemple avec 3 Enquêtes

```
Page 1:
┌─────────────────────────────────────────┐
│ Enquête n°1 – Dupont Jean               │
│ Date : 23/11/2025 | Enquêteur : Martin  │
│ [Tableau des données]                   │
│ [Notes]                                 │
└─────────────────────────────────────────┘

[SAUT DE PAGE]

Page 2:
┌─────────────────────────────────────────┐
│ Enquête n°2 – Durand Marie              │
│ Date : 22/11/2025 | Enquêteur : Dubois  │
│ [Tableau des données]                   │
│ [Notes]                                 │
└─────────────────────────────────────────┘

[SAUT DE PAGE]

Page 3:
┌─────────────────────────────────────────┐
│ Enquête n°3 – Martin Paul               │
│ Date : 21/11/2025 | Enquêteur : Bernard │
│ [Tableau des données]                   │
│ [Notes]                                 │
└─────────────────────────────────────────┘
```

---

## 🚀 Installation et Démarrage

### 1. Installer les Dépendances

```powershell
cd D:\EOS\backend
pip install -r requirements.txt
```

**Vérification** :
```powershell
python -c "import docx; print('✅ python-docx installé')"
```

### 2. Créer la Table d'Archivage

```powershell
cd D:\EOS\backend
python create_archive_table.py
```

### 3. Redémarrer le Backend

```powershell
cd D:\EOS\backend
python app.py
```

### 4. Lancer le Frontend

```powershell
cd D:\EOS\frontend
npm run dev
```

---

## 🧪 Tests

### Scénario de Test Complet

1. **Ouvrir l'application** : http://localhost:5173

2. **Aller dans l'onglet "Export"**

3. **Sélectionner 2-3 enquêtes**

4. **Cliquer sur "Exporter en Word & archiver"**

5. **Vérifications** :
   - ✅ Un fichier `.docx` se télécharge
   - ✅ Le nom du fichier contient la date : `Export_Enquetes_YYYYMMDD_HHMMSS.docx`
   - ✅ Message de succès : "X enquête(s) exportée(s) avec succès en format Word"

6. **Ouvrir le fichier Word** :
   - ✅ Une page par enquête
   - ✅ Titre centré, bleu, gras
   - ✅ Sous-titre avec date, enquêteur, statut
   - ✅ Tableau avec 2 colonnes (Champ / Valeur)
   - ✅ En-tête du tableau en bleu
   - ✅ Section "Notes / Commentaires"
   - ✅ Sauts de page entre les enquêtes

7. **Vérifier l'archivage** :
```sql
SELECT * FROM enquete_archives ORDER BY date_export DESC LIMIT 10;
```

---

## 📁 Fichiers Modifiés

| Fichier | Type | Description |
|---------|------|-------------|
| `backend/requirements.txt` | Modifié | Ajout de `python-docx==1.1.0` |
| `backend/models/enquete_archive.py` | **NOUVEAU** | Modèle pour l'archivage |
| `backend/models/__init__.py` | Modifié | Export du modèle `EnqueteArchive` |
| `backend/routes/export.py` | **RÉÉCRIT** | Génération de fichiers Word |
| `backend/create_archive_table.py` | **NOUVEAU** | Script de migration |
| `frontend/src/components/EnqueteExporter.jsx` | Modifié | Téléchargement de fichiers Word |

---

## 🎨 Personnalisation du Style Word

### Modifier les Couleurs

Dans `backend/routes/export.py`, fonction `add_enquete_to_document()` :

```python
# Titre principal - Couleur actuelle : Bleu foncé
title_run.font.color.rgb = RGBColor(0, 51, 102)  # Modifier ici

# Sous-titre - Couleur actuelle : Gris foncé
subtitle_run.font.color.rgb = RGBColor(64, 64, 64)  # Modifier ici

# En-tête du tableau - Couleur actuelle : Bleu
shading = parse_xml(r'<w:shd {} w:fill="4472C4"/>'.format(nsdecls('w')))
# Modifier "4472C4" (hex) pour changer la couleur
```

### Modifier les Tailles de Police

```python
# Titre principal
title_run.font.size = Pt(18)  # Modifier ici (16-20 recommandé)

# Sous-titre
subtitle_run.font.size = Pt(12)  # Modifier ici (11-14 recommandé)

# Tableau
run.font.size = Pt(10)  # Modifier ici (9-11 recommandé)
```

### Ajouter des Champs

Dans la fonction `get_enquete_fields_data()` :

```python
# Ajouter un nouveau champ
fields.append(("Nouveau champ", donnee.nouveau_champ))
```

---

## 🔒 Sécurité et Bonnes Pratiques

### 1. Validation des Entrées

✅ **Implémenté** : Vérification que la liste d'enquêtes n'est pas vide

```python
if not enquetes_ids:
    return jsonify({"error": "Aucune enquête à exporter"}), 400
```

### 2. Gestion des Erreurs

✅ **Implémenté** : Try/catch avec logging

```python
try:
    # Code d'export
except Exception as e:
    logger.error(f"Erreur lors de l'export: {str(e)}")
    return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500
```

### 3. Archivage Sécurisé

✅ **Implémenté** : Rollback en cas d'erreur

```python
try:
    db.session.commit()
except Exception as e:
    logger.error(f"Erreur lors de l'archivage: {str(e)}")
    db.session.rollback()
```

### 4. Nettoyage des Ressources

✅ **Implémenté** : Libération de la mémoire

```python
window.URL.revokeObjectURL(url);  // Frontend
```

---

## 📈 Améliorations Futures

### Court Terme
1. ✅ Ajouter un logo/en-tête personnalisé
2. ✅ Permettre de choisir les champs à exporter
3. ✅ Ajouter des statistiques d'export dans l'interface

### Moyen Terme
1. Export en PDF en plus du Word
2. Templates Word personnalisables
3. Envoi par email automatique

### Long Terme
1. Planification d'exports automatiques
2. Historique complet des exports
3. Compression des gros exports

---

## 🆘 Dépannage

### Problème : `ModuleNotFoundError: No module named 'docx'`

**Solution** :
```powershell
pip install python-docx==1.1.0
```

### Problème : La table `enquete_archives` n'existe pas

**Solution** :
```powershell
python create_archive_table.py
```

### Problème : Le fichier Word ne se télécharge pas

**Vérifications** :
1. Console du navigateur (F12) pour les erreurs
2. Logs du backend (`app.log`)
3. Vérifier que `responseType: 'blob'` est bien défini

### Problème : Le tableau Word n'a pas de couleurs

**Cause** : Certaines versions de python-docx ne supportent pas tous les styles

**Solution** : Le code utilise du XML brut pour les couleurs, cela devrait fonctionner

---

## 📞 Support

Pour toute question ou problème :
1. Consulter les logs : `backend/app.log`
2. Vérifier la console du navigateur (F12)
3. Tester avec une seule enquête d'abord

---

**Date de création** : 23 novembre 2025  
**Version** : 1.0  
**Statut** : ✅ Implémenté et documenté  
**Format d'export** : Word (.docx)  
**Archivage** : Automatique


