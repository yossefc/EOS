"""
Modèle pour les exports groupés d'enquêtes
Un export batch contient plusieurs enquêtes exportées ensemble dans un fichier Word
"""
from extensions import db
from datetime import datetime

class ExportBatch(db.Model):
    """
    Table pour tracker les exports groupés d'enquêtes
    Chaque batch correspond à un fichier Word généré contenant plusieurs enquêtes
    """
    __tablename__ = 'export_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)  # Chemin relatif depuis exports/
    file_size = db.Column(db.Integer, nullable=True)  # Taille en octets
    enquete_count = db.Column(db.Integer, nullable=False, default=0)  # Nombre d'enquêtes dans le batch
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utilisateur = db.Column(db.String(100), nullable=True)
    
    # Liste des IDs d'enquêtes (stockée en JSON)
    enquete_ids = db.Column(db.Text, nullable=True)  # Format: "1,2,3,4,5"
    
    def __repr__(self):
        return f'<ExportBatch {self.id} - {self.enquete_count} enquêtes - {self.filename}>'
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'filename': self.filename,
            'filepath': self.filepath,
            'file_size': self.file_size,
            'enquete_count': self.enquete_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'utilisateur': self.utilisateur,
            'enquete_ids': [int(id) for id in self.enquete_ids.split(',') if id] if self.enquete_ids else []
        }
    
    def get_enquete_ids_list(self):
        """Retourne la liste des IDs d'enquêtes"""
        if not self.enquete_ids:
            return []
        return [int(id) for id in self.enquete_ids.split(',') if id]
    
    def set_enquete_ids_list(self, ids_list):
        """Définit la liste des IDs d'enquêtes"""
        self.enquete_ids = ','.join(str(id) for id in ids_list)
        self.enquete_count = len(ids_list)

