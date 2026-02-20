"""
Route pour analyser une enquete complete avec toutes ses donnees
"""
from flask import jsonify

def analyze_enquete(app, db):
    @app.route('/api/analyze-enquete/<int:enquete_id>', methods=['GET'])
    def analyze_enquete_route(enquete_id):
        try:
            result = db.session.execute(db.text("""
                SELECT 
                    d.id,
                    d.client_id,
                    d.fichier_id,
                    d."numeroDossier",
                    d.nom,
                    d.prenom,
                    d."dateNaissance",
                    d."lieuNaissance",
                    d.adresse1,
                    d.adresse2,
                    d.adresse3,
                    d."codePostal",
                    d.ville,
                    d."paysResidence",
                    d."telephonePersonnel",
                    d."typeDemande",
                    d."elementDemandes",
                    d.statut_validation,
                    d.est_contestation,
                    de.code_resultat,
                    de.elements_retrouves,
                    de.date_retour,
                    de.nom_employeur,
                    de.adresse1_employeur,
                    de.code_postal_employeur,
                    de.ville_employeur,
                    de.telephone_employeur,
                    de.banque_domiciliation,
                    de.code_banque,
                    de.code_guichet,
                    de.libelle_guichet,
                    de.titulaire_compte,
                    de.memo1,
                    de.memo2,
                    de.memo3,
                    de.memo4,
                    de.memo5
                FROM donnees d
                LEFT JOIN donnees_enqueteur de ON de.donnee_id = d.id
                WHERE d.id = :enquete_id
            """), {'enquete_id': enquete_id})
            
            row = result.fetchone()
            if not row:
                return jsonify({'success': False, 'error': 'Enquete non trouvee'}), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'table_donnees': {
                        'id': row[0],
                        'client_id': row[1],
                        'fichier_id': row[2],
                        'numeroDossier': row[3],
                        'nom': row[4],
                        'prenom': row[5],
                        'dateNaissance': str(row[6]) if row[6] else None,
                        'lieuNaissance': row[7],
                        'adresse1': row[8],
                        'adresse2': row[9],
                        'adresse3': row[10],
                        'codePostal': row[11],
                        'ville': row[12],
                        'paysResidence': row[13],
                        'telephonePersonnel': row[14],
                        'typeDemande': row[15],
                        'elementDemandes': row[16],
                        'statut_validation': row[17],
                        'est_contestation': row[18]
                    },
                    'table_donnees_enqueteur': {
                        'code_resultat': row[19],
                        'elements_retrouves': row[20],
                        'date_retour': str(row[21]) if row[21] else None,
                        'nom_employeur': row[22],
                        'adresse1_employeur': row[23],
                        'code_postal_employeur': row[24],
                        'ville_employeur': row[25],
                        'telephone_employeur': row[26],
                        'banque_domiciliation': row[27],
                        'code_banque': row[28],
                        'code_guichet': row[29],
                        'libelle_guichet': row[30],
                        'titulaire_compte': row[31],
                        'memo1': row[32],
                        'memo2': row[33],
                        'memo3': row[34],
                        'memo4': row[35],
                        'memo5': row[36]
                    }
                }
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
