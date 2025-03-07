from datetime import datetime
from extensions import db

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
    """Modèle pour les données"""
    __tablename__ = 'donnees'

    id = db.Column(db.Integer, primary_key=True)
    fichier_id = db.Column(db.Integer, db.ForeignKey('fichiers.id'), nullable=False)
    enqueteurId = db.Column(db.Integer, db.ForeignKey('enqueteurs.id'), nullable=True)
    
    # Relation avec DonneeEnqueteur
    donnee_enqueteur = db.relationship('DonneeEnqueteur', backref='donnee', lazy=True, uselist=False, cascade='all, delete-orphan')
    # Relation avec Enqueteur
    enqueteur = db.relationship('Enqueteur', backref='enquetes', lazy=True)
    
    # Données transmises par EOS FRANCE
    numeroDossier = db.Column(db.String(10))
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
    prenom = db.Column(db.String(20))
    dateNaissance = db.Column(db.Date)
    lieuNaissance = db.Column(db.String(50))
    codePostalNaissance = db.Column(db.String(10))
    paysNaissance = db.Column(db.String(32))
    nomPatronymique = db.Column(db.String(30))
    adresse1 = db.Column(db.String(32))
    adresse2 = db.Column(db.String(32))
    adresse3 = db.Column(db.String(32))
    adresse4 = db.Column(db.String(32))
    ville = db.Column(db.String(32))
    codePostal = db.Column(db.String(10))
    paysResidence = db.Column(db.String(32))
    telephonePersonnel = db.Column(db.String(15))
    telephoneEmployeur = db.Column(db.String(15))
    telecopieEmployeur = db.Column(db.String(15))
    nomEmployeur = db.Column(db.String(32))
    banqueDomiciliation = db.Column(db.String(32))
    libelleGuichet = db.Column(db.String(30))
    titulaireCompte = db.Column(db.String(32))
    codeBanque = db.Column(db.String(5))
    codeGuichet = db.Column(db.String(5))
    numeroCompte = db.Column(db.String(11))
    ribCompte = db.Column(db.String(2))
    datedenvoie = db.Column(db.Date)
    elementDemandes = db.Column(db.String(10))
    elementObligatoires = db.Column(db.String(10))
    elementContestes = db.Column(db.String(10))
    codeMotif = db.Column(db.String(16))
    motifDeContestation = db.Column(db.String(64))
    cumulMontantsPrecedents = db.Column(db.Numeric(8, 2), nullable=True)
    codesociete = db.Column(db.String(2))
    urgence = db.Column(db.String(1))
    commentaire = db.Column(db.String(1000))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'fichier_id': self.fichier_id,
            'enqueteurId': self.enqueteurId,
            'numeroDossier': self.numeroDossier,
            'referenceDossier': self.referenceDossier,
            'numeroInterlocuteur': self.numeroInterlocuteur,
            'guidInterlocuteur': self.guidInterlocuteur,
            'typeDemande': self.typeDemande,
            'numeroDemande': self.numeroDemande,
            'numeroDemandeContestee': self.numeroDemandeContestee,
            'numeroDemandeInitiale': self.numeroDemandeInitiale,
            'forfaitDemande': self.forfaitDemande,
            'dateRetourEspere': self.dateRetourEspere.strftime('%d/%m/%Y') if self.dateRetourEspere else None,
            'qualite': self.qualite,
            'nom': self.nom,
            'prenom': self.prenom,
            'dateNaissance': self.dateNaissance.strftime('%d/%m/%Y') if self.dateNaissance else None,
            'lieuNaissance': self.lieuNaissance,
            'codePostalNaissance': self.codePostalNaissance,
            'paysNaissance': self.paysNaissance,
            'nomPatronymique': self.nomPatronymique,
            'adresse1': self.adresse1,
            'adresse2': self.adresse2,
            'adresse3': self.adresse3,
            'adresse4': self.adresse4,
            'ville': self.ville,
            'codePostal': self.codePostal,
            'paysResidence': self.paysResidence,
            'telephonePersonnel': self.telephonePersonnel,
            'telephoneEmployeur': self.telephoneEmployeur,
            'telecopieEmployeur': self.telecopieEmployeur,
            'nomEmployeur': self.nomEmployeur,
            'banqueDomiciliation': self.banqueDomiciliation,
            'libelleGuichet': self.libelleGuichet,
            'titulaireCompte': self.titulaireCompte,
            'codeBanque': self.codeBanque,
            'codeGuichet': self.codeGuichet,
            'numeroCompte': self.numeroCompte,
            'ribCompte': self.ribCompte,
            'datedenvoie': self.datedenvoie.strftime('%d/%m/%Y') if self.datedenvoie else None,
            'elementDemandes': self.elementDemandes,
            'elementObligatoires': self.elementObligatoires,
            'elementContestes': self.elementContestes,
            'codeMotif': self.codeMotif,
            'motifDeContestation': self.motifDeContestation,
            'cumulMontantsPrecedents': str(self.cumulMontantsPrecedents) if self.cumulMontantsPrecedents else None,
            'codesociete': self.codesociete,
            'urgence': self.urgence,
            'commentaire': self.commentaire,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
