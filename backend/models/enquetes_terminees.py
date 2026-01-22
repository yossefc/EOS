from extensions import db
from datetime import datetime

class EnqueteTerminee(db.Model):
    """Modèle pour stocker les enquêtes validées par un directeur"""
    __tablename__ = 'enquetes_terminees'
    
    id = db.Column(db.Integer, primary_key=True)
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False)
    confirmed_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_by = db.Column(db.String(100), nullable=False)
    
    # Relation avec Donnee
    donnee = db.relationship('Donnee', backref=db.backref('validation', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'donnee_id': self.donnee_id,
            'confirmed_at': self.confirmed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'confirmed_by': self.confirmed_by
        }