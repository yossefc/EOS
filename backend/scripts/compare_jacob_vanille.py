"""Comparer les 2 enquêtes JACOB VANILLE pour voir si ce sont des clients différents"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['DATABASE_URL'] = 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db'

from app import create_app
from models.models import Donnee
from models.client import Client

app = create_app()

with app.app_context():
    # Récupérer les 2 enquêtes
    enquete1 = Donnee.query.get(31420)
    enquete2 = Donnee.query.get(37003)
    
    if not enquete1 or not enquete2:
        print("❌ Enquêtes non trouvées")
        sys.exit(1)
    
    print("=" * 80)
    print("COMPARAISON DES 2 ENQUÊTES JACOB VANILLE")
    print("=" * 80)
    
    # Comparer les clients
    client1 = Client.query.get(enquete1.client_id) if enquete1.client_id else None
    client2 = Client.query.get(enquete2.client_id) if enquete2.client_id else None
    
    print("\n🏢 CLIENT")
    print("-" * 80)
    print(f"Enquête 1 (ID {enquete1.id}):")
    print(f"  client_id: {enquete1.client_id}")
    print(f"  Client: {client1.nom if client1 else 'N/A'} ({client1.code if client1 else 'N/A'})")
    
    print(f"\nEnquête 2 (ID {enquete2.id}):")
    print(f"  client_id: {enquete2.client_id}")
    print(f"  Client: {client2.nom if client2 else 'N/A'} ({client2.code if client2 else 'N/A'})")
    
    if enquete1.client_id == enquete2.client_id:
        print(f"\n✅ MÊME CLIENT: {client1.nom if client1 else 'N/A'}")
    else:
        print(f"\n⚠️ CLIENTS DIFFÉRENTS!")
    
    # Comparer les données personnelles
    print("\n👤 IDENTITÉ")
    print("-" * 80)
    print(f"{'Champ':<30} {'Enquête 1 (31420)':<25} {'Enquête 2 (37003)':<25} {'Match':<10}")
    print("-" * 80)
    
    comparisons = [
        ('Nom', enquete1.nom, enquete2.nom),
        ('Prénom', enquete1.prenom, enquete2.prenom),
        ('Date naissance', str(enquete1.dateNaissance), str(enquete2.dateNaissance)),
        ('Lieu naissance', enquete1.lieuNaissance, enquete2.lieuNaissance),
        ('Nom patronymique', enquete1.nomPatronymique, enquete2.nomPatronymique),
    ]
    
    for field, val1, val2 in comparisons:
        match = "✅" if val1 == val2 else "❌"
        print(f"{field:<30} {str(val1)[:24]:<25} {str(val2)[:24]:<25} {match:<10}")
    
    # Comparer les adresses
    print("\n🏠 ADRESSE")
    print("-" * 80)
    
    adresse_comparisons = [
        ('Adresse1', enquete1.adresse1, enquete2.adresse1),
        ('Adresse2', enquete1.adresse2, enquete2.adresse2),
        ('Ville', enquete1.ville, enquete2.ville),
        ('Code postal', enquete1.codePostal, enquete2.codePostal),
        ('Pays', enquete1.paysResidence, enquete2.paysResidence),
    ]
    
    for field, val1, val2 in adresse_comparisons:
        match = "✅" if val1 == val2 else "❌"
        val1_str = str(val1)[:24] if val1 else "N/A"
        val2_str = str(val2)[:24] if val2 else "N/A"
        print(f"{field:<30} {val1_str:<25} {val2_str:<25} {match:<10}")
    
    # Comparer les données d'enquête
    print("\n📋 DONNÉES D'ENQUÊTE")
    print("-" * 80)
    
    enquete_comparisons = [
        ('Numéro dossier', enquete1.numeroDossier, enquete2.numeroDossier),
        ('Type demande', enquete1.typeDemande, enquete2.typeDemande),
        ('Statut', enquete1.statut_validation, enquete2.statut_validation),
        ('Fichier ID', enquete1.fichier_id, enquete2.fichier_id),
        ('Enquêteur ID', enquete1.enqueteurId, enquete2.enqueteurId),
        ('Date création', str(enquete1.created_at)[:19], str(enquete2.created_at)[:19]),
        ('Date màj', str(enquete1.updated_at)[:19], str(enquete2.updated_at)[:19]),
    ]
    
    for field, val1, val2 in enquete_comparisons:
        match = "✅" if val1 == val2 else "❌"
        print(f"{field:<30} {str(val1)[:24]:<25} {str(val2)[:24]:<25} {match:<10}")
    
    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    same_client = enquete1.client_id == enquete2.client_id
    same_identity = (
        enquete1.nom == enquete2.nom and 
        enquete1.prenom == enquete2.prenom and
        enquete1.dateNaissance == enquete2.dateNaissance
    )
    same_address = (
        enquete1.adresse1 == enquete2.adresse1 and
        enquete1.ville == enquete2.ville and
        enquete1.codePostal == enquete2.codePostal
    )
    
    if same_client and same_identity:
        if same_address:
            print("✅ Même personne, même adresse - Probablement un doublon ou 2 enquêtes successives")
        else:
            print("⚠️ Même personne, adresse différente - Peut-être un déménagement")
    elif same_client and not same_identity:
        print("❌ Clients différents avec homonymes (même nom mais identité différente)")
    else:
        print("❌ Clients totalement différents (clients EOS différents)")
    
    # Recommandation
    print("\n💡 RECOMMANDATION:")
    if same_client and same_identity:
        if enquete2.updated_at > enquete1.updated_at:
            print(f"   → Utiliser l'enquête {enquete2.id} (plus récente: {enquete2.updated_at})")
        else:
            print(f"   → Utiliser l'enquête {enquete1.id} (plus récente: {enquete1.updated_at})")
    else:
        print("   → Demander à l'utilisateur de choisir ou comparer avec les données de la contestation")
