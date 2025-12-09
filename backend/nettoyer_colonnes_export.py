"""
Script pour supprimer les colonnes exporte_word et date_export_word
de la base de données
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = 'instance/eos.db'
BACKUP_PATH = f'instance/eos_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

print("=" * 70)
print("NETTOYAGE DES COLONNES D'EXPORT WORD")
print("=" * 70)
print()

if not os.path.exists(DB_PATH):
    print(f"❌ Base de données introuvable: {DB_PATH}")
    exit(1)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si les colonnes existent
    cursor.execute("PRAGMA table_info(donnees)")
    columns = [row[1] for row in cursor.fetchall()]
    
    has_exporte_word = 'exporte_word' in columns
    has_date_export = 'date_export_word' in columns
    
    if not has_exporte_word and not has_date_export:
        print("✓ Les colonnes n'existent pas dans la base de données.")
        print("  Aucune action nécessaire.")
        conn.close()
        exit(0)
    
    print("⚠️  Colonnes trouvées à supprimer:")
    if has_exporte_word:
        print("  - exporte_word")
    if has_date_export:
        print("  - date_export_word")
    print()
    
    # Créer une sauvegarde
    print(f"→ Création d'une sauvegarde: {BACKUP_PATH}")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print("  ✓ Sauvegarde créée")
    print()
    
    # SQLite ne supporte pas DROP COLUMN directement
    # Il faut recréer la table sans ces colonnes
    print("→ Reconstruction de la table 'donnees' sans les colonnes d'export...")
    
    # Récupérer la structure actuelle
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='donnees'")
    create_sql = cursor.fetchone()[0]
    
    # Créer une nouvelle table temporaire
    cursor.execute("""
        CREATE TABLE donnees_temp AS 
        SELECT 
            id, fichier_id, enqueteurId, enquete_originale_id, est_contestation,
            date_contestation, motif_contestation_code, motif_contestation_detail,
            historique, statut_validation, numeroDossier, referenceDossier,
            numeroInterlocuteur, guidInterlocuteur, typeDemande, numeroDemande,
            numeroDemandeContestee, numeroDemandeInitiale, forfaitDemande,
            dateRetourEspere, qualite, nom, prenom, dateNaissance, lieuNaissance,
            codePostalNaissance, paysNaissance, nomPatronymique, adresse1, adresse2,
            adresse3, adresse4, ville, codePostal, paysResidence, telephonePersonnel,
            telephoneEmployeur, telecopieEmployeur, nomEmployeur, banqueDomiciliation,
            libelleGuichet, titulaireCompte, codeBanque, codeGuichet, numeroCompte,
            ribCompte, datedenvoie, elementDemandes, elementObligatoires,
            elementContestes, codeMotif, motifDeContestation, cumulMontantsPrecedents,
            codesociete, urgence, commentaire, date_butoir, created_at, updated_at
        FROM donnees
    """)
    
    # Supprimer l'ancienne table
    cursor.execute("DROP TABLE donnees")
    
    # Renommer la table temporaire
    cursor.execute("ALTER TABLE donnees_temp RENAME TO donnees")
    
    # Recréer les index
    cursor.execute("CREATE INDEX idx_donnee_fichier_id ON donnees(fichier_id)")
    cursor.execute("CREATE INDEX idx_donnee_numeroDossier ON donnees(numeroDossier)")
    cursor.execute("CREATE INDEX idx_donnee_nom ON donnees(nom)")
    cursor.execute("CREATE INDEX idx_donnee_enqueteurId ON donnees(enqueteurId)")
    
    conn.commit()
    print("  ✓ Table reconstruite avec succès")
    print()
    
    # Vérifier
    cursor.execute("PRAGMA table_info(donnees)")
    new_columns = [row[1] for row in cursor.fetchall()]
    
    if 'exporte_word' not in new_columns and 'date_export_word' not in new_columns:
        print("=" * 70)
        print("✅ NETTOYAGE RÉUSSI!")
        print("=" * 70)
        print()
        print(f"Colonnes dans la table: {len(new_columns)}")
        print(f"Sauvegarde disponible: {BACKUP_PATH}")
        print()
        print("⚠️  REDÉMARREZ le serveur Flask (Ctrl+C puis python app.py)")
    else:
        print("❌ ERREUR: Les colonnes sont toujours présentes")
        exit(1)
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    print()
    if os.path.exists(BACKUP_PATH):
        print(f"💡 Une sauvegarde a été créée: {BACKUP_PATH}")
        print("   Vous pouvez la restaurer en cas de problème")
    exit(1)
