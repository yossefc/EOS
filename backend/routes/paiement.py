from flask import Blueprint, request, jsonify, send_file
from sqlalchemy import func, and_, desc
from models.models_enqueteur import DonneeEnqueteur
from models.models import Donnee
from models.enqueteur import Enqueteur
from models.tarifs import EnqueteFacturation
from extensions import db
from datetime import datetime, timedelta
import logging
import os
import tempfile
from services.pdf_service import generate_paiement_pdf

logger = logging.getLogger(__name__)

paiement_bp = Blueprint('paiement', __name__)

@paiement_bp.route('/api/paiement/enqueteurs-a-payer', methods=['GET'])
def get_enqueteurs_a_payer():
    """Retourne la liste des enquêteurs avec des paiements en attente"""
    try:
        # Requête simplifiée - récupère tous les enquêteurs qui ont des enquêtes
        enqueteurs = Enqueteur.query.join(
            Donnee, Donnee.enqueteurId == Enqueteur.id
        ).distinct().all()
        
        # Préparer la réponse
        enqueteurs_a_payer = []
        for enqueteur in enqueteurs:
            # Calculer le montant total à payer pour cet enquêteur
            facturations = db.session.query(
                EnqueteFacturation
            ).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                Donnee.enqueteurId == enqueteur.id,
                EnqueteFacturation.paye == False
            ).all()
            
            total_montant = sum(float(f.resultat_enqueteur_montant or 0) for f in facturations)
            
            # Ajouter l'enquêteur s'il a des facturations non payées
            if facturations:
                enqueteurs_a_payer.append({
                    'id': enqueteur.id,
                    'nom': enqueteur.nom,
                    'prenom': enqueteur.prenom,
                    'email': enqueteur.email,
                    'nombre_facturations': len(facturations),
                    'montant_total': total_montant
                })
        
        return jsonify({
            'success': True,
            'data': enqueteurs_a_payer
        })
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@paiement_bp.route('/api/paiement/enqueteur/<int:enqueteur_id>/facturations', methods=['GET'])
def get_facturations_enqueteur(enqueteur_id):
    """Retourne les facturations non payées d'un enquêteur spécifique, y compris les contestations en cours"""
    try:
        # Récupérer toutes les facturations non payées pour cet enquêteur
        # Incluant EXPLICITEMENT celles qui n'ont pas de code_resultat (contestations en cours)
        facturations = db.session.query(
            EnqueteFacturation.id,
            Donnee.numeroDossier,
            Donnee.typeDemande,  # Ajout du type de demande pour identifier les contestations
            DonneeEnqueteur.elements_retrouves,
            EnqueteFacturation.resultat_enqueteur_montant,
            EnqueteFacturation.created_at,
            DonneeEnqueteur.code_resultat
        ).join(
            Donnee, EnqueteFacturation.donnee_id == Donnee.id
        ).join(
            DonneeEnqueteur, EnqueteFacturation.donnee_enqueteur_id == DonneeEnqueteur.id
        ).filter(
            Donnee.enqueteurId == enqueteur_id,
            EnqueteFacturation.paye == False
            # On retire la condition sur le montant pour voir toutes les facturations
            # EnqueteFacturation.resultat_enqueteur_montant > 0
        ).order_by(
            EnqueteFacturation.created_at.desc()
        ).all()

        # Convertir le résultat en liste de dictionnaires
        facturations_liste = []
        for id, numeroDossier, typeDemande, elements_retrouves, montant, created_at, code_resultat in facturations:
            # Pour les contestations en cours, ajouter un montant forfaitaire
            if typeDemande == 'CON' and not code_resultat:
                status = "Contestation en cours"
                # On peut définir un montant forfaitaire pour les contestations en cours
                # ou laisser à 0 et l'ajuster visuellement dans le frontend
                montant_affiche = 0
            else:
                status = code_resultat or "En attente"
                montant_affiche = float(montant) if montant else 0
                
            facturations_liste.append({
                'id': id,
                'numeroDossier': numeroDossier,
                'typeDemande': typeDemande,  # Pour identifier les contestations
                'elements_retrouves': elements_retrouves,
                'montant': montant_affiche,
                'date': created_at.strftime('%Y-%m-%d'),
                'code_resultat': code_resultat,
                'status': status
            })

        # Récupérer les informations de l'enquêteur
        enqueteur = db.session.get(Enqueteur, enqueteur_id)
        if not enqueteur:
            return jsonify({
                'success': False,
                'error': f"Enquêteur {enqueteur_id} non trouvé"
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'enqueteur': {
                    'id': enqueteur.id,
                    'nom': enqueteur.nom,
                    'prenom': enqueteur.prenom,
                    'email': enqueteur.email
                },
                'facturations': facturations_liste,
                'montant_total': sum(f['montant'] for f in facturations_liste)
            }
        })

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des facturations pour l'enquêteur {enqueteur_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@paiement_bp.route('/api/paiement/marquer-payes', methods=['POST'])
def marquer_facturations_payees():
    """Marque plusieurs facturations comme payées"""
    try:
        data = request.json
        facturation_ids = data.get('facturation_ids', [])
        reference_paiement = data.get('reference_paiement', '')
        date_paiement = data.get('date_paiement')

        if not facturation_ids:
            return jsonify({
                'success': False,
                'error': "Aucune facturation sélectionnée"
            }), 400

        # Convertir la date de paiement si elle est fournie
        if date_paiement:
            date_paiement = datetime.strptime(date_paiement, '%Y-%m-%d').date()
        else:
            date_paiement = datetime.now().date()

        # Mettre à jour les facturations
        updated = EnqueteFacturation.query.filter(
            EnqueteFacturation.id.in_(facturation_ids),
            EnqueteFacturation.paye == False
        ).update({
            'paye': True,
            'date_paiement': date_paiement,
            'reference_paiement': reference_paiement
        }, synchronize_session=False)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"{updated} facturations marquées comme payées",
            'count': updated
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Erreur lors du marquage des facturations comme payées: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@paiement_bp.route('/api/paiement/historique', methods=['GET'])
def get_historique_paiements():
    """Récupère l'historique des paiements effectués"""
    try:
        # Paramètres de filtrage
        mois = request.args.get('mois', type=int)
        annee = request.args.get('annee', type=int)
        enqueteur_id = request.args.get('enqueteur_id', type=int)

        # Construire la requête de base
        query = db.session.query(
            EnqueteFacturation.reference_paiement,
            EnqueteFacturation.date_paiement,
            func.count(EnqueteFacturation.id).label('nombre_facturations'),
            func.sum(EnqueteFacturation.resultat_enqueteur_montant).label('montant_total'),
            func.min(EnqueteFacturation.created_at).label('periode_debut'),
            func.max(EnqueteFacturation.created_at).label('periode_fin')
        ).filter(
            EnqueteFacturation.paye == True
        )

        # Appliquer les filtres si fournis
        if mois and annee:
            debut_mois = datetime(annee, mois, 1)
            if mois == 12:
                fin_mois = datetime(annee + 1, 1, 1) - timedelta(days=1)
            else:
                fin_mois = datetime(annee, mois + 1, 1) - timedelta(days=1)
            
            query = query.filter(
                EnqueteFacturation.date_paiement >= debut_mois,
                EnqueteFacturation.date_paiement <= fin_mois
            )

        if enqueteur_id:
            query = query.join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                Donnee.enqueteurId == enqueteur_id
            )

        # Grouper par référence de paiement et date
        query = query.group_by(
            EnqueteFacturation.reference_paiement,
            EnqueteFacturation.date_paiement
        ).order_by(
            desc(EnqueteFacturation.date_paiement)
        )

        # Exécuter la requête
        paiements = query.all()

        # Convertir le résultat en liste de dictionnaires
        paiements_liste = []
        for reference, date, nombre, montant, debut, fin in paiements:
            # Si la référence est vide, utiliser "MANUELLE-" + date
            if not reference:
                reference = f"MANUELLE-{date}"
                
            paiements_liste.append({
                'reference': reference,
                'date': date.strftime('%Y-%m-%d'),
                'nombre_facturations': nombre,
                'montant_total': float(montant),
                'periode': {
                    'debut': debut.strftime('%Y-%m-%d'),
                    'fin': fin.strftime('%Y-%m-%d')
                }
            })

        return jsonify({
            'success': True,
            'data': paiements_liste
        })

    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique des paiements: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@paiement_bp.route('/api/paiement/generer-pdf/<int:enqueteur_id>', methods=['GET'])
