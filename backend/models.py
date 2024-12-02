from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Fichier(db.Model):
    __tablename__ = 'fichiers'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    donnees = db.relationship('Donnee', backref='fichier', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'date_upload': self.date_upload.strftime('%Y-%m-%d %H:%M:%S')
        }

class Donnee(db.Model):
    __tablename__ = 'donnees'

    id = db.Column(db.Integer, primary_key=True)
    fichier_id = db.Column(db.Integer, db.ForeignKey('fichiers.id'), nullable=False)
    numeroDossier = db.Column(db.String(10), index=True)
    referenceDossier = db.Column(db.String(15))
    numeroInterlocuteur = db.Column(db.String(12))
    guidInterlocuteur = db.Column(db.String(36))
    typeDemande = db.Column(db.String(3))
    numeroDemande = db.Column(db.String(11))
    numeroDemandeContestee = db.Column(db.String(11))
    numeroDemandeInitiale = db.Column(db.String(11))
    forfaitDemande = db.Column(db.String(16))
    dateRetourEspere = db.Column(db.Date)
    qualite = db.Column(db.String(10))
    nom = db.Column(db.String(30))
    prenom = db.Column(db.String(30))
    dateNaissance = db.Column(db.Date)
    lieuNaissance = db.Column(db.String(50))
    codePostalNaissance = db.Column(db.String(10))
    paysNaissance = db.Column(db.String(32))
    nomPatronymique = db.Column(db.String(30))
    dateRetour = db.Column(db.Date)
    codeResultat = db.Column(db.String(1))
    elementsRetrouves = db.Column(db.String(10))
    flagEtatCivilErrone = db.Column(db.String(1))
    numeroFacture = db.Column(db.String(9))
    dateFacture = db.Column(db.Date)
    montantFacture = db.Column(db.Numeric(8, 2), nullable=True)  # Ajout de nullable=True
    tarifApplique = db.Column(db.Numeric(8, 2), nullable=True)
    cumulMontantsPrecedents = db.Column(db.Numeric(8, 2), nullable=True)
    repriseFacturation = db.Column(db.Numeric(8, 2), nullable=True)
    remiseEventuelle = db.Column(db.Numeric(8, 2), nullable=True)
    dateDeces = db.Column(db.Date)
    numeroActeDeces = db.Column(db.String(10))
    codeInseeDeces = db.Column(db.String(5))
    codePostalDeces = db.Column(db.String(10))
    localiteDeces = db.Column(db.String(32))
    adresse1 = db.Column(db.String(32))
    adresse2 = db.Column(db.String(32))
    adresse3 = db.Column(db.String(32))
    adresse4 = db.Column(db.String(32))
    codePostal = db.Column(db.String(10))
    ville = db.Column(db.String(32))
    paysResidence = db.Column(db.String(32))
    telephonePersonnel = db.Column(db.String(15))
    telephoneEmployeur = db.Column(db.String(15))
    nomEmployeur = db.Column(db.String(32))
    telephoneDeEmployeur = db.Column(db.String(15))
    telecopieEmployeur = db.Column(db.String(15))
    adresse1Employeur = db.Column(db.String(32))
    adresse2Employeur = db.Column(db.String(32))
    adresse3Employeur = db.Column(db.String(32))
    adresse4Employeur = db.Column(db.String(32))
    codePostalEmployeur = db.Column(db.String(10))
    villeEmployeur = db.Column(db.String(32))
    paysEmployeur = db.Column(db.String(32))
    banqueDomiciliation = db.Column(db.String(32))
    libelleGuichet = db.Column(db.String(30))
    titulaireCompte = db.Column(db.String(32))
    codeBanque = db.Column(db.String(5))
    codeGuichet = db.Column(db.String(5))
    numeroCompte = db.Column(db.String(11))
    ribCompte = db.Column(db.String(2))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def safe_numeric_convert(value):
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'fichier_id': self.fichier_id,
            'numeroDossier': self.numeroDossier,
            'referenceDossier': self.referenceDossier,
            'nom': self.nom,
            'prenom': self.prenom,
            'dateNaissance': self.dateNaissance.strftime('%d/%m/%Y') if self.dateNaissance else None,
            'lieuNaissance': self.lieuNaissance,
            'adresse1': self.adresse1,
            'adresse2': self.adresse2,
            'adresse3': self.adresse3,
            'adresse4': self.adresse4,
            'codePostal': self.codePostal,
            'ville': self.ville,
            'telephonePersonnel': self.telephonePersonnel,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }