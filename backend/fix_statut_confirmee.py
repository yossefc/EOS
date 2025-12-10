"""
Script pour corriger le statut des enquêtes existantes
Passe les enquêtes avec données enquêteur de 'en_attente' à 'confirmee'
"""
from app import create_app
from extensions import db
from models.models import Donnee
from models.models_enqueteur import DonneeEnqueteur

def fix_statut_confirmee():
    """
    Trouve toutes les enquêtes qui ont des données enquêteur complètes
    mais qui sont toujours au statut 'en_attente', et les passe à 'confirmee'
    """
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 Correctif du statut 'confirmee' pour les enquêtes existantes")
        print("=" * 60)
        print()
        
        # Trouver toutes les enquêtes avec données enquêteur mais statut en_attente
        enquetes = db.session.query(Donnee).join(
            DonneeEnqueteur, Donnee.id == DonneeEnqueteur.donnee_id
        ).filter(
            Donnee.statut_validation == 'en_attente',
            DonneeEnqueteur.code_resultat.isnot(None),
            DonneeEnqueteur.code_resultat.in_(['P', 'H', 'N', 'Z', 'I', 'Y'])
        ).all()
        
        count = len(enquetes)
        
        if count == 0:
            print("✅ Aucune enquête à corriger")
            print("   Toutes les enquêtes avec données enquêteur ont déjà le bon statut")
            return True
        
        print(f"📊 Trouvé {count} enquête(s) à corriger :")
        print()
        
        # Afficher la liste
        for enquete in enquetes:
            donnee_enq = DonneeEnqueteur.query.filter_by(donnee_id=enquete.id).first()
            print(f"  • Enquête #{enquete.id} - {enquete.numeroDossier}")
            print(f"    Nom: {enquete.nom} {enquete.prenom}")
            print(f"    Code résultat: {donnee_enq.code_resultat}")
            print(f"    Statut actuel: {enquete.statut_validation}")
            print()
        
        # Demander confirmation
        print("⚠️  Cette opération va changer le statut de ces enquêtes à 'confirmee'")
        print("   Elles deviendront alors validables par l'administrateur")
        print()
        
        confirmation = input("Voulez-vous continuer ? (tapez 'OUI' pour confirmer) : ")
        
        if confirmation.upper() != 'OUI':
            print()
            print("❌ Opération annulée")
            return False
        
        print()
        print("🔄 Mise à jour en cours...")
        print()
        
        # Mettre à jour les statuts
        updated_count = 0
        for enquete in enquetes:
            old_statut = enquete.statut_validation
            enquete.statut_validation = 'confirmee'
            
            # Ajouter à l'historique
            enquete.add_to_history(
                'correction_statut',
                f'Correction automatique du statut: {old_statut} → confirmee (enquête déjà complétée par l\'enquêteur)',
                'Système'
            )
            
            updated_count += 1
            print(f"  ✓ Enquête #{enquete.id}: {old_statut} → confirmee")
        
        # Sauvegarder les changements
        db.session.commit()
        
        print()
        print("=" * 60)
        print(f"✅ Mise à jour terminée avec succès !")
        print(f"   {updated_count} enquête(s) corrigée(s)")
        print("=" * 60)
        print()
        print("📝 Prochaines étapes :")
        print("   1. Ces enquêtes sont maintenant au statut 'confirmee'")
        print("   2. Elles apparaîtront avec le bouton '✓ Valider' dans l'onglet Données")
        print("   3. L'administrateur peut maintenant les valider")
        print()
        
        return True

if __name__ == '__main__':
    try:
        fix_statut_confirmee()
    except Exception as e:
        print()
        print("❌ Erreur lors de l'exécution du script :")
        print(f"   {str(e)}")
        print()
        import traceback
        traceback.print_exc()

