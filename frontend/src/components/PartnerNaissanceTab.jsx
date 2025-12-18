import { useState, useCallback } from 'react';
import { Calendar, MapPin, Loader2 } from 'lucide-react';
import axios from 'axios';
import PropTypes from 'prop-types';

/**
 * Onglet spécifique PARTNER pour la saisie de la date et du lieu de naissance mis à jour
 */
const PartnerNaissanceTab = ({ formData, handleInputChange }) => {
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Recherche d'adresse pour le lieu de naissance
  const searchLieuNaissance = useCallback(async (query) => {
    if (query.length > 2) {
      setIsLoading(true);
      try {
        const response = await axios.get(
          `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&type=municipality&limit=5`
        );
        if (response.data.features?.length > 0) {
          const villes = response.data.features.map(feature => ({
            ville: feature.properties.city,
            codePostal: feature.properties.postcode,
            label: `${feature.properties.city} (${feature.properties.postcode})`
          }));
          setSuggestions(villes);
        }
      } catch (error) {
        console.error('Erreur lors de la recherche de ville:', error);
      } finally {
        setIsLoading(false);
      }
    } else {
      setSuggestions([]);
    }
  }, []);

  const handleLieuNaissanceChange = (e) => {
    const value = e.target.value;
    handleInputChange(e);
    searchLieuNaissance(value);
  };

  const selectVille = (ville) => {
    // Créer un événement synthétique pour handleInputChange
    const syntheticEvent = {
      target: {
        name: 'lieuNaissance_maj',
        value: ville.ville
      }
    };
    handleInputChange(syntheticEvent);
    setSuggestions([]);
  };

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
        <p className="text-sm text-blue-800">
          <strong>Pour PARTNER uniquement :</strong> Saisissez ici la date et le lieu de naissance mis à jour suite à votre enquête.
        </p>
      </div>

      {/* Date de naissance mise à jour */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Calendar className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Date de naissance (mise à jour)
          </h3>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Choisir une date
          </label>
          <input
            type="date"
            name="dateNaissance_maj"
            value={formData.dateNaissance_maj || ''}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="mt-2 text-xs text-gray-500">
            Sélectionnez la date de naissance telle que retrouvée pendant l&apos;enquête
          </p>
        </div>
      </div>

      {/* Lieu de naissance mis à jour */}
      <div className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <MapPin className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">
            Lieu de naissance (mise à jour)
          </h3>
        </div>
        
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Lieu de naissance
          </label>
          <div className="relative">
            <input
              type="text"
              name="lieuNaissance_maj"
              value={formData.lieuNaissance_maj || ''}
              onChange={handleLieuNaissanceChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Commencez à taper le nom de la ville..."
              autoComplete="off"
            />
            {isLoading && (
              <div className="absolute right-3 top-3">
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
              </div>
            )}
          </div>
          
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {suggestions.map((ville, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => selectVille(ville)}
                  className="w-full px-4 py-2 text-left hover:bg-blue-50 focus:bg-blue-50 focus:outline-none border-b last:border-b-0"
                >
                  <div className="font-medium text-gray-900">{ville.ville}</div>
                  <div className="text-sm text-gray-500">{ville.codePostal}</div>
                </button>
              ))}
            </div>
          )}
          
          <p className="mt-2 text-xs text-gray-500">
            L&apos;autocomplétion vous aide à trouver la ville exacte
          </p>
        </div>
      </div>
    </div>
  );
};

PartnerNaissanceTab.propTypes = {
  formData: PropTypes.object.isRequired,
  handleInputChange: PropTypes.func.isRequired,
};

export default PartnerNaissanceTab;

