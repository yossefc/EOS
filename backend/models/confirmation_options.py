"""
Modèle pour stocker les options de confirmation personnalisées par client
"""
from extensions import db
from datetime import datetime

class ConfirmationOption(db.Model):
    """Options de confirmation personnalisées pour chaque client"""
    __tablename__ = 'confirmation_options'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    option_text = db.Column(db.String(255), nullable=False)
    usage_count = db.Column(db.Integer, default=1)  # Compteur d'utilisation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation
    client = db.relationship('Client', backref='confirmation_options', lazy=True)
    
    # Index unique pour éviter les doublons
    __table_args__ = (
        db.UniqueConstraint('client_id', 'option_text', name='uq_client_option'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'option_text': self.option_text,
            'usage_count': self.usage_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


