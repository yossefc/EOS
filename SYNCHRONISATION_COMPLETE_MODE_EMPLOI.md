# 🔄 SYNCHRONISATION COMPLÈTE ENTRE DEUX ORDINATEURS

## 📋 VOTRE SITUATION

Vous avez installé le programme EOS sur deux ordinateurs différents :
- **Ordinateur A (chez vous)** : Contient toutes les données, incluant le client Sherlock
- **Ordinateur B (chez lui)** : Installation fraîche, le client Sherlock n'apparaît pas

Vous voulez :
1. ✅ Transférer TOUTES les données (clients, tarifs, mappings) de l'ordinateur A vers B
2. ✅ Permettre à d'autres ordinateurs de se connecter au programme via l'adresse IP

---

## 🎯 SOLUTION EN 3 ÉTAPES

### ═══════════════════════════════════════════════════════════════
### ÉTAPE 1 : EXPORTER LES DONNÉES (SUR ORDINATEUR A)
### ═══════════════════════════════════════════════════════════════

**Sur l'ordinateur qui a toutes les données (chez vous) :**

1. Ouvrez PowerShell dans `D:\EOS`

2. Exécutez le script d'export :
   ```cmd
   .\SYNCHRONISER_VERS_AUTRE_ORDI.bat
   ```

3. Le script va créer **5 fichiers SQL** dans `D:\EOS\` :
   - `TOUS_CLIENTS_EXPORT.sql` (incluant Sherlock !)
   - `TOUS_TARIFS_EXPORT.sql`
   - `TOUS_PROFILS_IMPORT_EXPORT.sql`
   - `TOUS_MAPPINGS_IMPORT_EXPORT.sql`
   - `TOUTES_REGLES_TARIFAIRES_EXPORT.sql`

4. **Copiez ces 5 fichiers** sur une clé USB ou envoyez-les par email

---

### ═══════════════════════════════════════════════════════════════
### ÉTAPE 2 : IMPORTER LES DONNÉES (SUR ORDINATEUR B)
### ═══════════════════════════════════════════════════════════════

**Sur l'autre ordinateur (chez lui) :**

1. **Copiez les 5 fichiers SQL** reçus dans `D:\EOS\`

2. Ouvrez PowerShell dans `D:\EOS`

3. Exécutez le script d'import :
   ```cmd
   .\IMPORTER_DEPUIS_AUTRE_ORDI.bat
   ```

4. Le script va importer TOUTES les données :
   - ✅ Tous les clients (PARTNER, Sherlock, etc.)
   - ✅ Tous les tarifs
   - ✅ Tous les profils d'import
   - ✅ Tous les mappings de colonnes
   - ✅ Toutes les règles tarifaires

5. **Redémarrez l'application** :
   ```cmd
   .\DEMARRER_EOS_SIMPLE.bat
   ```

6. **Vérifiez** : Le client Sherlock devrait maintenant apparaître dans la liste des clients !

---

### ═══════════════════════════════════════════════════════════════
### ÉTAPE 3 : CONFIGURER L'ACCÈS RÉSEAU
### ═══════════════════════════════════════════════════════════════

Pour permettre à d'autres ordinateurs de se connecter via l'IP :

#### 🖥️ SUR L'ORDINATEUR SERVEUR (où l'application tourne)

##### A) Trouver l'adresse IP

1. Ouvrez PowerShell
2. Tapez : `ipconfig`
3. Cherchez "Adresse IPv4" (ex: `192.168.1.100`)
4. **NOTEZ CETTE ADRESSE**

##### B) Ouvrir le pare-feu Windows

1. Appuyez sur `Windows + R`
2. Tapez : `wf.msc`
3. Cliquez sur "Règles de trafic entrant"
4. Cliquez sur "Nouvelle règle..."

**Créez 2 règles :**

**RÈGLE 1 - Backend (Port 5000) :**
- Type : Port
- Protocole : TCP
- Port : 5000
- Action : Autoriser la connexion
- Profils : Cochez les 3 (Domaine, Privé, Public)
- Nom : `EOS Backend (Port 5000)`

**RÈGLE 2 - Frontend (Port 5173) :**
- Type : Port
- Protocole : TCP
- Port : 5173
- Action : Autoriser la connexion
- Profils : Cochez les 3 (Domaine, Privé, Public)
- Nom : `EOS Frontend (Port 5173)`

##### C) Démarrer l'application

```cmd
.\DEMARRER_EOS_SIMPLE.bat
```

Vous devriez voir :
```
Backend : Running on http://192.168.X.X:5000
Frontend : Network: http://192.168.X.X:5173
```

#### 💻 SUR L'ORDINATEUR CLIENT (qui veut se connecter)

1. Ouvrez un navigateur web (Chrome, Edge, Firefox...)

2. Dans la barre d'adresse, tapez :
   ```
   http://192.168.X.X:5173
   ```
   (Remplacez `192.168.X.X` par l'adresse IP du serveur)

3. L'application EOS s'ouvre !

4. Connectez-vous normalement avec vos identifiants

---

## ❓ QUESTIONS FRÉQUENTES

### Q1 : Chaque ordinateur a une IP différente, c'est normal ?

**✅ OUI, c'est NORMAL !**

- **Serveur** (où l'app tourne) : `192.168.1.100`
- **Client 1** (qui se connecte) : `192.168.1.101`
- **Client 2** (autre ordi) : `192.168.1.102`

Pour se connecter, les clients utilisent l'IP du **SERVEUR** dans leur navigateur.

Le frontend détecte automatiquement l'IP grâce à cette configuration :
```javascript
API_URL: `http://${window.location.hostname}:5000`
```

Vous n'avez **RIEN à modifier** dans le code !

---

### Q2 : L'application est déjà configurée pour le réseau ?

**✅ OUI !**

Le backend est déjà configuré pour écouter sur toutes les interfaces :
```python
app.run(host='0.0.0.0', port=5000)  # 0.0.0.0 = toutes les interfaces
```

Le frontend détecte automatiquement l'IP du client.

Vous devez juste **ouvrir le pare-feu** (Étape 3B).

---

### Q3 : Dois-je refaire la synchronisation à chaque fois ?

**Non**, seulement quand vous ajoutez :
- Un nouveau client
- De nouveaux tarifs
- De nouveaux mappings

Pour une synchronisation ponctuelle :
1. Ordinateur A : `SYNCHRONISER_VERS_AUTRE_ORDI.bat`
2. Copiez les 5 fichiers SQL vers ordinateur B
3. Ordinateur B : `IMPORTER_DEPUIS_AUTRE_ORDI.bat`

---

### Q4 : Comment vérifier que Sherlock est bien importé ?

Après l'import, connectez-vous à la base de données :

```cmd
psql -U postgres -d eos_db
```

Puis tapez :
```sql
SELECT id, code, nom, actif FROM clients ORDER BY id;
```

Vous devriez voir Sherlock dans la liste !

---

## 🔧 RÉSOLUTION DE PROBLÈMES

### ❌ "Cette page n'est pas accessible"

**Solutions :**
1. Vérifiez que le pare-feu est ouvert (Étape 3B)
2. Vérifiez que l'application est démarrée sur le serveur
3. Vérifiez que les deux PC sont sur le même réseau Wi-Fi/Ethernet
4. Testez la connexion : `ping 192.168.X.X`

---

### ❌ "Network Error" ou "CORS Error"

**Solution :**

1. Ouvrez `D:\EOS\backend\config.py`
2. Ajoutez l'IP du client dans `CORS_ORIGINS` :

```python
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 
    'http://localhost:5173,http://192.168.1.100:5173,http://192.168.1.101:5173'
).split(',')
```

3. Redémarrez le backend

---

### ❌ "Erreur lors de l'import des clients"

**Solution :**

1. Vérifiez que PostgreSQL est démarré
2. Vérifiez que vous êtes dans `D:\EOS`
3. Vérifiez que les 5 fichiers SQL sont bien présents
4. Réessayez l'import

---

## 📝 RÉCAPITULATIF ULTRA-RAPIDE

### 🔵 SYNCHRONISER LES DONNÉES (Sherlock, etc.)

**Ordinateur A (source) :**
```cmd
cd D:\EOS
.\SYNCHRONISER_VERS_AUTRE_ORDI.bat
```
→ Copiez les 5 fichiers SQL générés

**Ordinateur B (cible) :**
```cmd
cd D:\EOS
.\IMPORTER_DEPUIS_AUTRE_ORDI.bat
.\DEMARRER_EOS_SIMPLE.bat
```

---

### 🌐 ACCÈS RÉSEAU

**Serveur :**
1. `ipconfig` → Notez l'IP
2. Ouvrez ports 5000 et 5173 dans pare-feu
3. `.\DEMARRER_EOS_SIMPLE.bat`

**Client :**
1. Ouvrez navigateur
2. Allez sur : `http://[IP_SERVEUR]:5173`

