"""
Script pour nettoyer les fichiers bloqués et leurs données liées
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from models.models import Fichier, Donnee
from models.models_enqueteur import DonneeEnqueteur
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         Nettoyage des fichiers bloqués et données liées       ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Trouver tous les fichiers
    fichiers = Fichier.query.all()
    
    print(f"📋 {len(fichiers)} fichier(s) trouvé(s)\n")
    
    # Désactiver l'autoflush pour éviter les problèmes de contraintes
    with db.session.no_autoflush:
        for fichier in fichiers:
            print(f"📄 Fichier ID={fichier.id}: {fichier.nom}")
            
            # Compter les données liées
            donnees = Donnee.query.filter_by(fichier_id=fichier.id).all()
            print(f"   → {len(donnees)} donnée(s)")
            
            if len(donnees) > 0:
                # 1. Supprimer d'abord les enquete_facturation liées aux DonneeEnqueteur
                for donnee in donnees:
                    de = DonneeEnqueteur.query.filter_by(donnee_id=donnee.id).first()
                    if de:
                        # Supprimer les facturations liées
                        db.session.execute(text("DELETE FROM enquete_facturation WHERE donnee_enqueteur_id = :de_id"), {"de_id": de.id})
                        print(f"      ✓ Suppression facturations pour donnee_enqueteur_id={de.id}")
                        
                        # Supprimer DonneeEnqueteur
                        db.session.delete(de)
                        print(f"      ✓ Suppression DonneeEnqueteur pour donnee_id={donnee.id}")
                
                # 2. Puis supprimer les Donnee
                for donnee in donnees:
                    db.session.delete(donnee)
                print(f"      ✓ Suppression de {len(donnees)} donnée(s)")
            
            # Enfin supprimer le fichier
            db.session.delete(fichier)
            print(f"   ✅ Fichier supprimé\n")
    
    db.session.commit()
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              ✅ Nettoyage terminé avec succès                 ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    print("Vous pouvez maintenant :")
    print("  1. Réessayer l'import de fichiers")
    print("  2. Les anciens fichiers bloqués ont été supprimés")
    print()

