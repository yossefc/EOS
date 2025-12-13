# 🚀 GUIDE ULTRA-SIMPLE - Système EOS
*Pour collègue sans connaissances en programmation*

## ⚡ Installation en 3 Étapes

### Étape 1 : Télécharger les Logiciels (une seule fois)

**Python** (obligatoire)
1. Aller sur https://python.org/downloads/
2. Cliquer sur le gros bouton jaune "Download Python"
3. Lancer le fichier téléchargé
4. ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" 
5. Cliquer "Install Now"

**Node.js** (obligatoire)
1. Aller sur https://nodejs.org/
2. Cliquer sur le bouton vert "LTS"
3. Lancer le fichier téléchargé
4. Suivre l'installation normale (tout par défaut)

### Étape 2 : Installer EOS
1. Copier le dossier **EOS** complet sur votre ordinateur
2. Double-cliquer sur `INSTALLATION_AUTOMATIQUE.bat`
3. ☕ Attendre 5-10 minutes (téléchargement automatique)
4. L'installation est terminée quand vous voyez "INSTALLATION TERMINEE"

### Étape 3 : Utiliser EOS
1. Double-cliquer sur `DEMARRER_EOS.bat`
2. ⏳ Attendre 30 secondes
3. Le navigateur s'ouvre automatiquement
4. C'est prêt ! 🎉

---

## 🎯 Utilisation Quotidienne

### Pour Démarrer EOS
- Double-cliquer sur `DEMARRER_EOS.bat`
- Attendre l'ouverture automatique du navigateur

### Adresses Importantes
- **Administration** : http://localhost:5173
- **Enquêteurs** : http://localhost:5173/enqueteur.html

### Comptes de Test
- **Admin** : `admin` / `admin123`
- **Enquêteur** : `enq001` / `pass123`

### Pour Arrêter EOS
- Fermer les fenêtres noires (cmd) qui se sont ouvertes
- Ou redémarrer l'ordinateur

---

## 🆘 En Cas de Problème

### Le script d'installation dit "Python non trouvé"
➡️ Réinstaller Python en cochant bien "Add Python to PATH"

### Le script dit "Node.js non trouvé"  
➡️ Réinstaller Node.js depuis nodejs.org

### Le navigateur ne s'ouvre pas
➡️ Ouvrir manuellement http://localhost:5173

### Ça ne marche toujours pas
➡️ Redémarrer l'ordinateur et refaire Étape 3

### Page d'erreur dans le navigateur
➡️ Attendre 1-2 minutes de plus, parfois c'est lent à démarrer

---

## 📁 Fichiers Importants (NE PAS SUPPRIMER)

```
EOS/
├── DEMARRER_EOS.bat                 ← POUR LANCER LE SYSTÈME
├── INSTALLATION_AUTOMATIQUE.bat     ← POUR INSTALLER
├── backend/                         ← SERVEUR (ne pas toucher)
│   └── instance/eos.db             ← BASE DE DONNÉES (important!)
└── frontend/                        ← INTERFACE (ne pas toucher)
```

**⚠️ TRÈS IMPORTANT :** Ne jamais supprimer le fichier `backend/instance/eos.db` - c'est votre base de données complète !

---

## 🔄 Partage avec un Autre Collègue

Pour partager EOS avec quelqu'un d'autre :

1. **Arrêter EOS** (fermer les fenêtres cmd)
2. **Copier le dossier EOS complet**
3. **Donner** le dossier + ce guide
4. L'autre personne fait juste l'Étape 2 (installation) puis Étape 3 (utilisation)

**Note :** Toutes vos données seront conservées dans la copie !

---

## 📞 Support Ultra-Simple

### Si vous êtes bloqué :
1. **Redémarrer l'ordinateur**
2. **Refaire Étape 3** (DEMARRER_EOS.bat)
3. **Si ça ne marche toujours pas** : Refaire Étape 2 (INSTALLATION_AUTOMATIQUE.bat)

### Messages d'erreur courants :
- "Port déjà utilisé" ➡️ Redémarrer l'ordinateur
- "Fichier non trouvé" ➡️ Vérifier que vous êtes dans le bon dossier EOS
- Écran noir ➡️ Normal ! Attendre que le navigateur s'ouvre

---

**🎯 Objectif :** Double-cliquer sur `DEMARRER_EOS.bat` et ça marche !

**💡 Astuce :** Créer un raccourci de `DEMARRER_EOS.bat` sur le bureau pour un accès rapide.