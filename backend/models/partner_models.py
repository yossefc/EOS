"""
Modèles SQLAlchemy pour les fonctionnalités PARTNER
"""
from datetime import datetime
from extensions import db


class PartnerRequestKeyword(db.Model):
    """
    Mots-clés pour parser le champ RECHERCHE (admin editable)
    Permet de détecter les demandes sans séparateurs
    """
    __tablename__ = 'partner_request_keywords'
    __table_args__ = (
        db.Index('idx_partner_keywords_client', 'client_id'),
        db.Index('idx_partner_keywords_code', 'request_code'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    request_code = db.Column(db.String(20), nullable=False)  # ADDRESS|PHONE|EMPLOYER|BANK|BIRTH
    pattern = db.Column(db.String(100), nullable=False)       # ex: "ADRESSE", "EMPLOYEUR"
    is_regex = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=0)               # Ordre de détection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    client = db.relationship('Client', backref='partner_keywords')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'request_code': self.request_code,
            'pattern': self.pattern,
            'is_regex': self.is_regex,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PartnerCaseRequest(db.Model):
    """
    Demandes par dossier (normalisation)
    Stocke les demandes détectées et leur statut POS/NEG
    """
    __tablename__ = 'partner_case_requests'
    __table_args__ = (
        db.UniqueConstraint('donnee_id', 'request_code', name='uq_partner_case_request'),
        db.Index('idx_partner_requests_donnee', 'donnee_id'),
        db.Index('idx_partner_requests_status', 'status'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id', ondelete='CASCADE'), nullable=False)
    request_code = db.Column(db.String(20), nullable=False)  # ADDRESS|PHONE|EMPLOYER|BANK|BIRTH
    requested = db.Column(db.Boolean, default=True)          # Demandé dans RECHERCHE
    found = db.Column(db.Boolean, default=False)             # Trouvé par l'enquêteur
    status = db.Column(db.String(10), nullable=True)         # POS|NEG
    memo = db.Column(db.Text, nullable=True)                 # Explication si NEG
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    donnee = db.relationship('Donnee', backref='partner_requests')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'donnee_id': self.donnee_id,
            'request_code': self.request_code,
            'requested': self.requested,
            'found': self.found,
            'status': self.status,
            'memo': self.memo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PartnerTarifRule(db.Model):
    """
    Tarifs combinés (lettre + demandes)
    Permet de définir des tarifs selon la lettre et la combinaison de demandes
    """
    __tablename__ = 'partner_tarif_rules'
    __table_args__ = (
        db.UniqueConstraint('client_id', 'tarif_lettre', 'request_key', name='uq_partner_tarif_rule'),
        db.Index('idx_partner_tarifs_client', 'client_id', 'tarif_lettre'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False)
    tarif_lettre = db.Column(db.String(5), nullable=False)   # A, B, C, etc.
    request_key = db.Column(db.String(100), nullable=False)  # "ADDRESS" ou "ADDRESS+EMPLOYER"
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    client = db.relationship('Client', backref='partner_tarif_rules')
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'tarif_lettre': self.tarif_lettre,
            'request_key': self.request_key,
            'amount': float(self.amount) if self.amount else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def build_request_key(request_codes):
        """
        Construit une clé de demandes normalisée (triée + jointe)
        
        Args:
            request_codes (list): Liste de codes de demandes
            
        Returns:
            str: Clé normalisée (ex: "ADDRESS+EMPLOYER")
        """
        if not request_codes:
            return ""
        return "+".join(sorted(set(request_codes)))