def generer_pdf_paiement(enqueteur_id):
    """Génère un PDF de relevé de paiement pour un enquêteur"""
    try:
        reference_paiement = request.args.get('reference')
        date_paiement_str = request.args.get('date')
        
        # Vérifier si les paramètres sont fournis
        if not reference_paiement or not date_paiement_str:
            # S'ils ne sont pas fournis, on cherche toutes les facturations non payées
            non_payees = True
            date_paiement = datetime.now().date()
        else:
            # Sinon, on cherche les facturations correspondant aux paramètres
            non_payees = False
            date_paiement = datetime.strptime(date_paiement_str, '%Y-%m-%d').date()
        
        # Récupérer l'enquêteur
        enqueteur = db.session.get(Enqueteur, enqueteur_id)
        if not enqueteur:
            return jsonify({
                'success': False,
                'error': f"Enquêteur {enqueteur_id} non trouvé"
            }), 404
        
        # Récupérer les facturations
        if non_payees:
            # Facturations non payées
            facturations = db.session.query(
                EnqueteFacturation
            ).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                Donnee.enqueteurId == enqueteur_id,
                EnqueteFacturation.paye == False,
                EnqueteFacturation.resultat_enqueteur_montant > 0
            ).all()
            
            if not facturations:
                return jsonify({
                    'success': False,
                    'error': "Aucune facturation non payée trouvée pour cet enquêteur"
                }), 404
        else:
            # Facturations d'un paiement spécifique
            facturations = db.session.query(
                EnqueteFacturation
            ).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                Donnee.enqueteurId == enqueteur_id,
                EnqueteFacturation.paye == True,
                EnqueteFacturation.reference_paiement == reference_paiement,
                EnqueteFacturation.date_paiement == date_paiement
            ).all()
            
            if not facturations:
                return jsonify({
                    'success': False,
                    'error': "Aucune facturation trouvée pour cette référence et cette date"
                }), 404
        
        # Récupérer plus d'informations pour chaque facturation
        facturations_details = []
        montant_total = 0
        
        for facturation in facturations:
            donnee = db.session.get(Donnee, facturation.donnee_id)
            donnee_enqueteur = db.session.get(DonneeEnqueteur, facturation.donnee_enqueteur_id)
            
            facturations_details.append({
                'id': facturation.id,
                'numeroDossier': donnee.numeroDossier,
                'elements_retrouves': donnee_enqueteur.elements_retrouves,
                'code_resultat': donnee_enqueteur.code_resultat,
                'montant': float(facturation.resultat_enqueteur_montant),
                'date_creation': facturation.created_at.strftime('%Y-%m-%d')
            })
            
            montant_total += float(facturation.resultat_enqueteur_montant)
        
        # Générer le PDF
        pdf_path = generate_paiement_pdf(
            enqueteur=enqueteur,
            facturations=facturations_details,
            montant_total=montant_total,
            reference_paiement=reference_paiement if not non_payees else f"RELEVE-{datetime.now().strftime('%Y%m%d')}",
            date_paiement=date_paiement,
            non_payees=non_payees
        )
        
        # Envoyer le fichier
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"paiement_{enqueteur.nom}_{datetime.now().strftime('%Y%m%d')}.pdf",
            # Supprime le fichier après l'envoi (nécessaire si on utilise un fichier temporaire)
            max_age=0
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du PDF de paiement: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@paiement_bp.route('/api/paiement/stats/periodes', methods=['GET'])
def get_stats_periodes():
    """Récupère les statistiques de paiement par période (optionnellement filtrées par client)"""
    try:
        # Paramètres
        nb_mois = request.args.get('mois', 12, type=int)
        client_id = request.args.get('client_id', type=int)  # ✅ AJOUT: Filtre optionnel
        
        if client_id:
            logger.info(f"Stats périodes filtrées pour client_id={client_id}")
        else:
            logger.info("Stats périodes pour TOUS les clients")
        
        # Date de début (mois actuel - nb_mois)
        now = datetime.now()
        date_debut = datetime(now.year, now.month, 1) - timedelta(days=1)
        for _ in range(nb_mois):
            if date_debut.month == 1:
                date_debut = datetime(date_debut.year - 1, 12, 1)
            else:
                date_debut = datetime(date_debut.year, date_debut.month - 1, 1)
        
        # Liste des mois à couvrir
        periodes = []
        current_date = date_debut
        while current_date < now:
            if current_date.month == 12:
                next_month = datetime(current_date.year + 1, 1, 1)
            else:
                next_month = datetime(current_date.year, current_date.month + 1, 1)
            
            periodes.append({
                'annee': current_date.year,
                'mois': current_date.month,
                'debut': current_date,
                'fin': next_month - timedelta(days=1)
            })
            
            current_date = next_month
        
        # Statistiques pour chaque période
        stats = []
        
        for periode in periodes:
            # Base query pour enquêtes traitées
            query_enquetes = db.session.query(func.count(DonneeEnqueteur.id)).join(
                Donnee, DonneeEnqueteur.donnee_id == Donnee.id
            )
            
            # ✅ AJOUT: Filtre client si fourni
            if client_id:
                query_enquetes = query_enquetes.filter(Donnee.client_id == client_id)
            
            nb_enquetes = query_enquetes.filter(
                DonneeEnqueteur.code_resultat.isnot(None),
                Donnee.statut_validation.in_(['confirmee', 'archivee']),
                DonneeEnqueteur.updated_at >= periode['debut'],
                DonneeEnqueteur.updated_at <= periode['fin']
            ).scalar() or 0
            
            # Base query pour facturations
            query_fact = db.session.query(EnqueteFacturation).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                EnqueteFacturation.created_at >= periode['debut'],
                EnqueteFacturation.created_at <= periode['fin'],
                Donnee.statut_validation.in_(['confirmee', 'archivee'])
            )
            
            # ✅ AJOUT: Filtre client si fourni
            if client_id:
                query_fact = query_fact.filter(EnqueteFacturation.client_id == client_id)
            
            montant_facture = query_fact.with_entities(
                func.sum(EnqueteFacturation.resultat_eos_montant)
            ).scalar() or 0
            
            montant_enqueteurs = query_fact.with_entities(
                func.sum(EnqueteFacturation.resultat_enqueteur_montant)
            ).scalar() or 0
            
            # Stats des paiements
            query_paiement = db.session.query(EnqueteFacturation).join(
                Donnee, EnqueteFacturation.donnee_id == Donnee.id
            ).filter(
                EnqueteFacturation.paye == True,
                EnqueteFacturation.date_paiement >= periode['debut'],
                EnqueteFacturation.date_paiement <= periode['fin'],
                Donnee.statut_validation.in_(['confirmee', 'archivee'])
            )
            
            # ✅ AJOUT: Filtre client si fourni
            if client_id:
                query_paiement = query_paiement.filter(EnqueteFacturation.client_id == client_id)
            
            montant_paye = query_paiement.with_entities(
                func.sum(EnqueteFacturation.resultat_enqueteur_montant)
            ).scalar() or 0
            
            stats.append({
                'periode': f"{periode['mois']:02d}/{periode['annee']}",
                'nb_enquetes': nb_enquetes,
                'montant_facture': float(montant_facture),
                'montant_enqueteurs': float(montant_enqueteurs),
                'montant_paye': float(montant_paye),
                'marge': float(montant_facture) - float(montant_enqueteurs)
            })
        
        # Trier les périodes du plus récent au plus ancien
        stats.reverse()
        
        return jsonify({
            'success': True,
            'data': stats,
            'client_id': client_id  # ✅ AJOUT: Indiquer le filtre appliqué
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques par période: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    # backend/routes/paiement.py - Ajoutez cette route

@paiement_bp.route('/api/paiement/debug-facturations', methods=['GET'])
def debug_facturations():
    """API de diagnostic pour vérifier les associations facturations-enquêteurs"""
    try:
        # Récupérer toutes les facturations
        facturations = EnqueteFacturation.query.all()
        
        total = len(facturations)
        with_amount = sum(1 for f in facturations if f.resultat_enqueteur_montant > 0)
        not_paid = sum(1 for f in facturations if not f.paye)
        valid_not_paid = sum(1 for f in facturations if not f.paye and f.resultat_enqueteur_montant > 0)
        
        # Vérifier les associations enquêteur-facturation
        enqueteurs_with_enquetes = db.session.query(
            Donnee.enqueteurId, 
            func.count(EnqueteFacturation.id)
        ).join(
            EnqueteFacturation, 
            Donnee.id == EnqueteFacturation.donnee_id
        ).filter(
            Donnee.enqueteurId.isnot(None),
            EnqueteFacturation.paye == False,
            EnqueteFacturation.resultat_enqueteur_montant > 0
        ).group_by(
            Donnee.enqueteurId
        ).all()
        
        # Échantillon de facturations
        sample_facturations = [{
            'id': f.id,
            'donnee_id': f.donnee_id,
            'montant': float(f.resultat_enqueteur_montant) if f.resultat_enqueteur_montant else 0,
            'paye': f.paye
        } for f in facturations[:4]]

        # Liste des enquêtes sans enquêteur assigné
        no_enqueteur = db.session.query(
            Donnee.id, Donnee.numeroDossier
        ).join(
            EnqueteFacturation,
            Donnee.id == EnqueteFacturation.donnee_id
        ).filter(
            Donnee.enqueteurId.is_(None),
            EnqueteFacturation.resultat_enqueteur_montant > 0
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_facturations': total,
                'with_amount': with_amount,
                'not_paid': not_paid,
                'valid_not_paid': valid_not_paid,
                'enqueteurs_with_enquetes': enqueteurs_with_enquetes,
                'sample_facturations': sample_facturations,
                'enquetes_sans_enqueteur': [{'id': id, 'numero': num} for id, num in no_enqueteur]
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
@paiement_bp.route('/api/paiement/diagnostic', methods=['GET'])
def diagnostic_facturations():
    """Route de diagnostic pour vérifier l'état des facturations"""
    try:
        # Compter le nombre total de facturations
        total_facturations = db.session.query(func.count(EnqueteFacturation.id)).scalar() or 0
        
        # Compter les facturations avec montant > 0
        with_amount = db.session.query(func.count(EnqueteFacturation.id)).filter(
            EnqueteFacturation.resultat_enqueteur_montant > 0
        ).scalar() or 0
        
        # Compter les facturations non payées
        not_paid = db.session.query(func.count(EnqueteFacturation.id)).filter(
            EnqueteFacturation.paye == False
        ).scalar() or 0
        
        # Compter les facturations non payées avec montant > 0
        valid_not_paid = db.session.query(func.count(EnqueteFacturation.id)).filter(
            EnqueteFacturation.paye == False,
            EnqueteFacturation.resultat_enqueteur_montant > 0
        ).scalar() or 0
        
        # Voir les enquêteurs avec des enquêtes
        enqueteurs_with_enquetes = db.session.query(
            Enqueteur.id, Enqueteur.nom, Enqueteur.prenom,
            func.count(Donnee.id).label('count')
        ).join(
            Donnee, Donnee.enqueteurId == Enqueteur.id
        ).group_by(
            Enqueteur.id, Enqueteur.nom, Enqueteur.prenom
        ).all()
        
        # Récupérer quelques facturations pour inspecter
        sample_facturations = EnqueteFacturation.query.limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_facturations': total_facturations,
                'with_amount': with_amount,
                'not_paid': not_paid,
                'valid_not_paid': valid_not_paid,
                'enqueteurs_with_enquetes': [
                    {'id': e[0], 'nom': e[1], 'prenom': e[2], 'count': e[3]}
                    for e in enqueteurs_with_enquetes
                ],
                'sample_facturations': [
                    {
                        'id': f.id,
                        'donnee_id': f.donnee_id,
                        'montant': float(f.resultat_enqueteur_montant) if f.resultat_enqueteur_montant else 0,
                        'paye': f.paye
                    } for f in sample_facturations
                ]
            }
        })
    except Exception as e:
        logger.error(f"Erreur lors du diagnostic: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
def register_paiement_routes(app):
    """Enregistre les routes de paiement"""
    app.register_blueprint(paiement_bp)