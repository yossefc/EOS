# 🔄 Instructions de Mise à Jour EOS

## Utilisation du script de mise à jour

### Sur le serveur principal (où vous développez)

Après avoir fait vos modifications et les avoir commitées :

```bash
git add .
git commit -m "Description des modifications"
git push
```

### Sur les autres serveurs/ordinateurs

**Méthode 1 : Double-clic (le plus simple)**
1. Double-cliquez sur `METTRE_A_JOUR.bat`
2. Suivez les instructions à l'écran
3. Redémarrez le backend et rechargez le frontend

**Méthode 2 : Ligne de commande**
```powershell
.\METTRE_A_JOUR.ps1
```

## Que fait le script ?

Le script effectue automatiquement les opérations suivantes :

1. ✅ Vérifie l'état du dépôt Git local
2. ✅ Récupère les dernières modifications (`git pull`)
3. ✅ Met à jour les dépendances Python (`pip install -r requirements.txt`)
4. ✅ Met à jour les dépendances npm (`npm install`)
5. ✅ Vérifie la configuration de la base de données
6. ✅ Affiche les derniers commits

## Après la mise à jour

### 1. Redémarrer le Backend
Si le backend est en cours d'exécution :
- Arrêtez-le (Ctrl+C dans la console)
- Relancez avec : `.\DEMARRER_EOS_COMPLET.bat`

### 2. Recharger le Frontend
Dans votre navigateur :
- Appuyez sur **Ctrl+F5** (rechargement avec vidage du cache)
- Ou **F5** (rechargement simple)

## Configuration initiale (première fois uniquement)

Si c'est la première fois que vous installez sur ce serveur, définissez d'abord la variable d'environnement :

```powershell
$env:DATABASE_URL="postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
```

Pour la rendre permanente :
```powershell
[System.Environment]::SetEnvironmentVariable('DATABASE_URL', 'postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db', 'User')
```

## Problèmes courants

### ❌ "Not a git repository"
- Vous n'êtes pas dans le bon dossier
- Naviguez vers le dossier `EOS` avant de lancer le script

### ❌ "pip not available"
- Python n'est pas installé ou pas dans le PATH
- Réinstallez Python avec l'option "Add to PATH"

### ❌ "npm not available"
- Node.js n'est pas installé
- Installez Node.js depuis https://nodejs.org

### ⚠️ "Modifications locales non commitées"
- Vous avez des changements non sauvegardés
- Le script vous demandera si vous voulez continuer quand même
- Recommandé : commitez ou annulez vos modifications d'abord

## Support

Pour toute question, contactez l'administrateur du système.
