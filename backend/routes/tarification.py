# backend/routes/tarification.py

from flask import Blueprint, request, jsonify
from models.tarifs import TarifEOS, TarifEnqueteur, EnqueteFacturation
from services.tarification_service import TarificationService
from extensions import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

tarification_bp = Blueprint('tarification', __name__)

# Routes pour les tarifs EOS
@tarification_bp.route('/api/tarifs/eos', methods=['GET'])
def get_tarifs_eos():
    """Récupère la liste des tarifs EOS"""
    try:
        tarifs = TarifEOS.query.filter_by(actif=True).all()
        return jsonify({
            'success': True,
            'data': [tarif.to_dict() for tarif in tarifs]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tarifs EOS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/eos/<int:id>', methods=['GET'])
def get_tarif_eos(id):
    """Récupère un tarif EOS spécifique"""
    try:
        tarif = TarifEOS.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': tarif.to_dict()
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du tarif EOS {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/eos', methods=['POST'])
def create_tarif_eos():
    """Crée un nouveau tarif EOS"""
    try:
        data = request.json
        
        # Valider les données
        if not data.get('code') or not data.get('montant'):
            return jsonify({
                'success': False,
                'error': 'Code et montant sont obligatoires'
            }), 400
        
        # Vérifier si un tarif actif existe déjà pour ce code
        existing_tarif = TarifEOS.query.filter_by(
            code=data.get('code'),
            actif=True,
            date_fin=None
        ).first()
        
        if existing_tarif:
            # Désactiver l'ancien tarif
            existing_tarif.actif = False
            existing_tarif.date_fin = datetime.utcnow().date()
        
        # Créer le nouveau tarif
        nouveau_tarif = TarifEOS(
            code=data.get('code'),
            description=data.get('description'),
            montant=data.get('montant'),
            date_debut=datetime.utcnow().date(),
            actif=True
        )
        
        db.session.add(nouveau_tarif)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif EOS créé avec succès',
            'data': nouveau_tarif.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création du tarif EOS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/eos/<int:id>', methods=['PUT'])
def update_tarif_eos(id):
    """Met à jour un tarif EOS existant"""
    try:
        tarif = TarifEOS.query.get_or_404(id)
        data = request.json
        
        # Mettre à jour les champs
        if 'description' in data:
            tarif.description = data['description']
        if 'montant' in data:
            tarif.montant = data['montant']
        if 'actif' in data:
            tarif.actif = data['actif']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif EOS mis à jour avec succès',
            'data': tarif.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la mise à jour du tarif EOS {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/eos/<int:id>', methods=['DELETE'])
def delete_tarif_eos(id):
    """Supprime un tarif EOS (désactivation logique)"""
    try:
        tarif = TarifEOS.query.get_or_404(id)
        
        # Désactivation logique
        tarif.actif = False
        tarif.date_fin = datetime.utcnow().date()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif EOS désactivé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la désactivation du tarif EOS {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Routes pour les tarifs Enquêteur
@tarification_bp.route('/api/tarifs/enqueteur', methods=['GET'])
def get_tarifs_enqueteur():
    """Récupère la liste des tarifs Enquêteur"""
    try:
        # Filtrer par enquêteur si spécifié
        enqueteur_id = request.args.get('enqueteur_id')
        
        if enqueteur_id:
            tarifs = TarifEnqueteur.query.filter_by(
                enqueteur_id=enqueteur_id,
                actif=True
            ).all()
        else:
            tarifs = TarifEnqueteur.query.filter_by(actif=True).all()
            
        return jsonify({
            'success': True,
            'data': [tarif.to_dict() for tarif in tarifs]
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tarifs Enquêteur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/enqueteur/<int:id>', methods=['GET'])
def get_tarif_enqueteur(id):
    """Récupère un tarif Enquêteur spécifique"""
    try:
        tarif = TarifEnqueteur.query.get_or_404(id)
        return jsonify({
            'success': True,
            'data': tarif.to_dict()
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du tarif Enquêteur {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/enqueteur', methods=['POST'])
def create_tarif_enqueteur():
    """Crée un nouveau tarif Enquêteur"""
    try:
        data = request.json
        
        # Valider les données
        if not data.get('code') or not data.get('montant'):
            return jsonify({
                'success': False,
                'error': 'Code et montant sont obligatoires'
            }), 400
        
        # Vérifier si un tarif actif existe déjà pour ce code et cet enquêteur
        existing_tarif = TarifEnqueteur.query.filter_by(
            code=data.get('code'),
            enqueteur_id=data.get('enqueteur_id'),
            actif=True,
            date_fin=None
        ).first()
        
        if existing_tarif:
            # Désactiver l'ancien tarif
            existing_tarif.actif = False
            existing_tarif.date_fin = datetime.utcnow().date()
        
        # Créer le nouveau tarif
        nouveau_tarif = TarifEnqueteur(
            code=data.get('code'),
            description=data.get('description'),
            montant=data.get('montant'),
            enqueteur_id=data.get('enqueteur_id'),  # Peut être None (tarif par défaut)
            date_debut=datetime.utcnow().date(),
            actif=True
        )
        
        db.session.add(nouveau_tarif)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif Enquêteur créé avec succès',
            'data': nouveau_tarif.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création du tarif Enquêteur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/enqueteur/<int:id>', methods=['PUT'])
def update_tarif_enqueteur(id):
    """Met à jour un tarif Enquêteur existant"""
    try:
        tarif = TarifEnqueteur.query.get_or_404(id)
        data = request.json
        
        # Mettre à jour les champs
        if 'description' in data:
            tarif.description = data['description']
        if 'montant' in data:
            tarif.montant = data['montant']
        if 'actif' in data:
            tarif.actif = data['actif']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif Enquêteur mis à jour avec succès',
            'data': tarif.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la mise à jour du tarif Enquêteur {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/enqueteur/<int:id>', methods=['DELETE'])
def delete_tarif_enqueteur(id):
    """Supprime un tarif Enquêteur (désactivation logique)"""
    try:
        tarif = TarifEnqueteur.query.get_or_404(id)
        
        # Désactivation logique
        tarif.actif = False
        tarif.date_fin = datetime.utcnow().date()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarif Enquêteur désactivé avec succès'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la désactivation du tarif Enquêteur {id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Routes pour la facturation
@tarification_bp.route('/api/facturation/<int:donnee_enqueteur_id>', methods=['GET'])
def get_facturation(donnee_enqueteur_id):
    """Récupère les informations de facturation pour une enquête spécifique"""
    try:
        facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur_id).first()
        
        if not facturation:
            # Calculer les tarifs si aucune facturation n'existe
            facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur_id)
        
        if facturation:
            return jsonify({
                'success': True,
                'data': facturation.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Impossible de calculer la facturation'
            }), 404
            
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la facturation {donnee_enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/facturation/recalculer/<int:donnee_enqueteur_id>', methods=['POST'])
def recalculer_facturation(donnee_enqueteur_id):
    """Force le recalcul de la facturation pour une enquête spécifique"""
    try:
        facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur_id)
        
        if facturation:
            return jsonify({
                'success': True,
                'message': 'Facturation recalculée avec succès',
                'data': facturation.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Impossible de recalculer la facturation'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors du recalcul de la facturation {donnee_enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/facturation/payer', methods=['POST'])
def marquer_comme_paye():
    """Marque un ensemble de facturations comme payées"""
    try:
        data = request.json
        facturation_ids = data.get('facturation_ids', [])
        reference_paiement = data.get('reference_paiement')
        
        if not facturation_ids:
            return jsonify({
                'success': False,
                'error': 'Aucun ID de facturation fourni'
            }), 400
        
        count = TarificationService.marquer_comme_paye(facturation_ids, reference_paiement)
        
        return jsonify({
            'success': True,
            'message': f'{count} facturations marquées comme payées',
            'count': count
        })
        
    except Exception as e:
        logger.error(f"Erreur lors du marquage des paiements: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/facturation/enqueteur/<int:enqueteur_id>', methods=['GET'])
def get_enqueteur_earnings(enqueteur_id):
    """Récupère les gains d'un enquêteur"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        # Si un seul des deux est spécifié, utiliser les deux
        if (month and not year) or (year and not month):
            now = datetime.utcnow()
            month = month or now.month
            year = year or now.year
        
        earnings = TarificationService.get_enqueteur_earnings(enqueteur_id, month, year)
        
        if earnings:
            return jsonify({
                'success': True,
                'data': earnings
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Impossible de calculer les gains'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors du calcul des gains de l'enquêteur {enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarifs/initialiser', methods=['POST'])
def initialiser_tarifs():
    """Initialise les tarifs par défaut"""
    try:
        success = TarificationService.initialiser_tarifs_par_defaut()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Tarifs par défaut initialisés avec succès'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Erreur lors de l\'initialisation des tarifs'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des tarifs: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_tarification_routes(app):
    """Enregistre les routes de tarification"""
    app.register_blueprint(tarification_bp)