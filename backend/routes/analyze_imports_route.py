# -*- coding: utf-8 -*-
"""
Route pour analyser la structure des imports
"""
from flask import jsonify

def analyze_imports(app, db):
    @app.route('/api/analyze-imports', methods=['GET'])
    def analyze_imports_route():
        try:
            # Get sample from database
            result = db.session.execute(db.text("""
                SELECT 
                    d.id,
                    d."numeroDossier",
                    d.nom,
                    d.prenom,
                    d."typeDemande",
                    d.statut_validation,
                    d.est_contestation,
                    c.code as client_code
                FROM donnees d
                JOIN clients c ON d.client_id = c.id
                WHERE c.code = 'PARTNER'
                AND d.est_contestation = false
                AND d.statut_validation = 'archive'
                ORDER BY d.id
                LIMIT 20
            """))
            
            samples = []
            for row in result.fetchall():
                samples.append({
                    'id': row[0],
                    'numeroDossier': row[1],
                    'nom': row[2],
                    'prenom': row[3],
                    'typeDemande': row[4],
                    'statut': row[5],
                    'contestation': row[6],
                    'client': row[7]
                })
            
            return jsonify({
                'success': True,
                'count': len(samples),
                'samples': samples
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
