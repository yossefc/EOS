"""Script pour vérifier les données Sherlock en base de données"""
import sys
import io
import os

# Forcer UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Importer les modules nécessaires
try:
    from app import create_app
    from models import SherlockDonnee, Fichier
    from extensions import db
    
    print("="*80)
    print("VÉRIFICATION DES DONNÉES SHERLOCK EN BASE DE DONNÉES")
    print("="*80)
    
    # Vérifier la variable d'environnement
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("\n❌ ERREUR: DATABASE_URL n'est pas définie!")
        print("\n📝 SOLUTION:")
        print("   Exécutez d'abord le script START_POSTGRESQL.ps1")
        print("   OU définissez manuellement:")
        print('   $env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"')
        sys.exit(1)
    
    print(f"\n📊 Base de données: {db_url.split('@')[1] if '@' in db_url else 'N/A'}")
    
    # Créer l'application
    app = create_app()
    
    with app.app_context():
        # 1. Compter les enregistrements
        total_count = db.session.query(SherlockDonnee).count()
        print(f"\n1️⃣ NOMBRE D'ENREGISTREMENTS:")
        print(f"   Total SherlockDonnee: {total_count}")
        
        if total_count == 0:
            print("\n❌ AUCUNE DONNÉE EN BASE!")
            print("\n📝 DIAGNOSTIC:")
            print("   → L'IMPORT N'A PAS FONCTIONNÉ")
            print("   → Les données ne sont pas en base de données")
            print("\n💡 SOLUTION:")
            print("   1. Vérifiez que le serveur Flask a été redémarré")
            print("   2. Vérifiez les LOGS pendant l'import pour voir les erreurs")
            print("   3. Réessayez l'import")
            sys.exit(0)
        
        # 2. Lister les fichiers
        print(f"\n2️⃣ FICHIERS IMPORTÉS:")
        fichiers = db.session.query(Fichier).join(
            SherlockDonnee, SherlockDonnee.fichier_id == Fichier.id
        ).distinct().all()
        
        for fichier in fichiers:
            count = db.session.query(SherlockDonnee).filter_by(fichier_id=fichier.id).count()
            print(f"   • Fichier ID {fichier.id}: {fichier.nom}")
            print(f"     Date: {fichier.date_upload}")
            print(f"     Enregistrements: {count}")
        
        # 3. Examiner le premier enregistrement en détail
        print(f"\n3️⃣ PREMIER ENREGISTREMENT (DÉTAILS):")
        first = db.session.query(SherlockDonnee).first()
        
        if not first:
            print("   Aucun enregistrement trouvé")
        else:
            print(f"   ID: {first.id}")
            print(f"   Fichier ID: {first.fichier_id}")
            print(f"   Created at: {first.created_at}")
            print()
            
            # Champs qui posent problème (avec accents)
            champs_problematiques = [
                ('dossier_id', 'DossierId'),
                ('reference_interne', 'RéférenceInterne'),
                ('demande', 'Demande'),
                ('ec_civilite', 'EC-Civilité'),
                ('ec_prenom', 'EC-Prénom'),
                ('ec_prenom2', 'EC-Prénom2'),
                ('ec_prenom3', 'EC-Prénom3'),
                ('ec_prenom4', 'EC-Prénom4'),
                ('ec_nom_usage', 'EC-Nom Usage'),
                ('ec_date_naissance', 'EC-Date Naissance'),
                ('naissance_cp', 'Naissance CP'),
                ('ec_localite_naissance', 'EC-Localité Naissance'),
                ('naissance_insee', 'Naissance INSEE'),
                ('ad_l4_numero', 'AD-L4 Numéro'),
                ('ad_l4_voie', 'AD-L4 Voie'),
                ('ad_l6_cp', 'AD-L6 CP'),
                ('ad_l6_localite', 'AD-L6 Localité'),
                ('ad_l7_pays', 'AD-L7 Pays'),
                ('ad_email', 'AD-Email'),
            ]
            
            print("   📋 VALEURS DES CHAMPS:")
            for field_name, display_name in champs_problematiques:
                value = getattr(first, field_name, None)
                if value is None or value == '' or str(value).lower() == 'nan':
                    status = "❌"
                    display_value = "(VIDE)"
                else:
                    status = "✅"
                    display_value = str(value)[:50]  # Limiter à 50 caractères
                
                print(f"   {status} {display_name:25s}: {display_value}")
        
        # 4. Statistiques sur les champs vides
        print(f"\n4️⃣ STATISTIQUES DES CHAMPS VIDES:")
        
        champs_a_verifier = [
            'reference_interne',
            'ec_civilite',
            'ec_prenom',
            'ec_localite_naissance',
            'ad_l4_numero',
        ]
        
        for field in champs_a_verifier:
            count_vides = db.session.query(SherlockDonnee).filter(
                db.or_(
                    getattr(SherlockDonnee, field) == None,
                    getattr(SherlockDonnee, field) == '',
                    getattr(SherlockDonnee, field) == 'nan'
                )
            ).count()
            
            count_remplis = total_count - count_vides
            pourcentage = (count_remplis / total_count * 100) if total_count > 0 else 0
            
            if count_vides > 0:
                status = "⚠️" if count_vides == total_count else "⚠️"
            else:
                status = "✅"
            
            print(f"   {status} {field:25s}: {count_remplis}/{total_count} remplis ({pourcentage:.1f}%)")
        
        # 5. Diagnostic final
        print(f"\n5️⃣ DIAGNOSTIC:")
        print("="*80)
        
        # Vérifier si les champs problématiques sont vides
        count_ref_vide = db.session.query(SherlockDonnee).filter(
            db.or_(
                SherlockDonnee.reference_interne == None,
                SherlockDonnee.reference_interne == '',
                SherlockDonnee.reference_interne == 'nan'
            )
        ).count()
        
        count_civilite_vide = db.session.query(SherlockDonnee).filter(
            db.or_(
                SherlockDonnee.ec_civilite == None,
                SherlockDonnee.ec_civilite == '',
                SherlockDonnee.ec_civilite == 'nan'
            )
        ).count()
        
        count_prenom_vide = db.session.query(SherlockDonnee).filter(
            db.or_(
                SherlockDonnee.ec_prenom == None,
                SherlockDonnee.ec_prenom == '',
                SherlockDonnee.ec_prenom == 'nan'
            )
        ).count()
        
        if count_ref_vide == total_count and count_civilite_vide == total_count and count_prenom_vide == total_count:
            print("\n❌ PROBLÈME CONFIRMÉ:")
            print("   → Les champs avec accents sont VIDES en base de données")
            print("   → L'IMPORT n'a pas fonctionné correctement")
            print("\n💡 CAUSE PROBABLE:")
            print("   → Le serveur Flask n'a PAS été redémarré après les corrections")
            print("   → L'ancien code (sans normalisation) est toujours en mémoire")
            print("\n🔧 SOLUTION:")
            print("   1. REDÉMARREZ le serveur Flask (Ctrl+C puis python app.py)")
            print("   2. SUPPRIMEZ ce fichier importé")
            print("   3. RÉIMPORTEZ le fichier")
            print("   4. Relancez ce script pour vérifier")
        
        elif count_ref_vide == 0 and count_civilite_vide == 0 and count_prenom_vide == 0:
            print("\n✅ DONNÉES CORRECTES EN BASE:")
            print("   → Tous les champs avec accents sont remplis")
            print("   → L'import a fonctionné correctement")
            print("\n💡 SI L'EXPORT EST VIDE:")
            print("   → Le problème vient de la fonction d'EXPORT")
            print("   → Vérifiez que le serveur Flask a été redémarré")
            print("   → Vérifiez les logs de l'export")
        
        else:
            print("\n⚠️ DONNÉES PARTIELLES:")
            print("   → Certains champs sont remplis, d'autres non")
            print("   → Import partiellement réussi")
            print("\n💡 SOLUTION:")
            print("   → SUPPRIMEZ ce fichier")
            print("   → REDÉMARREZ Flask")
            print("   → RÉIMPORTEZ le fichier")
        
        print("\n" + "="*80)

except ImportError as e:
    print(f"\n❌ ERREUR D'IMPORT: {e}")
    print("\n💡 SOLUTION:")
    print("   Exécutez ce script depuis le dossier backend:")
    print("   cd D:\\EOS\\backend")
    print("   python verifier_donnees_sherlock.py")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
