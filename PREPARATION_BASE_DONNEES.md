# Préparation de la Base de Données pour le Partage

## État Actuel de la Base de Données

### Localisation
- **Fichier principal** : `backend/instance/eos.db`
- **Type** : SQLite (base de données fichier unique)
- **Taille actuelle** : ~278 KB

### Avantages de SQLite pour le partage
✅ **Fichier unique** - Facile à copier et partager
✅ **Pas de serveur requis** - Fonctionne directement
✅ **Cross-platform** - Compatible Windows/Mac/Linux
✅ **Données incluses** - Tout est dans un seul fichier

## Contenu de la Base de Données

### Tables Principales
- `enquetes` - Données des enquêtes saisies
- `enqueteurs` - Comptes et informations des enquêteurs
- `tarifs` - Grilles tarifaires configurées
- `enquetes_terminees` - Archives des enquêtes validées
- `etat_civil` - Données d'état civil
- `enquete_archive` - Historique des enquêtes

### Données de Démonstration
La base contient actuellement :
- Comptes enquêteurs de test
- Exemples d'enquêtes
- Configuration des tarifs
- Données d'état civil de démonstration

## Préparation pour le Partage

### Option 1 : Partage avec Données Complètes
**Avantages :**
- Le système fonctionne immédiatement
- Exemples pour comprendre le fonctionnement
- Pas de configuration supplémentaire

**Fichiers à inclure :**
- `backend/instance/eos.db` (base complète)

### Option 2 : Base Vierge + Script d'Initialisation
**Avantages :**
- Démarrage propre
- Pas de données de test
- Plus petit fichier

**Créer une base vierge :**
```bash
cd backend
python init_db.py
```

### Recommandation : Les Deux Options

## Instructions de Sauvegarde

### Avant Partage
1. **Arrêter le serveur** pour éviter corruption
2. **Copier la base** : `cp backend/instance/eos.db backup/eos_backup.db`
3. **Vérifier l'intégrité** : Tester l'ouverture de la base

### Script de Sauvegarde
```bash
# Windows
copy "backend\instance\eos.db" "backup\eos_backup_%date%.db"

# Linux/Mac
cp backend/instance/eos.db backup/eos_backup_$(date +%Y%m%d).db
```

## Restauration et Migration

### Pour le Destinataire
1. **Placer le fichier** dans `backend/instance/eos.db`
2. **Vérifier les permissions** de lecture/écriture
3. **Démarrer le serveur** normalement

### En cas de Problème
```bash
cd backend
python reset_db.py  # Recrée une base vierge
python init_db.py   # Initialise avec données de base
```

## Sécurité des Données

### Informations Sensibles
- ⚠️ **Mots de passe** : Stockés en hash (sécurisé)
- ⚠️ **Données personnelles** : Selon contenu des enquêtes
- ⚠️ **Données financières** : Tarifs et calculs de paiement

### Recommandations
1. **Anonymiser si nécessaire** avant partage
2. **Changer les mots de passe** par défaut après installation
3. **Vérifier le contenu** des enquêtes partagées

## Scripts de Migration

### Anonymisation (si requise)
```python
# Script d'anonymisation des données sensibles
import sqlite3

def anonymiser_donnees():
    conn = sqlite3.connect('backend/instance/eos.db')
    cursor = conn.cursor()
    
    # Anonymiser les noms dans les enquêtes
    cursor.execute("UPDATE enquetes SET nom_famille = 'FAMILLE_' || id")
    cursor.execute("UPDATE enquetes SET nom_individu = 'INDIVIDU_' || id")
    
    # Réinitialiser les mots de passe
    cursor.execute("UPDATE enqueteurs SET mot_de_passe = 'temp123'")
    
    conn.commit()
    conn.close()
```

## Vérification Post-Installation

### Tests à Effectuer
1. **Connexion admin** : Vérifier l'accès administrateur
2. **Connexion enquêteur** : Tester un compte enquêteur
3. **Création enquête** : Saisir une enquête test
4. **Export** : Tester les fonctions d'export
5. **Calculs** : Vérifier les calculs de tarification

### Commandes de Test
```bash
# Vérifier la base
sqlite3 backend/instance/eos.db ".tables"
sqlite3 backend/instance/eos.db ".schema enquetes"

# Tester la connexion Python
python -c "from backend.models.models import db; print('DB OK')"
```

---

**Note :** La base de données SQLite est autonome et portable. Il suffit de copier le fichier `eos.db` pour transférer toutes les données.