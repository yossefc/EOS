# backend/models/tarifs.py

from extensions import db
from datetime import datetime

class TarifEOS(db.Model):
    """Modèle pour les tarifs facturés par EOS France"""
    __tablename__ = 'tarifs_eos'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False, unique=True)  # Ex: 'A', 'AT', 'D', etc.
    description = db.Column(db.String(100))
    montant = db.Column(db.Numeric(8, 2), nullable=False)
    date_debut = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    date_fin = db.Column(db.Date)
    actif = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'montant': float(self.montant) if self.montant else 0,
            'date_debut': self.date_debut.strftime('%Y-%m-%d') if self.date_debut else None,
            'date_fin': self.date_fin.strftime('%Y-%m-%d') if self.date_fin else None,
            'actif': self.actif
        }

class TarifEnqueteur(db.Model):
    """Modèle pour les tarifs payés aux enquêteurs"""
    __tablename__ = 'tarifs_enqueteur'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=False)  # Ex: 'A', 'AT', 'D', etc.
    description = db.Column(db.String(100))
    montant = db.Column(db.Numeric(8, 2), nullable=False)
    enqueteur_id = db.Column(db.Integer, db.ForeignKey('enqueteurs.id'), nullable=True)  # Si NULL, c'est le tarif par défaut
    date_debut = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    date_fin = db.Column(db.Date)
    actif = db.Column(db.Boolean, default=True)
    
    # Relation avec Enqueteur
    enqueteur = db.relationship('Enqueteur', backref='tarifs', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'montant': float(self.montant) if self.montant else 0,
            'enqueteur_id': self.enqueteur_id,
            'enqueteur_nom': f"{self.enqueteur.nom} {self.enqueteur.prenom}" if self.enqueteur else "Tarif par défaut",
            'date_debut': self.date_debut.strftime('%Y-%m-%d') if self.date_debut else None,
            'date_fin': self.date_fin.strftime('%Y-%m-%d') if self.date_fin else None,
            'actif': self.actif
        }

class TarifClient(db.Model):
    """Modèle pour les tarifs spécifiques aux clients (ex: CLIENT_X)"""
    __tablename__ = 'tarifs_client'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    code_lettre = db.Column(db.String(10), nullable=False)  # Ex: 'A', 'B', 'C', etc.
    description = db.Column(db.String(100))
    montant = db.Column(db.Numeric(8, 2), nullable=False)
    date_debut = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    date_fin = db.Column(db.Date)
    actif = db.Column(db.Boolean, default=True)
    
    # Relation avec Client
    client = db.relationship('Client', backref='tarifs_client', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'code_lettre': self.code_lettre,
            'description': self.description,
            'montant': float(self.montant) if self.montant else 0,
            'date_debut': self.date_debut.strftime('%Y-%m-%d') if self.date_debut else None,
            'date_fin': self.date_fin.strftime('%Y-%m-%d') if self.date_fin else None,
            'actif': self.actif
        }

class EnqueteFacturation(db.Model):
    """Modèle pour stocker les informations de facturation par enquête"""
    __tablename__ = 'enquete_facturation'
    
    id = db.Column(db.Integer, primary_key=True)
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False)
    donnee_enqueteur_id = db.Column(db.Integer, db.ForeignKey('donnees_enqueteur.id'), nullable=False)
    
    # Montants EOS France (facturation client)
    tarif_eos_code = db.Column(db.String(10))
    tarif_eos_montant = db.Column(db.Numeric(8, 2))
    resultat_eos_montant = db.Column(db.Numeric(8, 2))  # Montant final après ajustements
    
    # Montants Enquêteur (rémunération)
    tarif_enqueteur_code = db.Column(db.String(10))
    tarif_enqueteur_montant = db.Column(db.Numeric(8, 2))
    resultat_enqueteur_montant = db.Column(db.Numeric(8, 2))  # Montant final après ajustements
    
    # Statut de paiement enquêteur
# Dans la classe EnqueteFacturation, assurez-vous que cette ligne définit explicitement False comme valeur par défaut
    paye = db.Column(db.Boolean, default=False, nullable=False)    
    date_paiement = db.Column(db.Date)
    reference_paiement = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    donnee = db.relationship('Donnee', backref='facturations', lazy=True)
    donnee_enqueteur = db.relationship('DonneeEnqueteur', backref='facturations', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'donnee_id': self.donnee_id,
            'donnee_enqueteur_id': self.donnee_enqueteur_id,
            'tarif_eos_code': self.tarif_eos_code,
            'tarif_eos_montant': float(self.tarif_eos_montant) if self.tarif_eos_montant else 0,
            'resultat_eos_montant': float(self.resultat_eos_montant) if self.resultat_eos_montant else 0,
            'tarif_enqueteur_code': self.tarif_enqueteur_code,
            'tarif_enqueteur_montant': float(self.tarif_enqueteur_montant) if self.tarif_enqueteur_montant else 0,
            'resultat_enqueteur_montant': float(self.resultat_enqueteur_montant) if self.resultat_enqueteur_montant else 0,
            'paye': self.paye,
            'date_paiement': self.date_paiement.strftime('%Y-%m-%d') if self.date_paiement else None,
            'reference_paiement': self.reference_paiement,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }