"""
Script pour corriger les contestations sans numeroDossier
Attribue un numeroDossier basé sur l'ID ou génère un numéro unique
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from extensions import db
from models.models import Donnee

app = create_app()

with app.app_context():
    # Trouver toutes les contestations sans numeroDossier
    contestations_sans_numero = Donnee.query.filter(
        Donnee.est_contestation == True,
        db.or_(
            Donnee.numeroDossier.is_(None),
            Donnee.numeroDossier == ''
        )
    ).all()
    
    print(f"\n{'='*60}")
    print(f"CORRECTION DES CONTESTATIONS SANS numeroDossier")
    print(f"{'='*60}\n")
    print(f"Trouvé {len(contestations_sans_numero)} contestations sans numeroDossier\n")
    
    if not contestations_sans_numero:
        print("✅ Toutes les contestations ont un numeroDossier")
        sys.exit(0)
    
    # Afficher les 5 premières
    for i, c in enumerate(contestations_sans_numero[:5], 1):
        print(f"{i}. ID {c.id}: {c.nom} {c.prenom}")
        print(f"   Type: {c.typeDemande}, Enquête orig: {c.enquete_originale_id}")
    
    if len(contestations_sans_numero) > 5:
        print(f"   ... et {len(contestations_sans_numero) - 5} autres")
    
    print(f"\n{'-'*60}")
    reponse = input("\nVoulez-vous générer des numeroDossier pour ces contestations ? (o/n): ")
    
    if reponse.lower() != 'o':
        print("❌ Opération annulée")
        sys.exit(0)
    
    # Générer des numeroDossier
    print(f"\n{'='*60}")
    print("GÉNÉRATION DES numeroDossier...")
    print(f"{'='*60}\n")
    
    corriges = 0
    for c in contestations_sans_numero:
        # Générer un numeroDossier unique basé sur l'ID
        # Format: CON-{ID}
        nouveau_numero = f"CON-{c.id}"
        
        # Vérifier que ce numéro n'existe pas déjà
        existe = Donnee.query.filter_by(numeroDossier=nouveau_numero).first()
        if existe and existe.id != c.id:
            # Si le numéro existe déjà, ajouter un suffixe
            nouveau_numero = f"CON-{c.id}-{c.client_id}"
        
        c.numeroDossier = nouveau_numero
        corriges += 1
        
        if corriges <= 5:
            print(f"✅ ID {c.id} ({c.nom}): numeroDossier = '{nouveau_numero}'")
    
    if corriges > 5:
        print(f"   ... et {corriges - 5} autres")
    
    # Sauvegarder
    try:
        db.session.commit()
        print(f"\n✅ {corriges} contestations corrigées avec succès!")
        print(f"\n{'='*60}")
        print("VÉRIFICATION POST-CORRECTION")
        print(f"{'='*60}\n")
        
        # Vérifier JACOB VANILLE
        jacob = Donnee.query.filter(
            Donnee.nom.ilike('%JACOB VANILLE%')
        ).filter_by(est_contestation=True).first()
        
        if jacob:
            print(f"JACOB VANILLE (ID {jacob.id}):")
            print(f"  ✅ numeroDossier: {jacob.numeroDossier}")
            print(f"\n  🔗 URL test: http://localhost:5000/api/historique-enquete/{jacob.numeroDossier}")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Erreur lors de la sauvegarde: {e}")
        sys.exit(1)
