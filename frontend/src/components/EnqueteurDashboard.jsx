import { useState, useEffect, lazy, Suspense } from 'react';
import axios from 'axios';
import {
  Database, BarChart2, RefreshCw, AlertCircle, 
  Search, X, Pencil, History,  LogOut, DollarSign
} from 'lucide-react';
import config from '../config';
import PropTypes from 'prop-types';
EnqueteurDashboard.propTypes = {
  enqueteur: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    nom: PropTypes.string,
    prenom: PropTypes.string,
    email: PropTypes.string,
  }),
  onLogout: PropTypes.func.isRequired,
};


// Importation des composants
const UpdateModal = lazy(() => import('./UpdateModal'));
const HistoryModal = lazy(() => import('./HistoryModal'));
const EarningsViewer = lazy(() => import('./EarningsViewer'));

const API_URL = config.API_URL;

const EnqueteurDashboard = ({ enqueteur, onLogout }) => {
  // États pour les données
  const [enquetes, setEnquetes] = useState([]);
  const [filteredEnquetes, setFilteredEnquetes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // État pour l'onglet actif
  const [activeTab, setActiveTab] = useState('enquetes');
  
  // État pour les modals
  const [selectedDonnee, setSelectedDonnee] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  
  // État pour la recherche
  const [searchTerm, setSearchTerm] = useState('');
  
  // Récupérer les enquêtes assignées à l'enquêteur
  const fetchEnquetesAssignees = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Récupérer l'ID de l'enquêteur depuis localStorage ou props
      const enqueteurId = enqueteur?.id || localStorage.getItem('enqueteurId');
      
      if (!enqueteurId) {
        throw new Error("ID d'enquêteur non trouvé");
      }
      
      const response = await axios.get(`${API_URL}/api/donnees-complete`);
      
      if (response.data.success) {
        // Filtrer les enquêtes assignées à cet enquêteur
        const enquetesAssignees = response.data.data.filter(
          item => item.enqueteurId === enqueteurId || 
                  item.enqueteurId === parseInt(enqueteurId)
        );
        
        setEnquetes(enquetesAssignees);
        setFilteredEnquetes(enquetesAssignees);
      } else {
        throw new Error(response.data.error || "Erreur lors du chargement des données");
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
    } finally {
      setLoading(false);
    }
  };
  
  // Chargement initial
  useEffect(() => {
    fetchEnquetesAssignees();
  }, [enqueteur]);
  
  // Filtrer les enquêtes selon le terme de recherche
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredEnquetes(enquetes);
      return;
    }
    
    const lowerSearch = searchTerm.toLowerCase();
    const filteredResults = enquetes.filter(
      enquete => 
        (enquete.numeroDossier?.toLowerCase() || '').includes(lowerSearch) ||
        (enquete.nom?.toLowerCase() || '').includes(lowerSearch) ||
        (enquete.prenom?.toLowerCase() || '').includes(lowerSearch) ||
        (enquete.referenceDossier?.toLowerCase() || '').includes(lowerSearch)
    );
    
    setFilteredEnquetes(filteredResults);
  }, [searchTerm, enquetes]);
  
  // Ouvrir le modal de mise à jour
  const handleOpenUpdateModal = (donnee) => {
    setSelectedDonnee(donnee);
    setShowUpdateModal(true);
  };
  
  // Ouvrir le modal d'historique
  const handleOpenHistoryModal = (donnee) => {
    setSelectedDonnee(donnee);
    setShowHistoryModal(true);
  };
  
  // Status display helper
  const getStatusDisplay = (code) => {
    switch (code) {
      case 'P': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Positif</span>;
      case 'N': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Négatif</span>;
      case 'H': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Confirmé</span>;
      case 'Z': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Annulé (agence)</span>;
      case 'I': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">Intraitable</span>;
      case 'Y': return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Annulé (EOS)</span>;
      default: return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-500">En attente</span>;
    }
  };
  
  // Calculer les statistiques
  const stats = {
    total: enquetes.length,
    enAttente: enquetes.filter(e => !e.code_resultat).length,
    positifs: enquetes.filter(e => e.code_resultat === 'P').length,
    negatifs: enquetes.filter(e => e.code_resultat === 'N').length,
    confirmes: enquetes.filter(e => e.code_resultat === 'H').length,
    autres: enquetes.filter(e => e.code_resultat && !['P', 'N', 'H'].includes(e.code_resultat)).length
  };
  
  return (
    <div className="container mx-auto p-4 max-w-7xl">
      {/* Header avec infos enquêteur et logout */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 text-blue-700 rounded-full w-12 h-12 flex items-center justify-center text-xl font-bold">
              {enqueteur?.prenom?.charAt(0) || ''}{enqueteur?.nom?.charAt(0) || ''}
            </div>
            <div>
              <h2 className="text-lg font-medium">{enqueteur?.prenom} {enqueteur?.nom}</h2>
              <p className="text-sm text-gray-500">{enqueteur?.email}</p>
            </div>
          </div>
          <button 
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
          >
            <LogOut className="w-4 h-4" />
            <span>Déconnexion</span>
          </button>
        </div>
      </div>
      
      {/* Navigation par onglets */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="flex space-x-6 -mb-px">
          <button
            onClick={() => setActiveTab('enquetes')}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'enquetes'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <Database className="w-5 h-5" />
            <span>Mes Enquêtes</span>
          </button>
          
          <button
            onClick={() => setActiveTab('statistiques')}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'statistiques'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <BarChart2 className="w-5 h-5" />
            <span>Statistiques & Revenus</span>
          </button>
        </nav>
      </div>
      
      {/* Contenu des onglets */}
      {activeTab === 'enquetes' ? (
        <>
          {/* Barre d'outils */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-gray-900">Mes Enquêtes Assignées</h2>
              <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full text-xs font-medium">
                {filteredEnquetes.length}
              </span>
            </div>
            
            <div className="flex gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                
                {searchTerm && (
                  <button
                    onClick={() => setSearchTerm('')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              
              <button
                onClick={fetchEnquetesAssignees}
                className="flex items-center gap-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>{loading ? 'Chargement...' : 'Actualiser'}</span>
              </button>
            </div>
          </div>
          
          {/* Messages d'erreur */}
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <p>{error}</p>
            </div>
          )}
          
          {/* Statistiques rapides */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white shadow rounded-lg p-4 border-l-4 border-blue-500">
              <p className="text-sm text-gray-500">Total</p>
              <p className="text-xl font-semibold">{stats.total}</p>
            </div>
            <div className="bg-white shadow rounded-lg p-4 border-l-4 border-yellow-500">
              <p className="text-sm text-gray-500">En attente</p>
              <p className="text-xl font-semibold text-yellow-500">{stats.enAttente}</p>
            </div>
            <div className="bg-white shadow rounded-lg p-4 border-l-4 border-green-500">
              <p className="text-sm text-gray-500">Positifs</p>
              <p className="text-xl font-semibold text-green-500">{stats.positifs}</p>
            </div>
            <div className="bg-white shadow rounded-lg p-4 border-l-4 border-red-500">
              <p className="text-sm text-gray-500">Négatifs</p>
              <p className="text-xl font-semibold text-red-500">{stats.negatifs}</p>
            </div>
            <div className="bg-white shadow rounded-lg p-4 border-l-4 border-purple-500">
              <p className="text-sm text-gray-500">Autres</p>
              <p className="text-xl font-semibold text-purple-500">{stats.confirmes + stats.autres}</p>
            </div>
          </div>
          
          {/* Tableau des enquêtes */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 bg-gray-50 border-b">
              <h3 className="font-medium">Liste de mes enquêtes</h3>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      N° Dossier
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nom
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Prénom
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Éléments
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan="7" className="px-6 py-4 text-center">
                        <div className="flex justify-center items-center">
                          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                          <span>Chargement...</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredEnquetes.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                        Aucune enquête ne vous est assignée pour le moment
                      </td>
                    </tr>
                  ) : (
                    filteredEnquetes.map((donnee) => (
                      <tr key={donnee.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {donnee.numeroDossier}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {donnee.nom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {donnee.prenom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {donnee.typeDemande === 'ENQ' ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Enquête
                            </span>
                          ) : donnee.typeDemande === 'CON' ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                              Contestation
                            </span>
                          ) : (
                            donnee.typeDemande
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {getStatusDisplay(donnee.code_resultat)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {donnee.elements_retrouves || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end space-x-2">
                            <button
                              onClick={() => handleOpenUpdateModal(donnee)}
                              className="text-blue-600 hover:text-blue-900 bg-blue-50 p-1.5 rounded-md"
                              title="Mettre à jour"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleOpenHistoryModal(donnee)}
                              className="text-amber-600 hover:text-amber-900 bg-amber-50 p-1.5 rounded-md"
                              title="Historique"
                            >
                              <History className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-6 gap-2">
            <DollarSign className="w-6 h-6 text-green-500" />
            <h2 className="text-xl font-bold">Mes Revenus et Statistiques</h2>
          </div>
          
          <Suspense fallback={<div className="flex justify-center py-12"><RefreshCw className="w-8 h-8 animate-spin text-blue-500" /></div>}>
            <EarningsViewer enqueteurId={enqueteur?.id || localStorage.getItem('enqueteurId')} />
          </Suspense>
        </div>
      )}
      
      {/* Modals */}
      {showUpdateModal && selectedDonnee && (
        <Suspense fallback={<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
        </div>}>
          <UpdateModal 
            isOpen={showUpdateModal}
            onClose={(refresh) => {
              setShowUpdateModal(false);
              if (refresh) fetchEnquetesAssignees();
            }}
            data={selectedDonnee}
          />
        </Suspense>
      )}
      
      {showHistoryModal && selectedDonnee && (
        <Suspense fallback={<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
        </div>}>
          <HistoryModal
            isOpen={showHistoryModal}
            onClose={() => setShowHistoryModal(false)}
            donneeId={selectedDonnee.id}
          />
        </Suspense>
      )}
    </div>
  );
};

export default EnqueteurDashboard;