"""
Script de diagnostic pour analyser les enquêtes Partner et comprendre le problème d'export
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur
from models.client import Client

def diagnostic_partner_exports():
    """Analyse les enquêtes Partner validées"""
    
    # Récupérer le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        print("❌ Client PARTNER non trouvé")
        return
    
    print("=" * 80)
    print("DIAGNOSTIC DES EXPORTS PARTNER")
    print("=" * 80)
    print(f"\n✅ Client PARTNER trouvé (ID: {partner.id})\n")
    
    # Récupérer toutes les enquêtes Partner validées non exportées
    enquetes = db.session.query(
        Donnee, DonneeEnqueteur
    ).outerjoin(
        DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
    ).filter(
        Donnee.client_id == partner.id,
        Donnee.statut_validation == 'validee',
        Donnee.exported == False
    ).all()
    
    print(f"📊 Total d'enquêtes validées non exportées: {len(enquetes)}\n")
    
    # Catégoriser
    enquetes_pos = []
    enquetes_neg = []
    contestations_pos = []
    contestations_neg = []
    sans_code = []
    
    for donnee, donnee_enq in enquetes:
        code = donnee_enq.code_resultat if donnee_enq else None
        est_contest = donnee.est_contestation
        
        if not code:
            sans_code.append((donnee, donnee_enq))
            continue
        
        if est_contest:
            if code in ['P', 'H']:
                contestations_pos.append((donnee, donnee_enq))
            elif code in ['N', 'I']:
                contestations_neg.append((donnee, donnee_enq))
        else:
            if code in ['P', 'H']:
                enquetes_pos.append((donnee, donnee_enq))
            elif code in ['N', 'I']:
                enquetes_neg.append((donnee, donnee_enq))
    
    # Afficher les résultats
    print("📈 RÉPARTITION PAR TYPE ET RÉSULTAT:")
    print(f"  • Enquêtes Positives (P, H):      {len(enquetes_pos)}")
    print(f"  • Enquêtes Négatives (N, I):      {len(enquetes_neg)}")
    print(f"  • Contestations Positives (P, H): {len(contestations_pos)}")
    print(f"  • Contestations Négatives (N, I): {len(contestations_neg)}")
    print(f"  • Sans code résultat:             {len(sans_code)}")
    print()
    
    # Détails pour chaque catégorie
    def afficher_details(liste, titre):
        if not liste:
            return
        print(f"\n{'='*80}")
        print(f"{titre} ({len(liste)})")
        print(f"{'='*80}")
        for donnee, donnee_enq in liste[:10]:  # Limiter à 10 premiers
            code = donnee_enq.code_resultat if donnee_enq else "N/A"
            print(f"  Dossier: {donnee.numeroDossier:15} | Nom: {donnee.nom:30} | Code: {code:2} | Contest: {donnee.est_contestation}")
        if len(liste) > 10:
            print(f"  ... et {len(liste) - 10} autres")
    
    afficher_details(enquetes_pos, "ENQUÊTES POSITIVES")
    afficher_details(enquetes_neg, "ENQUÊTES NÉGATIVES")
    afficher_details(contestations_pos, "CONTESTATIONS POSITIVES")
    afficher_details(contestations_neg, "CONTESTATIONS NÉGATIVES")
    afficher_details(sans_code, "SANS CODE RÉSULTAT")
    
    # Vérifier les problèmes potentiels
    print(f"\n{'='*80}")
    print("⚠️  PROBLÈMES POTENTIELS DÉTECTÉS")
    print(f"{'='*80}")
    
    if sans_code:
        print(f"\n❌ {len(sans_code)} enquête(s) validée(s) SANS code résultat !")
        print("   → Ces enquêtes ne seront exportées dans AUCUN fichier")
        print("   → Solution: Ajouter un code résultat (P, H, N, ou I) à ces enquêtes")
    
    # Vérifier les codes incorrects
    codes_incorrects = []
    for donnee, donnee_enq in enquetes:
        if donnee_enq and donnee_enq.code_resultat not in ['P', 'H', 'N', 'I', None]:
            codes_incorrects.append((donnee, donnee_enq))
    
    if codes_incorrects:
        print(f"\n❌ {len(codes_incorrects)} enquête(s) avec code résultat incorrect !")
        for donnee, donnee_enq in codes_incorrects[:5]:
            print(f"   • Dossier {donnee.numeroDossier}: Code = '{donnee_enq.code_resultat}'")
    
    # Vérifier si est_contestation est bien défini
    contestations_sans_flag = []
    for donnee, donnee_enq in enquetes:
        # Si numeroDossier contient "CONT" ou si le nom de fichier contient "CONTESTATION"
        # mais est_contestation = False
        if not donnee.est_contestation:
            if donnee.typeDemande == 'CON' or (donnee.enquete_originale_id is not None):
                contestations_sans_flag.append(donnee)
    
    if contestations_sans_flag:
        print(f"\n⚠️  {len(contestations_sans_flag)} contestation(s) potentielle(s) non marquée(s) !")
        for donnee in contestations_sans_flag[:5]:
            print(f"   • Dossier {donnee.numeroDossier}: typeDemande={donnee.typeDemande}, enquete_originale_id={donnee.enquete_originale_id}")
    
    print(f"\n{'='*80}")
    print("✅ Diagnostic terminé")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        diagnostic_partner_exports()

