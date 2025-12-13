# 🚀 Installation des Fonctionnalités d'Export

## ⚠️ IMPORTANT

Le serveur Flask **DOIT ÊTRE ARRÊTÉ** avant la migration !

---

## 📋 ÉTAPES D'INSTALLATION

### **1️⃣ Arrêter le serveur Flask**

Dans le terminal backend, appuyez sur **Ctrl+C**

### **2️⃣ Exécuter la migration**

**Double-cliquez sur ce fichier :**
```
d:\EOS\backend\AJOUTER_COLONNES_EXPORT.bat
```

Ou en ligne de commande :
```powershell
cd d:\EOS\backend
python setup_export_features.py
```

Vous devriez voir :
```
✅ CONFIGURATION TERMINÉE
```

### **3️⃣ Redémarrer le serveur Flask**

```powershell
cd d:\EOS\backend
python app.py
```

### **4️⃣ Rafraîchir le navigateur**

Appuyez sur **F5** sur http://localhost:5173

---

## ✨ NOUVELLES FONCTIONNALITÉS

### **1. Export intelligent (nouvelles enquêtes uniquement)**

- Le bouton affiche : **"Export Word (X nouvelles)"**
- X = nombre d'enquêtes jamais exportées
- Les enquêtes restent visibles après export
- Impossible de ré-exporter les mêmes enquêtes

### **2. Document Word amélioré**

Chaque enquête = **UNE PAGE** avec:
- **En haut** : Date de réception + Nombre de dossiers exportés
- **Corps** : TOUTES les données de l'enquête
- **Pas de nom d'enquêteur** dans le document

### **3. Assignation d'enquêteur**

- Route `POST /api/donnees` : paramètre `enqueteurId`
- Route `PUT /api/donnees/<id>` : modification enquêteur
- Route `GET /api/donnees/non-exportees/count` : compteur

---

## 🔍 VÉRIFICATION

Après installation, vérifiez :

1. **Aucune erreur** au démarrage du serveur
2. **Le bouton affiche** "Export Word (X nouvelles)"
3. **Cliquez sur Export** → Document Word téléchargé
4. **Cliquez à nouveau** → "Aucune nouvelle enquête à exporter"

---

## ❌ DÉPANNAGE

### Erreur: "no such column: donnees.exported"

**Cause**: La migration n'a pas été exécutée

**Solution**: 
1. Arrêtez le serveur (Ctrl+C)
2. Exécutez `AJOUTER_COLONNES_EXPORT.bat`
3. Redémarrez

### Le bouton affiche toujours le total

**Cause**: Le frontend n'a pas été rafraîchi

**Solution**: Appuyez sur F5 dans le navigateur

---

## 📊 COLONNES AJOUTÉES

| Colonne | Type | Description |
|---------|------|-------------|
| `exported` | BOOLEAN | False = pas encore exportée, True = déjà exportée |
| `exported_at` | DATETIME | Date et heure du dernier export |

---

**Version**: 2.0  
**Date**: 9 décembre 2025

