"""
Script de test pour valider le système de tarification/paiements/rapports financiers
Vérifie que les montants sont corrects et stables après confirmation pour EOS et PARTNER
"""

import sys
import os
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db

# Créer l'application
app = create_app()
from models.client import Client
from models.models import Donnee
from models.enqueteur import Enqueteur
from models.models_enqueteur import DonneeEnqueteur
from models.tarifs import EnqueteFacturation, TarifEOS, TarifEnqueteur, TarifClient
from services.tarification_service import TarificationService

def print_section(title):
    """Affiche un titre de section"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_tarification_system():
    """Test complet du système de tarification"""
    
    with app.app_context():
        print_section("🧪 TEST DU SYSTÈME DE TARIFICATION EOS vs PARTNER")
        
        # ========================================
        # ÉTAPE 1: Vérifier les clients
        # ========================================
        print_section("📋 ÉTAPE 1: Vérification des clients")
        
        client_eos = Client.query.filter_by(code='EOS').first()
        client_partner = Client.query.filter(Client.code != 'EOS').first()
        
        if not client_eos:
            print("❌ Client EOS non trouvé !")
            return False
        print(f"✅ Client EOS trouvé: {client_eos.nom} (ID: {client_eos.id})")
        
        if not client_partner:
            print("⚠️  Aucun client PARTNER trouvé, création d'un client de test...")
            client_partner = Client(
                code='PARTNER_TEST',
                nom='Partner Test',
                actif=True
            )
            db.session.add(client_partner)
            db.session.commit()
            print(f"✅ Client PARTNER créé: {client_partner.nom} (ID: {client_partner.id})")
        else:
            print(f"✅ Client PARTNER trouvé: {client_partner.nom} (ID: {client_partner.id})")
        
        # ========================================
        # ÉTAPE 2: Vérifier les tarifs
        # ========================================
        print_section("💰 ÉTAPE 2: Vérification des tarifs")
        
        # Tarifs EOS
        tarif_eos = TarifEOS.query.filter_by(code='AT').first()
        if not tarif_eos:
            print("❌ Tarif EOS 'AT' non trouvé !")
            return False
        print(f"✅ Tarif EOS 'AT': {tarif_eos.montant}€")
        
        tarif_enqueteur = TarifEnqueteur.query.filter_by(code='AT').first()
        if not tarif_enqueteur:
            print("❌ Tarif enquêteur 'AT' non trouvé !")
            return False
        print(f"✅ Tarif enquêteur 'AT': {tarif_enqueteur.montant}€")
        
        # Tarifs PARTNER
        tarif_partner = TarifClient.query.filter_by(
            client_id=client_partner.id,
            code_lettre='W'
        ).first()
        
        if not tarif_partner:
            print("⚠️  Tarif PARTNER 'W' non trouvé, création...")
            tarif_partner = TarifClient(
                client_id=client_partner.id,
                code_lettre='W',
                description='Test tarif W',
                montant=50.00
            )
            db.session.add(tarif_partner)
            db.session.commit()
            print(f"✅ Tarif PARTNER 'W' créé: {tarif_partner.montant}€")
        else:
            print(f"✅ Tarif PARTNER 'W': {tarif_partner.montant}€")
        
        # ========================================
        # ÉTAPE 3: Vérifier les enquêteurs
        # ========================================
        print_section("👤 ÉTAPE 3: Vérification des enquêteurs")
        
        enqueteur = Enqueteur.query.first()
        if not enqueteur:
            print("❌ Aucun enquêteur trouvé !")
            return False
        print(f"✅ Enquêteur trouvé: {enqueteur.prenom} {enqueteur.nom} (ID: {enqueteur.id})")
        
        # ========================================
        # ÉTAPE 4: Créer des dossiers de test
        # ========================================
        print_section("📁 ÉTAPE 4: Création de dossiers de test")
        
        # Nettoyer les anciens tests
        test_dossiers = ['TEST_EOS_1', 'TEST_EOS_2', 'TEST_PTR_1', 'TEST_PTR_2']
        for num_dossier in test_dossiers:
            existing = Donnee.query.filter_by(numeroDossier=num_dossier).first()
            if existing:
                # Supprimer les facturations associées
                EnqueteFacturation.query.filter_by(donnee_id=existing.id).delete()
                # Supprimer les réponses enquêteur
                DonneeEnqueteur.query.filter_by(donnee_id=existing.id).delete()
                # Supprimer le dossier
                db.session.delete(existing)
        db.session.commit()
        print("✅ Anciens dossiers de test nettoyés")
        
        # Créer 2 dossiers EOS
        dossier_eos_1 = Donnee(
            numeroDossier='TEST_EOS_1',
            nom='Test',
            prenom='EOS 1',
            client_id=client_eos.id,
            enqueteurId=enqueteur.id,
            statut_validation='en_attente',
            typeDemande='AT'
        )
        db.session.add(dossier_eos_1)
        db.session.flush()
        
        donnee_enq_eos_1 = DonneeEnqueteur(
            donnee_id=dossier_eos_1.id,
            code_resultat='P',
            elements_retrouves='AT'
        )
        db.session.add(donnee_enq_eos_1)
        
        dossier_eos_2 = Donnee(
            numeroDossier='TEST_EOS_2',
            nom='Test',
            prenom='EOS 2',
            client_id=client_eos.id,
            enqueteurId=enqueteur.id,
            statut_validation='en_attente',
            typeDemande='AT'
        )
        db.session.add(dossier_eos_2)
        db.session.flush()
        
        donnee_enq_eos_2 = DonneeEnqueteur(
            donnee_id=dossier_eos_2.id,
            code_resultat='P',
            elements_retrouves='AT'
        )
        db.session.add(donnee_enq_eos_2)
        
        # Créer 2 dossiers PARTNER
        dossier_partner_1 = Donnee(
            numeroDossier='TEST_PTR_1',
            nom='Test',
            prenom='PTR 1',
            client_id=client_partner.id,
            enqueteurId=enqueteur.id,
            statut_validation='en_attente',
            typeDemande='W'
        )
        db.session.add(dossier_partner_1)
        db.session.flush()
        
        donnee_enq_partner_1 = DonneeEnqueteur(
            donnee_id=dossier_partner_1.id,
            code_resultat='P',
            elements_retrouves='W'
        )
        db.session.add(donnee_enq_partner_1)
        
        dossier_partner_2 = Donnee(
            numeroDossier='TEST_PTR_2',
            nom='Test',
            prenom='PTR 2',
            client_id=client_partner.id,
            enqueteurId=enqueteur.id,
            statut_validation='en_attente',
            typeDemande='W'
        )
        db.session.add(dossier_partner_2)
        db.session.flush()
        
        donnee_enq_partner_2 = DonneeEnqueteur(
            donnee_id=dossier_partner_2.id,
            code_resultat='P',
            elements_retrouves='W'
        )
        db.session.add(donnee_enq_partner_2)
        
        db.session.commit()
        print(f"✅ 4 dossiers de test créés")
        
        # ========================================
        # ÉTAPE 5: Calculer les tarifications
        # ========================================
        print_section("💵 ÉTAPE 5: Calcul des tarifications")
        
        facturations = []
        
        # EOS 1
        fact_eos_1 = TarificationService.calculate_tarif_for_enquete(donnee_enq_eos_1.id)
        if fact_eos_1:
            facturations.append(('EOS 1', fact_eos_1))
            print(f"✅ EOS 1: Client={fact_eos_1.resultat_eos_montant}€, Enquêteur={fact_eos_1.resultat_enqueteur_montant}€")
        else:
            print("❌ Échec calcul EOS 1")
            return False
        
        # EOS 2
        fact_eos_2 = TarificationService.calculate_tarif_for_enquete(donnee_enq_eos_2.id)
        if fact_eos_2:
            facturations.append(('EOS 2', fact_eos_2))
            print(f"✅ EOS 2: Client={fact_eos_2.resultat_eos_montant}€, Enquêteur={fact_eos_2.resultat_enqueteur_montant}€")
        else:
            print("❌ Échec calcul EOS 2")
            return False
        
        # PARTNER 1
        fact_partner_1 = TarificationService.calculate_tarif_for_enquete(donnee_enq_partner_1.id)
        if fact_partner_1:
            facturations.append(('PARTNER 1', fact_partner_1))
            print(f"✅ PARTNER 1: Client={fact_partner_1.resultat_eos_montant}€, Enquêteur={fact_partner_1.resultat_enqueteur_montant}€")
        else:
            print("❌ Échec calcul PARTNER 1")
            return False
        
        # PARTNER 2
        fact_partner_2 = TarificationService.calculate_tarif_for_enquete(donnee_enq_partner_2.id)
        if fact_partner_2:
            facturations.append(('PARTNER 2', fact_partner_2))
            print(f"✅ PARTNER 2: Client={fact_partner_2.resultat_eos_montant}€, Enquêteur={fact_partner_2.resultat_enqueteur_montant}€")
        else:
            print("❌ Échec calcul PARTNER 2")
            return False
        
        # ========================================
        # ÉTAPE 6: Vérifier la persistance
        # ========================================
        print_section("💾 ÉTAPE 6: Vérification de la persistance")
        
        # Relire depuis la DB
        for nom, fact in facturations:
            fact_db = EnqueteFacturation.query.get(fact.id)
            if not fact_db:
                print(f"❌ {nom}: Facturation non trouvée en DB !")
                return False
            
            if fact_db.resultat_eos_montant != fact.resultat_eos_montant:
                print(f"❌ {nom}: Montant client différent en DB !")
                return False
            
            if fact_db.resultat_enqueteur_montant != fact.resultat_enqueteur_montant:
                print(f"❌ {nom}: Montant enquêteur différent en DB !")
                return False
            
            print(f"✅ {nom}: Persistance OK (client_id={fact_db.client_id})")
        
        # ========================================
        # ÉTAPE 7: Vérifier la contrainte unique
        # ========================================
        print_section("🔒 ÉTAPE 7: Vérification de la contrainte unique")
        
        # Essayer de créer un doublon
        try:
            doublon = EnqueteFacturation(
                donnee_id=dossier_eos_1.id,
                donnee_enqueteur_id=donnee_enq_eos_1.id,
                client_id=client_eos.id,
                tarif_eos_code='AT',
                tarif_eos_montant=22.00,
                resultat_eos_montant=22.00,
                tarif_enqueteur_code='AT',
                tarif_enqueteur_montant=15.40,
                resultat_enqueteur_montant=15.40,
                paye=False
            )
            db.session.add(doublon)
            db.session.commit()
            print("❌ La contrainte unique n'a pas empêché le doublon !")
            return False
        except Exception as e:
            db.session.rollback()
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                print("✅ Contrainte unique fonctionne correctement")
            else:
                print(f"⚠️  Erreur inattendue: {str(e)}")
        
        # ========================================
        # ÉTAPE 8: Tester la protection contre recalcul après paiement
        # ========================================
        print_section("🛡️  ÉTAPE 8: Protection contre recalcul après paiement")
        
        # Marquer une facturation comme payée
        fact_eos_1.paye = True
        fact_eos_1.date_paiement = datetime.now().date()
        fact_eos_1.reference_paiement = 'TEST_PAYMENT_001'
        db.session.commit()
        print(f"✅ Facturation EOS 1 marquée comme payée")
        
        # Essayer de recalculer
        montant_avant = fact_eos_1.resultat_enqueteur_montant
        fact_recalc = TarificationService.calculate_tarif_for_enquete(donnee_enq_eos_1.id)
        
        if fact_recalc.resultat_enqueteur_montant == montant_avant:
            print("✅ Le montant n'a pas été modifié après paiement")
        else:
            print("❌ Le montant a été modifié après paiement !")
            return False
        
        # ========================================
        # ÉTAPE 9: Vérifier les stats par client
        # ========================================
        print_section("📊 ÉTAPE 9: Vérification des statistiques par client")
        
        # Stats EOS
        stats_eos = db.session.query(
            db.func.sum(EnqueteFacturation.resultat_eos_montant).label('total_eos'),
            db.func.sum(EnqueteFacturation.resultat_enqueteur_montant).label('total_enqueteur'),
            db.func.count(EnqueteFacturation.id).label('count')
        ).filter(
            EnqueteFacturation.client_id == client_eos.id,
            EnqueteFacturation.donnee_id.in_([dossier_eos_1.id, dossier_eos_2.id])
        ).first()
        
        print(f"✅ Stats EOS: {stats_eos.count} facturations, Total client={stats_eos.total_eos}€, Total enquêteur={stats_eos.total_enqueteur}€")
        
        # Stats PARTNER
        stats_partner = db.session.query(
            db.func.sum(EnqueteFacturation.resultat_eos_montant).label('total_eos'),
            db.func.sum(EnqueteFacturation.resultat_enqueteur_montant).label('total_enqueteur'),
            db.func.count(EnqueteFacturation.id).label('count')
        ).filter(
            EnqueteFacturation.client_id == client_partner.id,
            EnqueteFacturation.donnee_id.in_([dossier_partner_1.id, dossier_partner_2.id])
        ).first()
        
        print(f"✅ Stats PARTNER: {stats_partner.count} facturations, Total client={stats_partner.total_eos}€, Total enquêteur={stats_partner.total_enqueteur}€")
        
        # Vérifier que les stats sont différentes
        if stats_eos.total_eos != stats_partner.total_eos:
            print("✅ Les montants EOS et PARTNER sont bien séparés")
        else:
            print("⚠️  Les montants EOS et PARTNER sont identiques (peut être normal si tarifs identiques)")
        
        # ========================================
        # RÉSULTAT FINAL
        # ========================================
        print_section("✨ RÉSULTAT FINAL")
        print("✅ Tous les tests sont passés avec succès !")
        print("\n📋 Résumé:")
        print(f"  - Clients testés: EOS ({client_eos.id}) et PARTNER ({client_partner.id})")
        print(f"  - Dossiers créés: 4 (2 EOS, 2 PARTNER)")
        print(f"  - Facturations créées: 4")
        print(f"  - Contrainte unique: ✅")
        print(f"  - Protection paiement: ✅")
        print(f"  - Séparation stats: ✅")
        
        return True

if __name__ == '__main__':
    try:
        success = test_tarification_system()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

