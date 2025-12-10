import { useState, useEffect, lazy, Suspense,useCallback } from 'react';
import axios from 'axios';
import {
  Database, Search, Filter, RefreshCw, 
  AlertCircle, X,
  History,  FileDown, Pencil, Download, CalendarDays,
  CheckCircle, XCircle
} from 'lucide-react';
import config from '../config';

// Import other components but not EnqueteExporter directly
// This prevents circular dependencies
const UpdateModal = lazy(() => import('./UpdateModal'));
const HistoryModal = lazy(() => import('./HistoryModal'));

const API_URL = config.API_URL;

const DataViewer = () => {
  // State for data
  const [donnees, setDonnees] = useState([]);
  const [filteredDonnees, setFilteredDonnees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [itemsPerPage] = useState(500);
  
  // State for filtering and sorting
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    typeDemande: '',
    code_resultat: '',
    elements_retrouves: '',
    dateStart: '',
    dateEnd: '',
    showOnlyUnassigned: false
  });
  
  // State for modals
  const [selectedDonnee, setSelectedDonnee] = useState(null);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  
  // State for export
  const [exportingData, setExportingData] = useState(false);
  const [nonExporteesCount, setNonExporteesCount] = useState(0);
  
  // State for validation
  const [validating, setValidating] = useState(false);
  const [successMessage, setSuccessMessage] = useState(null);
  
  // State for enqueteurs
  const [enqueteurs, setEnqueteurs] = useState([]);
  
  // Fetch data with pagination and server-side filters
  const fetchData = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      // Construire les paramètres de requête avec filtres
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: itemsPerPage.toString()
      });
      
      // Ajouter les filtres à la requête
      if (searchTerm) params.append('search', searchTerm);
      if (filters.typeDemande) params.append('typeDemande', filters.typeDemande);
      if (filters.code_resultat) params.append('code_resultat', filters.code_resultat);
      if (filters.dateStart) params.append('date_reception_start', filters.dateStart);
      if (filters.dateEnd) params.append('date_reception_end', filters.dateEnd);
      if (filters.showOnlyUnassigned) params.append('enqueteurId', 'unassigned');
      
      const response = await axios.get(`${API_URL}/api/donnees-complete?${params.toString()}`);
      
      if (response.data.success) {
        setDonnees(response.data.data);
        setFilteredDonnees(response.data.data); // Pas de filtrage côté client, les données sont déjà filtrées
        setTotalItems(response.data.total || 0);
        setTotalPages(response.data.pages || 1);
      } else {
        throw new Error(response.data.error || "Erreur lors du chargement des données");
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
    } finally {
      setLoading(false);
    }
  }, [itemsPerPage, searchTerm, filters]);
  
  // Récupérer le nombre d'enquêtes non exportées
  const fetchNonExporteesCount = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/donnees/non-exportees/count`);
      if (response.data.success) {
        setNonExporteesCount(response.data.count);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération du compteur:", error);
      setNonExporteesCount(0);
    }
  };
  
  // Récupérer la liste des enquêteurs
  const fetchEnqueteurs = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/enqueteurs`);
      if (response.data.success) {
        setEnqueteurs(response.data.data || []);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des enquêteurs:", error);
      setEnqueteurs([]);
    }
  };
  
  // Charger les données initiales
  useEffect(() => {
    fetchNonExporteesCount();
    fetchEnqueteurs();
  }, []);
  
  // Recharger les données quand la page ou les filtres changent
  useEffect(() => {
    fetchData(currentPage);
  }, [currentPage, fetchData]);
  
  // Retourner à la page 1 quand les filtres ou la recherche changent
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    } else {
      fetchData(1);
    }
  }, [searchTerm, filters]);
  
  // Handle opening update modal
  const handleOpenUpdateModal = (donnee) => {
    setSelectedDonnee(donnee);
    setShowUpdateModal(true);
  };
  
  // Handle opening history modal
  const handleOpenHistoryModal = (donnee) => {
    setSelectedDonnee(donnee);
    setShowHistoryModal(true);
  };
  
  // Validation handlers
  const handleValiderEnquete = async (enqueteId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir valider cette enquête ? Elle sera archivée et apparaîtra dans l\'onglet Export des résultats.')) {
      return;
    }
    
    try {
      setValidating(true);
      setError(null);
      
      const response = await axios.put(`${API_URL}/api/enquetes/${enqueteId}/valider`, {
        utilisateur: 'Administrateur'
      });
      
      if (response.data.success) {
        setSuccessMessage('Enquête validée avec succès !');
        // Retirer l'enquête du tableau local
        setDonnees(prev => prev.filter(d => d.id !== enqueteId));
        setFilteredDonnees(prev => prev.filter(d => d.id !== enqueteId));
        
        // Effacer le message après 3 secondes
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        throw new Error(response.data.error || 'Erreur lors de la validation');
      }
    } catch (error) {
      console.error('Erreur:', error);
      setError(error.response?.data?.error || error.message || 'Erreur lors de la validation');
    } finally {
      setValidating(false);
    }
  };
  
  const handleRefuserEnquete = async (enqueteId) => {
    const motif = window.prompt('Motif du refus (optionnel):');
    if (motif === null) return; // User cancelled
    
    try {
      setValidating(true);
      setError(null);
      
      const response = await axios.put(`${API_URL}/api/enquetes/${enqueteId}/refuser`, {
        utilisateur: 'Administrateur',
        motif: motif || 'Aucun motif spécifié'
      });
      
      if (response.data.success) {
        setSuccessMessage('Enquête refusée, statut remis à en_attente');
        // Rafraîchir les données pour mettre à jour le statut
        await fetchData(currentPage);
        
        // Effacer le message après 3 secondes
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        throw new Error(response.data.error || 'Erreur lors du refus');
      }
    } catch (error) {
      console.error('Erreur:', error);
      setError(error.response?.data?.error || error.message || 'Erreur lors du refus');
    } finally {
      setValidating(false);
    }
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

  // Fonction pour déterminer la classe CSS de la ligne en fonction de la date butoir
  const getButoirRowClass = (dateButoir) => {
    if (!dateButoir) return '';
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const butoirDate = new Date(dateButoir);
    butoirDate.setHours(0, 0, 0, 0);
    
    // Calculer la différence en jours
    const diffTime = butoirDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      // Date dépassée - Rouge
      return 'bg-red-50 hover:bg-red-100';
    } else if (diffDays <= 7) {
      // Date dans moins de 7 jours - Orange
      return 'bg-orange-50 hover:bg-orange-100';
    } else {
      // Date dans plus de 7 jours - Vert
      return 'bg-green-50 hover:bg-green-100';
    }
  };

  // Fonction pour déterminer la classe CSS du texte de la date butoir
  const getButoirTextClass = (dateButoir) => {
    if (!dateButoir) return 'text-gray-700';
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const butoirDate = new Date(dateButoir);
    butoirDate.setHours(0, 0, 0, 0);
    
    // Calculer la différence en jours
    const diffTime = butoirDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      // Date dépassée - Rouge
      return 'text-red-700 font-bold';
    } else if (diffDays <= 7) {
      // Date dans moins de 7 jours - Orange
      return 'text-orange-700 font-semibold';
    } else {
      // Date dans plus de 7 jours - Vert
      return 'text-green-700 font-medium';
    }
  };

  // Fonction pour obtenir le badge de statut de la date butoir
  const getButoirBadge = (dateButoir) => {
    if (!dateButoir) return null;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const butoirDate = new Date(dateButoir);
    butoirDate.setHours(0, 0, 0, 0);
    
    // Calculer la différence en jours
    const diffTime = butoirDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
      return (
        <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
          Échue ({Math.abs(diffDays)} jour{Math.abs(diffDays) > 1 ? 's' : ''})
        </span>
      );
    } else if (diffDays === 0) {
      return (
        <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
          Aujourd'hui
        </span>
      );
    } else if (diffDays <= 7) {
      return (
        <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
          Dans {diffDays} jour{diffDays > 1 ? 's' : ''}
        </span>
      );
    } else {
      return (
        <span className="ml-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
          Dans {diffDays} jours
        </span>
      );
    }
  };
  
  // Handle export to Word
  // Handle enquêteur change
  const handleEnqueteurChange = async (donneeId, enqueteurId) => {
    try {
      const response = await axios.put(`${API_URL}/api/donnees/${donneeId}`, {
        enqueteurId: enqueteurId || null
      });
      
      if (response.data.success) {
        // Rafraîchir les données
        await fetchData(currentPage);
      } else {
        alert(response.data.error || "Erreur lors de l'assignation");
      }
    } catch (error) {
      console.error("Erreur lors de l'assignation de l'enquêteur:", error);
      alert(error.response?.data?.error || "Erreur lors de l'assignation de l'enquêteur");
    }
  };
  
  // Handle export to Word
  const handleExportWord = async () => {
    try {
      setExportingData(true);
      
      const response = await axios.post(`${API_URL}/api/export-enquetes`, {}, {
        responseType: 'blob'
      });
      
      // Vérifier si c'est un message JSON (aucune enquête à exporter)
      if (response.data.type === 'application/json') {
        const text = await response.data.text();
        const json = JSON.parse(text);
        alert(json.message || "Aucune nouvelle enquête à exporter");
        return;
      }
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Export_Nouvelles_Enquetes_${new Date().toISOString().split('T')[0]}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Rafraîchir le compteur après export
      await fetchNonExporteesCount();
      await fetchData(currentPage);
      
    } catch (error) {
      console.error("Erreur lors de l'export:", error);
      alert(error.response?.data?.error || "Erreur lors de l'export");
    } finally {
      setExportingData(false);
    }
  };
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <Database className="w-6 h-6 text-blue-500" />
          Exploration des Données
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={handleExportWord}
            disabled={exportingData || nonExporteesCount === 0}
            className="flex items-center gap-1 px-3 py-1.5 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            title={`Exporter les ${nonExporteesCount} nouvelles enquêtes non encore exportées`}
          >
            {exportingData ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            <span>Export Word ({nonExporteesCount} nouvelles)</span>
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1 px-3 py-1.5 border rounded hover:bg-gray-50"
          >
            <Filter className="w-4 h-4" />
            <span>Filtres</span>
          </button>
          <button
            onClick={() => fetchData(currentPage)}
            className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Actualiser</span>
          </button>
        </div>
      </div>
      
      {/* Success message */}
      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded flex items-center gap-2">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <p>{successMessage}</p>
          <button 
            onClick={() => setSuccessMessage(null)}
            className="ml-auto text-green-700 hover:text-green-900"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Search bar */}
      <div className="flex items-center p-2 bg-white border rounded">
        <Search className="w-5 h-5 text-gray-400 mr-2" />
        <input
          type="text"
          placeholder="Rechercher par numéro, nom, prénom..."
          className="flex-1 outline-none"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        
        {searchTerm && (
          <button
            onClick={() => setSearchTerm('')}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      
      {/* Filters */}
      {showFilters && (
        <div className="bg-gray-50 border rounded p-4 space-y-4">
          <h3 className="font-medium">Filtres de recherche</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Type de demande
              </label>
              <select
                value={filters.typeDemande}
                onChange={(e) => setFilters({...filters, typeDemande: e.target.value})}
                className="w-full p-2 border rounded"
              >
                <option value="">Tous</option>
                <option value="ENQ">Enquête</option>
                <option value="CON">Contestation</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Code résultat
              </label>
              <select
                value={filters.code_resultat}
                onChange={(e) => setFilters({...filters, code_resultat: e.target.value})}
                className="w-full p-2 border rounded"
              >
                <option value="">Tous</option>
                <option value="P">Positif (P)</option>
                <option value="N">Négatif (N)</option>
                <option value="H">Confirmé (H)</option>
                <option value="Z">Annulé agence (Z)</option>
                <option value="I">Intraitable (I)</option>
                <option value="Y">Annulé EOS (Y)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Éléments retrouvés
              </label>
              <select
                value={filters.elements_retrouves}
                onChange={(e) => setFilters({...filters, elements_retrouves: e.target.value})}
                className="w-full p-2 border rounded"
              >
                <option value="">Tous</option>
                <option value="A">Adresse (A)</option>
                <option value="T">Téléphone (T)</option>
                <option value="B">Banque (B)</option>
                <option value="E">Employeur (E)</option>
                <option value="R">Revenus (R)</option>
                <option value="D">Décès (D)</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date début
              </label>
              <input
                type="date"
                value={filters.dateStart}
                onChange={(e) => setFilters({...filters, dateStart: e.target.value})}
                className="w-full p-2 border rounded"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Date fin
              </label>
              <input
                type="date"
                value={filters.dateEnd}
                onChange={(e) => setFilters({...filters, dateEnd: e.target.value})}
                className="w-full p-2 border rounded"
              />
            </div>
          </div>
          
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.showOnlyUnassigned}
                onChange={(e) => setFilters({...filters, showOnlyUnassigned: e.target.checked})}
                className="rounded text-blue-600"
              />
              <span className="ml-2 text-sm text-gray-700">
                Afficher uniquement les enquêtes non assignées
              </span>
            </label>
          </div>
          
          <div className="flex justify-end">
            <button
              onClick={() => setFilters({
                typeDemande: '',
                code_resultat: '',
                elements_retrouves: '',
                dateStart: '',
                dateEnd: '',
                showOnlyUnassigned: false
              })}
              className="px-4 py-2 border text-gray-700 rounded-md hover:bg-gray-50"
            >
              Réinitialiser
            </button>
          </div>
        </div>
      )}
      
      {/* Data table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-4 border-b bg-gray-50 flex justify-between items-center">
          <div>
            <h3 className="font-medium">Liste des dossiers</h3>
            <p className="text-sm text-gray-500 mt-1">
              Page {currentPage} sur {totalPages} ({totalItems} dossiers au total)
            </p>
          </div>
          <div>
            {loading && <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />}
          </div>
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
                  Date Butoir
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Éléments
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Enquêteur
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading && filteredDonnees.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-6 py-4 text-center">
                    <div className="flex justify-center items-center">
                      <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                      <span>Chargement...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredDonnees.length === 0 ? (
                <tr>
                  <td colSpan="9" className="px-6 py-4 text-center text-gray-500">
                    Aucun résultat trouvé
                  </td>
                </tr>
              ) : (
                filteredDonnees.map((donnee) => (
                  <tr key={donnee.id} className={`${getButoirRowClass(donnee.date_butoir)} transition-colors`}>
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {donnee.date_butoir ? (
                        <div className="flex items-center gap-1">
                          <span className={`inline-flex items-center gap-1 ${getButoirTextClass(donnee.date_butoir)}`}>
                            <CalendarDays className="w-4 h-4" />
                            {new Date(donnee.date_butoir).toLocaleDateString('fr-FR')}
                          </span>
                          {getButoirBadge(donnee.date_butoir)}
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {donnee.elements_retrouves || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <select
                        value={donnee.enqueteurId || ''}
                        onChange={(e) => handleEnqueteurChange(donnee.id, e.target.value)}
                        className="block w-full px-2 py-1 text-sm border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        <option value="">Non assigné</option>
                        {enqueteurs.map((enq) => (
                          <option key={enq.id} value={enq.id}>
                            {enq.prenom} {enq.nom}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        {/* Boutons de validation - affichés seulement si l'enquête a une réponse */}
                        {donnee.can_validate && (
                          <>
                            <button
                              onClick={() => handleValiderEnquete(donnee.id)}
                              disabled={validating}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                              title="Valider"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleRefuserEnquete(donnee.id)}
                              disabled={validating}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                              title="Refuser"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        
                        {/* Boutons standards */}
                        <button
                          onClick={() => handleOpenUpdateModal(donnee)}
                          className="text-blue-600 hover:text-blue-900"
                          title="Mettre à jour"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleOpenHistoryModal(donnee)}
                          className="text-amber-600 hover:text-amber-900"
                          title="Historique"
                        >
                          <History className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => window.open(`${API_URL}/api/export/${donnee.id}`, '_blank')}
                          className="text-green-600 hover:text-green-900"
                          title="Exporter"
                        >
                          <FileDown className="w-4 h-4" />
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
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-between items-center px-4 py-3 bg-white border rounded-lg">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Précédent
            </button>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Suivant
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Affichage de <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> à{' '}
                <span className="font-medium">
                  {Math.min(currentPage * itemsPerPage, totalItems)}
                </span>{' '}
                sur <span className="font-medium">{totalItems}</span> résultats
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setCurrentPage(1)}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Première page</span>
                  <span>«</span>
                </button>
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Précédent</span>
                  <span>‹</span>
                </button>
                
                {[...Array(Math.min(5, totalPages)).keys()].map(i => {
                  // Calculate the page number to display
                  let pageNum;
                  if (totalPages <= 5) {
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i;
                  } else {
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`relative inline-flex items-center px-4 py-2 border ${
                        currentPage === pageNum
                          ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      } text-sm font-medium`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Suivant</span>
                  <span>›</span>
                </button>
                <button
                  onClick={() => setCurrentPage(totalPages)}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Dernière page</span>
                  <span>»</span>
                </button>
              </nav>
            </div>
          </div>
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
              if (refresh) fetchData(currentPage);
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

export default DataViewer;