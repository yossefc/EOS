# 📦 RÉSUMÉ DES SCRIPTS CRÉÉS POUR VOUS

## ✅ CE QUI A ÉTÉ FAIT

J'ai créé un système complet pour :

1. **Synchroniser toutes les données** entre deux ordinateurs (incluant le client Sherlock)
2. **Configurer l'accès réseau** pour permettre la connexion depuis d'autres ordinateurs via IP

---

## 📁 FICHIERS CRÉÉS

### 🚀 FICHIER DE DÉMARRAGE

| Fichier | Description |
|---------|-------------|
| `___COMMENCER_ICI___.txt` | **COMMENCEZ PAR CE FICHIER !** Guide de navigation |

### 📚 GUIDES COMPLETS

| Fichier | Usage |
|---------|-------|
| `LISEZMOI_SYNCHRONISATION.txt` | Guide rapide et simple (recommandé pour débuter) |
| `SYNCHRONISATION_COMPLETE_MODE_EMPLOI.md` | Guide complet avec FAQ et résolution de problèmes |
| `GUIDE_ACCES_RESEAU.txt` | Guide détaillé pour l'accès réseau (pare-feu, IP, etc.) |

### 🔄 SCRIPTS DE SYNCHRONISATION DES DONNÉES

| Fichier | Où l'utiliser | Description |
|---------|---------------|-------------|
| `SYNCHRONISER_VERS_AUTRE_ORDI.bat` | **Ordinateur SOURCE** (celui qui a les données) | Exporte TOUTES les données |
| `IMPORTER_DEPUIS_AUTRE_ORDI.bat` | **Ordinateur CIBLE** (celui qui doit recevoir) | Importe TOUTES les données |

### 📊 SCRIPTS SQL D'EXPORT

| Fichier | Ce qu'il fait |
|---------|---------------|
| `EXPORT_TOUS_CLIENTS.sql` | Exporte tous les clients (PARTNER, Sherlock, etc.) |
| `EXPORT_TOUS_TARIFS.sql` | Exporte tous les tarifs de tous les clients |
| `EXPORT_PROFILS_IMPORT.sql` | Exporte tous les profils d'import |
| `EXPORT_MAPPINGS_IMPORT.sql` | Exporte tous les mappings de colonnes |
| `EXPORT_REGLES_TARIFAIRES.sql` | Exporte toutes les règles tarifaires |

### 🌐 SCRIPTS DE CONFIGURATION RÉSEAU

| Fichier | Droits requis | Description |
|---------|---------------|-------------|
| `CREER_REGLES_PAREFEU.ps1` | **ADMIN** | Crée automatiquement les règles de pare-feu pour les ports 5000 et 5173 |
| `VERIFIER_CONFIG_RESEAU.ps1` | Normal | Vérifie la configuration réseau (IP, pare-feu, ports) |

---

## 🎯 COMMENT UTILISER

### Scénario 1️⃣ : Transférer les données (Sherlock manquant)

#### Sur l'ordinateur qui a toutes les données :

```cmd
cd D:\EOS
.\SYNCHRONISER_VERS_AUTRE_ORDI.bat
```

**Résultat** : 5 fichiers SQL sont créés dans `D:\EOS\`

#### Copier les fichiers

Transférez les 5 fichiers SQL vers l'autre ordinateur (USB, email, réseau partagé...)

#### Sur l'autre ordinateur :

```cmd
cd D:\EOS
.\IMPORTER_DEPUIS_AUTRE_ORDI.bat
.\DEMARRER_EOS_SIMPLE.bat
```

**Résultat** : Le client Sherlock apparaît maintenant ! ✅

---

### Scénario 2️⃣ : Permettre l'accès réseau depuis d'autres PC

#### Sur l'ordinateur serveur (en PowerShell ADMIN) :

```powershell
cd D:\EOS
.\CREER_REGLES_PAREFEU.ps1
.\DEMARRER_EOS_SIMPLE.bat
.\VERIFIER_CONFIG_RESEAU.ps1
```

**Résultat** : Le script affiche votre IP (ex: `192.168.1.100`)

#### Sur l'autre ordinateur (client) :

1. Ouvrez un navigateur
2. Tapez : `http://192.168.1.100:5173` (remplacez par votre IP)
3. L'application s'ouvre ! ✅

---

### Scénario 3️⃣ : Les deux ! (Synchronisation + Accès réseau)

Faites d'abord le **Scénario 1** puis le **Scénario 2**.

---

## 🔍 DÉTAILS TECHNIQUES

### Ce que fait `SYNCHRONISER_VERS_AUTRE_ORDI.bat` :

1. Se connecte à PostgreSQL
2. Exécute les 5 scripts SQL d'export
3. Génère 5 fichiers `.sql` contenant toutes les données :
   - Tous les clients (incluant Sherlock)
   - Tous les tarifs
   - Tous les profils d'import
   - Tous les mappings
   - Toutes les règles tarifaires

### Ce que fait `IMPORTER_DEPUIS_AUTRE_ORDI.bat` :

1. Vérifie que les 5 fichiers SQL sont présents
2. Se connecte à PostgreSQL
3. Supprime les anciennes données (pour éviter les doublons)
4. Importe les nouvelles données
5. Met à jour les séquences PostgreSQL

