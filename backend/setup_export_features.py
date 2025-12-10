#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migration pour implémenter les fonctionnalités d'export
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = 'instance/eos.db'

print("=" * 70)
print("CONFIGURATION DES FONCTIONNALITÉS D'EXPORT")
print("=" * 70)
print()

if not os.path.exists(DB_PATH):
    print(f"❌ Base de données introuvable: {DB_PATH}")
    exit(1)

# Créer une sauvegarde
backup_path = f'instance/eos_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
print(f"→ Création sauvegarde: {backup_path}")
shutil.copy2(DB_PATH, backup_path)
print("  ✓ Sauvegarde créée")
print()

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier colonnes actuelles
    cursor.execute("PRAGMA table_info(donnees)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Colonnes actuelles: {len(columns)}")
    print()
    
    # Étape 1: Nettoyer anciennes colonnes si présentes
    old_cols = ['exporte_word', 'date_export_word']
    has_old = any(col in columns for col in old_cols)
    
    if has_old:
        print("⚠️  Nettoyage des anciennes colonnes...")
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
        cursor.execute("DROP TABLE donnees")
        cursor.execute("ALTER TABLE donnees_temp RENAME TO donnees")
        cursor.execute("CREATE INDEX idx_donnee_fichier_id ON donnees(fichier_id)")
        cursor.execute("CREATE INDEX idx_donnee_numeroDossier ON donnees(numeroDossier)")
        cursor.execute("CREATE INDEX idx_donnee_nom ON donnees(nom)")
        cursor.execute("CREATE INDEX idx_donnee_enqueteurId ON donnees(enqueteurId)")
        conn.commit()
        print("  ✓ Anciennes colonnes supprimées")
        print()
    
    # Étape 2: Ajouter les nouvelles colonnes pour l'export
    cursor.execute("PRAGMA table_info(donnees)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'exported' not in columns:
        print("→ Ajout colonne 'exported' (booléen)")
        cursor.execute("ALTER TABLE donnees ADD COLUMN exported BOOLEAN DEFAULT 0 NOT NULL")
        conn.commit()
        print("  ✓ Colonne 'exported' ajoutée")
    else:
        print("  ✓ Colonne 'exported' existe déjà")
    
    if 'exported_at' not in columns:
        print("→ Ajout colonne 'exported_at' (DateTime)")
        cursor.execute("ALTER TABLE donnees ADD COLUMN exported_at DATETIME")
        conn.commit()
        print("  ✓ Colonne 'exported_at' ajoutée")
    else:
        print("  ✓ Colonne 'exported_at' existe déjà")
    
    # Vérification finale
    cursor.execute("PRAGMA table_info(donnees)")
    final_columns = [row[1] for row in cursor.fetchall()]
    
    print()
    print("=" * 70)
    print("✅ CONFIGURATION TERMINÉE")
    print("=" * 70)
    print(f"\nTotal colonnes: {len(final_columns)}")
    print(f"Sauvegarde: {backup_path}")
    print()
    print("Nouvelles colonnes:")
    print("  - exported: Booléen indiquant si l'enquête a été exportée")
    print("  - exported_at: Date/heure du dernier export")
    print()
    print("⚠️  Redémarrez le serveur Flask")
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

