"""
Routes de maintenance pour l'application EOS
"""
from flask import Blueprint, jsonify
from extensions import db
from models.models_enqueteur import DonneeEnqueteur

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/api/maintenance/clear-donnees-enqueteur', methods=['DELETE'])
def clear_donnees_enqueteur():
    """Supprime toutes les données de la table donnees_enqueteur"""
    try:
        # Compter le nombre d'enregistrements avant suppression
        count_before = DonneeEnqueteur.query.count()
        
        if count_before == 0:
            return jsonify({
                'message': 'La table donnees_enqueteur est déjà vide',
                'count_deleted': 0
            }), 200
        
        # Supprimer tous les enregistrements
        DonneeEnqueteur.query.delete()
        db.session.commit()
        
        # Vérifier que la table est vide
        count_after = DonneeEnqueteur.query.count()
        
        return jsonify({
            'message': f'Suppression réussie ! {count_before} enregistrement(s) supprimé(s)',
            'count_deleted': count_before,
            'count_remaining': count_after
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Erreur lors de la suppression : {str(e)}'
        }), 500




