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
    __table_args__ = (
    db.Index('idx_donnee_fichier_id', 'fichier_id'),
    db.Index('idx_donnee_numeroDossier', 'numeroDossier'),
    db.Index('idx_donnee_nom', 'nom'),
    db.Index('idx_donnee_enqueteurId', 'enqueteurId'),
)
    id = db.Column(db.Integer, primary_key=True)
    fichier_id = db.Column(db.Integer, db.ForeignKey('fichiers.id'), nullable=False)
    enqueteurId = db.Column(db.Integer, db.ForeignKey('enqueteurs.id'), nullable=True)
    
    # Relation avec DonneeEnqueteur
    donnee_enqueteur = db.relationship('DonneeEnqueteur', backref='donnee', lazy=True, uselist=False, cascade='all, delete-orphan')
    # Relation avec Enqueteur
    enqueteur = db.relationship('Enqueteur', backref='enquetes', lazy=True)
    enquete_originale_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=True)
    est_contestation = db.Column(db.Boolean, default=False, nullable=False)
    date_contestation = db.Column(db.Date)
    motif_contestation_code = db.Column(db.String(16))
    motif_contestation_detail = db.Column(db.String(255))
    historique = db.Column(db.Text)  # Stocké en JSON
    
    # Champ pour le statut de validation
    statut_validation = db.Column(db.String(20), default='en_attente', nullable=False)
    
    # Relation avec l'enquête originale
    enquete_originale = db.relationship('Donnee', remote_side=[id], 
                                       backref='contestations', 
                                       foreign_keys=[enquete_originale_id])
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
        result = {
            'id': self.id,
            'fichier_id': self.fichier_id,
            'enqueteurId': self.enqueteurId,
            'est_contestation': self.est_contestation,
            'enquete_originale_id': self.enquete_originale_id,
            'date_contestation': self.date_contestation.strftime('%Y-%m-%d') if self.date_contestation else None,
            'motif_contestation_code': self.motif_contestation_code,
            'motif_contestation_detail': self.motif_contestation_detail,
            'enqueteOriginale': None,  # Ce champ sera rempli ci-dessous si applicable
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
            'statut_validation': self.statut_validation,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        if self.est_contestation and self.enquete_originale_id:
            original = Donnee.query.get(self.enquete_originale_id)
            if original:
                # Trouver l'enquêteur si possible
                enqueteur_nom = "Non assigné"
                if original.enqueteurId:
                    from models.enqueteur import Enqueteur
                    enqueteur = Enqueteur.query.get(original.enqueteurId)
                    if enqueteur:
                        enqueteur_nom = f"{enqueteur.nom} {enqueteur.prenom}"
                
                result['enqueteOriginale'] = {
                    'id': original.id,
                    'numeroDossier': original.numeroDossier,
                    'typeDemande': original.typeDemande,
                    'nom': original.nom,
                    'prenom': original.prenom,
                    'enqueteurId': original.enqueteurId,
                    'enqueteurNom': enqueteur_nom  # Ajouter le nom directement
                }

        return result
        # Méthode pour ajouter un événement à l'historique
    def add_to_history(self, event_type, event_details, user=None):
        import json
        history_list = []
        
        # Charger l'historique existant s'il y en a un
        if self.historique:
            try:
                history_list = json.loads(self.historique)
            except:
                history_list = []
        
        # Ajouter le nouvel événement
        history_list.append({
            'date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,  # Ex: 'creation', 'modification', 'contestation'
            'details': event_details,
            'user': user
        })
        
        # Sauvegarder l'historique mis à jour
        self.historique = json.dumps(history_list)
        return history_list
        
    def get_history(self):
        import json
        if not self.historique:
            return []
        try:
            return json.loads(self.historique)
        except:
            return []
