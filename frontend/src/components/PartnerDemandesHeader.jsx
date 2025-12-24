import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import axios from 'axios';
import { CheckCircle, XCircle, Loader, AlertCircle, RefreshCw } from 'lucide-react';
import PropTypes from 'prop-types';
import config from '../config';

const API_URL = config.API_URL;

/**
 * Affichage compact des demandes PARTNER dans l'en-tête du modal
 * Expose une méthode refresh() pour recharger les demandes depuis le parent
 */
const PartnerDemandesHeader = forwardRef(({ donneeId }, ref) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const REQUEST_INFO = {
    ADDRESS: { label: 'Adresse', icon: '🏠', color: 'blue' },
    PHONE: { label: 'Tél', icon: '📞', color: 'green' },
    EMPLOYER: { label: 'Employeur', icon: '🏢', color: 'purple' },
    BANK: { label: 'Banque', icon: '🏦', color: 'indigo' },
    BIRTH: { label: 'Naissance', icon: '🎂', color: 'pink' }
  };

  const fetchRequests = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/partner/case-requests/${donneeId}`);
      if (response.data.success) {
        setRequests(response.data.requests || []);
      }
    } catch (err) {
      console.error('Erreur chargement demandes:', err);
      setError('Erreur chargement');
    } finally {
      setLoading(false);
    }
  };

  // Exposer la méthode refresh au parent via ref
  useImperativeHandle(ref, () => ({
    refresh: fetchRequests
  }));

  useEffect(() => {
    if (donneeId) {
      fetchRequests();
    }
  }, [donneeId]);

  const handleRecalculate = async () => {
    try {
      const response = await axios.post(`${API_URL}/api/partner/case-requests/${donneeId}/recalculate`);
      if (response.data.success) {
        setRequests(response.data.requests || []);
      }
    } catch (err) {
      console.error('Erreur recalcul:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Loader className="w-4 h-4 animate-spin" />
        <span>Chargement demandes...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-600">
        <AlertCircle className="w-4 h-4" />
        <span>{error}</span>
      </div>
    );
  }

  if (requests.length === 0) {
    return (
      <div className="text-sm text-gray-500 italic">
        Aucune demande détectée dans RECHERCHE
      </div>
    );
  }

  const posCount = requests.filter(r => r.status === 'POS').length;
  const negCount = requests.filter(r => r.status === 'NEG').length;

  return (
    <div className="space-y-3">
      {/* Résumé global */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-base font-bold text-indigo-900">
            🔍 Demandes détectées ({requests.length})
          </span>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-bold shadow-sm">
              <CheckCircle className="w-4 h-4" />
              {posCount} POS
            </span>
            <span className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-100 text-red-800 rounded-full text-sm font-bold shadow-sm">
              <XCircle className="w-4 h-4" />
              {negCount} NEG
            </span>
          </div>
        </div>
        
        <button
          onClick={handleRecalculate}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg"
          title="Recalculer les statuts POS/NEG"
        >
          <RefreshCw className="w-4 h-4" />
          Recalculer
        </button>
      </div>

      {/* Liste des demandes */}
      <div className="flex flex-wrap gap-2">
        {requests.map((request) => {
          const info = REQUEST_INFO[request.request_code] || { 
            label: request.request_code, 
            icon: '❓', 
            color: 'gray' 
          };
          const isPositive = request.status === 'POS';
          
          return (
            <div
              key={request.id}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all duration-200 shadow-sm hover:shadow-md ${
                isPositive
                  ? 'bg-green-50 border-green-400 hover:bg-green-100'
                  : 'bg-red-50 border-red-400 hover:bg-red-100'
              }`}
              title={!isPositive && request.memo ? request.memo : ''}
            >
              <span className="text-lg">{info.icon}</span>
              <span className="text-sm font-semibold text-gray-900">{info.label}</span>
              {isPositive ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
            </div>
          );
        })}
      </div>

      {/* Info export */}
      <div className="text-sm text-gray-700 bg-indigo-50 border-2 border-indigo-300 rounded-lg px-4 py-2.5 shadow-sm">
        <span className="font-bold text-indigo-900">📄 Export :</span> 
        {posCount > 0 ? (
          <span className="text-green-700 font-bold"> Global POS ✅</span>
        ) : (
          <span className="text-red-700 font-bold"> Global NEG ❌</span>
        )}
        <span className="text-gray-600"> · {posCount > 0 ? `Au moins 1 demande trouvée` : `Toutes les demandes non trouvées`}</span>
      </div>
    </div>
  );
});

PartnerDemandesHeader.displayName = 'PartnerDemandesHeader';

PartnerDemandesHeader.propTypes = {
  donneeId: PropTypes.number.isRequired
};

export default PartnerDemandesHeader;

