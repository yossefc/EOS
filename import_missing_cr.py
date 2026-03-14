# -*- coding: utf-8 -*-
"""
Script pour importer TOUTES les enquetes manquantes depuis les fichiers CR backup
"""
import os
import sys
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:iseeyou@localhost/eos_db')
CR_FOLDER = r"E:\LDMEOS\reponses_cr backup"

def normalize_text(text):
    """Normalise le texte pour comparaison"""
    if pd.isna(text) or text is None:
        return ''
    return str(text).strip().upper()

def convert_date(date_value):
    """Convertit une date en format YYYY-MM-DD"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, str):
        for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
            try:
                return datetime.strptime(date_value, fmt).date()
            except:
                continue
    elif hasattr(date_value, 'date'):
        return date_value.date()
    
    return None

def main():
    print("=== IMPORT DES ENQUETES MANQUANTES ===\n")
    
    # Connexion à la base
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Récupérer l'ID du client PARTNER
    result = session.execute(text("SELECT id FROM clients WHERE code = 'PARTNER'"))
    partner_row = result.fetchone()
    if not partner_row:
        print("❌ Client PARTNER non trouvé")
        return
    
    client_id = partner_row[0]
    print(f"✓ Client PARTNER ID: {client_id}\n")
    
    # 2. Charger tous les numéros de dossier déjà en base
    print("Chargement des enquêtes existantes...")
    result = session.execute(text("""
        SELECT DISTINCT UPPER(TRIM("numeroDossier")) 
        FROM donnees 
        WHERE client_id = :client_id 
        AND est_contestation = false
        AND statut_validation = 'archive'
        AND "numeroDossier" IS NOT NULL
    """), {'client_id': client_id})
    
    dossiers_existants = {row[0] for row in result.fetchall()}
    print(f"✓ {len(dossiers_existants)} enquêtes archivées trouvées\n")
    
    # 3. Parcourir tous les fichiers Excel CR
    print("Analyse des fichiers Excel CR...")
    enquetes_a_importer = []
    fichiers_traites = 0
    
    for filename in sorted(os.listdir(CR_FOLDER)):
        if not (filename.endswith('.xls') or filename.endswith('.xlsx')):
            continue
        
        filepath = os.path.join(CR_FOLDER, filename)
        
        try:
            df = pd.read_excel(filepath)
            
            # Vérifier si c'est un fichier principal (avec colonnes NUM, NOM, etc.)
            if 'NUM' not in df.columns:
                continue
            
            fichiers_traites += 1
            
            for idx, row in df.iterrows():
                num = normalize_text(row.get('NUM', ''))
                
                if not num or num in dossiers_existants:
                    continue
                
                # Cette enquête n'existe pas encore en base
                enquete = {
                    'numeroDossier': str(row['NUM']),
                    'nom': normalize_text(row.get('NOM', '')),
                    'prenom': normalize_text(row.get('PRENOM', '')),
                    'dateNaissance': convert_date(row.get('DATE NAISSANCE')),
                    'lieuNaissance': normalize_text(row.get('LIEU NAISSANCE', '')),
                    'adresse1': str(row.get('ADR1', ''))[:255] if pd.notna(row.get('ADR1')) else None,
                    'adresse2': str(row.get('ADR2', ''))[:255] if pd.notna(row.get('ADR2')) else None,
                    'adresse3': str(row.get('ADR3', ''))[:255] if pd.notna(row.get('ADR3')) else None,
                    'codePostal': str(row.get('CP', ''))[:20] if pd.notna(row.get('CP')) else None,
                    'ville': normalize_text(row.get('VILLE', '')),
                    'paysResidence': normalize_text(row.get('PAYS', 'FRANCE')),
                    'telephonePersonnel': str(row.get('TEL', ''))[:50] if pd.notna(row.get('TEL')) else None,
                    
                    # Type de demande
                    'typeDemande': str(row.get('TD', 'REL'))[:3] if pd.notna(row.get('TD')) else 'REL',
                    'elementDemandes': str(row.get('Elem', 'A'))[:50] if pd.notna(row.get('Elem')) else 'A',
                    
                    # Données enquêteur (résultats)
                    'code_resultat': str(row.get('Resultat', 'POS'))[:10] if pd.notna(row.get('Resultat')) else 'POS',
                    'elements_retrouves': str(row.get('Elem trouvé', ''))[:255] if pd.notna(row.get('Elem trouvé')) else None,
                    'date_retour': convert_date(row.get('Dat retour')),
                    
                    # Employeur
                    'nom_employeur': str(row.get('Employeur', ''))[:255] if pd.notna(row.get('Employeur')) else None,
                    'adresse1_employeur': str(row.get('ADR EMPL1', ''))[:255] if pd.notna(row.get('ADR EMPL1')) else None,
                    'adresse2_employeur': str(row.get('ADR EMPL2', ''))[:255] if pd.notna(row.get('ADR EMPL2')) else None,
                    'adresse3_employeur': str(row.get('ADR EMPL3', ''))[:255] if pd.notna(row.get('ADR EMPL3')) else None,
                    'code_postal_employeur': str(row.get('CP EMPL', ''))[:20] if pd.notna(row.get('CP EMPL')) else None,
                    'ville_employeur': str(row.get('VIL EMPL', ''))[:255] if pd.notna(row.get('VIL EMPL')) else None,
                    'telephone_employeur': str(row.get('TEL EMPL', ''))[:50] if pd.notna(row.get('TEL EMPL')) else None,
                    
                    # Banque
                    'banque_domiciliation': str(row.get('Banque', ''))[:255] if pd.notna(row.get('Banque')) else None,
                    'code_banque': str(row.get('CB', ''))[:20] if pd.notna(row.get('CB')) else None,
                    'code_guichet': str(row.get('CG', ''))[:20] if pd.notna(row.get('CG')) else None,
                    'libelle_guichet': str(row.get('Lib Guichet', ''))[:255] if pd.notna(row.get('Lib Guichet')) else None,
                    'titulaire_compte': str(row.get('Tit. compte', ''))[:255] if pd.notna(row.get('Tit. compte')) else None,
                    
                    # Mémos
                    'memo1': str(row.get('MEMO1', ''))[:1000] if pd.notna(row.get('MEMO1')) else None,
                    'memo2': str(row.get('MEMO2', ''))[:1000] if pd.notna(row.get('MEMO2')) else None,
                    'memo3': str(row.get('MEMO3', ''))[:1000] if pd.notna(row.get('MEMO3')) else None,
                    'memo4': str(row.get('MEMO4', ''))[:1000] if pd.notna(row.get('MEMO4')) else None,
                    'memo5': str(row.get('MEMO5', ''))[:1000] if pd.notna(row.get('MEMO5')) else None,
                    
                    'fichier_source': filename
                }
                
                enquetes_a_importer.append(enquete)
                dossiers_existants.add(num)  # Pour éviter les doublons
            
            if fichiers_traites % 50 == 0:
                print(f"  Traité {fichiers_traites} fichiers... ({len(enquetes_a_importer)} enquêtes à importer)")
        
        except Exception as e:
            print(f"  ⚠ Erreur fichier {filename}: {e}")
            continue
    
    print(f"\n✓ {fichiers_traites} fichiers traités")
    print(f"📊 {len(enquetes_a_importer)} enquêtes à importer\n")
    
    if len(enquetes_a_importer) == 0:
        print("✓ Toutes les enquêtes sont déjà en base !")
        return
    
    # 4. Importer par lots
    print("Début de l'import...")
    batch_size = 100
    imported_count = 0
    errors = []
    
    for i in range(0, len(enquetes_a_importer), batch_size):
        batch = enquetes_a_importer[i:i+batch_size]
        
        try:
            for enq in batch:
                # Insérer l'enquête
                result = session.execute(text("""
                    INSERT INTO donnees (
                        client_id, "numeroDossier", nom, prenom, "dateNaissance", "lieuNaissance",
                        adresse1, adresse2, adresse3, "codePostal", ville, "paysResidence",
                        "telephonePersonnel", "typeDemande", "elementDemandes",
                        est_contestation, statut_validation, "dateCreation"
                    ) VALUES (
                        :client_id, :numeroDossier, :nom, :prenom, :dateNaissance, :lieuNaissance,
                        :adresse1, :adresse2, :adresse3, :codePostal, :ville, :paysResidence,
                        :telephonePersonnel, :typeDemande, :elementDemandes,
                        false, 'archive', NOW()
                    ) RETURNING id
                """), {
                    'client_id': client_id,
                    'numeroDossier': enq['numeroDossier'],
                    'nom': enq['nom'],
                    'prenom': enq['prenom'],
                    'dateNaissance': enq['dateNaissance'],
                    'lieuNaissance': enq['lieuNaissance'],
                    'adresse1': enq['adresse1'],
                    'adresse2': enq['adresse2'],
                    'adresse3': enq['adresse3'],
                    'codePostal': enq['codePostal'],
                    'ville': enq['ville'],
                    'paysResidence': enq['paysResidence'],
                    'telephonePersonnel': enq['telephonePersonnel'],
                    'typeDemande': enq['typeDemande'],
                    'elementDemandes': enq['elementDemandes']
                })
                
                donnee_id = result.fetchone()[0]
                
                # Insérer les données enquêteur
                session.execute(text("""
                    INSERT INTO donnees_enqueteur (
                        donnee_id, code_resultat, elements_retrouves, date_retour,
                        nom_employeur, adresse1_employeur, adresse2_employeur, adresse3_employeur,
                        code_postal_employeur, ville_employeur, telephone_employeur,
                        banque_domiciliation, code_banque, code_guichet, libelle_guichet, titulaire_compte,
                        memo1, memo2, memo3, memo4, memo5
                    ) VALUES (
                        :donnee_id, :code_resultat, :elements_retrouves, :date_retour,
                        :nom_employeur, :adresse1_employeur, :adresse2_employeur, :adresse3_employeur,
                        :code_postal_employeur, :ville_employeur, :telephone_employeur,
                        :banque_domiciliation, :code_banque, :code_guichet, :libelle_guichet, :titulaire_compte,
                        :memo1, :memo2, :memo3, :memo4, :memo5
                    )
                """), {
                    'donnee_id': donnee_id,
                    'code_resultat': enq['code_resultat'],
                    'elements_retrouves': enq['elements_retrouves'],
                    'date_retour': enq['date_retour'],
                    'nom_employeur': enq['nom_employeur'],
                    'adresse1_employeur': enq['adresse1_employeur'],
                    'adresse2_employeur': enq['adresse2_employeur'],
                    'adresse3_employeur': enq['adresse3_employeur'],
                    'code_postal_employeur': enq['code_postal_employeur'],
                    'ville_employeur': enq['ville_employeur'],
                    'telephone_employeur': enq['telephone_employeur'],
                    'banque_domiciliation': enq['banque_domiciliation'],
                    'code_banque': enq['code_banque'],
                    'code_guichet': enq['code_guichet'],
                    'libelle_guichet': enq['libelle_guichet'],
                    'titulaire_compte': enq['titulaire_compte'],
                    'memo1': enq['memo1'],
                    'memo2': enq['memo2'],
                    'memo3': enq['memo3'],
                    'memo4': enq['memo4'],
                    'memo5': enq['memo5']
                })
                
                imported_count += 1
            
            session.commit()
            print(f"  ✓ Lot {i//batch_size + 1}: {len(batch)} enquêtes importées ({imported_count}/{len(enquetes_a_importer)})")
        
        except Exception as e:
            session.rollback()
            error_msg = f"Erreur lot {i//batch_size + 1}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)
    
    print(f"\n{'='*60}")
    print(f"✓ Import terminé !")
    print(f"  - {imported_count} enquêtes importées avec succès")
    print(f"  - {len(errors)} erreurs")
    print(f"{'='*60}\n")
    
    session.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Import interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
