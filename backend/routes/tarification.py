# backend/routes/tarification.py

from flask import Blueprint, request, jsonify
from models.tarifs import TarifEOS, TarifEnqueteur, EnqueteFacturation
from services.tarification_service import TarificationService
from extensions import db
import logging
from datetime import datetime
from models.models_enqueteur import DonneeEnqueteur
from models.models import Donnee



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
    
@tarification_bp.route('/api/tarification/creer-facturations-manquantes', methods=['POST'])
def creer_facturations_manquantes():
    """Crée des facturations pour toutes les contestations sans facturation"""
    try:
        # Récupérer toutes les contestations
        contestations = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, 
            Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.est_contestation == True
        ).all()
        
        created_count = 0
        
        for donnee, donnee_enqueteur in contestations:
            # Vérifier si une facturation existe déjà
            existing = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
            
            if not existing:
                # Créer une facturation
                facturation = EnqueteFacturation(
                    donnee_id=donnee.id,
                    donnee_enqueteur_id=donnee_enqueteur.id,
                    tarif_eos_code=donnee_enqueteur.code_resultat or "ENCOURS",
                    tarif_eos_montant=0.0,
                    resultat_eos_montant=0.0,
                    tarif_enqueteur_code=donnee_enqueteur.code_resultat or "ENCOURS",
                    tarif_enqueteur_montant=0.0,
                    resultat_enqueteur_montant=0.0,
                    paye=False
                )
                db.session.add(facturation)
                created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{created_count} facturations créées pour des contestations',
            'count': created_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des facturations manquantes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@tarification_bp.route('/api/contestations/check-facturations', methods=['GET'])
