"""
Modèle pour le stockage des fichiers d'archives d'enquêtes
Ce modèle complète EnqueteArchive en ajoutant le stockage physique des fichiers
"""
from extensions import db
from datetime import datetime

class EnqueteArchiveFile(db.Model):
    """
    Table pour stocker les informations des fichiers d'archives générés
    Permet de conserver les fichiers sur disque et de les re-télécharger
    """
    __tablename__ = 'enquete_archive_files'
    
    id = db.Column(db.Integer, primary_key=True)
    enquete_id = db.Column(db.Integer, db.ForeignKey('donnees.id'), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)  # Chemin relatif depuis le dossier exports/
    type_export = db.Column(db.String(20), default='word', nullable=False)  # word, csv, txt
    file_size = db.Column(db.Integer, nullable=True)  # Taille du fichier en octets
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utilisateur = db.Column(db.String(100), nullable=True)
    
    # Relation avec la table Donnee
    enquete = db.relationship('Donnee', backref='archive_file', lazy=True)
    
    def __repr__(self):
        return f'<EnqueteArchiveFile {self.id} - Enquête {self.enquete_id} - {self.filename}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'enquete_id': self.enquete_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'type_export': self.type_export,
            'file_size': self.file_size,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'utilisateur': self.utilisateur
        }
