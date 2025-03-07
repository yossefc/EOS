from extensions import db
from datetime import datetime
import os

class Enqueteur(db.Model):
    __tablename__ = 'enqueteurs'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telephone = db.Column(db.String(20))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    vpn_config_generated = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'email': self.email,
            'telephone': self.telephone,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S'),
            'vpn_config_generated': self.vpn_config_generated
        }
    
    def generate_vpn_config(self):
        """Génère le fichier de configuration VPN pour l'enquêteur."""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_dir = os.path.join(base_dir, 'vpn_template')
            output_dir = os.path.join(base_dir, 'vpn_configs')
            
            # Créer le répertoire de sortie s'il n'existe pas
            os.makedirs(output_dir, exist_ok=True)
            
            # Lire le template
            with open(os.path.join(template_dir, 'client_template.ovpn'), 'r') as f:
                config_content = f.read()
            
            # Lire les certificats et clés
            with open(os.path.join(template_dir, 'ca.crt'), 'r') as f:
                ca_cert = f.read()
            with open(os.path.join(template_dir, 'client1.crt'), 'r') as f:
                client_cert = f.read()
            with open(os.path.join(template_dir, 'client1.key'), 'r') as f:
                client_key = f.read()
            with open(os.path.join(template_dir, 'ta.key'), 'r') as f:
                ta_key = f.read()
            
            # Intégrer les certificats dans le fichier de configuration
            config_content = config_content.replace('ca ca.crt', f'<ca>\n{ca_cert}</ca>')
            config_content = config_content.replace('cert client1.crt', f'<cert>\n{client_cert}</cert>')
            config_content = config_content.replace('key client1.key', f'<key>\n{client_key}</key>')
            config_content = config_content.replace('tls-auth ta.key 1', f'<tls-auth>\n{ta_key}</tls-auth>\nkey-direction 1')
            
            # Chemin du fichier de sortie
            output_file = os.path.join(output_dir, f'client{self.id}.ovpn')
            
            # Écrire le fichier de configuration
            with open(output_file, 'w') as f:
                f.write(config_content)
            
            self.vpn_config_generated = True
            return output_file
            
        except Exception as e:
            raise Exception(f"Erreur lors de la génération du fichier VPN: {str(e)}")
    
    @classmethod
    def create_with_vpn(cls, nom, prenom, email, telephone=None):
        """
        Crée un nouvel enquêteur et génère sa configuration VPN.
        
        Args:
            nom (str): Nom de l'enquêteur
            prenom (str): Prénom de l'enquêteur
            email (str): Email de l'enquêteur
            telephone (str, optional): Numéro de téléphone de l'enquêteur
            
        Returns:
            tuple: (enqueteur, config_path) - L'enquêteur créé et le chemin vers sa configuration VPN
        """
        try:
            # Créer l'enquêteur
            enqueteur = cls(
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone
            )
            
            # Ajouter à la base de données
            db.session.add(enqueteur)
            db.session.commit()
            
            # Générer la configuration VPN
            config_path = enqueteur.generate_vpn_config()
            db.session.commit()
            
            return enqueteur, config_path
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Erreur lors de la création de l'enquêteur: {str(e)}")