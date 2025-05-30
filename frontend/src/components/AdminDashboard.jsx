import  { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Check, X, RefreshCw, Calendar, User, FileText,
  CheckCircle, XCircle, Clock, AlertCircle
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const STATUT_LABELS = {
  'en_attente': { label: 'En attente', color: 'text-orange-600 bg-orange-50 border-orange-200', icon: Clock },
  'confirmee': { label: 'Confirmée', color: 'text-green-600 bg-green-50 border-green-200', icon: CheckCircle },
  'refusee': { label: 'Refusée', color: 'text-red-600 bg-red-50 border-red-200', icon: XCircle }
};

const CODE_RESULTAT_LABELS = {
  'P': 'Positif',
  'N': 'Négatif / NPA',
  'H': 'Confirmé',
  'Z': 'Annulé (agence)',
  'I': 'Intraitable',
  'Y': 'Annulé (EOS)'
};

const AdminDashboard = () => {
  const [enquetesAValider, setEnquetesAValider] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [loadingActions, setLoadingActions] = useState({});

  // Charger les enquêtes à valider
  const loadEnquetesAValider = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/enquetes/a-valider`);
      if (response.data.success) {
        setEnquetesAValider(response.data.data);
      } else {
        setError('Erreur lors du chargement des enquêtes');
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEnquetesAValider();
  }, []);

  // Valider une enquête (confirmer ou refuser)
  const validerEnquete = async (enqueteId, action) => {
    try {
      setLoadingActions(prev => ({ ...prev, [enqueteId]: action }));
      setError(null);
      setSuccess(null);

      const response = await axios.put(
        `${API_URL}/api/enquete/valider/${enqueteId}`,
        {
          action: action,
          admin_nom: 'Administrateur' // À remplacer par le nom réel de l'admin connecté
        }
      );

      if (response.data.success) {
        setSuccess(`Enquête ${action}e avec succès`);
        // Retirer l'enquête de la liste
        setEnquetesAValider(prev => prev.filter(e => e.id !== enqueteId));
      } else {
        setError(response.data.error || 'Erreur lors de la validation');
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError('Erreur lors de la validation de l\'enquête');
    } finally {
      setLoadingActions(prev => ({ ...prev, [enqueteId]: null }));
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 animate-spin" />
          <span>Chargement des enquêtes...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard Administrateur</h1>
              <p className="text-gray-600 mt-1">Validation des enquêtes terminées</p>
            </div>
            <button
              onClick={loadEnquetesAValider}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Actualiser</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="w-6 h-6 text-orange-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">En attente</p>
                <p className="text-2xl font-bold text-gray-900">{enquetesAValider.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Confirmées aujourdhui</p>
                <p className="text-2xl font-bold text-gray-900">-</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Refusées aujourdhui</p>
                <p className="text-2xl font-bold text-gray-900">-</p>
              </div>
            </div>
          </div>
        </div>

        {/* Liste des enquêtes */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900">
              Enquêtes à valider ({enquetesAValider.length})
            </h2>
          </div>

          {enquetesAValider.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">Aucune enquête en attente de validation</p>
              <p className="text-sm">Toutes les enquêtes ont été traitées.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Dossier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Demandeur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Enquêteur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Résultat
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Éléments
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Mis à jour
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {enquetesAValider.map((enquete) => {
                    const StatutIcon = STATUT_LABELS[enquete.statut_validation]?.icon || Clock;
                    const isProcessing = loadingActions[enquete.id];
                    
                    return (
                      <tr key={enquete.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {enquete.numeroDossier}
                              </div>
                              <div className="text-sm text-gray-500">
                                {enquete.typeDemande === 'ENQ' ? 'Enquête' : 'Contestation'}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {enquete.nom} {enquete.prenom}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <User className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-900">
                              {enquete.enqueteurNom}
                            </span>
                          </div>
                        </td>
                       <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                            <StatutIcon className="w-4 h-4 text-gray-400" />
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                            ${enquete.code_resultat === 'P' ? 'bg-green-100 text-green-800' :
                                enquete.code_resultat === 'N' ? 'bg-red-100 text-red-800' :
                                enquete.code_resultat === 'I' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-gray-100 text-gray-800'}`}>
                            {enquete.code_resultat} - {CODE_RESULTAT_LABELS[enquete.code_resultat] || enquete.code_resultat}
                            </span>
                        </div>
                        </td>

                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-900">
                            {enquete.elements_retrouves || '-'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-900">
                              {formatDate(enquete.updated_at)}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => validerEnquete(enquete.id, 'confirmer')}
                              disabled={isProcessing}
                              className={`inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white 
                                ${isProcessing === 'confirmer' 
                                  ? 'bg-gray-400 cursor-not-allowed' 
                                  : 'bg-green-600 hover:bg-green-700'} 
                                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors`}
                            >
                              {isProcessing === 'confirmer' ? (
                                <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                              ) : (
                                <Check className="w-3 h-3 mr-1" />
                              )}
                              Confirmer
                            </button>
                            
                            <button
                              onClick={() => validerEnquete(enquete.id, 'refuser')}
                              disabled={isProcessing}
                              className={`inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white 
                                ${isProcessing === 'refuser' 
                                  ? 'bg-gray-400 cursor-not-allowed' 
                                  : 'bg-red-600 hover:bg-red-700'} 
                                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors`}
                            >
                              {isProcessing === 'refuser' ? (
                                <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                              ) : (
                                <X className="w-3 h-3 mr-1" />
                              )}
                              Refuser
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