---

## 📚 FICHIERS CRÉÉS

| Fichier | Description |
|---------|-------------|
| `SYNCHRONISER_VERS_AUTRE_ORDI.bat` | Export toutes les données (ordinateur source) |
| `IMPORTER_DEPUIS_AUTRE_ORDI.bat` | Import toutes les données (ordinateur cible) |
| `EXPORT_TOUS_CLIENTS.sql` | Script SQL d'export des clients |
| `EXPORT_TOUS_TARIFS.sql` | Script SQL d'export des tarifs |
| `EXPORT_PROFILS_IMPORT.sql` | Script SQL d'export des profils d'import |
| `EXPORT_MAPPINGS_IMPORT.sql` | Script SQL d'export des mappings |
| `EXPORT_REGLES_TARIFAIRES.sql` | Script SQL d'export des règles tarifaires |
| `GUIDE_ACCES_RESEAU.txt` | Guide détaillé de l'accès réseau |

---

## ✅ CHECKLIST FINALE

### Synchronisation des données
- [ ] Export effectué sur ordinateur A
- [ ] 5 fichiers SQL copiés sur ordinateur B
- [ ] Import effectué sur ordinateur B
- [ ] Application redémarrée
- [ ] Client Sherlock visible dans la liste

### Accès réseau
- [ ] Adresse IP du serveur trouvée
- [ ] Pare-feu configuré (ports 5000 et 5173)
- [ ] Application démarrée sur le serveur
- [ ] Connexion réussie depuis un autre PC
- [ ] Pas d'erreur CORS

---

## 🆘 BESOIN D'AIDE ?

Consultez le guide détaillé : **GUIDE_ACCES_RESEAU.txt**

Ou contactez le support technique.

---

**Bonne synchronisation ! 🚀**

