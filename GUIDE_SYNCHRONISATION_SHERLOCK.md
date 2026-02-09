# 🔄 GUIDE DE SYNCHRONISATION - CORRECTIONS SHERLOCK

## 📋 Résumé du problème

**6 champs manquants dans l'export:**
1. RéférenceInterne
2. EC-Civilité
3. EC-Prénom
4. EC-Localité Naissance
5. AD-L4 Numéro
6. AD-L6 Localité

**Cause:** Les données n'ont pas été importées correctement en base de données à cause de l'erreur `montant_ht`.

---

## ✅ SOLUTION - Étapes à suivre sur L'AUTRE ORDINATEUR

### Étape 1: Vérifier que les corrections sont présentes

Exécutez le script de diagnostic:
```bash
cd D:\EOS\backend
python diagnostic_sherlock.py
```

**Résultat attendu:** Tous les ✅ doivent être verts.

**Si des ❌ apparaissent:**
- Les corrections ne sont PAS sur cet ordinateur
- Vous devez copier les fichiers depuis CET ordinateur

---

### Étape 2: Copier les fichiers corrigés (si nécessaire)

**Fichiers à copier depuis CET ordinateur vers L'AUTRE ordinateur:**

```
D:\EOS\backend\import_engine.py
D:\EOS\backend\app.py
```

**Méthode:**
1. Sur CET ordinateur: Copiez ces 2 fichiers sur une clé USB
2. Sur L'AUTRE ordinateur: Remplacez les fichiers existants
3. Ou utilisez Git pour synchroniser

---

### Étape 3: REDÉMARRER le serveur Flask

Sur l'autre ordinateur:

1. **Arrêter le serveur:**
   - Trouvez la fenêtre du terminal où Flask tourne
   - Appuyez sur `Ctrl+C`

2. **Redémarrer le serveur:**
   ```bash
   cd D:\EOS\backend
   python app.py
   ```

3. **Vérifier que le serveur démarre sans erreur**

---

### Étape 4: Supprimer l'ancien import (important!)

Dans l'interface web:
1. Allez dans la section "Fichiers Sherlock"
2. **Supprimez** le fichier précédemment importé
3. Cela supprimera les données partielles/incorrectes

---

### Étape 5: RÉIMPORTER le fichier Sherlock

1. Importez à nouveau le fichier Excel Sherlock
2. L'import devrait maintenant **réussir complètement**
3. Vérifiez qu'il n'y a **aucune erreur** dans les logs

---

### Étape 6: Tester l'export

1. Exportez les données Sherlock
2. Ouvrez le fichier Excel exporté
3. **Vérifiez que TOUS les champs ont des valeurs:**
   - RéférenceInterne = `DANS_SHERLOCK_260114008` ✅
   - EC-Civilité = `Monsieur` ✅
   - EC-Prénom = `DANIEN YOUNSOUF` ✅
   - EC-Localité Naissance = `PARIS 10E ARRONDISSEMENT` ✅
   - AD-L4 Numéro = `46` ✅
   - AD-L6 Localité = `Mulhouse` ✅

4. **Vérifiez aussi le formatage:**
   - Dates: `30/06/1986` (pas `1986-06-30 00:00:00`) ✅
   - Codes: `75110` (pas `75110.0`) ✅
   - Pas de tarifs dans l'export ✅

---

## 🔍 VÉRIFICATION RAPIDE

### Test 1: Diagnostic du code
```bash
python diagnostic_sherlock.py
```
**Attendu:** Tous ✅

### Test 2: Analyse des données
```bash
python analyse_donnees_manquantes.py
```
**Attendu:** 0 champs manquants après réimport

---

## ⚠️ POINTS IMPORTANTS

1. **TOUJOURS redémarrer Flask** après modification du code
2. **TOUJOURS supprimer l'ancien fichier** avant de réimporter
3. **Vérifier les logs** pendant l'import pour détecter les erreurs
4. Les **corrections sont dans le code**, pas dans la base de données

---

## 📞 DÉPANNAGE

### Problème: Toujours des erreurs après redémarrage

**Vérifier:**
- Le bon serveur Flask est-il redémarré? (pas un ancien processus)
- Les bons fichiers sont-ils modifiés? (vérifier le chemin)
- Y a-t-il des erreurs dans le terminal Flask?

### Problème: Import échoue toujours

**Vérifier:**
- `diagnostic_sherlock.py` montre tous ✅?
- Le fichier Excel est-il bien formaté?
- Y a-t-il d'autres erreurs dans les logs?

### Problème: Export toujours vide

**Cause:** Les données ne sont pas en base de données
**Solution:** Supprimer + Réimporter (voir Étapes 4-5)

---

## ✅ CHECKLIST FINALE

- [ ] Fichiers corrigés copiés sur l'autre ordinateur
- [ ] Serveur Flask redémarré
- [ ] Ancien fichier Sherlock supprimé
- [ ] Nouveau fichier Sherlock importé SANS erreur
- [ ] Export testé et données présentes
- [ ] Dates au format JJ/MM/AAAA
- [ ] Codes sans .0
- [ ] Pas de tarifs dans l'export

---

**Une fois toutes ces étapes complétées, l'export devrait contenir toutes les données correctement formatées!**
