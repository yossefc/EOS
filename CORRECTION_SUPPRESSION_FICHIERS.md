# Correction du Problème de Suppression de Fichiers

## 🔴 Problème Identifié

Lorsqu'un fichier était supprimé depuis l'onglet "Import de fichiers", les données dans la table `donnees` étaient supprimées, **MAIS** les données associées dans la table `donnees_enqueteur` restaient en base de données, créant des données orphelines.

## 🔍 Cause du Problème

Dans le fichier `backend/routes/files.py`, la fonction `delete_file()` utilisait une suppression en masse avec SQLAlchemy :

```python
# ❌ ANCIEN CODE (PROBLÉMATIQUE)
Donnee.query.filter_by(fichier_id=file.id).delete()
```

Cette méthode de suppression en masse **ne déclenche pas** les cascades SQLAlchemy définies dans les modèles. Les enregistrements `DonneeEnqueteur` liés aux `Donnee` n'étaient donc pas supprimés.

## ✅ Solution Appliquée

### 1. Correction de la Route de Suppression

Le code a été modifié pour utiliser la suppression en cascade automatique de SQLAlchemy :

```python
# ✅ NOUVEAU CODE (CORRIGÉ)
# Supprimer l'entrée de la base de données
# La cascade 'all, delete-orphan' définie dans le modèle Fichier
# supprimera automatiquement toutes les Donnee associées,
# et la cascade sur Donnee supprimera les DonneeEnqueteur
db.session.delete(file)
db.session.commit()
```

### 2. Ajout de la Colonne `chemin` au Modèle Fichier

Le modèle `Fichier` a été mis à jour pour inclure la colonne `chemin` qui était utilisée dans le code mais manquante dans le modèle :

```python
class Fichier(db.Model):
    __tablename__ = 'fichiers'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    chemin = db.Column(db.String(500), nullable=True)  # ✅ AJOUTÉ
    date_upload = db.Column(db.DateTime, default=lambda: datetime.now(datetime.UTC).replace(tzinfo=None))
    donnees = db.relationship('Donnee', backref='fichier', lazy=True, cascade='all, delete-orphan')
```

### 3. Migration de la Base de Données

Un script de migration a été créé et exécuté pour ajouter la colonne `chemin` à la table `fichiers` existante.

## 🔗 Relations en Cascade

Le système utilise maintenant correctement les cascades définies dans les modèles :

```
Fichier (supprimé)
    ↓ cascade='all, delete-orphan'
Donnee (supprimée automatiquement)
    ↓ cascade='all, delete-orphan'
DonneeEnqueteur (supprimée automatiquement)
```

## 📝 Fichiers Modifiés

1. **`backend/routes/files.py`** - Correction de la fonction `delete_file()`
2. **`backend/models/models.py`** - Ajout de la colonne `chemin` au modèle `Fichier`
3. **`backend/fix_fichiers_table.py`** - Script de migration (créé)
4. **`backend/migrations/add_chemin_to_fichiers.py`** - Migration Alembic (créée)

## ✨ Résultat

Désormais, lorsqu'un fichier est supprimé depuis l'onglet "Import de fichiers" :

1. ✅ Le fichier physique est supprimé du disque
2. ✅ L'enregistrement `Fichier` est supprimé de la base de données
3. ✅ Tous les enregistrements `Donnee` liés sont supprimés automatiquement (cascade)
4. ✅ Tous les enregistrements `DonneeEnqueteur` liés sont supprimés automatiquement (cascade)
5. ✅ Aucune donnée orpheline ne reste en base de données

## 🧪 Test Recommandé

Pour vérifier que la correction fonctionne :

1. Importer un fichier OST
2. Assigner des enquêtes à des enquêteurs (créant des entrées dans `donnees_enqueteur`)
3. Supprimer le fichier depuis l'onglet "Import de fichiers"
4. Vérifier que toutes les données associées ont été supprimées :

```sql
-- Vérifier qu'il n'y a pas de données orphelines
SELECT * FROM donnees_enqueteur 
WHERE donnee_id NOT IN (SELECT id FROM donnees);
```

Le résultat devrait être vide (aucune donnée orpheline).

## 📅 Date de Correction

**1er décembre 2025**



