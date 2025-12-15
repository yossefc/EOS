"""
Script de réinitialisation COMPLÈTE de la configuration multi-client
Crée le client EOS + profil + mappings CORRECTS
"""
import os
import sys

# Définir DATABASE_URL
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import db, create_app
from models.client import Client
from models.import_config import ImportProfile, ImportFieldMapping

def main():
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║    RÉINITIALISATION COMPLÈTE - Client EOS + Mappings          ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # === ÉTAPE 1 : Client EOS ===
            print("ÉTAPE 1 : Client EOS")
            eos_client = Client.query.filter_by(code='EOS').first()
            if not eos_client:
                print("  ➕ Création du client EOS...")
                eos_client = Client(code='EOS', nom='EOS', actif=True)
                db.session.add(eos_client)
                db.session.commit()
                print("    ✅ Client EOS créé")
            else:
                print(f"  ✅ Client EOS existe déjà (ID={eos_client.id})")
            print()
            
            # === ÉTAPE 2 : Profil d'import ===
            print("ÉTAPE 2 : Profil d'import")
            eos_profile = ImportProfile.query.filter_by(
                client_id=eos_client.id, 
                name='EOS - Fichier TXT fixe'
            ).first()
            
            if not eos_profile:
                print("  ➕ Création du profil d'import EOS...")
                eos_profile = ImportProfile(
                    client_id=eos_client.id,
                    name='EOS - Fichier TXT fixe',
                    file_type='TXT_FIXED'
                )
                db.session.add(eos_profile)
                db.session.commit()
                print("    ✅ Profil d'import créé")
            else:
                print(f"  ✅ Profil d'import existe déjà (ID={eos_profile.id})")
            print()
            
            # === ÉTAPE 3 : SUPPRESSION des anciens mappings ===
            print("ÉTAPE 3 : Nettoyage des anciens mappings")
            old_count = ImportFieldMapping.query.filter_by(import_profile_id=eos_profile.id).count()
            if old_count > 0:
                print(f"  🗑️  Suppression de {old_count} anciens mappings...")
                ImportFieldMapping.query.filter_by(import_profile_id=eos_profile.id).delete()
                db.session.commit()
                print("    ✅ Anciens mappings supprimés")
            else:
                print("  ✅ Aucun ancien mapping à supprimer")
            print()
            
            # === ÉTAPE 4 : Création des VRAIS mappings ===
            print("ÉTAPE 4 : Création des VRAIS mappings (depuis utils.py)")
            
            # VRAIS COLUMN_SPECS copiés directement de utils.py
            COLUMN_SPECS = [
                ("numeroDossier", 0, 10),
                ("referenceDossier", 10, 15),
                ("numeroInterlocuteur", 25, 12),
                ("guidInterlocuteur", 37, 36),
                ("typeDemande", 73, 3),
                ("numeroDemande", 76, 11),
                ("numeroDemandeContestee", 87, 11),
                ("numeroDemandeInitiale", 98, 11),
                ("forfaitDemande", 109, 16),
                ("dateRetourEspere", 125, 10),
                ("qualite", 135, 10),
                ("nom", 145, 30),
                ("prenom", 175, 20),
                ("dateNaissance", 195, 10),
                ("lieuNaissance", 205, 50),
                ("codePostalNaissance", 255, 10),
                ("paysNaissance", 265, 32),
                ("nomPatronymique", 297, 30),
                ("adresse1", 327, 32),
                ("adresse2", 359, 32),
                ("adresse3", 391, 32),
                ("adresse4", 423, 32),
                ("ville", 455, 32),
                ("codePostal", 487, 10),
                ("paysResidence", 497, 32),
                ("telephonePersonnel", 529, 15),
                ("telephoneEmployeur", 544, 15),
                ("telecopieEmployeur", 559, 15),
                ("nomEmployeur", 574, 32),
                ("banqueDomiciliation", 606, 32),
                ("libelleGuichet", 638, 30),
                ("titulaireCompte", 668, 32),
                ("codeBanque", 700, 5),
                ("codeGuichet", 705, 5),
                ("numeroCompte", 710, 11),
                ("ribCompte", 721, 2),
                ("datedenvoie", 723, 10),
                ("elementDemandes", 733, 10),
                ("elementObligatoires", 743, 10),
                ("elementContestes", 753, 10),
                ("codeMotif", 763, 16),
                ("motifDeContestation", 779, 64),
                ("cumulMontantsPrecedents", 843, 8),
                ("codeSociete", 851, 2),
                ("urgence", 853, 1),
                ("commentaire", 854, 1000)
            ]
            
            print(f"  ➕ Création de {len(COLUMN_SPECS)} mappings...")
            created = 0
            
            for field_name, start_pos, length in COLUMN_SPECS:
                mapping = ImportFieldMapping(
                    import_profile_id=eos_profile.id,
                    internal_field=field_name,
                    start_pos=start_pos,
                    length=length,
                    strip_whitespace=True
                )
                db.session.add(mapping)
                created += 1
            
            db.session.commit()
            print(f"    ✅ {created} mappings créés avec les positions correctes")
            print()
            
            # === VÉRIFICATION ===
            print("VÉRIFICATION FINALE :")
            examples = ['numeroDossier', 'nom', 'prenom', 'adresse1', 'ville', 'codePostal', 'titulaireCompte']
            
            for field in examples:
                m = ImportFieldMapping.query.filter_by(
                    import_profile_id=eos_profile.id, 
                    internal_field=field
                ).first()
                if m:
                    end_pos = m.start_pos + m.length
                    print(f"  • {m.internal_field:25s} : [{m.start_pos:3d}:{end_pos:3d}] (longueur {m.length:3d})")
            
            print("\n╔════════════════════════════════════════════════════════════════╗")
            print("║          ✅ RÉINITIALISATION TERMINÉE AVEC SUCCÈS              ║")
            print("╚════════════════════════════════════════════════════════════════╝\n")
            
            print("La base de données est maintenant correctement configurée :")
            print(f"  • Client EOS (ID={eos_client.id})")
            print(f"  • Profil d'import (ID={eos_profile.id})")
            print(f"  • {created} mappings de champs avec les VRAIES positions")
            print()
            print("Prochaines étapes :")
            print("  1. Redémarrez le backend (DEMARRER_EOS_POSTGRESQL.bat)")
            print("  2. Testez l'import d'un fichier TXT")
            print()
            
            return 0
            
        except Exception as e:
            print(f"\n❌ ERREUR : {e}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == '__main__':
    sys.exit(main())

