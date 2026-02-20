"""
Route pour verifier l'import
"""
from flask import jsonify

def verify_import(app, db):
    @app.route('/api/verify-import', methods=['GET'])
    def verify_import_route():
        try:
            # Compter par client
            result = db.session.execute(db.text("""
                SELECT 
                    c.id as client_id,
                    c.code as client_code,
                    c.nom as client_nom,
                    COUNT(d.id) as nb_enquetes,
                    COUNT(de.id) as nb_donnees_enqueteur
                FROM clients c
                LEFT JOIN donnees d ON d.client_id = c.id
                LEFT JOIN donnees_enqueteur de ON de.donnee_id = d.id
                GROUP BY c.id, c.code, c.nom
                ORDER BY nb_enquetes DESC
            """))
            
            clients = []
            for row in result.fetchall():
                clients.append({
                    'client_id': row[0],
                    'code': row[1],
                    'nom': row[2],
                    'nb_enquetes': row[3],
                    'nb_donnees_enqueteur': row[4]
                })
            
            # Exemple d'enquete
            sample = db.session.execute(db.text("""
                SELECT id, client_id, "numeroDossier", nom, prenom, ville, "codePostal"
                FROM donnees
                ORDER BY id
                LIMIT 5
            """)).fetchall()
            
            samples = []
            for row in sample:
                samples.append({
                    'id': row[0],
                    'client_id': row[1],
                    'numeroDossier': row[2],
                    'nom': row[3],
                    'prenom': row[4],
                    'ville': row[5],
                    'codePostal': row[6]
                })
            
            return jsonify({
                'success': True,
                'clients': clients,
                'samples': samples
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
