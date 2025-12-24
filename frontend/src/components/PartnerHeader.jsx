import { AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';

/**
 * Bloc INSTRUCTIONS à afficher en haut du contenu du modal
 * (RECHERCHE est déjà affichée dans PartnerDemandesHeader)
 */
const PartnerInstructions = ({ instructions }) => {
  if (!instructions) return null;
  
  return (
    <div className="mb-6 bg-amber-50 border-2 border-amber-400 rounded-lg p-4 shadow-md">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-lg font-bold text-amber-900 mb-2">
            📋 INSTRUCTIONS
          </h3>
          <div className="text-amber-900 whitespace-pre-wrap leading-relaxed">
            {instructions}
          </div>
        </div>
      </div>
    </div>
  );
};

PartnerInstructions.propTypes = {
  instructions: PropTypes.string,
};

export default PartnerInstructions;
