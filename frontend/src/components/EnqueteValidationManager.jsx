import { useState, useEffect } from 'react';
import {
  RefreshCw, Check, AlertCircle, Search, 
  ClipboardCheck, Clock, FileX, Trash2
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteValidationManager = () => {
  // État pour les enquêtes en attente
  const [enquetesPending, setEnquetesPending] = useState([]);
  
  // État pour les enquêtes terminées (cachées localement)
  const [enquetesCompleted, setEnquetesCompleted] = useState([]);
  
  // États pour gérer le chargement et les erreurs
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // État pour le filtrage
  const [searchTerm, setSearchTerm] = useState('');
  
  // État pour l'onglet actif
  const [activeTab, setActiveTab] = useState('pending');
  
  // Récupérer les enquêtes en attente depuis le serveur
  const fetchPendingEnquetes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Vérifier si l'API existe, sinon utiliser des données simulées
      try {
        const response = await fetch(`${API_URL}/api/enquetes/pending`);
        
        if (response.status === 404) {
          console.warn("L'endpoint /api/enquetes/pending n'existe pas encore. Utilisation de données simulées.");
          // Simuler des données en attendant que l'API soit implémentée
          setEnquetesPending([
            {
              id: 1,
              numeroDossier: "ENQ00001",
              nom: "Dupont",
              prenom: "Jean",
              created_at: new Date().toISOString(),
              typeDemande: "ENQ"
            },
            {
              id: 2,
              numeroDossier: "ENQ00002",
              nom: "Martin",
              prenom: "Sophie",
              created_at: new Date().toISOString(),
              typeDemande: "ENQ"
            },
            {
              id: 3,
              numeroDossier: "CON00001",
              nom: "Durant",
              prenom: "Paul",
              created_at: new Date().toISOString(),
              typeDemande: "CON"
            }
          ]);
          return;
        }
        
        const data = await response.json();
        
        if (data.success) {
          setEnquetesPending(data.data);
        } else {
          throw new Error(data.error || "Erreur lors du chargement des enquêtes");
        }
      } catch (error) {
        if (error.message.includes("Unexpected token")) {
          console.warn("L'endpoint /api/enquetes/pending n'est pas encore implémenté. Utilisation de données simulées.");
          // Simuler des données en attendant que l'API soit implémentée
          setEnquetesPending([
            {
              id: 1,
              numeroDossier: "ENQ00001",
              nom: "Dupont",
              prenom: "Jean",
              created_at: new Date().toISOString(),
              typeDemande: "ENQ"
            },
            {
              id: 2,
              numeroDossier: "ENQ00002",
              nom: "Martin",
              prenom: "Sophie",
              created_at: new Date().toISOString(),
              typeDemande: "ENQ"
            },
            {
              id: 3,
              numeroDossier: "CON00001",
              nom: "Durant",
              prenom: "Paul",
              created_at: new Date().toISOString(),
              typeDemande: "CON"
            }
          ]);
        } else {
          console.error("Erreur:", error);
          setError("Erreur lors du chargement des enquêtes en attente: " + (error.message));
        }
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Récupérer les enquêtes terminées (uniquement si elles ne sont pas déjà en cache)
  const fetchCompletedEnquetes = async (forceRefresh = false) => {
    // Vérifier d'abord si nous avons des données en cache
    const cachedData = localStorage.getItem('completedEnquetes');
    
    if (cachedData && !forceRefresh) {
      // Utiliser les données du cache
      try {
        const parsedData = JSON.parse(cachedData);
        setEnquetesCompleted(parsedData);
        return;
      } catch (error) {
        console.error("Erreur lors de la lecture du cache:", error);
        // En cas d'erreur, continuer pour charger depuis le serveur
      }
    }
    
    // Si pas de cache ou forceRefresh, charger depuis le serveur
    try {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`${API_URL}/api/enquetes/completed`);
        
        if (response.status === 404) {
          console.warn("L'endpoint /api/enquetes/completed n'existe pas encore. Utilisation de données simulées.");
          // Simuler des données en attendant que l'API soit implémentée
          const simulatedData = [
            {
              id: 10,
              numeroDossier: "ENQ00010",
              nom: "Bernard",
              prenom: "Marie",
              confirmedAt: new Date().toISOString(),
              confirmedBy: "Directeur",
              typeDemande: "ENQ"
            },
            {
              id: 11,
              numeroDossier: "ENQ00011",
              nom: "Petit",
              prenom: "Thomas",
              confirmedAt: new Date().toISOString(),
              confirmedBy: "Directeur",
              typeDemande: "ENQ"
            }
          ];
          setEnquetesCompleted(simulatedData);
          
          // Sauvegarder dans le cache
          localStorage.setItem('completedEnquetes', JSON.stringify(simulatedData));
          return;
        }
        
        const data = await response.json();
        
        if (data.success) {
          setEnquetesCompleted(data.data);
          
          // Sauvegarder dans le cache
          localStorage.setItem('completedEnquetes', JSON.stringify(data.data));
        } else {
          throw new Error(data.error || "Erreur lors du chargement des enquêtes terminées");
        }
      } catch (error) {
        if (error.message.includes("Unexpected token")) {
          console.warn("L'endpoint /api/enquetes/completed n'est pas encore implémenté. Utilisation de données simulées.");
          // Simuler des données en attendant que l'API soit implémentée
          const simulatedData = [
            {
              id: 10,
              numeroDossier: "ENQ00010",
              nom: "Bernard",
              prenom: "Marie",
              confirmedAt: new Date().toISOString(),
              confirmedBy: "Directeur",
              typeDemande: "ENQ"
            },
            {
              id: 11,
              numeroDossier: "ENQ00011",
              nom: "Petit",
              prenom: "Thomas",
              confirmedAt: new Date().toISOString(),
              confirmedBy: "Directeur",
              typeDemande: "ENQ"
            }
          ];
          setEnquetesCompleted(simulatedData);
          
          // Sauvegarder dans le cache
          localStorage.setItem('completedEnquetes', JSON.stringify(simulatedData));
        } else {
          console.error("Erreur:", error);
          setError("Erreur lors du chargement des enquêtes terminées: " + (error.message));
        }
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Confirmer une enquête
  const confirmEnquete = async (enqueteId) => {
    try {
      setLoading(true);
      setError(null);
      
      // Comme l'API n'existe pas encore, simuler la confirmation
      console.warn("L'endpoint /api/enquetes/confirm n'existe pas encore. Simulation de la confirmation.");
      
      // Trouver l'enquête à confirmer
      const enqueteToConfirm = enquetesPending.find(e => e.id === enqueteId);
      
      if (!enqueteToConfirm) {
        setError("Enquête non trouvée");
        return;
      }
      
      // Créer une version confirmée
      const confirmedEnquete = {
        ...enqueteToConfirm,
        confirmedAt: new Date().toISOString(),
        confirmedBy: localStorage.getItem('userName') || 'Directeur'
      };
      
      // Mettre à jour les listes
      setEnquetesPending(prev => prev.filter(e => e.id !== enqueteId));
      setEnquetesCompleted(prev => [confirmedEnquete, ...prev]);
      
      // Mettre à jour le cache
      const cachedData = localStorage.getItem('completedEnquetes');
      let updatedCache = [];
      
      if (cachedData) {
        try {
          updatedCache = JSON.parse(cachedData);
          updatedCache = [confirmedEnquete, ...updatedCache];
        } catch (error) {
          console.error("Erreur lors de la mise à jour du cache:", error);
          updatedCache = [confirmedEnquete];
        }
      } else {
        updatedCache = [confirmedEnquete];
      }
      
      localStorage.setItem('completedEnquetes', JSON.stringify(updatedCache));
      
      setSuccess("Enquête confirmée avec succès");
      
      // Effacer le message de succès après 3 secondes
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
      
    } catch (error) {
      console.error("Erreur:", error);
      setError("Erreur lors de la confirmation: " + (error.message));
    } finally {
      setLoading(false);
    }
  };
  
  // Supprimer définitivement une enquête (pour les cas exceptionnels)
  const deleteEnquete = async (enqueteId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer définitivement cette enquête ?")) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Simulation en attendant que l'API soit implémentée
      console.warn("L'endpoint /api/enquetes/:id n'existe pas encore. Simulation de la suppression.");
      
      // Mettre à jour la liste des enquêtes en attente
      setEnquetesPending(prev => prev.filter(e => e.id !== enqueteId));
      
      setSuccess("Enquête supprimée avec succès");
      
      // Effacer le message de succès après 3 secondes
      setTimeout(() => {
        setSuccess(null);
      }, 3000);
      
    } catch (error) {
      console.error("Erreur:", error);
      setError("Erreur lors de la suppression: " + (error.message));
    } finally {
      setLoading(false);
    }
  };
  
  // Charger les données initiales
  useEffect(() => {
    fetchPendingEnquetes();
    fetchCompletedEnquetes();
  }, []);
  
  // Filtrer les enquêtes selon le terme de recherche
  const filteredPendingEnquetes = enquetesPending.filter(enquete => 
    searchTerm === '' || 
    enquete.numeroDossier?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    enquete.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    enquete.prenom?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const filteredCompletedEnquetes = enquetesCompleted.filter(enquete => 
    searchTerm === '' || 
    enquete.numeroDossier?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    enquete.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    enquete.prenom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    enquete.confirmedBy?.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  return (
    <div className="space-y-4">
      {/* En-tête avec titre et boutons */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <ClipboardCheck className="w-6 h-6 text-blue-500" />
          Validation des Enquêtes
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={() => {
              setActiveTab('pending');
              fetchPendingEnquetes();
            }}
            className="flex items-center gap-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Actualiser</span>
          </button>
          
          <button
            onClick={() => {
              setActiveTab('completed');
              fetchCompletedEnquetes(true);
            }}
            className="flex items-center gap-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Rafraîchir le cache</span>
          </button>
        </div>
      </div>
      
      {/* Messages d'erreur et de succès */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-center gap-2">
          <Check className="w-5 h-5 flex-shrink-0" />
          <p>{success}</p>
        </div>
      )}
      
      {/* Navigation par onglets */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('pending')}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'pending'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <Clock className="w-5 h-5" />
            <span>Enquêtes en attente</span>
            <span className="bg-blue-100 text-blue-600 py-0.5 px-2 rounded-full text-xs">
              {enquetesPending.length}
            </span>
          </button>
          
          <button
            onClick={() => setActiveTab('completed')}
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2
              ${activeTab === 'completed'
                ? 'border-green-500 text-green-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
          >
            <Check className="w-5 h-5" />
            <span>Enquêtes validées</span>
            <span className="bg-green-100 text-green-600 py-0.5 px-2 rounded-full text-xs">
              {enquetesCompleted.length}
            </span>
          </button>
        </nav>
      </div>
      
      {/* Barre de recherche */}
      <div className="flex items-center p-2 bg-white border rounded-lg">
        <Search className="w-5 h-5 text-gray-400 mr-2" />
        <input
          type="text"
          placeholder="Rechercher une enquête..."
          className="flex-1 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="text-gray-400 hover:text-gray-600"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
      
      {/* Contenu des onglets */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Onglet des enquêtes en attente */}
        {activeTab === 'pending' && (
          <div>
            <div className="p-4 bg-blue-50 border-b">
              <h3 className="font-medium">Enquêtes en attente de validation</h3>
              <p className="text-sm text-gray-600 mt-1">
                Ces enquêtes doivent être vérifiées et validées par un directeur.
              </p>
            </div>
            
            {loading && enquetesPending.length === 0 ? (
              <div className="flex justify-center items-center p-12">
                <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
              </div>
            ) : filteredPendingEnquetes.length === 0 ? (
              <div className="text-center p-12 text-gray-500">
                <FileX className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Aucune enquête en attente</p>
                <p className="mt-1">Toutes les enquêtes ont été validées ou le filtre ne donne aucun résultat.</p>
              </div>
            ) : (
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
                        Date de création
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredPendingEnquetes.map((enquete) => (
                      <tr key={enquete.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {enquete.numeroDossier}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.nom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.prenom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(enquete.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.typeDemande === 'ENQ' ? 'Enquête' : 
                           enquete.typeDemande === 'CON' ? 'Contestation' : 
                           enquete.typeDemande}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex space-x-2">
                            <button
                              onClick={() => confirmEnquete(enquete.id)}
                              className="text-green-600 hover:text-green-900 bg-green-100 px-3 py-1 rounded-md"
                              disabled={loading}
                            >
                              Confirmer
                            </button>
                            <button
                              onClick={() => deleteEnquete(enquete.id)}
                              className="text-red-600 hover:text-red-900 bg-red-100 px-3 py-1 rounded-md"
                              disabled={loading}
                            >
                              Supprimer
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
        
        {/* Onglet des enquêtes validées */}
        {activeTab === 'completed' && (
          <div>
            <div className="p-4 bg-green-50 border-b">
              <h3 className="font-medium">Enquêtes validées</h3>
              <p className="text-sm text-gray-600 mt-1">
                Ces enquêtes ont été validées par un directeur et sont affichées depuis le cache local.
              </p>
            </div>
            
            {loading ? (
              <div className="flex justify-center items-center p-12">
                <RefreshCw className="w-8 h-8 animate-spin text-green-500" />
              </div>
            ) : filteredCompletedEnquetes.length === 0 ? (
              <div className="text-center p-12 text-gray-500">
                <FileX className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-medium">Aucune enquête validée</p>
                <p className="mt-1">Aucune enquête na encore été validée, ou le filtre ne donne aucun résultat.</p>
              </div>
            ) : (
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
                        Date de validation
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confirmé par
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredCompletedEnquetes.map((enquete) => (
                      <tr key={enquete.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {enquete.numeroDossier}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.nom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.prenom}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(enquete.confirmedAt).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.confirmedBy}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {enquete.typeDemande === 'ENQ' ? 'Enquête' : 
                           enquete.typeDemande === 'CON' ? 'Contestation' : 
                           enquete.typeDemande}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default EnqueteValidationManager;