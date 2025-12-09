import sqlite3

conn = sqlite3.connect('instance/eos.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(donnees)')
cols = [row[1] for row in cursor.fetchall()]

with open('resultat_verification.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total de colonnes: {len(cols)}\n\n")
    
    export_cols = [c for c in cols if 'export' in c.lower()]
    if export_cols:
        f.write("❌ Colonnes 'export' trouvées:\n")
        for col in export_cols:
            f.write(f"  - {col}\n")
        f.write("\n")
        f.write("Ces colonnes doivent être supprimées.\n")
        f.write("Exécutez: python nettoyer_colonnes_export.py\n")
    else:
        f.write("✅ Aucune colonne 'export' trouvée.\n")
        f.write("La base de données est propre.\n")

conn.close()
print("Vérification terminée. Voir resultat_verification.txt")
