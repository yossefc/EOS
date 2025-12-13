# 👥 ASSIGNATION D'ENQUÊTEUR

**Date**: 9 décembre 2025

---

## ✅ FONCTIONNALITÉS AJOUTÉES

### **1. Sélecteur d'enquêteur dans le tableau "Données"**

✅ **Où** : Onglet "Données" → Colonne "Enquêteur"  
✅ **Quoi** : Dropdown pour assigner un enquêteur directement depuis le tableau

**Fonctionnement** :
- Chaque ligne du tableau affiche un `<select>`
- Liste tous les enquêteurs disponibles
- Option "Non assigné" par défaut
- Sauvegarde automatique au changement
- Rafraîchit les données après assignation

---

### **2. Sélecteur d'enquêteur dans la modal "MAJ"**

✅ **Où** : Modal de mise à jour → Onglet "Informations"  
✅ **Quoi** : Section "Assignation de l'enquêteur" avec dropdown

**Fonctionnement** :
- Affiché en haut de l'onglet "Informations"
- Liste tous les enquêteurs disponibles
- Pré-sélectionne l'enquêteur actuel
- Sauvegardé avec les autres modifications
- Mise à jour indépendante des données enquêteur

---

## 🔧 MODIFICATIONS TECHNIQUES

### **Frontend - DataViewer.jsx**

**1. Nouveaux states** (ligne ~54):
```javascript
const [enqueteurs, setEnqueteurs] = useState([]);
const [nonExporteesCount, setNonExporteesCount] = useState(0);
```

**2. Chargement des enquêteurs** (ligne ~82):
```javascript
const fetchEnqueteurs = async () => {
  const response = await axios.get(`${API_URL}/api/enqueteurs`);
  setEnqueteurs(response.data.data || []);
};
```

**3. Handler de changement** (ligne ~340):
```javascript
const handleEnqueteurChange = async (donneeId, enqueteurId) => {
  await axios.put(`${API_URL}/api/donnees/${donneeId}`, {
    enqueteurId: enqueteurId || null
  });
  await fetchData(currentPage);
};
```

**4. Sélecteur dans le tableau** (ligne ~752):
```javascript
<select
  value={donnee.enqueteurId || ''}
  onChange={(e) => handleEnqueteurChange(donnee.id, e.target.value)}
>
  <option value="">Non assigné</option>
  {enqueteurs.map((enq) => (
    <option key={enq.id} value={enq.id}>
      {enq.prenom} {enq.nom}
    </option>
  ))}
</select>
```

---

### **Frontend - UpdateModal.jsx**

**1. Ajout au formData** (ligne ~98):
```javascript
const [formData, setFormData] = useState({
  enqueteurId: null,  // <-- AJOUTÉ
  code_resultat: 'P',
  // ...
});
```

**2. State pour les enquêteurs** (ligne ~197):
```javascript
const [enqueteurs, setEnqueteurs] = useState([]);

useEffect(() => {
  const fetchEnqueteurs = async () => {
    const response = await axios.get(`${API_URL}/api/enqueteurs`);
    setEnqueteurs(response.data.data || []);
  };
  if (isOpen) fetchEnqueteurs();
}, [isOpen]);
```

**3. Initialisation avec les données** (ligne ~226):
```javascript
setFormData(prev => ({
  ...prev,
  enqueteurId: data.enqueteurId || null,  // <-- AJOUTÉ
  code_resultat: 'P',
  // ...
}));
```

**4. Mise à jour avant sauvegarde** (ligne ~759):
```javascript
// Mettre à jour l'enquêteur assigné si changé
if (formData.enqueteurId !== data.enqueteurId) {
  await axios.put(`${API_URL}/api/donnees/${data.id}`, {
    enqueteurId: formData.enqueteurId || null
  });
}
```

**5. Sélecteur dans l'onglet "Informations"** (ligne ~1020):
```javascript
<div className="border-t pt-4 mb-4">
  <h4 className="font-medium mb-3">Assignation de l'enquêteur</h4>
  <div>
    <label className="block text-sm text-gray-600 mb-1">
      Enquêteur assigné
    </label>
    <select
      name="enqueteurId"
      value={formData.enqueteurId || ''}
      onChange={handleInputChange}
      className="w-full p-2 border rounded focus:ring-2 focus:ring-indigo-500"
    >
      <option value="">Non assigné</option>
      {enqueteurs.map((enq) => (
        <option key={enq.id} value={enq.id}>
          {enq.prenom} {enq.nom}
        </option>
      ))}
    </select>
    <p className="text-xs text-gray-500 mt-1">
      Sélectionnez l'enquêteur responsable de ce dossier
    </p>
  </div>
</div>
```

---

## 🎯 UTILISATION

### **Dans le tableau "Données"**

1. Allez dans l'onglet "Données"
2. Dans la colonne "Enquêteur", cliquez sur le dropdown
3. Sélectionnez un enquêteur
4. **Sauvegarde automatique** ✅

### **Dans la modal "MAJ"**

1. Cliquez sur le bouton "Crayon" (MAJ) d'une enquête
2. Allez dans l'onglet "Informations" (par défaut)
3. En haut, section "Assignation de l'enquêteur"
4. Sélectionnez un enquêteur
5. Cliquez sur "Enregistrer" en bas
6. **Sauvegardé avec toutes les modifications** ✅

---

## 🔄 ROUTES BACKEND UTILISÉES

### `GET /api/enqueteurs`
- Récupère la liste de tous les enquêteurs
- Utilisé pour remplir les dropdowns
- Retourne : `{ success: true, data: [...] }`

### `PUT /api/donnees/<id>`
- Met à jour une enquête (y compris `enqueteurId`)
- Body : `{ enqueteurId: 123 }` ou `{ enqueteurId: null }`
- Retourne : `{ success: true, data: {...} }`

---

## ✨ AVANTAGES

✅ **Assignation rapide** : Directement depuis le tableau  
✅ **Assignation précise** : Dans la modal MAJ avec toutes les infos  
✅ **Indépendance** : Ne modifie pas les données enquêteur  
✅ **Flexibilité** : Possibilité de désassigner (Non assigné)  
✅ **Temps réel** : Rafraîchissement automatique après modification

---

## 📝 NOTES

- L'enquêteur assigné est stocké dans `donnees.enqueteurId`
- Aucun impact sur les données d'enquête (`donnees_enqueteur`)
- Les deux méthodes (tableau + modal) sont indépendantes
- La liste des enquêteurs est chargée dynamiquement
- "Non assigné" correspond à `enqueteurId = null`

---

**Version**: 1.0  
**Auteur**: Assistant  
**Statut**: ✅ Implémenté et fonctionnel

