from extensions import db
from datetime import datetime

class DonneeEnqueteur(db.Model):
    """Modèle pour les informations collectées par les enquêteurs"""
    __tablename__ = 'donnees_enqueteur'
    __table_args__ = (
        db.Index('idx_donnee_enqueteur_client_id', 'client_id'),  # MULTI-CLIENT
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)  # MULTI-CLIENT
    donnee_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False)
    
    # Informations de base
    code_resultat = db.Column(db.String(1))  # P, N, H, Z, I, Y
    elements_retrouves = db.Column(db.String(10))  # A, T, B, E, R ou D
    flag_etat_civil_errone = db.Column(db.String(1))  # E ou vide
    date_retour = db.Column(db.Date)
    
    # État civil corrigé (nouveaux champs)
    qualite_corrigee = db.Column(db.String(10))
    nom_corrige = db.Column(db.String(30))
    prenom_corrige = db.Column(db.String(20))
    nom_patronymique_corrige = db.Column(db.String(30))
    code_postal_naissance_corrige = db.Column(db.String(10))
    pays_naissance_corrige = db.Column(db.String(32))
    type_divergence = db.Column(db.String(20))  # Type de divergence d'état civil
    
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
    
    # Notes personnelles
    notes_personnelles = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        result = {
            'id': self.id,
            'donnee_id': self.donnee_id,
            'code_resultat': self.code_resultat,
            'elements_retrouves': self.elements_retrouves,
            'flag_etat_civil_errone': self.flag_etat_civil_errone,
            'date_retour': self.date_retour.strftime('%Y-%m-%d') if self.date_retour else None,
            
            # État civil corrigé
            'qualite_corrigee': self.qualite_corrigee,
            'nom_corrige': self.nom_corrige,
            'prenom_corrige': self.prenom_corrige,
            'nom_patronymique_corrige': self.nom_patronymique_corrige,
            'code_postal_naissance_corrige': self.code_postal_naissance_corrige,
            'pays_naissance_corrige': self.pays_naissance_corrige,
            'type_divergence': self.type_divergence,
            
            # Adresse
            'adresse1': self.adresse1,
            'adresse2': self.adresse2,
            'adresse3': self.adresse3,
            'adresse4': self.adresse4,
            'code_postal': self.code_postal,
            'ville': self.ville,
            'pays_residence': self.pays_residence,
            'telephone_personnel': self.telephone_personnel,
            'telephone_chez_employeur': self.telephone_chez_employeur,
            
            # Employeur
            'nom_employeur': self.nom_employeur,
            'telephone_employeur': self.telephone_employeur,
            'telecopie_employeur': self.telecopie_employeur,
            'adresse1_employeur': self.adresse1_employeur,
            'adresse2_employeur': self.adresse2_employeur,
            'adresse3_employeur': self.adresse3_employeur,
            'adresse4_employeur': self.adresse4_employeur,
            'code_postal_employeur': self.code_postal_employeur,
            'ville_employeur': self.ville_employeur,
            'pays_employeur': self.pays_employeur,
            
            # Informations bancaires
            'banque_domiciliation': self.banque_domiciliation,
            'libelle_guichet': self.libelle_guichet,
            'titulaire_compte': self.titulaire_compte,
            'code_banque': self.code_banque,
            'code_guichet': self.code_guichet,
            
            # Décès
            'date_deces': self.date_deces.strftime('%Y-%m-%d') if self.date_deces else None,
            'numero_acte_deces': self.numero_acte_deces,
            'code_insee_deces': self.code_insee_deces,
            'code_postal_deces': self.code_postal_deces,
            'localite_deces': self.localite_deces,
            
            # Revenus
            'commentaires_revenus': self.commentaires_revenus,
            'montant_salaire': float(self.montant_salaire) if self.montant_salaire else None,
            'periode_versement_salaire': self.periode_versement_salaire,
            'frequence_versement_salaire': self.frequence_versement_salaire,
            
            # Autres revenus
            'nature_revenu1': self.nature_revenu1,
            'montant_revenu1': float(self.montant_revenu1) if self.montant_revenu1 else None,
            'periode_versement_revenu1': self.periode_versement_revenu1,
            'frequence_versement_revenu1': self.frequence_versement_revenu1,
            
            'nature_revenu2': self.nature_revenu2,
            'montant_revenu2': float(self.montant_revenu2) if self.montant_revenu2 else None,
            'periode_versement_revenu2': self.periode_versement_revenu2,
            'frequence_versement_revenu2': self.frequence_versement_revenu2,
            
            'nature_revenu3': self.nature_revenu3,
            'montant_revenu3': float(self.montant_revenu3) if self.montant_revenu3 else None,
            'periode_versement_revenu3': self.periode_versement_revenu3,
            'frequence_versement_revenu3': self.frequence_versement_revenu3,
            
            # Facturation
            'numero_facture': self.numero_facture,
            'date_facture': self.date_facture.strftime('%Y-%m-%d') if self.date_facture else None,
            'montant_facture': float(self.montant_facture) if self.montant_facture else None,
            'tarif_applique': float(self.tarif_applique) if self.tarif_applique else None,
            'cumul_montants_precedents': float(self.cumul_montants_precedents) if self.cumul_montants_precedents else None,
            'reprise_facturation': float(self.reprise_facturation) if self.reprise_facturation else None,
            'remise_eventuelle': float(self.remise_eventuelle) if self.remise_eventuelle else None,
            
            # Mémos
            'memo1': self.memo1,
            'memo2': self.memo2,
            'memo3': self.memo3,
            'memo4': self.memo4,
            'memo5': self.memo5,
            
            # Notes personnelles
            'notes_personnelles': self.notes_personnelles,

            
            
            # Timestamps
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        # Nettoyer les valeurs 'nan'/'None' de pandas
        return {k: (None if isinstance(v, str) and v.strip().lower() in ('nan', 'none') else v) for k, v in result.items()}