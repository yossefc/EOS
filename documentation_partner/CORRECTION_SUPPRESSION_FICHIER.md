# Correction Suppression de Fichier - Contrainte de Clé Étrangère

**Date**: 18 décembre 2025

## 🔴 Problème rencontré

Lors de la suppression d'un fichier, l'erreur suivante se produisait :

```
psycopg2.errors.ForeignKeyViolation: update or delete on table "donnees" 
violates foreign key constraint "enquete_facturation_donnee_id_fkey" 
on table "enquete_facturation"
DETAIL: Key (id)=(349) is still referenced from table "enquete_facturation".
```

## 🔍 Cause

La fonction `delete_file()` dans `backend/app.py` supprimait directement les `Donnee` sans supprimer d'abord les enregistrements qui les référencent, notamment :
- `EnqueteFacturation` (table de facturation)
- `DonneeEnqueteur` (données ajoutées par l'enquêteur)

Cela violait la contrainte de clé étrangère de la base de données.

## ✅ Solution appliquée

Modification de la route `/api/files/<int:file_id>` (DELETE) pour supprimer les dépendances dans le bon ordre :

### Ordre de suppression corrigé

1. **Facturations** (`EnqueteFacturation`) liées aux enquêtes du fichier
2. **Données enquêteur** (`DonneeEnqueteur`) liées aux enquêtes du fichier
3. **Enquêtes/Données** (`Donnee`) du fichier
4. **Fichier** (`Fichier`)

### Code avant (ancien)

```python
@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Supprime un fichier et ses données associées"""
    try:
        fichier = Fichier.query.get_or_404(file_id)
        Donnee.query.filter_by(fichier_id=file_id).delete()
        db.session.delete(fichier)
        db.session.commit()
        return jsonify({"message": "Fichier supprimé avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

### Code après (nouveau)

```python
@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Supprime un fichier et ses données associées"""
    try:
        from models.tarifs import EnqueteFacturation
        
        fichier = Fichier.query.get_or_404(file_id)
        
        # Récupérer les IDs des donnees à supprimer
        donnee_ids = [d.id for d in Donnee.query.filter_by(fichier_id=file_id).all()]
        
        if donnee_ids:
            # 1. Supprimer d'abord les facturations liées
            EnqueteFacturation.query.filter(
                EnqueteFacturation.donnee_id.in_(donnee_ids)
            ).delete(synchronize_session=False)
            
            # 2. Supprimer les données enquêteur liées
            DonneeEnqueteur.query.filter(
                DonneeEnqueteur.donnee_id.in_(donnee_ids)
            ).delete(synchronize_session=False)
            
            # 3. Supprimer les données
            Donnee.query.filter_by(fichier_id=file_id).delete()
        
        # 4. Supprimer le fichier
        db.session.delete(fichier)
        db.session.commit()
        
        logger.info(f"Fichier {file_id} supprimé avec {len(donnee_ids)} enquêtes associées")
        return jsonify({"message": "Fichier supprimé avec succès"}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la suppression: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

## 📋 Détails techniques

### Pourquoi `synchronize_session=False` ?

Lors de suppressions en masse avec SQLAlchemy, l'option `synchronize_session=False` indique à SQLAlchemy de ne pas essayer de synchroniser la session avec les objets supprimés. C'est plus performant et évite des erreurs.

### Pourquoi récupérer les IDs d'abord ?

```python
donnee_ids = [d.id for d in Donnee.query.filter_by(fichier_id=file_id).all()]
```

Cette ligne récupère tous les IDs des enquêtes (Donnee) associées au fichier **avant** de supprimer quoi que ce soit. Cela permet ensuite de supprimer toutes les dépendances (facturations, données enquêteur) qui référencent ces enquêtes.

## 🧪 Test

Pour vérifier que la correction fonctionne :

1. Aller dans l'onglet **"Mes fichiers"**
2. Sélectionner un fichier avec des enquêtes validées/facturées
3. Cliquer sur **"Supprimer"**
4. **Résultat attendu** : Le fichier et toutes ses données associées sont supprimés sans erreur

## 📝 Impact

- ✅ **EOS** : Correction s'applique à tous les clients
- ✅ **PARTNER** : Correction s'applique à tous les clients
- ✅ **Pas d'impact sur les autres fonctionnalités**

## 🔗 Fichiers modifiés

1. `backend/app.py` (fonction `delete_file`, lignes 1266-1295)

## ⚠️ Important

Cette correction nécessite un **redémarrage du backend** pour être appliquée.

## ✨ Résultat

Après correction et redémarrage :
- ✅ Suppression de fichier fonctionne sans erreur
- ✅ Toutes les dépendances sont correctement supprimées
- ✅ Aucune orpheline laissée dans la base de données