def check_contestations_facturations():
    """Vérifie les facturations de toutes les contestations"""
    try:
        # Récupérer toutes les contestations
        contestations = Donnee.query.filter_by(est_contestation=True).all()
        
        results = []
        for contestation in contestations:
            donnee_enqueteur = DonneeEnqueteur.query.filter_by(donnee_id=contestation.id).first()
            facturation = None
            
            if donnee_enqueteur:
                facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
            
            results.append({
                'id': contestation.id,
                'numeroDossier': contestation.numeroDossier,
                'enquete_originale_id': contestation.enquete_originale_id,
                'enqueteurId': contestation.enqueteurId,
                'code_resultat': donnee_enqueteur.code_resultat if donnee_enqueteur else None,
                'elements_retrouves': donnee_enqueteur.elements_retrouves if donnee_enqueteur else None,
                'has_donnee_enqueteur': donnee_enqueteur is not None,
                'has_facturation': facturation is not None,
                'montant': float(facturation.resultat_enqueteur_montant) if facturation else None
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'data': results
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des facturations: {str(e)}")
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
    
@tarification_bp.route('/api/tarification/stats/global', methods=['GET'])
def get_global_stats():
    """Récupère les statistiques financières globales"""
    try:
        from sqlalchemy import func
        
        # Calcul du total facturé par EOS
        total_eos = db.session.query(func.sum(EnqueteFacturation.resultat_eos_montant)).scalar() or 0
        
        # Calcul du total à payer aux enquêteurs
        total_enqueteurs = db.session.query(func.sum(EnqueteFacturation.resultat_enqueteur_montant)).scalar() or 0
        
        # Nombre d'enquêtes traitées
        enquetes_traitees = db.session.query(func.count(DonneeEnqueteur.id)).filter(
            DonneeEnqueteur.code_resultat.isnot(None)
        ).scalar() or 0
        
        # Nombre d'enquêtes positives
        enquetes_positives = db.session.query(func.count(DonneeEnqueteur.id)).filter(
            DonneeEnqueteur.code_resultat.in_(['P', 'H'])
        ).scalar() or 0
        
        # Calcul de la marge
        marge = float(total_eos) - float(total_enqueteurs)
        pourcentage_marge = (marge / float(total_eos) * 100) if float(total_eos) > 0 else 0
        
        # Dernière date de paiement
        derniere_date = db.session.query(
            func.max(EnqueteFacturation.date_paiement)
        ).filter(
            EnqueteFacturation.paye == True
        ).scalar()
        
        return jsonify({
            'success': True,
            'data': {
                'total_eos': float(total_eos),
                'total_enqueteurs': float(total_enqueteurs),
                'marge': marge,
                'pourcentage_marge': pourcentage_marge,
                'derniere_date_paiement': derniere_date.strftime('%Y-%m-%d') if derniere_date else None,
                'enquetes_traitees': enquetes_traitees,
                'enquetes_positives': enquetes_positives
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques globales: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tarification_bp.route('/api/tarification/enquetes-a-facturer', methods=['GET'])
def get_enquetes_a_facturer():
    """Récupère la liste des enquêtes terminées à facturer"""
    try:
        from models.models import Donnee
        from models.models_enqueteur import DonneeEnqueteur
        from models.enqueteur import Enqueteur
        
        # Requête pour obtenir les enquêtes positives avec leur facturation
        results = db.session.query(
            Donnee, DonneeEnqueteur
        ).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            DonneeEnqueteur.code_resultat.in_(['P', 'H'])
        ).all()
        
        enquetes = []
        
        for donnee, donnee_enqueteur in results:
            # Récupérer la facturation
            facturation = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
            
            # Récupérer l'enquêteur
            enqueteur = Enqueteur.query.filter_by(id=donnee.enqueteurId).first() if donnee.enqueteurId else None
            
            # Si la facturation n'existe pas, la calculer maintenant
            if not facturation:
                facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
            
            # Ajouter à la liste
            enquetes.append({
                'donnee_id': donnee.id,
                'numero_dossier': donnee.numeroDossier,
                'enqueteur': f"{enqueteur.nom} {enqueteur.prenom}" if enqueteur else "Non assigné",
                'elements_retrouves': donnee_enqueteur.elements_retrouves or '-',
                'date_resultat': donnee_enqueteur.updated_at.strftime('%Y-%m-%d') if donnee_enqueteur.updated_at else None,
                'code_resultat': donnee_enqueteur.code_resultat or '-',
                'montant_eos': float(facturation.resultat_eos_montant) if facturation else 0,
                'montant_enqueteur': float(facturation.resultat_enqueteur_montant) if facturation else 0,
                'marge': float(facturation.resultat_eos_montant or 0) - float(facturation.resultat_enqueteur_montant or 0)
            })
        
        return jsonify({
            'success': True,
            'data': enquetes
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des enquêtes à facturer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@tarification_bp.route('/api/contestations/create-missing-facturations', methods=['POST'])
def create_missing_contestation_facturations():
    """Crée des facturations pour toutes les contestations qui n'en ont pas"""
    try:
        # Récupérer toutes les contestations sans facturation
        contestations_sans_facturation = db.session.query(
            Donnee, DonneeEnqueteur
        ).outerjoin(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.est_contestation == True
        ).all()
        
        created_count = 0
        
        for donnee, donnee_enqueteur in contestations_sans_facturation:
            if not donnee_enqueteur:
                # Créer DonneeEnqueteur s'il n'existe pas
                donnee_enqueteur = DonneeEnqueteur(donnee_id=donnee.id)
                db.session.add(donnee_enqueteur)
                db.session.commit()
            
            # Vérifier si une facturation existe déjà
            existing = EnqueteFacturation.query.filter_by(donnee_enqueteur_id=donnee_enqueteur.id).first()
            
            if not existing:
                # Forcer un code résultat s'il n'existe pas
                if not donnee_enqueteur.code_resultat:
                    donnee_enqueteur.code_resultat = 'P'  # Par défaut Positif
                
                if not donnee_enqueteur.elements_retrouves:
                    donnee_enqueteur.elements_retrouves = 'A'  # Par défaut Adresse
                
                # Vérifier et assigner un enquêteur si nécessaire
                if not donnee.enqueteurId:
                    # Essayer d'assigner depuis l'enquête originale
                    if donnee.enquete_originale_id:
                        enquete_originale = Donnee.query.get(donnee.enquete_originale_id)
                        if enquete_originale and enquete_originale.enqueteurId:
                            donnee.enqueteurId = enquete_originale.enqueteurId
                        else:
                            # Assigner le premier enquêteur disponible
                            from models.enqueteur import Enqueteur
                            default_enqueteur = Enqueteur.query.first()
                            if default_enqueteur:
                                donnee.enqueteurId = default_enqueteur.id
                
                db.session.commit()
                
                # Calculer la facturation
                facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
                if facturation:
                    created_count += 1
        
        return jsonify({
            'success': True,
            'message': f'{created_count} facturations créées pour des contestations',
            'count': created_count
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors de la création des facturations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@tarification_bp.route('/api/tarification/calculer-toutes-facturations', methods=['POST'])
def calculer_toutes_facturations():
    """Force le recalcul de toutes les facturations"""
    try:
        # Récupérer toutes les données enquêteur avec résultat positif ou confirmé
        donnees_enqueteur = DonneeEnqueteur.query.filter(
            DonneeEnqueteur.code_resultat.in_(['P', 'H'])
        ).all()
        
        count = 0
        for donnee_enqueteur in donnees_enqueteur:
            facturation = TarificationService.calculate_tarif_for_enquete(donnee_enqueteur.id)
            if facturation:
                count += 1
        
        return jsonify({
            'success': True,
            'message': f'{count} facturations calculées avec succès'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors du calcul des facturations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_tarification_routes(app):
    """Enregistre les routes de tarification"""
    app.register_blueprint(tarification_bp)