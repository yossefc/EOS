from datetime import datetime
from extensions import db

class EnqueteTerminee(db.Model):
    """Modèle pour les enquêtes terminées et validées par un directeur"""
    __tablename__ = 'enquetes_terminees'
    
    id = db.Column(db.Integer, primary_key=True)
    originalId = db.Column(db.Integer)  # ID original de l'enquête (pour référence)
    
    # Informations de confirmation
    confirmedBy = db.Column(db.String(100), nullable=False)  # Nom du directeur qui a confirmé
    confirmedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date de confirmation
    
    # Copie des données de l'enquête originale
    numeroDossier = db.Column(db.String(10), index=True)
    referenceDossier = db.Column(db.String(15))
    typeDemande = db.Column(db.String(3))
    nom = db.Column(db.String(30))
    prenom = db.Column(db.String(20))
    dateNaissance = db.Column(db.Date)
    lieuNaissance = db.Column(db.String(50))
    codePostal = db.Column(db.String(10))
    ville = db.Column(db.String(32))
    
    # Timestamp de création dans la table des terminées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'originalId': self.originalId,
            'confirmedBy': self.confirmedBy,
            'confirmedAt': self.confirmedAt.strftime('%Y-%m-%d %H:%M:%S') if self.confirmedAt else None,
            'numeroDossier': self.numeroDossier,
            'referenceDossier': self.referenceDossier,
            'typeDemande': self.typeDemande,
            'nom': self.nom,
            'prenom': self.prenom,
            'dateNaissance': self.dateNaissance.strftime('%d/%m/%Y') if self.dateNaissance else None,
            'lieuNaissance': self.lieuNaissance,
            'codePostal': self.codePostal,
            'ville': self.ville,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }