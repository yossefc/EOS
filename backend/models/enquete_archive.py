"""
Modèle pour l'archivage des enquêtes exportées
"""
from extensions import db
from datetime import datetime

class EnqueteArchive(db.Model):
    """
    Table pour archiver les enquêtes exportées
    """
    __tablename__ = 'enquete_archives'
    
    id = db.Column(db.Integer, primary_key=True)
    enquete_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False)
    date_export = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nom_fichier = db.Column(db.String(255), nullable=True)
    utilisateur = db.Column(db.String(100), nullable=True)
    
    # Relation avec la table Donnee
    enquete = db.relationship('Donnee', backref='archives', lazy=True)
    
    def __repr__(self):
        return f'<EnqueteArchive {self.id} - Enquête {self.enquete_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'enquete_id': self.enquete_id,
            'date_export': self.date_export.strftime('%Y-%m-%d %H:%M:%S') if self.date_export else None,
            'nom_fichier': self.nom_fichier,
            'utilisateur': self.utilisateur
        }










