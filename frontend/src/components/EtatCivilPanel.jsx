// frontend/src/components/EtatCivilPanel.jsx
import React, { useState, useEffect } from 'react';
import { AlertCircle, InfoIcon, Check } from 'lucide-react';

const EtatCivilPanel = ({ 
  originalData, 
  formData, 
  setFormData, 
  onValidate 
}) => {
  const [showPanel, setShowPanel] = useState(false);
  const [errors, setErrors] = useState({});
  
  // État civil corrigé
  const [correctedData, setCorrectedData] = useState({
    qualite: '',
    nom: '',
    prenom: '',
    nomPatronymique: '',
    dateNaissance: '',
    lieuNaissance: '',
    codePostalNaissance: '',
    paysNaissance: '',
  });

  // État pour suivre quelle divergence est sélectionnée
  const [selectedDivergence, setSelectedDivergence] = useState(null);

  // Définir quels champs sont modifiables selon le type de divergence
  const getEditableFields = () => {
    switch(selectedDivergence) {
      case 'date1':
      case 'date2':
        return ['dateNaissance'];
      case 'prenom':
        return ['prenom'];
      case 'lieuNaissance':
        return ['lieuNaissance', 'codePostalNaissance'];
      case 'dateConjoint':
        return ['dateNaissance'];
      default:
        return [];
    }
  };

  // Liste des types de divergences autorisées selon le cahier des charges
  const divergenceTypes = [
    { 
      id: 'date1', 
      label: 'Un chiffre d\'écart dans la date de naissance',
      description: 'Ex: 12/06/1966 au lieu de 12/05/1966. Le lieu de naissance doit être identique.'
    },
    { 
      id: 'date2', 
      label: 'Deux chiffres d\'écart dans la date de naissance',
      description: 'Ex: 22/06/1966 au lieu de 12/05/1966. Nécessite confirmation par source non administrative.'
    },
    { 
      id: 'prenom', 
      label: 'Prénom différent (correspond au 2ème ou 3ème prénom)',
      description: 'Tous les autres éléments doivent être identiques.'
    },
    { 
      id: 'lieuNaissance', 
      label: 'Lieu de naissance différent',
      description: 'Requiert une confirmation par source non administrative. Tous les autres éléments doivent être identiques.'
    },
    { 
      id: 'dateConjoint', 
      label: 'Date de naissance correspond à celle du conjoint',
      description: 'La date de naissance retrouvée correspond à la date de naissance du conjoint de l\'intervenant.'
    }
  ];

  // Initialiser avec les données originales quand elles changent
  useEffect(() => {
    if (originalData) {
      setCorrectedData({
        qualite: originalData.qualite || '',
        nom: originalData.nom || '',
        prenom: originalData.prenom || '',
        nomPatronymique: originalData.nomPatronymique || '',
        dateNaissance: originalData.dateNaissance || '',
        lieuNaissance: originalData.lieuNaissance || '',
        codePostalNaissance: originalData.codePostalNaissance || '',
        paysNaissance: originalData.paysNaissance || '',
      });
    }
  }, [originalData]);

  // Reset quand le type de divergence change
  useEffect(() => {
    if (selectedDivergence) {
      // Réinitialiser avec les données originales
      setCorrectedData(prev => ({
        ...prev,
        qualite: originalData.qualite || '',
        nom: originalData.nom || '',
        prenom: originalData.prenom || '',
        nomPatronymique: originalData.nomPatronymique || '',
        dateNaissance: originalData.dateNaissance || '',
        lieuNaissance: originalData.lieuNaissance || '',
        codePostalNaissance: originalData.codePostalNaissance || '',
        paysNaissance: originalData.paysNaissance || '',
      }));
      
      setErrors({});
    }
  }, [selectedDivergence, originalData]);

  const handlePanelToggle = () => {
    setShowPanel(!showPanel);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Vérifier si le champ est autorisé à être modifié
    const editableFields = getEditableFields();
    if (editableFields.includes(name) || !selectedDivergence) {
      setCorrectedData({
        ...correctedData,
        [name]: value
      });
      
      // Effacer l'erreur pour ce champ
      if (errors[name]) {
        setErrors(prev => {
          const newErrors = {...prev};
          delete newErrors[name];
          return newErrors;
        });
      }
    }
  };

  const validateDivergence = () => {
    // Validation selon le type de divergence
    const newErrors = {};
    
    // Validation commune - vérifier que les champs essentiels sont remplis
    if (!correctedData.nom) newErrors.nom = "Le nom est requis";
    if (!correctedData.prenom) newErrors.prenom = "Le prénom est requis";
    if (!correctedData.dateNaissance) newErrors.dateNaissance = "La date de naissance est requise";
    
    // Si aucune divergence n'est sélectionnée
    if (!selectedDivergence) {
      newErrors.general = "Veuillez sélectionner un type de divergence";
      setErrors(newErrors);
      return false;
    }
    
    // Validation spécifique selon le type de divergence
    if (selectedDivergence === 'date1') {
      // Vérifier qu'il y a exactement un chiffre d'écart
      const originalDate = formatDateForComparison(originalData.dateNaissance);
      const correctedDate = formatDateForComparison(correctedData.dateNaissance);
      
      if (!originalDate || !correctedDate) {
        newErrors.dateNaissance = "Format de date invalide";
      } else {
        // Compter les chiffres différents
        let diffCount = 0;
        for (let i = 0; i < originalDate.length; i++) {
          if (originalDate[i] !== correctedDate[i]) diffCount++;
        }
        
        if (diffCount !== 1) {
          newErrors.dateNaissance = "La date doit présenter exactement un chiffre d'écart";
        }
      }
    } else if (selectedDivergence === 'date2') {
      // Vérifier qu'il y a exactement deux chiffres d'écart
      const originalDate = formatDateForComparison(originalData.dateNaissance);
      const correctedDate = formatDateForComparison(correctedData.dateNaissance);
      
      if (!originalDate || !correctedDate) {
        newErrors.dateNaissance = "Format de date invalide";
      } else {
        // Compter les chiffres différents
        let diffCount = 0;
        for (let i = 0; i < originalDate.length; i++) {
          if (originalDate[i] !== correctedDate[i]) diffCount++;
        }
        
        if (diffCount !== 2) {
          newErrors.dateNaissance = "La date doit présenter exactement deux chiffres d'écart";
        }
      }
    } else if (selectedDivergence === 'prenom') {
      // Vérifier que le prénom est différent
      if (correctedData.prenom === originalData.prenom) {
        newErrors.prenom = "Le prénom doit être différent";
      }
    } else if (selectedDivergence === 'lieuNaissance') {
      // Vérifier que le lieu de naissance est différent
      if (correctedData.lieuNaissance === originalData.lieuNaissance) {
        newErrors.lieuNaissance = "Le lieu de naissance doit être différent";
      }
    }
    
    setErrors(newErrors);
    
    // Si pas d'erreurs, on peut appliquer les changements
    if (Object.keys(newErrors).length === 0) {
      // Mettre à jour le formulaire avec le flag d'état civil erroné
      setFormData({
        ...formData,
        flag_etat_civil_errone: 'E',
        type_divergence: selectedDivergence,
        // Ajouter les informations corrigées selon le type de divergence
        qualite_corrigee: correctedData.qualite,
        nom_corrige: correctedData.nom,
        prenom_corrige: correctedData.prenom,
        nom_patronymique_corrige: correctedData.nomPatronymique,
        date_naissance_corrigee: correctedData.dateNaissance,
        lieu_naissance_corrige: correctedData.lieuNaissance,
        code_postal_naissance_corrige: correctedData.codePostalNaissance,
        pays_naissance_corrige: correctedData.paysNaissance,
        // Ajouter une explication dans le mémo
        memo5: `${formData.memo5 ? formData.memo5 + '\n\n' : ''}État civil corrigé (${selectedDivergence}):\n` +
               `Type de divergence: ${divergenceTypes.find(d => d.id === selectedDivergence)?.label || selectedDivergence}\n` +
               `Date de naissance: ${correctedData.dateNaissance || 'Non modifiée'}\n` +
               `Prénom: ${correctedData.prenom || 'Non modifié'}\n` +
               `Lieu de naissance: ${correctedData.lieuNaissance || 'Non modifié'}\n`
      });
      
      // Notifier le composant parent
      onValidate(correctedData, selectedDivergence);
      
      // Fermer le panel
      setShowPanel(false);
      return true;
    }
    
    return false;
  };

  // Fonction utilitaire pour formater les dates pour la comparaison
  const formatDateForComparison = (dateString) => {
    if (!dateString) return null;
    
    // Supprimer tous les caractères non numériques
    return dateString.replace(/\D/g, '');
  };

  const resetEtatCivil = () => {
    // Réinitialiser l'état civil corrigé
    setCorrectedData({
      qualite: '',
      nom: '',
      prenom: '',
      nomPatronymique: '',
      dateNaissance: '',
      lieuNaissance: '',
      codePostalNaissance: '',
      paysNaissance: '',
    });
    
    // Réinitialiser le flag et les mémos associés
    setFormData({
      ...formData,
      flag_etat_civil_errone: '',
      type_divergence: '',
      qualite_corrigee: '',
      nom_corrige: '',
      prenom_corrige: '',
      nom_patronymique_corrige: '',
      date_naissance_corrigee: '',
      lieu_naissance_corrige: '',
      code_postal_naissance_corrige: '',
      pays_naissance_corrige: '',
      memo5: formData.memo5?.replace(/État civil corrigé:.*$/s, '') || ''
    });
    
    // Réinitialiser les erreurs et le type de divergence
    setErrors({});
    setSelectedDivergence(null);
  };

  // Détermine si un champ est modifiable
  const isFieldEditable = (fieldName) => {
    if (!selectedDivergence) return true; // Si aucune divergence n'est sélectionnée, tous les champs sont modifiables
    return getEditableFields().includes(fieldName);
  };

  return (
    <div className="bg-white border rounded-lg p-4 mb-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-medium flex items-center gap-2">
          <InfoIcon className="w-5 h-5 text-blue-500" />
          Gestion des écarts d'état civil
        </h3>
        <button
          type="button"
          onClick={handlePanelToggle}
          className="px-3 py-1 text-sm text-blue-600 border border-blue-300 rounded hover:bg-blue-50"
        >
          {showPanel ? 'Masquer' : 'Afficher'}
        </button>
      </div>

      {/* Bouton pour signaler un état civil erroné */}
      <div className="flex items-center gap-2 mb-4">
        <div className="flex-1">
          <span className="text-sm">
            État civil erroné ?
          </span>
          {formData.flag_etat_civil_errone === 'E' && (
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              <AlertCircle className="w-3 h-3 mr-1" />
              État civil divergent détecté
            </span>
          )}
        </div>
        
        <div className="flex gap-2">
          {formData.flag_etat_civil_errone === 'E' ? (
            <button
              type="button"
              onClick={resetEtatCivil}
              className="px-3 py-1 text-sm text-red-600 border border-red-300 rounded hover:bg-red-50"
            >
              Réinitialiser
            </button>
          ) : (
            <select
              value={formData.flag_etat_civil_errone}
              onChange={(e) => {
                const value = e.target.value;
                setFormData(prev => ({...prev, flag_etat_civil_errone: value}));
                if (value === 'E') setShowPanel(true);
              }}
              className="px-3 py-1 text-sm border rounded"
            >
              <option value="">Non</option>
              <option value="E">Oui (E)</option>
            </select>
          )}
        </div>
      </div>

      {/* Panel détaillé pour la gestion des écarts d'état civil */}
      {(showPanel || formData.flag_etat_civil_errone === 'E') && (
        <div className="border-t pt-4">
          <div className="bg-blue-50 p-3 rounded mb-4">
            <h4 className="text-sm font-medium text-blue-700 mb-2">Quand utiliser le flag "État civil erroné" ?</h4>
            <p className="text-xs text-blue-600 mb-2">
              Selon le cahier des charges, vous pouvez considérer l'état civil comme correct dans les cas suivants :
            </p>
            <ul className="text-xs text-blue-600 list-disc ml-4 space-y-1">
              <li>Un chiffre d'écart dans la date de naissance (tous les autres éléments identiques)</li>
              <li>Deux chiffres d'écart dans la date de naissance avec confirmation par source non administrative</li>
              <li>Prénom différent mais correspondant au 2ème ou 3ème prénom d'état civil</li>
              <li>Lieu de naissance différent avec confirmation par source non administrative</li>
              <li>Date de naissance correspondant à celle du conjoint</li>
            </ul>
          </div>

          {/* État civil original en lecture seule */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">État civil original</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Nom</p>
                <p className="font-medium">{originalData.nom || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Prénom</p>
                <p className="font-medium">{originalData.prenom || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Date de naissance</p>
                <p className="font-medium">{originalData.dateNaissance || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Lieu de naissance</p>
                <p className="font-medium">{originalData.lieuNaissance || '-'}</p>
              </div>
            </div>
          </div>

          {/* Type de divergence */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">Type de divergence</h4>
            <div className="space-y-2">
              {divergenceTypes.map(type => (
                <div key={type.id} className="flex items-start gap-2">
                  <input
                    type="radio"
                    id={type.id}
                    name="divergenceType"
                    value={type.id}
                    checked={selectedDivergence === type.id}
                    onChange={() => setSelectedDivergence(type.id)}
                    className="mt-0.5"
                  />
                  <div>
                    <label htmlFor={type.id} className="text-sm font-medium cursor-pointer">
                      {type.label}
                    </label>
                    <p className="text-xs text-gray-500">{type.description}</p>
                  </div>
                </div>
              ))}
            </div>
            {errors.general && (
              <p className="text-xs text-red-500 mt-1">{errors.general}</p>
            )}
          </div>

          {/* État civil corrigé */}
          <div className="mb-4">
            <h4 className="text-sm font-medium mb-2">État civil corrigé</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">Nom</label>
                <input
                  type="text"
                  name="nom"
                  value={correctedData.nom}
                  onChange={handleInputChange}
                  className={`w-full px-2 py-1 text-sm border rounded ${errors.nom ? 'border-red-500' : ''} ${!isFieldEditable('nom') ? 'bg-gray-100' : ''}`}
                  disabled={!isFieldEditable('nom')}
                />
                {errors.nom && <p className="text-xs text-red-500 mt-0.5">{errors.nom}</p>}
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Prénom</label>
                <input
                  type="text"
                  name="prenom"
                  value={correctedData.prenom}
                  onChange={handleInputChange}
                  className={`w-full px-2 py-1 text-sm border rounded ${errors.prenom ? 'border-red-500' : ''} ${!isFieldEditable('prenom') ? 'bg-gray-100' : ''}`}
                  disabled={!isFieldEditable('prenom')}
                />
                {errors.prenom && <p className="text-xs text-red-500 mt-0.5">{errors.prenom}</p>}
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Date de naissance</label>
                <input
                  type="text"
                  name="dateNaissance"
                  value={correctedData.dateNaissance}
                  onChange={handleInputChange}
                  placeholder="JJ/MM/AAAA"
                  className={`w-full px-2 py-1 text-sm border rounded ${errors.dateNaissance ? 'border-red-500' : ''} ${!isFieldEditable('dateNaissance') ? 'bg-gray-100' : ''}`}
                  disabled={!isFieldEditable('dateNaissance')}
                />
                {errors.dateNaissance && <p className="text-xs text-red-500 mt-0.5">{errors.dateNaissance}</p>}
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Lieu de naissance</label>
                <input
                  type="text"
                  name="lieuNaissance"
                  value={correctedData.lieuNaissance}
                  onChange={handleInputChange}
                  className={`w-full px-2 py-1 text-sm border rounded ${errors.lieuNaissance ? 'border-red-500' : ''} ${!isFieldEditable('lieuNaissance') ? 'bg-gray-100' : ''}`}
                  disabled={!isFieldEditable('lieuNaissance')}
                />
                {errors.lieuNaissance && <p className="text-xs text-red-500 mt-0.5">{errors.lieuNaissance}</p>}
              </div>
              {/* Ajoutez d'autres champs selon besoin */}
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={resetEtatCivil}
              className="px-3 py-1 text-sm text-gray-600 border rounded hover:bg-gray-50"
            >
              Annuler
            </button>
            <button
              type="button"
              onClick={validateDivergence}
              className="px-3 py-1 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 flex items-center gap-1"
            >
              <Check className="w-4 h-4" />
              Valider la correction
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EtatCivilPanel;