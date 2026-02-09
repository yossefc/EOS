"""
Modèles pour la configuration générique d'import de fichiers
Permet de définir dynamiquement comment parser les fichiers selon le client
"""
from datetime import datetime
from extensions import db
import unicodedata


def normalize_column_name(name):
    """Normalise un nom de colonne en enlevant les accents et en mettant en majuscules"""
    if not name:
        return ""
    # Enlever les accents
    name_str = str(name)
    nfd = unicodedata.normalize('NFD', name_str)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    # Mettre en majuscules et enlever espaces superflus
    return without_accents.upper().strip()


class ImportProfile(db.Model):
    """Profil d'import pour un client spécifique"""
    __tablename__ = 'import_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # 'TXT_FIXED', 'EXCEL', etc.
    sheet_name = db.Column(db.String(255), nullable=True)  # Pour Excel
    encoding = db.Column(db.String(50), default='utf-8')  # Encodage du fichier
    actif = db.Column(db.Boolean, default=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now, nullable=False)
    date_modification = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relations
    field_mappings = db.relationship('ImportFieldMapping', backref='import_profile', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convertit le profil en dictionnaire"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'file_type': self.file_type,
            'sheet_name': self.sheet_name,
            'encoding': self.encoding,
            'actif': self.actif,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S') if self.date_creation else None,
            'date_modification': self.date_modification.strftime('%Y-%m-%d %H:%M:%S') if self.date_modification else None,
            'field_mappings_count': self.field_mappings.count()
        }
    
    def __repr__(self):
        return f'<ImportProfile {self.name} - {self.file_type} pour client_id={self.client_id}>'


class ImportFieldMapping(db.Model):
    """Mapping des champs pour un profil d'import"""
    __tablename__ = 'import_field_mappings'
    __table_args__ = (
        db.Index('idx_field_mapping_profile', 'import_profile_id'),
        db.Index('idx_field_mapping_field', 'internal_field'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    import_profile_id = db.Column(db.Integer, db.ForeignKey('import_profiles.id'), nullable=False)
    internal_field = db.Column(db.String(100), nullable=False)  # Nom de l'attribut dans Donnee
    
    # Pour TXT_FIXED
    start_pos = db.Column(db.Integer, nullable=True)  # Position de début (0-indexed)
    length = db.Column(db.Integer, nullable=True)  # Longueur du champ
    
    # Pour EXCEL
    column_name = db.Column(db.String(255), nullable=True)  # Nom de la colonne Excel
    column_index = db.Column(db.Integer, nullable=True)  # Index de la colonne (alternative)
    
    # Transformations optionnelles
    strip_whitespace = db.Column(db.Boolean, default=True)  # Supprimer espaces
    default_value = db.Column(db.String(255), nullable=True)  # Valeur par défaut si vide
    is_required = db.Column(db.Boolean, default=False)  # Champ obligatoire
    
    date_creation = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    def to_dict(self):
        """Convertit le mapping en dictionnaire"""
        return {
            'id': self.id,
            'import_profile_id': self.import_profile_id,
            'internal_field': self.internal_field,
            'start_pos': self.start_pos,
            'length': self.length,
            'column_name': self.column_name,
            'column_index': self.column_index,
            'strip_whitespace': self.strip_whitespace,
            'default_value': self.default_value,
            'is_required': self.is_required,
            'date_creation': self.date_creation.strftime('%Y-%m-%d %H:%M:%S') if self.date_creation else None
        }
    
    def extract_value(self, line_or_row, file_type, col_map=None):
        """
        Extrait la valeur depuis une ligne (TXT) ou une row pandas (EXCEL)
        
        Args:
            line_or_row: str pour TXT_FIXED, pandas.Series pour EXCEL
            file_type: 'TXT_FIXED' ou 'EXCEL'
            col_map: dict pour mapping des colonnes Excel normalisées
            
        Returns:
            La valeur extraite (str)
        """
        value = None
        
        if file_type == 'TXT_FIXED':
            if isinstance(line_or_row, str) and self.start_pos is not None and self.length is not None:
                value = line_or_row[self.start_pos:self.start_pos + self.length]
        
        elif file_type == 'EXCEL':
            if self.column_name:
                # Support des alias séparés par '|'
                aliases = [a.strip() for a in str(self.column_name).split('|')]
                
                target_col = None
                # Essayer chaque alias
                for alias in aliases:
                    if alias in line_or_row:
                        target_col = alias
                        break
                
                # Si aucun alias exact n'est trouvé, essayer via col_map (insensible à la casse et aux accents)
                if not target_col and col_map:
                    for alias in aliases:
                        norm_target = normalize_column_name(alias)
                        real_col_name = col_map.get(norm_target)
                        if real_col_name and real_col_name in line_or_row:
                            target_col = real_col_name
                            break
                
                if target_col:
                    value = line_or_row[target_col]
                
                value = str(value) if value is not None else None
                
            elif self.column_index is not None:
                try:
                    value = str(line_or_row.iloc[self.column_index]) if line_or_row.iloc[self.column_index] is not None else None
                except (KeyError, IndexError):
                    value = None
        
        # Appliquer les transformations
        if value and self.strip_whitespace:
            value = value.strip()
        
        # Valeur par défaut si vide
        if not value and self.default_value:
            value = self.default_value
        
        return value if value else None
    
    def __repr__(self):
        return f'<ImportFieldMapping {self.internal_field} for profile_id={self.import_profile_id}>'






