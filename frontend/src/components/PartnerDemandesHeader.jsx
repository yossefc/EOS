import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import axios from 'axios';
import { CheckCircle, XCircle, Loader, AlertCircle, RefreshCw } from 'lucide-react';
import PropTypes from 'prop-types';
import config from '../config';

const API_URL = config.API_URL;

/**
 * Affichage des demandes PARTNER
 * Mode compact: uniquement les badges
 * Mode normal: badges + résumé + bouton refresh + info export
 */
const PartnerDemandesHeader = forwardRef(({ donneeId, compact = false }, ref) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const REQUEST_INFO = {
    ADDRESS: { label: 'Adresse', icon: '🏠' },
    PHONE: { label: 'Tél', icon: '📞' },
    EMPLOYER: { label: 'Employeur', icon: '🏢' },
    BANK: { label: 'Banque', icon: '🏦' },
    BIRTH: { label: 'Naissance', icon: '🎂' }
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

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Loader className="w-3 h-3 animate-spin" />
        <span>Chargement...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center gap-2 text-xs text-red-600">
        <AlertCircle className="w-3 h-3" />
        <span>{error}</span>
      </div>
    );
  }

  // Empty state
  if (requests.length === 0) {
    return (
      <span className="text-xs text-slate-400 italic">Aucune demande</span>
    );
  }

  const posCount = requests.filter(r => r.status === 'POS').length;
  const negCount = requests.filter(r => r.status === 'NEG').length;

  // ==================== MODE COMPACT ====================
  if (compact) {
    return (
      <div className="flex items-center gap-2 flex-wrap">
        {requests.map((request) => {
          const info = REQUEST_INFO[request.request_code] || { label: request.request_code, icon: '❓' };
          const isPositive = request.status === 'POS';

          return (
            <span
              key={request.id}
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border
                ${isPositive
                  ? 'bg-green-50 text-green-700 border-green-200'
                  : 'bg-red-50 text-red-700 border-red-200'}`}
              title={request.memo || ''}
            >
              <span>{info.icon}</span>
              <span>{info.label}</span>
              {isPositive ? (
                <CheckCircle className="w-3 h-3" />
              ) : (
                <XCircle className="w-3 h-3" />
              )}
            </span>
          );
        })}
      </div>
    );
  }

  // ==================== MODE NORMAL (complet) ====================
  return (
    <div className="space-y-2">
      {/* Résumé global */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="text-xs font-black text-slate-700 uppercase tracking-wider">
            Demandes ({requests.length})
          </span>
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-50 text-green-700 rounded-lg text-[10px] font-black border border-green-200">
              {posCount} POS
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-50 text-red-700 rounded-lg text-[10px] font-black border border-red-200">
              {negCount} NEG
            </span>
          </div>
        </div>

        <button
          onClick={handleRecalculate}
          className="flex items-center gap-1.5 px-3 py-1 text-[10px] font-bold bg-white text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-50 transition-all shadow-sm"
          title="Recalculer les statuts POS/NEG"
        >
          <RefreshCw className="w-3 h-3" />
          Mettre à jour
        </button>
      </div>

      {/* Liste des demandes */}
      <div className="flex flex-wrap gap-1.5">
        {requests.map((request) => {
          const info = REQUEST_INFO[request.request_code] || { label: request.request_code, icon: '❓' };
          const isPositive = request.status === 'POS';

          return (
            <div
              key={request.id}
              className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-lg border transition-all ${isPositive
                ? 'bg-green-50/30 border-green-200'
                : 'bg-red-50/30 border-red-200'
                }`}
              title={!isPositive && request.memo ? request.memo : ''}
            >
              <span className="text-sm">{info.icon}</span>
              <span className="text-[10px] font-bold text-slate-700">{info.label}</span>
              {isPositive ? (
                <CheckCircle className="w-3 h-3 text-green-600" />
              ) : (
                <XCircle className="w-3 h-3 text-red-600" />
              )}
            </div>
          );
        })}
      </div>

      {/* Info export */}
      <div className="text-[10px] text-slate-600 bg-slate-100/50 border border-slate-200 rounded-lg px-3 py-1.5 flex items-center gap-2">
        <span className="font-black text-slate-800 uppercase tracking-tighter">Export :</span>
        {posCount > 0 ? (
          <span className="text-green-700 font-bold">POS ✅</span>
        ) : (
          <span className="text-red-700 font-bold">NEG ❌</span>
        )}
        <span className="opacity-60 italic">
          ({posCount > 0 ? `Au moins 1 trouvée` : `Aucune trouvée`})
        </span>
      </div>
    </div>
  );
});

PartnerDemandesHeader.displayName = 'PartnerDemandesHeader';

PartnerDemandesHeader.propTypes = {
  donneeId: PropTypes.number.isRequired,
  compact: PropTypes.bool
};

export default PartnerDemandesHeader;