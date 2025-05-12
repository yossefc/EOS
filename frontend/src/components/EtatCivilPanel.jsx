import  { useState } from 'react';
import PropTypes from 'prop-types';
import { AlertCircle, Save, X } from 'lucide-react';
import { COUNTRIES } from './countryData';

// Définition des PropTypes séparément, avant d'utiliser le composant
const EtatCivilPanelPropTypes = {
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
  setFormData: PropTypes.func.isRequired,
  onValidate: PropTypes.func
};

const EtatCivilPanel = ({ originalData, formData,  onValidate }) => {
  // État pour les champs corrigés
  const [correctedData, setCorrectedData] = useState({
    qualite: formData.qualite_corrigee || '',
    nom: formData.nom_corrige || '',
    prenom: formData.prenom_corrige || '',
    dateNaissance: formData.date_naissance_corrigee || '',
    lieuNaissance: formData.lieu_naissance_corrige || '',
    codePostalNaissance: formData.code_postal_naissance_corrige || '',
    paysNaissance: formData.pays_naissance_corrige || '',
    nomPatronymique: formData.nom_patronymique_corrige || ''
  });

  // État pour le type de divergence
  const [divergenceType, setDivergenceType] = useState(formData.type_divergence || '');
  const [showHelp, setShowHelp] = useState(false);

  // Gestion des changements
  const handleChange = (e) => {
    const { name, value } = e.target;
    setCorrectedData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Validation des corrections
  const handleValidate = () => {
    if (onValidate) {
      onValidate(correctedData, divergenceType);
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4">
      <h3 className="font-medium mb-4 flex items-center justify-between">
        <span>État civil d&apos;origine vs corrigé</span>
        <button
          type="button"
          onClick={() => setShowHelp(!showHelp)}
          className="text-blue-500 text-sm hover:underline"
        >
          {showHelp ? 'Masquer l\'aide' : 'Afficher l\'aide'}
        </button>
      </h3>

      {showHelp && (
        <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg mb-4">
          <h4 className="font-medium text-blue-800 mb-2">Aide sur les corrections d&apos;état civil</h4>
          <p className="text-sm text-blue-700 mb-2">
            Ce panneau vous permet de corriger les informations d&apos;état civil lorsque vous constatez de légères différences
            entre l&apos;état civil fourni et celui que vous avez retrouvé.
          </p>
          <ul className="list-disc list-inside text-sm text-blue-700 space-y-1 ml-2">
            <li>Utilisez le champ &quot;Type de divergence&quot; pour indiquer la nature des corrections</li>
            <li>Ne modifiez que les champs qui nécessitent une correction</li>
            <li>Les champs laissés vides conserveront les valeurs d&apos;origine</li>
            <li>Validez vos corrections avec le bouton &quot;Valider les corrections&quot;</li>
            <li>N&apos;oubliez pas d&apos;indiquer les différences constatées dans les mémos</li>
          </ul>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        {/* Colonne État civil d'origine */}
        <div className="border rounded-lg p-4 bg-gray-50">
          <h4 className="font-medium mb-3">État civil d&apos;origine</h4>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-500 mb-1">Qualité</p>
              <p className="font-medium">{originalData.qualite || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Nom</p>
              <p className="font-medium">{originalData.nom || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Prénom</p>
              <p className="font-medium">{originalData.prenom || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Nom patronymique</p>
              <p className="font-medium">{originalData.nomPatronymique || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Date de naissance</p>
              <p className="font-medium">{originalData.dateNaissance || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Lieu de naissance</p>
              <p className="font-medium">{originalData.lieuNaissance || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Code postal naissance</p>
              <p className="font-medium">{originalData.codePostalNaissance || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500 mb-1">Pays de naissance</p>
              <p className="font-medium">{originalData.paysNaissance || '-'}</p>
            </div>
          </div>
        </div>

        {/* Colonne État civil corrigé */}
        <div className="border rounded-lg p-4">
          <h4 className="font-medium mb-3">État civil corrigé</h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Qualité</label>
              <input
                type="text"
                name="qualite"
                value={correctedData.qualite}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.qualite || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Nom</label>
              <input
                type="text"
                name="nom"
                value={correctedData.nom}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.nom || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Prénom</label>
              <input
                type="text"
                name="prenom"
                value={correctedData.prenom}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.prenom || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Nom patronymique</label>
              <input
                type="text"
                name="nomPatronymique"
                value={correctedData.nomPatronymique}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.nomPatronymique || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Date de naissance</label>
              <input
                type="text"
                name="dateNaissance"
                value={correctedData.dateNaissance}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.dateNaissance || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Lieu de naissance</label>
              <input
                type="text"
                name="lieuNaissance"
                value={correctedData.lieuNaissance}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.lieuNaissance || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Code postal naissance</label>
              <input
                type="text"
                name="codePostalNaissance"
                value={correctedData.codePostalNaissance}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
                placeholder={originalData.codePostalNaissance || ""}
              />
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-1">Pays de naissance</label>
              <select
                name="paysNaissance"
                value={correctedData.paysNaissance}
                onChange={handleChange}
                className="w-full p-2 border rounded-md"
              >
                <option value="">Sélectionner un pays</option>
                {COUNTRIES.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Type de divergence */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Type de divergence
        </label>
        <select
          value={divergenceType}
          onChange={(e) => setDivergenceType(e.target.value)}
          className="w-full p-2 border rounded-md"
        >
          <option value="">Sélectionner le type de divergence</option>
          <option value="Orthographe">Erreur d&apos;orthographe</option>
          <option value="InversionPrenom">Inversion des prénoms</option>
          <option value="DateNaissance">Date de naissance erronée</option>
          <option value="LieuNaissance">Lieu de naissance erroné</option>
          <option value="NomUsage">Différence nom d&apos;usage/nom de naissance</option>
          <option value="Autre">Autre divergence</option>
        </select>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-yellow-700 mb-1">Important</h4>
            <p className="text-sm text-yellow-600">
              Les modifications d&apos;état civil doivent être justifiées dans les mémos. Assurez-vous de bien documenter
              les divergences constatées entre l&apos;état civil fourni et celui que vous avez retrouvé.
            </p>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          type="button"
          onClick={() => {
            setCorrectedData({
              qualite: '',
              nom: '',
              prenom: '',
              dateNaissance: '',
              lieuNaissance: '',
              codePostalNaissance: '',
              paysNaissance: '',
              nomPatronymique: ''
            });
            setDivergenceType('');
          }}
          className="flex items-center gap-1 px-4 py-2 text-red-600 bg-red-50 rounded-md hover:bg-red-100"
        >
          <X className="w-4 h-4" />
          <span>Réinitialiser</span>
        </button>

        <button
          type="button"
          onClick={handleValidate}
          className="flex items-center gap-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          disabled={!divergenceType}
        >
          <Save className="w-4 h-4" />
          <span>Valider les corrections</span>
        </button>
      </div>
    </div>
  );
};

// Assigner les propTypes après la définition du composant
EtatCivilPanel.propTypes = EtatCivilPanelPropTypes;

export default EtatCivilPanel;