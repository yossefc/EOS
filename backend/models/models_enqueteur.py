from extensions import db
from datetime import datetime

class DonneeEnqueteur(db.Model):
    """Modèle pour les informations collectées par les enquêteurs"""
    __tablename__ = 'donnees_enqueteur'

    id = db.Column(db.Integer, primary_key=True)
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False)
    
    # Informations de base
    code_resultat = db.Column(db.String(1))  # P, N, H, Z, I, Y
    elements_retrouves = db.Column(db.String(10))  # A, T, B, E, R ou D
    flag_etat_civil_errone = db.Column(db.String(1))  # E ou vide
    date_retour = db.Column(db.Date)
    
    # Informations d'adresse
    adresse1 = db.Column(db.String(32))  # Étage, Appartement, Porte, Chez
    adresse2 = db.Column(db.String(32))  # Bâtiment, Escalier, Résidence
    adresse3 = db.Column(db.String(32))  # Numéro, voie et/ou boîte postale
    adresse4 = db.Column(db.String(32))  # Lieu-dit, Hameau
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(32))
    pays_residence = db.Column(db.String(32))

    # Téléphones
    telephone_personnel = db.Column(db.String(15))
    telephone_chez_employeur = db.Column(db.String(15))
    
    # Informations employeur
    nom_employeur = db.Column(db.String(32))
    telephone_employeur = db.Column(db.String(15))
    telecopie_employeur = db.Column(db.String(15))
    adresse1_employeur = db.Column(db.String(32))
    adresse2_employeur = db.Column(db.String(32))
    adresse3_employeur = db.Column(db.String(32))
    adresse4_employeur = db.Column(db.String(32))
    code_postal_employeur = db.Column(db.String(10))
    ville_employeur = db.Column(db.String(32))
    pays_employeur = db.Column(db.String(32))

    # Informations bancaires
    banque_domiciliation = db.Column(db.String(32))
    libelle_guichet = db.Column(db.String(30))
    titulaire_compte = db.Column(db.String(32))
    code_banque = db.Column(db.String(5))
    code_guichet = db.Column(db.String(5))

    # Informations décès
    date_deces = db.Column(db.Date)
    numero_acte_deces = db.Column(db.String(10))
    code_insee_deces = db.Column(db.String(5))
    code_postal_deces = db.Column(db.String(10))
    localite_deces = db.Column(db.String(32))

    # Informations revenus
    commentaires_revenus = db.Column(db.String(128))
    montant_salaire = db.Column(db.Numeric(10, 2))
    periode_versement_salaire = db.Column(db.Integer)  # -1 ou jour du mois (1-31)
    frequence_versement_salaire = db.Column(db.String(2))  # Q, H, BM, M, T, S, A

    # Autres revenus 1
    nature_revenu1 = db.Column(db.String(30))
    montant_revenu1 = db.Column(db.Numeric(10, 2))
    periode_versement_revenu1 = db.Column(db.Integer)
    frequence_versement_revenu1 = db.Column(db.String(2))

    # Autres revenus 2
    nature_revenu2 = db.Column(db.String(30))
    montant_revenu2 = db.Column(db.Numeric(10, 2))
    periode_versement_revenu2 = db.Column(db.Integer)
    frequence_versement_revenu2 = db.Column(db.String(2))

    # Autres revenus 3
    nature_revenu3 = db.Column(db.String(30))
    montant_revenu3 = db.Column(db.Numeric(10, 2))
    periode_versement_revenu3 = db.Column(db.Integer)
    frequence_versement_revenu3 = db.Column(db.String(2))

    # Informations de facturation
    numero_facture = db.Column(db.String(9))
    date_facture = db.Column(db.Date)
    montant_facture = db.Column(db.Numeric(8, 2))
    tarif_applique = db.Column(db.Numeric(8, 2))
    cumul_montants_precedents = db.Column(db.Numeric(8, 2))
    reprise_facturation = db.Column(db.Numeric(8, 2))
    remise_eventuelle = db.Column(db.Numeric(8, 2))

    # Mémos/Commentaires
    memo1 = db.Column(db.String(64))
    memo2 = db.Column(db.String(64))
    memo3 = db.Column(db.String(64))
    memo4 = db.Column(db.String(64))
    memo5 = db.Column(db.String(1000))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'donnee_id': self.donnee_id,
            'code_resultat': self.code_resultat,
            'elements_retrouves': self.elements_retrouves,
            'adresse': {
                'adresse1': self.adresse1,
                'adresse2': self.adresse2,
                'adresse3': self.adresse3,
                'adresse4': self.adresse4,
                'code_postal': self.code_postal,
                'ville': self.ville,
                'pays': self.pays_residence
            },
            'telephones': {
                'personnel': self.telephone_personnel,
                'chez_employeur': self.telephone_chez_employeur
            },
            'employeur': {
                'nom': self.nom_employeur,
                'telephone': self.telephone_employeur,
                'adresse': {
                    'adresse1': self.adresse1_employeur,
                    'adresse2': self.adresse2_employeur,
                    'adresse3': self.adresse3_employeur,
                    'adresse4': self.adresse4_employeur,
                    'code_postal': self.code_postal_employeur,
                    'ville': self.ville_employeur,
                    'pays': self.pays_employeur
                }
            },
            'banque': {
                'domiciliation': self.banque_domiciliation,
                'guichet': self.libelle_guichet,
                'titulaire': self.titulaire_compte,
                'code_banque': self.code_banque,
                'code_guichet': self.code_guichet
            },
            'deces': {
                'date': self.date_deces.strftime('%Y-%m-%d') if self.date_deces else None,
                'numero_acte': self.numero_acte_deces,
                'code_insee': self.code_insee_deces,
                'code_postal': self.code_postal_deces,
                'localite': self.localite_deces
            },
            'revenus': {
                'salaire': {
                    'montant': float(self.montant_salaire) if self.montant_salaire else None,
                    'periode_versement': self.periode_versement_salaire,
                    'frequence_versement': self.frequence_versement_salaire,
                    'commentaires': self.commentaires_revenus
                },
                'autres_revenus': [
                    {
                        'nature': self.nature_revenu1,
                        'montant': float(self.montant_revenu1) if self.montant_revenu1 else None,
                        'periode_versement': self.periode_versement_revenu1,
                        'frequence_versement': self.frequence_versement_revenu1
                    },
                    {
                        'nature': self.nature_revenu2,
                        'montant': float(self.montant_revenu2) if self.montant_revenu2 else None,
                        'periode_versement': self.periode_versement_revenu2,
                        'frequence_versement': self.frequence_versement_revenu2
                    },
                    {
                        'nature': self.nature_revenu3,
                        'montant': float(self.montant_revenu3) if self.montant_revenu3 else None,
                        'periode_versement': self.periode_versement_revenu3,
                        'frequence_versement': self.frequence_versement_revenu3
                    }
                ]
            },
            'facturation': {
                'numero': self.numero_facture,
                'date': self.date_facture.strftime('%Y-%m-%d') if self.date_facture else None,
                'montant': float(self.montant_facture) if self.montant_facture else None,
                'tarif_applique': float(self.tarif_applique) if self.tarif_applique else None,
                'cumul_precedents': float(self.cumul_montants_precedents) if self.cumul_montants_precedents else None,
                'reprise': float(self.reprise_facturation) if self.reprise_facturation else None,
                'remise': float(self.remise_eventuelle) if self.remise_eventuelle else None
            },
            'memos': {
                'memo1': self.memo1,
                'memo2': self.memo2,
                'memo3': self.memo3,
                'memo4': self.memo4,
                'memo5': self.memo5
            }
        }