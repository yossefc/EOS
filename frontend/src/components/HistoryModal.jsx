import { useState, useEffect, useCallback } from 'react';
import { X, History, RefreshCw, AlertCircle, User } from 'lucide-react';
import PropTypes from 'prop-types';
import config from '../config';

const API_URL = config.API_URL;

const FIELD_LABELS = {
  code_resultat: 'Resultat',
  elements_retrouves: 'Element retrouve',
  proximite: 'Proximite',
  date_retour: 'Date retour',
  adresse1: 'Adresse 1',
  adresse2: 'Adresse 2',
  adresse3: 'Adresse 3',
  adresse4: 'Adresse 4',
  code_postal: 'Code postal',
  ville: 'Ville',
  pays_residence: 'Pays',
  telephone_personnel: 'Telephone 1',
  telephone_chez_employeur: 'Telephone 2',
  nom_employeur: 'Nom employeur',
  telephone_employeur: 'Tel employeur',
  memo1: 'Memo 1',
  memo2: 'Memo 2',
  memo3: 'Memo 3',
  memo4: 'Memo 4',
  memo5: 'Memo 5',
  notes_personnelles: 'Memo personnel',
};

const formatDate = (value) => {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('fr-FR');
};

const renderEnqueteur = (enqueteur) => {
  if (!enqueteur) return '-';
  const fullName = `${enqueteur.prenom || ''} ${enqueteur.nom || ''}`.trim();
  const email = enqueteur.email ? ` (${enqueteur.email})` : '';
  const tel = enqueteur.telephone ? ` - ${enqueteur.telephone}` : '';
  return `${fullName || 'Non assigne'}${email}${tel}`;
};

const renderFilledFields = (fields) => {
  if (!fields || Object.keys(fields).length === 0) {
    return <span className="text-gray-400">-</span>;
  }

  const filteredEntries = Object.entries(fields).filter(([key]) => key !== 'notes_personnelles');
  if (filteredEntries.length === 0) {
    return <span className="text-gray-400">-</span>;
  }

  return (
    <div className="flex flex-wrap gap-1.5">
      {filteredEntries.map(([key, value]) => (
        <span
          key={key}
          className="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs text-blue-800"
          title={`${FIELD_LABELS[key] || key}: ${value}`}
        >
          <strong>{FIELD_LABELS[key] || key}:</strong> {String(value)}
        </span>
      ))}
    </div>
  );
};

const HistoryModal = ({ isOpen, onClose, donneeId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [historyData, setHistoryData] = useState(null);

  const fetchHistoryData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/api/donnees/${donneeId}/historique`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Erreur lors de la recuperation de l'historique");
      }

      setHistoryData(data.data || null);
    } catch (err) {
      setError(err.message || "Une erreur s'est produite");
    } finally {
      setLoading(false);
    }
  }, [donneeId]);

  useEffect(() => {
    if (isOpen && donneeId) {
      fetchHistoryData();
    }
  }, [isOpen, donneeId, fetchHistoryData]);

  if (!isOpen) return null;

  const rows = historyData?.enquetes_meme_nom || [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-7xl max-h-[90vh] overflow-hidden">
        <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-cyan-50 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0">
            <History className="w-6 h-6 text-blue-600" />
            <div className="min-w-0">
              <h2 className="text-lg font-semibold text-gray-800 truncate">
                {historyData?.contestation_header || 'Historique'}
              </h2>
              <p className="text-sm text-gray-600 truncate">
                Nom: <strong>{historyData?.nom || '-'}</strong>
                {historyData?.prenom ? <> | Prenom: <strong>{historyData.prenom}</strong></> : null}
                {' '}| Total: <strong>{historyData?.count || 0}</strong>{' '}
                {historyData?.est_contestation ? (
                  <span className="ml-2 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-semibold text-amber-800">
                    Contestation
                  </span>
                ) : null}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
            aria-label="Fermer"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-4 overflow-y-auto max-h-[calc(90vh-130px)]">
          {loading ? (
            <div className="flex items-center justify-center py-8 gap-2 text-gray-600">
              <RefreshCw className="w-5 h-5 animate-spin" />
              Chargement...
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 text-red-700">
              <AlertCircle className="w-5 h-5 mt-0.5" />
              <span>{error}</span>
            </div>
          ) : rows.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Aucune enquete trouvee pour ce nom.
            </div>
          ) : (
            <div className="overflow-x-auto border rounded-lg">
              <table className="min-w-full text-sm">
                <thead className="bg-gray-50 text-gray-700">
                  <tr>
                    <th className="px-3 py-2 text-left">Date</th>
                    <th className="px-3 py-2 text-left">Client</th>
                    <th className="px-3 py-2 text-left">Dossier</th>
                    <th className="px-3 py-2 text-left">Nom / Prenom</th>
                    <th className="px-3 py-2 text-left">Element demande</th>
                    <th className="px-3 py-2 text-left">Resultat</th>
                    <th className="px-3 py-2 text-left">Element retrouve</th>
                    <th className="px-3 py-2 text-left">Memo personnel</th>
                    <th className="px-3 py-2 text-right">Montant</th>
                    <th className="px-3 py-2 text-left">Enqueteur</th>
                    <th className="px-3 py-2 text-left">Donnees saisies</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {rows.map((row, idx) => (
                    <tr key={row.id} className={`align-top ${idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}`}>
                      <td className="px-3 py-2 whitespace-nowrap">{formatDate(row.date)}</td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span className="inline-flex items-center rounded-full bg-indigo-50 border border-indigo-200 px-2 py-0.5 text-xs font-semibold text-indigo-700">
                          {row.client_nom || `Client ${row.client_id}`}
                        </span>
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        #{row.id} {row.numeroDossier ? `(${row.numeroDossier})` : ''}
                      </td>
                      <td className="px-3 py-2">
                        <div className="font-medium text-gray-800">{row.nom || '-'}</div>
                        <div className="text-gray-500">{row.prenom || '-'}</div>
                      </td>
                      <td className="px-3 py-2">{row.element_demandes || '-'}</td>
                      <td className="px-3 py-2 font-semibold">{row.code_resultat || '-'}</td>
                      <td className="px-3 py-2">{row.elements_retrouves || '-'}</td>
                      <td className="px-3 py-2 max-w-xs">
                        {row.memo_personnel ? (
                          <span className="line-clamp-3 whitespace-pre-wrap" title={row.memo_personnel}>
                            {row.memo_personnel}
                          </span>
                        ) : (
                          '-'
                        )}
                      </td>
                      <td className="px-3 py-2 text-right whitespace-nowrap">
                        {row.montant_eos != null ? (
                          <div>
                            <div className="font-semibold text-blue-700">{row.montant_eos.toFixed(2)} €</div>
                            {row.montant_enqueteur != null && (
                              <div className="text-xs text-green-600">{row.montant_enqueteur.toFixed(2)} € enq.</div>
                            )}
                          </div>
                        ) : <span className="text-gray-400">-</span>}
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex items-start gap-2">
                          <User className="w-4 h-4 mt-0.5 text-gray-400" />
                          <span>{renderEnqueteur(row.enqueteur)}</span>
                        </div>
                      </td>
                      <td className="px-3 py-2">
                        {renderFilledFields(row.donnee_enqueteur_saisie)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

HistoryModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  donneeId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
};

export default HistoryModal;
