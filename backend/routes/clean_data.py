"""
Script pour vider completement la table donnees et les tables liees
ATTENTION: OPERATION IRREVERSIBLE !
"""
from flask import jsonify

def clean_all_data(app, db):
    @app.route('/api/clean-all-donnees', methods=['POST'])
    def clean_all_donnees():
        """DANGER: Vide toutes les donnees de la table donnees"""
        try:
            # Compter avant suppression
            count_donnees = db.session.execute(db.text("SELECT COUNT(*) FROM donnees")).scalar()
            count_enqueteur = db.session.execute(db.text("SELECT COUNT(*) FROM donnees_enqueteur")).scalar()
            
            # Supprimer dans l'ordre (contraintes FK)
            db.session.execute(db.text("DELETE FROM donnees_enqueteur"))
            db.session.execute(db.text("DELETE FROM enquete_archives"))
            db.session.execute(db.text("DELETE FROM enquete_facturation"))
            db.session.execute(db.text("DELETE FROM donnees"))
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Toutes les donnees ont ete supprimees',
                'deleted': {
                    'donnees': count_donnees,
                    'donnees_enqueteur': count_enqueteur
                }
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
