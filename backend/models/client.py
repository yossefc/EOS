"""
Modèle Client pour gérer plusieurs clients dans l'application
Chaque client peut avoir son propre format d'import de fichier
"""
from datetime import datetime
from extensions import db


class Client(db.Model):
    """Modèle pour les clients (EOS, CLIENT_B, etc.)"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    nom = db.Column(db.String(255), nullable=False)
    actif = db.Column(db.Boolean, default=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now, nullable=False)
    date_modification = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    donnees = db.relationship('Donnee', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    fichiers = db.relationship('Fichier', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    import_profiles = db.relationship('ImportProfile', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertit le client en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'nom': self.nom,
            'actif': self.actif,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S') if self.date_creation else None,
            'date_modification': self.date_modification.strftime('%Y-%m-%d %H:%M:%S') if self.date_modification else None
        }
    
    def __repr__(self):
        return f'<Client {self.code} - {self.nom}>'



