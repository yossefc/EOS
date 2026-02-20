# -*- coding: utf-8 -*-
"""
Route temporaire pour comparer imports Excel vs Base de donnees
"""
from flask import Blueprint, jsonify
from backend.models.models import Donnee, DonneeEnqueteur, db
from sqlalchemy import func

compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/api/compare-excel-imports', methods=['GET'])
def compare_excel_imports():
    """Compare les imports Excel avec la base de donnees"""
    
    # 1. Nombre total d'enquetes PARTNER archivees dans la base
    partner_client = db.session.execute(
        db.text("SELECT id FROM clients WHERE code = 'PARTNER'")
    ).fetchone()
    
    if not partner_client:
        return jsonify({'error': 'Client PARTNER non trouve'}), 404
    
    client_id = partner_client[0]
    
    # Total enquetes archivees
    total_archives = Donnee.query.filter_by(
        client_id=client_id,
        est_contestation=False,
        statut_validation='archive'
    ).count()
    
    # Enquetes avec donnees enqueteur
    archives_avec_results = db.session.query(Donnee).join(
        DonneeEnqueteur,
        Donnee.id == DonneeEnqueteur.donnee_id
    ).filter(
        Donnee.client_id == client_id,
        Donnee.est_contestation == False,
        Donnee.statut_validation == 'archive',
        DonneeEnqueteur.code_resultat.isnot(None)
    ).count()
    
    # Enquetes SANS donnees enqueteur
    archives_sans_results = total_archives - archives_avec_results
    
    # Lire le fichier Excel pour comparaison
    try:
        with open('enquetes_excel_list.txt', 'r', encoding='utf-8') as f:
            excel_count = sum(1 for _ in f)
    except:
        excel_count = 17838  # Valeur connue
    
    return jsonify({
        'success': True,
        'excel': {
            'total_enquetes': excel_count,
            'description': 'Nombre total dans les fichiers CR backup'
        },
        'database': {
            'total_archives': total_archives,
            'avec_resultats': archives_avec_results,
            'sans_resultats': archives_sans_results
        },
        'difference': {
            'manquantes': excel_count - total_archives,
            'pourcentage_importe': round((total_archives / excel_count) * 100, 2) if excel_count > 0 else 0,
            'pourcentage_avec_resultats': round((archives_avec_results / total_archives) * 100, 2) if total_archives > 0 else 0
        }
    })