### Ce que fait `CREER_REGLES_PAREFEU.ps1` :

1. Vérifie les droits administrateur
2. Crée (ou recrée) deux règles de pare-feu :
   - **Port 5000** : Backend Flask
   - **Port 5173** : Frontend Vite/React
3. Active les règles pour tous les profils (Domaine, Privé, Public)

### Ce que fait `VERIFIER_CONFIG_RESEAU.ps1` :

1. Affiche votre adresse IP
2. Vérifie si les règles de pare-feu existent
3. Vérifie si les ports 5000 et 5173 sont en écoute
4. Affiche la configuration CORS
5. Donne l'adresse complète pour l'accès distant

---

## 💡 POINTS IMPORTANTS

### ✅ L'application est DÉJÀ configurée pour l'accès réseau !

- **Backend** : Écoute sur `0.0.0.0` (toutes les interfaces)
- **Frontend** : Détecte automatiquement l'IP avec `window.location.hostname`
- **CORS** : Configuré dans `backend/config.py` pour accepter plusieurs IP

**Vous n'avez RIEN à modifier dans le code !**

### ✅ Chaque ordinateur a une IP différente (c'est normal !)

- **Serveur** : `192.168.1.100` (exemple)
- **Client 1** : `192.168.1.101` (exemple)
- **Client 2** : `192.168.1.102` (exemple)

Les clients utilisent l'IP du **serveur** dans leur navigateur.

### ✅ La synchronisation est unidirectionnelle

Le script transfère les données de l'ordinateur **SOURCE** vers l'ordinateur **CIBLE**.

Si vous modifiez des données sur le CIBLE, elles ne seront PAS transférées vers le SOURCE (à moins de refaire la synchronisation dans l'autre sens).

---

## 📝 ORDRE RECOMMANDÉ

1. **Lisez** : `___COMMENCER_ICI___.txt`
2. **Suivez** : `LISEZMOI_SYNCHRONISATION.txt`
3. **En cas de problème** : `SYNCHRONISATION_COMPLETE_MODE_EMPLOI.md`
4. **Pour l'accès réseau** : `GUIDE_ACCES_RESEAU.txt`

---

## 🧪 TESTS RECOMMANDÉS

### Après la synchronisation :

1. Connectez-vous à l'application
2. Vérifiez que le client Sherlock apparaît dans la liste
3. Vérifiez que vous pouvez importer un fichier Sherlock
4. Vérifiez que les tarifs sont corrects

### Après la configuration réseau :

1. Sur le serveur, exécutez : `.\VERIFIER_CONFIG_RESEAU.ps1`
2. Sur un autre PC, ouvrez `http://[IP_SERVEUR]:5173`
3. Connectez-vous et vérifiez que tout fonctionne
4. Testez l'import et l'export

---

## ❓ FAQ RAPIDE

**Q : Dois-je refaire la synchronisation à chaque fois ?**

R : Non, seulement quand vous ajoutez de nouveaux clients, tarifs, ou mappings sur l'ordinateur source.

**Q : Puis-je utiliser ces scripts sur plus de 2 ordinateurs ?**

R : Oui ! Synchronisez depuis l'ordinateur source vers autant d'ordinateurs cibles que vous voulez.

**Q : Les données des enquêtes sont-elles aussi synchronisées ?**

R : Non, ces scripts ne synchronisent que la **configuration** (clients, tarifs, mappings). Les données d'enquêtes (table `donnees`) ne sont pas transférées.

**Q : Puis-je personnaliser les scripts ?**

R : Oui ! Tous les scripts sont modifiables. Les fichiers `.sql` sont des scripts PostgreSQL standards.

---

## 🔒 SÉCURITÉ

### Pare-feu

Les scripts ouvrent les ports **5000** et **5173** pour tous les profils réseau (Domaine, Privé, Public).

Si vous voulez limiter l'accès, modifiez `CREER_REGLES_PAREFEU.ps1` et retirez `-Profile Public`.

### CORS

La configuration CORS dans `backend/config.py` accepte plusieurs adresses IP.

Pour plus de sécurité, modifiez la ligne `CORS_ORIGINS` pour n'autoriser que les IP spécifiques :

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 
    'http://192.168.1.100:5173,http://192.168.1.101:5173'
).split(',')
```

---

## 🆘 SUPPORT

En cas de problème :

1. Exécutez : `.\VERIFIER_CONFIG_RESEAU.ps1`
2. Consultez : `SYNCHRONISATION_COMPLETE_MODE_EMPLOI.md` (section FAQ)
3. Consultez : `GUIDE_ACCES_RESEAU.txt` (section Résolution de problèmes)

---

## 🎉 CONCLUSION

Vous avez maintenant un système complet pour :

✅ Synchroniser toutes les données entre ordinateurs
✅ Permettre l'accès réseau depuis d'autres PC
✅ Diagnostiquer les problèmes de configuration
✅ Automatiser la configuration du pare-feu

**Tous les scripts sont prêts à l'emploi !**

Commencez par : `___COMMENCER_ICI___.txt`

Bonne synchronisation ! 🚀

