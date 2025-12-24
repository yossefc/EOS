import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Search } from 'lucide-react';
import PropTypes from 'prop-types';
import axios from 'axios';
import config from '../config';

/**
 * Composant pour afficher le statut des éléments demandés PARTNER
 * avec code couleur (vert = trouvé, rouge = non trouvé)
 */
const PartnerElementsStatus = ({ donneeId }) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (donneeId) {
      fetchRequests();
    }
  }, [donneeId]);

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
`${config.API_URL}/api/partner/case-requests/${donneeId}`      );
      if (response.data.success) {
        setRequests(response.data.requests || []);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des demandes:', error);
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const getRequestLabel = (code) => {
    const labels = {
      'ADDRESS': '📍 Adresse',
      'PHONE': '📞 Téléphone',
      'EMPLOYER': '💼 Employeur',
      'BANK': '🏦 Banque',
      'BIRTH': '🎂 Naissance'
    };
    return labels[code] || code;
  };

  const getStatusIcon = (status) => {
    if (status === 'POS') {
      return <CheckCircle className="w-5 h-5 text-green-600" />;
    } else if (status === 'NEG') {
      return <XCircle className="w-5 h-5 text-red-600" />;
    } else {
      return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusBgColor = (status) => {
    if (status === 'POS') {
      return 'bg-green-50 border-green-300';
    } else if (status === 'NEG') {
      return 'bg-red-50 border-red-300';
    } else {
      return 'bg-gray-50 border-gray-300';
    }
  };

  const getStatusTextColor = (status) => {
    if (status === 'POS') {
      return 'text-green-800';
    } else if (status === 'NEG') {
      return 'text-red-800';
    } else {
      return 'text-gray-800';
    }
  };

  const getStatusLabel = (status) => {
    if (status === 'POS') {
      return 'Trouvé';
    } else if (status === 'NEG') {
      return 'Non trouvé';
    } else {
      return 'En attente';
    }
  };

  if (loading) {
    return (
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-blue-600 animate-pulse" />
          <span className="text-blue-800">Chargement des éléments demandés...</span>
        </div>
      </div>
    );
  }

  if (requests.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border-2 border-blue-200 shadow-sm">
      <h4 className="font-bold text-blue-900 mb-3 text-base flex items-center gap-2">
        <Search className="w-5 h-5" />
        ÉLÉMENTS DEMANDÉS
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {requests.map((request) => (
          <div
            key={request.id}
            className={`rounded-lg p-3 border-2 transition-all duration-200 ${getStatusBgColor(request.status)}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <div className={`font-semibold text-sm mb-1 ${getStatusTextColor(request.status)}`}>
                  {getRequestLabel(request.request_code)}
                </div>
                <div className="flex items-center gap-2">
                  {getStatusIcon(request.status)}
                  <span className={`text-xs font-medium ${getStatusTextColor(request.status)}`}>
                    {getStatusLabel(request.status)}
                  </span>
                </div>
                {request.memo && request.status === 'NEG' && (
                  <div className="mt-2 text-xs text-red-700 bg-red-100 rounded px-2 py-1">
                    {request.memo}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-blue-200 text-xs text-blue-700">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-1">
            <CheckCircle className="w-4 h-4 text-green-600" />
            <span>Trouvé</span>
          </div>
          <div className="flex items-center gap-1">
            <XCircle className="w-4 h-4 text-red-600" />
            <span>Non trouvé</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4 text-gray-400" />
            <span>En attente</span>
          </div>
        </div>
      </div>
    </div>
  );
};

PartnerElementsStatus.propTypes = {
  donneeId: PropTypes.number.isRequired,
};

export default PartnerElementsStatus;

