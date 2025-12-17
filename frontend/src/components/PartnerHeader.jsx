import { Info, AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';

/**
 * Composant pour afficher les informations spécifiques PARTNER
 * dans le header et en haut du modal
 */
const PartnerHeader = ({ recherche, instructions }) => {
  return (
    <>
      {/* RECHERCHE dans le header (sous les infos principales) */}
      {recherche && (
        <div className="mt-3 pt-3 border-t border-blue-400/30">
          <div className="flex items-start gap-2">
            <Info className="w-4 h-4 text-blue-200 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="text-xs text-blue-200 font-medium mb-1">
                Éléments demandés
              </div>
              <div className="text-sm text-white font-medium">
                {recherche}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

PartnerHeader.propTypes = {
  recherche: PropTypes.string,
  instructions: PropTypes.string,
};

/**
 * Bloc INSTRUCTIONS à afficher en haut du contenu du modal
 */
export const PartnerInstructions = ({ instructions }) => {
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

export default PartnerHeader;


