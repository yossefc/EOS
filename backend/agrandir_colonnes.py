"""
Script pour agrandir les colonnes qui sont trop courtes dans PostgreSQL
"""
import os
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║      Agrandissement des colonnes trop courtes (PostgreSQL)     ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    # Liste des colonnes à agrandir
    # Format: (nom_colonne, nouvelle_taille)
    colonnes_a_agrandir = [
        # Colonnes de texte courtes -> 255
        ('adresse1', 255),
        ('adresse2', 255),
        ('adresse3', 255),
        ('adresse4', 255),
        ('ville', 255),
        ('codePostal', 255),
        ('paysResidence', 255),
        ('telephonePersonnel', 255),
        ('telephoneEmployeur', 255),
        ('nomEmployeur', 255),
        ('banqueDomiciliation', 255),
        ('libelleGuichet', 255),
        ('titulaireCompte', 255),
        ('codeBanque', 255),
        ('codeGuichet', 255),
        ('numeroCompte', 255),
        ('ribCompte', 255),
        ('nom', 255),
        ('prenom', 255),
        ('nomPrenom', 255),
        ('lieuNaissance', 255),
        ('codePostalNaissance', 255),
        ('paysNaissance', 255),
        ('nomPatronymique', 255),
    ]
    
    print("► Agrandissement des colonnes dans la table 'donnees'...\n")
    
    for colonne, taille in colonnes_a_agrandir:
        try:
            sql = f'ALTER TABLE donnees ALTER COLUMN "{colonne}" TYPE VARCHAR({taille});'
            db.session.execute(text(sql))
            print(f"  ✅ {colonne:30s} → VARCHAR({taille})")
        except Exception as e:
            if "does not exist" in str(e):
                print(f"  ⚠️  {colonne:30s} → colonne inexistante (ignorée)")
            else:
                print(f"  ❌ {colonne:30s} → erreur: {e}")
    
    db.session.commit()
    
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║          ✅ Colonnes agrandies avec succès                    ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    print("Vous pouvez maintenant :")
    print("  1. Redémarrer le backend : DEMARRER_EOS_POSTGRESQL.bat")
    print("  2. Réessayer l'import de fichiers")
    print()

