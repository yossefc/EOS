# 🔍 COMMENT VÉRIFIER LES DONNÉES EN BASE

## 🎯 Objectif

Ce script vous permet de **vérifier ce qu'il y a dans la base de données PostgreSQL** pour diagnostiquer si le problème vient de l'import ou de l'export.

---

## 🚀 MÉTHODE 1: Double-cliquer (Plus simple)

### Windows:

**Double-cliquez sur un de ces fichiers:**
- `backend/VERIFIER_BASE.bat`
- `backend/VERIFIER_BASE.ps1` (si .bat ne fonctionne pas)

Le script va:
1. Se connecter à la base de données
2. Afficher le nombre d'enregistrements
3. Montrer les valeurs des champs problématiques
4. Faire un diagnostic automatique

---

## 🚀 MÉTHODE 2: Ligne de commande

### PowerShell:
```powershell
cd D:\EOS\backend
$env:DATABASE_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
python verifier_donnees_sherlock.py
```

### CMD:
```cmd
cd D:\EOS\backend
set DATABASE_URL=postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db
python verifier_donnees_sherlock.py
```

---

## 📊 INTERPRÉTATION DES RÉSULTATS

### ✅ CAS 1: "DONNÉES CORRECTES EN BASE"

```
✅ reference_interne: 10/10 remplis (100%)
✅ ec_civilite: 10/10 remplis (100%)
✅ ec_prenom: 10/10 remplis (100%)

✅ DONNÉES CORRECTES EN BASE:
   → Tous les champs avec accents sont remplis
   → L'import a fonctionné correctement
```

**Diagnostic:** L'IMPORT fonctionne ✅
**Problème:** L'EXPORT ne récupère pas les données ❌

**Solution:**
1. Vérifiez que `app.py` contient les corrections d'export
2. Redémarrez le serveur Flask
3. Testez à nouveau l'export

---

### ❌ CAS 2: "CHAMPS AVEC ACCENTS SONT VIDES"

```
❌ reference_interne: 0/10 remplis (0%)
❌ ec_civilite: 0/10 remplis (0%)
❌ ec_prenom: 0/10 remplis (0%)

❌ PROBLÈME CONFIRMÉ:
   → Les champs avec accents sont VIDES en base
   → L'IMPORT n'a pas fonctionné correctement
```

**Diagnostic:** L'IMPORT ne fonctionne PAS ❌

**Cause:** Le serveur Flask n'a pas été redémarré après les corrections

**Solution:**
1. **REDÉMARREZ** le serveur Flask:
   ```
   Ctrl+C (arrêter)
   python app.py (redémarrer)
   ```
2. **SUPPRIMEZ** le fichier Sherlock importé
3. **RÉIMPORTEZ** le fichier
4. **RELANCEZ** ce script pour vérifier

---

### ⚠️ CAS 3: "AUCUNE DONNÉE EN BASE"

```
❌ AUCUNE DONNÉE EN BASE!

📝 DIAGNOSTIC:
   → L'IMPORT N'A PAS FONCTIONNÉ
   → Les données ne sont pas en base
```

**Diagnostic:** L'import a complètement échoué

**Solution:**
1. Vérifiez les **LOGS du serveur Flask** pendant l'import
2. Cherchez les erreurs dans les logs
3. Corrigez les erreurs
4. Réessayez l'import

---

## 🔧 DÉPANNAGE

### Erreur: "DATABASE_URL n'est pas définie"

**Solution:**
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://eos_user:eos_password@localhost:5432/eos_db"
```

Ou lancez d'abord:
```powershell
.\START_POSTGRESQL.ps1
```

---

### Erreur: "Impossible de se connecter à la base"

**Causes possibles:**
1. PostgreSQL n'est pas démarré
2. Les credentials sont incorrects
3. Le port est incorrect

**Solution:**
1. Démarrez PostgreSQL
2. Vérifiez `DATABASE_URL`

---

## 📋 EXEMPLE DE RÉSULTAT COMPLET

```
================================================================================
VÉRIFICATION DES DONNÉES SHERLOCK EN BASE DE DONNÉES
================================================================================

📊 Base de données: localhost:5432/eos_db

1️⃣ NOMBRE D'ENREGISTREMENTS:
   Total SherlockDonnee: 25

2️⃣ FICHIERS IMPORTÉS:
   • Fichier ID 73: IDS-L_DANS_SHERLOCK Logement_30012026_070028.xlsx
     Date: 2026-02-09 15:31:13
     Enregistrements: 25

3️⃣ PREMIER ENREGISTREMENT (DÉTAILS):
   ID: 1
   Fichier ID: 73
   Created at: 2026-02-09 15:31:13

   📋 VALEURS DES CHAMPS:
   ✅ DossierId              : 570405753
   ✅ RéférenceInterne       : DANS_SHERLOCK_260114008
   ✅ Demande                : Retour du 250711363+A+T+Logement
   ✅ EC-Civilité            : Monsieur
   ✅ EC-Prénom              : DANIEN YOUNSOUF
   ❌ EC-Prénom2             : (VIDE)
   ❌ EC-Prénom3             : (VIDE)
   ❌ EC-Prénom4             : (VIDE)
   ✅ EC-Nom Usage           : ANITAN
   ✅ EC-Date Naissance      : 1986-06-30 00:00:00
   ✅ Naissance CP           : 75010.0
   ✅ EC-Localité Naissance  : PARIS 10E ARRONDISSEMENT
   ✅ Naissance INSEE        : 75110.0
   ✅ AD-L4 Numéro           : 46
   ✅ AD-L4 Voie             : Rue de Bâle
   ✅ AD-L6 CP               : 68100
   ✅ AD-L6 Localité         : Mulhouse
   ✅ AD-L7 Pays             : France
   ✅ AD-Email               : oliveirastine@gmail.com

4️⃣ STATISTIQUES DES CHAMPS VIDES:
   ✅ reference_interne      : 25/25 remplis (100.0%)
   ✅ ec_civilite            : 25/25 remplis (100.0%)
   ✅ ec_prenom              : 25/25 remplis (100.0%)
   ✅ ec_localite_naissance  : 25/25 remplis (100.0%)
   ✅ ad_l4_numero           : 25/25 remplis (100.0%)

5️⃣ DIAGNOSTIC:
================================================================================

✅ DONNÉES CORRECTES EN BASE:
   → Tous les champs avec accents sont remplis
   → L'import a fonctionné correctement

💡 SI L'EXPORT EST VIDE:
   → Le problème vient de la fonction d'EXPORT
   → Vérifiez que le serveur Flask a été redémarré
   → Vérifiez les logs de l'export

================================================================================
```

---

## 🎯 RÉSUMÉ

**Ce script vous dit:**
1. ✅ ou ❌ Si les données sont en base
2. ✅ ou ❌ Si l'import a fonctionné
3. ✅ ou ❌ Si les champs avec accents sont remplis
4. 💡 Quelle est la cause du problème
5. 🔧 Comment le résoudre

**Utilisez-le après chaque import pour vérifier que tout est OK!**
