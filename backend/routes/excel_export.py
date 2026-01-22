from flask import Blueprint, request, send_file, jsonify
import pandas as pd
from io import BytesIO
from datetime import datetime
import logging
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client
from extensions import db
from client_utils import get_client_or_default

logger = logging.getLogger(__name__)
excel_export_bp = Blueprint('excel_export', __name__)

@excel_export_bp.route('/api/export-excel', methods=['POST', 'GET'])
def export_excel():
    """
    Exporte les données au format Excel
    Params (via JSON POST ou Query GET):
    - client_id: ID du client (optionnel)
    - client_code: Code du client (optionnel)
    - file_id: ID du fichier original (optionnel)
    - status: Filtre par statut (optionnel)
    """
    try:
        # Récupérer les paramètres
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args
            
        client_id_param = data.get('client_id')
        client_code_param = data.get('client_code')
        file_id = data.get('file_id')
        status = data.get('status')
        all_data = data.get('all_data', False) # Si True, ignore exported=False

        # Identifier le client
        client = None
        if client_id_param:
            client = db.session.get(Client, client_id_param)
        elif client_code_param:
            client = Client.query.filter_by(code=client_code_param).first()
        
        if not client:
            client = get_client_or_default()
            
        logger.info(f"Export Excel demandé pour client: {client.code}")

        # Construire la requête
        query = Donnee.query.filter(Donnee.client_id == client.id)
        
        if file_id:
            query = query.filter(Donnee.fichier_id == file_id)
        
        if status:
            query = query.filter(Donnee.statut_validation == status)
            
        if not all_data:
            # Par défaut, n'exporter que ce qui n'a pas été exporté
            query = query.filter(Donnee.exported == False)

        donnees = query.all()
        
        if not donnees:
            return jsonify({
                "success": False,
                "message": "Aucune donnée à exporter."
            }), 200

        # Préparer les données pour le DataFrame
        export_data = []
        for d in donnees:
            # Infos de base
            row = {
                'ID': d.id,
                'N° Dossier': d.numeroDossier,
                'Nom': d.nom,
                'Prénom': d.prenom,
                'Nom Patronymique': d.nomPatronymique,
                'Date Naissance': d.dateNaissance.strftime('%d/%m/%Y') if d.dateNaissance else '',
                'Lieu Naissance': d.lieuNaissance,
                'Adresse 1': d.adresse1,
                'Adresse 2': d.adresse2,
                'Code Postal': d.codePostal,
                'Ville': d.ville,
                'Email': d.email,
                'Téléphone': d.telephonePersonnel,
                'Type Demande': d.typeDemande,
                'Statut': d.statut_validation,
                'Créé le': d.created_at.strftime('%d/%m/%Y %H:%M')
            }
            
            # Joindre les infos de l'enquêteur si dispo
            de = DonneeEnqueteur.query.filter_by(donnee_id=d.id).first()
            if de:
                row.update({
                    'Résultat Code': de.code_resultat,
                    'Éléments Retrouvés': de.elements_retrouves,
                    'Adresse Résultat': de.adresse1,
                    'CP Résultat': de.code_postal,
                    'Ville Résultat': de.ville,
                    'Tel Résultat': de.telephone_personnel,
                    'Note Enquêteur': de.memo5
                })
            
            export_data.append(row)

        # Créer le DataFrame
        df = pd.DataFrame(export_data)
        
        # Générer le fichier Excel en mémoire
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Donnees')
            
            # Auto-ajuster la largeur des colonnes (syntaxe openpyxl)
            worksheet = writer.sheets['Donnees']
            for i, col in enumerate(df.columns):
                column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                column_letter = chr(65 + i) if i < 26 else f"{chr(64 + i // 26)}{chr(65 + i % 26)}"
                worksheet.column_dimensions[column_letter].width = min(column_len, 50)

        output.seek(0)
        
        # Marquer comme exporté si demandé (optionnel, activé par défaut ici)
        if not all_data:
            now = datetime.now()
            for d in donnees:
                d.exported = True
                d.exported_at = now
            db.session.commit()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Export_{client.code}_{timestamp}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'export Excel: {str(e)}", exc_info=True)
        return jsonify({"error": f"Erreur lors de l'export: {str(e)}"}), 500

def register_excel_export_routes(app):
    app.register_blueprint(excel_export_bp)
