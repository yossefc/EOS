"""
Script pour ajouter le mapping numeroDemandeContestee pour les fichiers de contestation PARTNER
Ce script ajoute plusieurs variantes possibles de noms de colonnes pour le numéro de demande contestée
"""
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.import_config import ImportProfile, ImportFieldMapping
from models.client import Client
from datetime import datetime

def add_contestation_mapping():
    """Ajoute le mapping numeroDemandeContestee pour PARTNER"""
    
    # Récupérer le client PARTNER
    partner = Client.query.filter_by(code='PARTNER').first()
    if not partner:
        print("❌ Client PARTNER non trouvé")
        return False
    
    # Récupérer le profil d'import PARTNER Excel
    profile = ImportProfile.query.filter_by(
        client_id=partner.id,
        file_type='EXCEL'
    ).first()
    
    if not profile:
        print("❌ Profil d'import PARTNER Excel non trouvé")
        return False
    
    print(f"✅ Profil trouvé: {profile.name} (ID: {profile.id})")
    
    # Noms de colonnes possibles pour numeroDemandeContestee
    column_names = [
        'NUM CONTESTE',
        'NUMERO CONTESTE',
        'NUM ENQUETE CONTESTEE',
        'NUM CONTESTEE',
        'NUMERO ENQUETE CONTESTEE',
        'NUM CONTESTATION',
        'NUMERO CONTESTATION',
        'NUM CONTESTE',
        'NUM CONTESTE',
        'NUM ENQUETE ORIGINALE',
        'NUMERO ENQUETE ORIGINALE'
    ]
    
    # Supprimer les anciens mappings pour numeroDemandeContestee
    existing = ImportFieldMapping.query.filter_by(
        import_profile_id=profile.id,
        internal_field='numeroDemandeContestee'
    ).all()
    
    if existing:
        print(f"⚠️ Suppression de {len(existing)} ancien(s) mapping(s) pour numeroDemandeContestee")
        for m in existing:
            db.session.delete(m)
    
    # Ajouter les nouveaux mappings
    added = 0
    for col_name in column_names:
        # Vérifier si le mapping existe déjà
        existing = ImportFieldMapping.query.filter_by(
            import_profile_id=profile.id,
            internal_field='numeroDemandeContestee',
            column_name=col_name
        ).first()
        
        if not existing:
            mapping = ImportFieldMapping(
                import_profile_id=profile.id,
                internal_field='numeroDemandeContestee',
                column_name=col_name,
                strip_whitespace=True,
                is_required=False,
                date_creation=datetime.now()
            )
            db.session.add(mapping)
            added += 1
            print(f"  ✅ Ajouté: {col_name} → numeroDemandeContestee")
    
    try:
        db.session.commit()
        print(f"\n✅ {added} nouveau(x) mapping(s) ajouté(s) avec succès")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erreur lors de l'ajout des mappings: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Ajout du mapping numeroDemandeContestee pour PARTNER")
    print("=" * 60)
    
    # Créer l'application Flask avec le contexte
    app = create_app()
    
    with app.app_context():
        success = add_contestation_mapping()
    
    if success:
        print("\n✅ Script terminé avec succès")
        sys.exit(0)
    else:
        print("\n❌ Script terminé avec des erreurs")
        sys.exit(1)

