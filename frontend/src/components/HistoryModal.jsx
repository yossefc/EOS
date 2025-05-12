import { useState, useEffect,useCallback } from 'react';
import axios from 'axios';
import { 
    X, Clock, AlertCircle, FileText, 
   CheckCircle, RefreshCw 
} from 'lucide-react';
import config from '../config';
import PropTypes from 'prop-types';

HistoryModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  donneeId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
};


const API_URL = config.API_URL;

const HistoryModal = ({ isOpen, onClose, donneeId }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [historyData, setHistoryData] = useState(null);
    

    
    const fetchHistoryData = useCallback(async () => {
        try {
          setLoading(true);
          setError(null);
          const response = await axios.get(`${API_URL}/api/donnees/${donneeId}/historique`);
          if (response.data.success) {
            setHistoryData(response.data.data);
          } else {
            throw new Error(response.data.error || "Erreur lors de la récupération de l'historique");
          }
        } catch (error) {
          console.error("Erreur:", error);
          setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
          setLoading(false);
        }
      }, [donneeId]);
      
      useEffect(() => {
        if (isOpen && donneeId) {
          fetchHistoryData();
        }
      }, [isOpen, donneeId, fetchHistoryData]);

    // Formater la date
    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('fr-FR');
    };
    
    if (!isOpen) return null;
    
    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-auto">
            <div className="bg-white rounded-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                {/* En-tête */}
                <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 p-4 rounded-t-xl sticky top-0 z-10">
                    <div className="flex justify-between items-start">
                        <div className="text-white">
                            <h2 className="text-xl font-bold">Historique du dossier</h2>
                            <p className="text-sm">Suivi des modifications et des contestations</p>
                        </div>
                        <button onClick={onClose} className="text-white/70 hover:text-white">
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>
                
                {/* Contenu */}
                <div className="p-6">
                    {loading ? (
                        <div className="flex justify-center items-center py-20">
                            <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
                        </div>
                    ) : error ? (
                        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                            <div className="flex items-center gap-2">
                                <AlertCircle className="w-5 h-5" />
                                <span>{error}</span>
                            </div>
                        </div>
                    ) : historyData ? (
                        <div className="space-y-6">
                            {/* Informations sur l'enquête originale si c'est une contestation */}
                            {historyData.est_contestation && historyData.enquete_originale && (
                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <h3 className="font-medium text-blue-800 flex items-center gap-2 mb-2">
                                        <FileText className="w-5 h-5" />
                                        Enquête originale contestée
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-gray-500">N° Dossier</p>
                                            <p className="font-medium">{historyData.enquete_originale.numeroDossier}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Type de demande</p>
                                            <p className="font-medium">{historyData.enquete_originale.typeDemande}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Nom et prénom</p>
                                            <p className="font-medium">{historyData.enquete_originale.nom} {historyData.enquete_originale.prenom}</p>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {/* Contestations associées si c'est une enquête originale */}
                            {!historyData.est_contestation && historyData.contestations && historyData.contestations.length > 0 && (
                                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                                    <h3 className="font-medium text-amber-800 flex items-center gap-2 mb-4">
                                        <AlertCircle className="w-5 h-5" />
                                        Contestations associées à cette enquête
                                    </h3>
                                    <div className="overflow-x-auto">
                                        <table className="min-w-full">
                                            <thead className="bg-amber-100">
                                                <tr>
                                                    <th className="px-4 py-2 text-left text-xs font-medium text-amber-800">N° Dossier</th>
                                                    <th className="px-4 py-2 text-left text-xs font-medium text-amber-800">Date</th>
                                                    <th className="px-4 py-2 text-left text-xs font-medium text-amber-800">Motif</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-amber-200">
                                                {historyData.contestations.map((contestation, index) => (
                                                    <tr key={index}>
                                                        <td className="px-4 py-2 text-sm">{contestation.numeroDossier}</td>
                                                        <td className="px-4 py-2 text-sm">{contestation.date || '-'}</td>
                                                        <td className="px-4 py-2 text-sm">{contestation.motif_detail || contestation.motif_code || '-'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            )}
                            
                            {/* Historique des modifications */}
                            <div className="border rounded-lg">
                                <h3 className="font-medium p-4 bg-gray-50 border-b">Historique des modifications</h3>
                                
                                {historyData.historique && historyData.historique.length > 0 ? (
                                    <div className="p-4">
                                        <div className="space-y-4">
                                            {historyData.historique.map((event, index) => (
                                                <div key={index} className="flex gap-4 pb-4 border-b last:border-0">
                                                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                                                        <Clock className="w-5 h-5 text-blue-600" />
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <h4 className="font-medium">{event.type}</h4>
                                                            <span className="text-sm text-gray-500">{formatDate(event.date)}</span>
                                                        </div>
                                                        <p className="text-gray-600 mt-1">{event.details}</p>
                                                        {event.user && (
                                                            <div className="text-sm text-gray-500 mt-1">
                                                                Par: {event.user}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : historyData.modifications && historyData.modifications.length > 0 ? (
                                    <div className="p-4">
                                        <div className="space-y-4">
                                            {historyData.modifications.map((mod, index) => (
                                                <div key={index} className="flex gap-4 pb-4 border-b last:border-0">
                                                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                                                        <CheckCircle className="w-5 h-5 text-green-600" />
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <h4 className="font-medium">Résultat d&apos;enquête</h4>
                                                            <span className="text-sm text-gray-500">{formatDate(mod.date)}</span>
                                                        </div>
                                                        <p className="text-gray-600 mt-1">
                                                            Code résultat: <span className="font-medium">{mod.code_resultat || 'Non défini'}</span>, 
                                                            Éléments retrouvés: <span className="font-medium">{mod.elements_retrouves || 'Non défini'}</span>
                                                        </p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="p-6 text-center text-gray-500">
                                        Aucune modification enregistrée pour cette enquête
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            Aucune donnée d&apos;historique disponible
                        </div>
                    )}
                </div>
                
                {/* Pied de page */}
                <div className="p-4 border-t flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
};

export default HistoryModal;