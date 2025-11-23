# 🚀 Démarrage Rapide - Export Word

## ⚡ Installation Express (5 minutes)

### 1. Installer python-docx

```powershell
cd D:\EOS\backend
pip install python-docx==1.1.0
```

### 2. Créer la table d'archivage

```powershell
python create_archive_table.py
```

### 3. Redémarrer le backend

```powershell
python app.py
```

### 4. Tester l'export

1. Ouvrir http://localhost:5173
2. Aller dans l'onglet "Export"
3. Sélectionner des enquêtes
4. Cliquer sur "Exporter en Word & archiver"
5. ✅ Un fichier `.docx` se télécharge !

---

## 📋 Checklist de Vérification

- [ ] `python-docx` installé
- [ ] Table `enquete_archives` créée
- [ ] Backend redémarré
- [ ] Frontend accessible
- [ ] Export fonctionne
- [ ] Fichier Word s'ouvre correctement
- [ ] Une page par enquête
- [ ] Tableau formaté
- [ ] Enquêtes archivées

---

## 🎯 Résultat Attendu

### Fichier Word Généré

**Nom** : `Export_Enquetes_20251123_143025.docx`

**Contenu** :
- Page 1 : Enquête n°1 avec tableau complet
- Page 2 : Enquête n°2 avec tableau complet
- Page 3 : Enquête n°3 avec tableau complet
- etc.

### Base de Données

**Table `enquete_archives`** :
```
id | enquete_id | date_export         | nom_fichier
---+------------+---------------------+---------------------------
1  | 123        | 2025-11-23 14:30:25 | Export_Enquetes_20251123...
2  | 124        | 2025-11-23 14:30:25 | Export_Enquetes_20251123...
3  | 125        | 2025-11-23 14:30:25 | Export_Enquetes_20251123...
```

---

## 🐛 Problèmes Courants

### Erreur : `ModuleNotFoundError: No module named 'docx'`

```powershell
pip install python-docx==1.1.0
```

### Erreur : `Table enquete_archives doesn't exist`

```powershell
python create_archive_table.py
```

### Le fichier ne se télécharge pas

1. Ouvrir la console du navigateur (F12)
2. Vérifier les erreurs
3. Relancer le backend

---

## 📞 Besoin d'Aide ?

Consultez `EXPORT_WORD_IMPLEMENTATION.md` pour la documentation complète.

---

**Temps total** : ~5 minutes  
**Difficulté** : ⭐ Facile

