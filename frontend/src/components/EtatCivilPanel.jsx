import { useState } from 'react';
import PropTypes from 'prop-types';
import { AlertCircle, Check, RotateCcw, HelpCircle, ChevronRight } from 'lucide-react';
import { COUNTRIES } from './countryData';

/**
 * Panel de comparaison/correction de l'état civil
 * Design compact avec 2 colonnes : Origine | Corrigé
 */
const EtatCivilPanel = ({ originalData, formData, onValidate }) => {
  const [correctedData, setCorrectedData] = useState({
    qualite: formData.qualite_corrigee || '',
    nom: formData.nom_corrige || '',
    prenom: formData.prenom_corrige || '',
    codePostalNaissance: formData.code_postal_naissance_corrige || '',
    paysNaissance: formData.pays_naissance_corrige || '',
    nomPatronymique: formData.nom_patronymique_corrige || ''
  });

  const [divergenceType, setDivergenceType] = useState(formData.type_divergence || '');
  const [showHelp, setShowHelp] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCorrectedData(prev => ({ ...prev, [name]: value }));
  };

  const handleValidate = () => {
    if (onValidate) {
      onValidate(correctedData, divergenceType);
    }
  };

  const handleReset = () => {
    setCorrectedData({
      qualite: '', nom: '', prenom: '',
      codePostalNaissance: '', paysNaissance: '', nomPatronymique: ''
    });
    setDivergenceType('');
  };

  // Champs à afficher
  const fields = [
    { key: 'qualite', label: 'Qualité', type: 'text' },
    { key: 'nom', label: 'Nom', type: 'text' },
    { key: 'prenom', label: 'Prénom', type: 'text' },
    { key: 'nomPatronymique', label: 'Nom patronymique', type: 'text' },
    { key: 'codePostalNaissance', label: 'CP naissance', type: 'text' },
    { key: 'paysNaissance', label: 'Pays naissance', type: 'select' },
  ];

  const divergenceOptions = [
    { value: '', label: 'Sélectionner...' },
    { value: 'Orthographe', label: 'Erreur d\'orthographe' },
    { value: 'InversionPrenom', label: 'Inversion des prénoms' },
    { value: 'DateNaissance', label: 'Date de naissance erronée' },
    { value: 'LieuNaissance', label: 'Lieu de naissance erroné' },
    { value: 'NomUsage', label: 'Différence nom d\'usage/naissance' },
    { value: 'Autre', label: 'Autre divergence' },
  ];

  return (
    <div className="space-y-4">
      {/* Header avec aide */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-700">Comparaison état civil</h3>
        <button
          type="button"
          onClick={() => setShowHelp(!showHelp)}
          className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
        >
          <HelpCircle className="w-3.5 h-3.5" />
          {showHelp ? 'Masquer l\'aide' : 'Aide'}
        </button>
      </div>

      {/* Aide (collapsible) */}
      {showHelp && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-700">
          <p className="mb-2">Corrigez les champs si vous constatez des différences avec l'état civil retrouvé :</p>
          <ul className="list-disc list-inside space-y-0.5 text-blue-600">
            <li>Ne modifiez que les champs nécessaires</li>
            <li>Champs vides = valeurs d'origine conservées</li>
            <li>Sélectionnez le type de divergence</li>
            <li>Documentez dans les mémos</li>
          </ul>
        </div>
      )}

      {/* Tableau comparatif */}
      <div className="border border-slate-200 rounded-lg overflow-hidden">
        {/* En-tête du tableau */}
        <div className="grid grid-cols-[1fr,2fr,auto,2fr] bg-slate-100 border-b border-slate-200">
          <div className="px-3 py-2 text-xs font-bold text-slate-500 uppercase">Champ</div>
          <div className="px-3 py-2 text-xs font-bold text-slate-500 uppercase">Origine</div>
          <div className="px-3 py-2"></div>
          <div className="px-3 py-2 text-xs font-bold text-slate-500 uppercase">Corrigé</div>
        </div>

        {/* Lignes */}
        {fields.map((field) => (
          <div
            key={field.key}
            className="grid grid-cols-[1fr,2fr,auto,2fr] border-b border-slate-100 last:border-b-0 hover:bg-slate-50/50"
          >
            {/* Label */}
            <div className="px-3 py-2 text-xs font-medium text-slate-600 flex items-center">
              {field.label}
            </div>

            {/* Valeur origine */}
            <div className="px-3 py-2 text-sm font-semibold text-slate-800 flex items-center bg-slate-50/50">
              {originalData[field.key] || <span className="text-slate-400">-</span>}
            </div>

            {/* Flèche */}
            <div className="px-2 py-2 flex items-center">
              <ChevronRight className="w-4 h-4 text-slate-300" />
            </div>

            {/* Input corrigé */}
            <div className="px-3 py-1.5 flex items-center">
              {field.type === 'select' ? (
                <select
                  name={field.key}
                  value={correctedData[field.key]}
                  onChange={handleChange}
                  className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded bg-white 
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">—</option>
                  {COUNTRIES.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  name={field.key}
                  value={correctedData[field.key]}
                  onChange={handleChange}
                  placeholder={originalData[field.key] || ''}
                  className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded bg-white 
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500
                             placeholder:text-slate-300"
                />
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer : Type divergence + Actions */}
      <div className="flex items-center gap-4 bg-slate-50 rounded-lg p-3 border border-slate-200">
        {/* Type de divergence */}
        <div className="flex items-center gap-2 flex-1">
          <label className="text-xs font-medium text-slate-600 whitespace-nowrap">Type de divergence :</label>
          <select
            value={divergenceType}
            onChange={(e) => setDivergenceType(e.target.value)}
            className="flex-1 px-2 py-1.5 text-sm border border-slate-200 rounded bg-white 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {divergenceOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>

        {/* Boutons */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-600 
                       bg-white border border-slate-200 rounded hover:bg-slate-50 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Réinitialiser
          </button>
          <button
            type="button"
            onClick={handleValidate}
            disabled={!divergenceType}
            className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-white 
                       bg-blue-600 rounded hover:bg-blue-700 transition-colors
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="w-3.5 h-3.5" />
            Valider corrections
          </button>
        </div>
      </div>

      {/* Note importante (compacte) */}
      <div className="flex items-start gap-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
        <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700">
          <strong>Important :</strong> Documentez les divergences dans l'onglet Commentaires.
        </p>
      </div>
    </div>
  );
};

EtatCivilPanel.propTypes = {
  originalData: PropTypes.shape({
    qualite: PropTypes.string,
    nom: PropTypes.string,
    prenom: PropTypes.string,
    dateNaissance: PropTypes.string,
    lieuNaissance: PropTypes.string,
    codePostalNaissance: PropTypes.string,
    paysNaissance: PropTypes.string,
    nomPatronymique: PropTypes.string
  }).isRequired,
  formData: PropTypes.object.isRequired,
  setFormData: PropTypes.func,
  onValidate: PropTypes.func
};

export default EtatCivilPanel;