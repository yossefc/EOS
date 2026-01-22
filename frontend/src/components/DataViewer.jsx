import { useState, useEffect, lazy, Suspense, useCallback } from 'react';
import axios from 'axios';
import {
  Database, Search, Filter, RefreshCw,
  AlertCircle, X, Trash2,
  History, FileDown, Pencil, Download, CalendarDays,
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

  // MULTI-CLIENT: État pour les clients
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [loadingClients, setLoadingClients] = useState(true);

  // État pour l'alerte enquêteur non assigné
  const [showInvestigatorAlert, setShowInvestigatorAlert] = useState(false);

  // État pour la modale de confirmation personnalisée
  const [confirmModal, setConfirmModal] = useState({
    show: false,
    enqueteId: null,
    title: '',
    message: '',
    action: null,
    confirmLabel: 'Confirmer',
    confirmColor: 'bg-blue-600 hover:bg-blue-700 shadow-blue-200'
  });

  // MULTI-CLIENT: Récupérer la liste des clients
  const fetchClients = useCallback(async () => {
    try {
      setLoadingClients(true);
      const response = await axios.get(`${API_URL}/api/clients`);
      if (response.data.success) {
        setClients(response.data.clients);
        // Sélectionner EOS par défaut
        const eosClient = response.data.clients.find(c => c.code === 'EOS');
        if (eosClient) {
          setSelectedClientId(eosClient.id);
        } else if (response.data.clients.length > 0) {
          setSelectedClientId(response.data.clients[0].id);
        }
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des clients:", error);
      // Continuer sans clients, le backend utilisera EOS par défaut
    } finally {
      setLoadingClients(false);
    }
  }, []);

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

      // MULTI-CLIENT: Ajouter le client_id si sélectionné
      if (selectedClientId) {
        params.append('client_id', selectedClientId.toString());
      }

      // Ajouter les filtres à la requête
      if (searchTerm) params.append('search', searchTerm);
      if (filters.typeDemande) params.append('typeDemande', filters.typeDemande);
      if (filters.code_resultat) params.append('code_resultat', filters.code_resultat);
      if (filters.dateStart) params.append('date_reception_start', filters.dateStart);
      if (filters.dateEnd) params.append('date_reception_end', filters.dateEnd);
      if (filters.showOnlyUnassigned) params.append('enqueteurId', 'unassigned');

      const response = await axios.get(`${API_URL}/api/donnees-complete?${params.toString()}`);

      console.log("🔍 API Response:", response);
      console.log("🔍 API Data:", response.data);

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
  }, [itemsPerPage, searchTerm, filters, selectedClientId]);

  // Récupérer le nombre d'enquêtes non exportées
  const fetchNonExporteesCount = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedClientId) {
        params.append('client_id', selectedClientId.toString());
      }

      const response = await axios.get(`${API_URL}/api/donnees/non-exportees/count?${params.toString()}`);
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
    fetchClients(); // MULTI-CLIENT
    fetchNonExporteesCount();
    fetchEnqueteurs();
  }, [fetchClients]);

  // Recharger les données quand la page ou le client changent
  useEffect(() => {
    if (selectedClientId !== null) {  // MULTI-CLIENT: Attendre que le client soit sélectionné
      fetchData(currentPage);
      fetchNonExporteesCount();
    }
  }, [currentPage, selectedClientId]);

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
    // Trouver l'enquête concernée pour vérifier l'enquêteur
    const enquete = donnees.find(d => d.id === enqueteId);

    if (!enquete || !enquete.enqueteurId) {
      setShowInvestigatorAlert(true);
      return;
    }

    // Utiliser la nouvelle modale personnalisée au lieu de window.confirm
    setConfirmModal({
      show: true,
      enqueteId: enqueteId,
      title: 'Validation de l\'enquête',
      message: 'Êtes-vous sûr de vouloir valider cette enquête ? Elle sera archivée et apparaîtra dans l\'onglet Export des résultats.',
      action: executeValiderEnquete,
      confirmLabel: 'Valider',
      confirmColor: 'bg-green-600 hover:bg-green-700 shadow-green-200'
    });
  };

  const handleSupprimerEnquete = (enqueteId) => {
    setConfirmModal({
      show: true,
      enqueteId: enqueteId,
      title: 'Suppression de l\'enquête',
      message: 'Attention : cette action est irréversible. Êtes-vous sûr de vouloir supprimer définitivement cette enquête ?',
      action: executeSupprimerEnquete,
      confirmLabel: 'Supprimer',
      confirmColor: 'bg-red-600 hover:bg-red-700 shadow-red-200'
    });
  };

  const executeSupprimerEnquete = async (enqueteId) => {
    try {
      setConfirmModal(prev => ({ ...prev, show: false }));
      setValidating(true);
      setError(null);

      const response = await axios.delete(`${API_URL}/api/enquetes/${enqueteId}`);

      if (response.data.success) {
        setSuccessMessage('Enquête supprimée définitivement.');
        // Retirer l'enquête du tableau local
        setDonnees(prev => prev.filter(d => d.id !== enqueteId));
        setFilteredDonnees(prev => prev.filter(d => d.id !== enqueteId));
        setTimeout(() => setSuccessMessage(null), 3000);
      } else {
        throw new Error(response.data.error || 'Erreur lors de la suppression');
      }
    } catch (error) {
      console.error('Erreur:', error);
      setError(error.response?.data?.error || error.message || 'Erreur lors de la suppression');
    } finally {
      setValidating(false);
    }
  };

  // Fonction réelle de validation appelée par la modale
  const executeValiderEnquete = async (enqueteId) => {
    try {
      setConfirmModal({ ...confirmModal, show: false });
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

  // Handle generic export
  const handleExport = async () => {
    try {
      const client = clients.find(c => c.id === selectedClientId);
      const isSherlock = client?.code === 'RG_SHERLOCK';

      setExportingData(true);

      if (isSherlock) {
        // Export Excel pour Sherlock
        const response = await axios.post(`${API_URL}/api/export/sherlock`, {
          client_id: selectedClientId
        }, {
          responseType: 'blob'
        });

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Export_Sherlock_${new Date().toISOString().split('T')[0]}.xls`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      } else {
        // Export Word legacy
        const response = await axios.post(`${API_URL}/api/export-enquetes`, {
          client_id: selectedClientId
        }, {
          responseType: 'blob'
        });

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
      }

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
        <div className="flex items-center gap-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Database className="w-6 h-6 text-blue-500" />
            Exploration des Données
          </h2>

          {/* MULTI-CLIENT: Sélecteur de client (Boutons stylisés) */}
          {!loadingClients && clients.length > 1 && (
            <div className="flex bg-slate-100/50 p-1 rounded-xl border border-slate-200/60 ml-2">
              {clients.map(client => (
                <button
                  key={client.id}
                  onClick={() => {
                    setSelectedClientId(client.id);
                    setCurrentPage(1);
                  }}
                  className={`
                    px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide transition-all
                    ${selectedClientId === client.id
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-slate-400 hover:text-slate-600'}
                  `}
                >
                  {client.nom}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {(() => {
            const client = clients.find(c => c.id === selectedClientId);
            const isSherlock = client?.code === 'RG_SHERLOCK';

            return (
              <button
                onClick={handleExport}
                disabled={exportingData || (!isSherlock && nonExporteesCount === 0)}
                className={`flex items-center gap-1.5 px-4 py-2 text-white rounded-xl font-semibold disabled:opacity-30 disabled:cursor-not-allowed shadow-sm transition-all ${isSherlock ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-emerald-500 hover:bg-emerald-600'}`}
                title={isSherlock ? "Exporter toutes les données Sherlock" : `Exporter les ${nonExporteesCount} nouvelles enquêtes non encore exportées`}
              >
                {exportingData ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                <span>{isSherlock ? 'Export Excel' : `Export Word (${nonExporteesCount})`}</span>
              </button>
            );
          })()}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1 px-3 py-1.5 border rounded hover:bg-gray-50"
          >
            <Filter className="w-4 h-4" />
            <span>Filtres</span>
          </button>
          <button
            onClick={() => fetchData(currentPage)}
            className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 shadow-sm transition-all"
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
                onChange={(e) => setFilters({ ...filters, typeDemande: e.target.value })}
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
                onChange={(e) => setFilters({ ...filters, code_resultat: e.target.value })}
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
                onChange={(e) => setFilters({ ...filters, elements_retrouves: e.target.value })}
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
                onChange={(e) => setFilters({ ...filters, dateStart: e.target.value })}
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
                onChange={(e) => setFilters({ ...filters, dateEnd: e.target.value })}
                className="w-full p-2 border rounded"
              />
            </div>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={filters.showOnlyUnassigned}
                onChange={(e) => setFilters({ ...filters, showOnlyUnassigned: e.target.checked })}
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

        {(() => {
          const isPartner = clients.find(c => c.id === selectedClientId)?.code === 'PARTNER';
          const colCount = isPartner ? 10 : 9;

          return (
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
                    {isPartner && (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lettre
                      </th>
                    )}
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
                      <td colSpan={colCount} className="px-6 py-4 text-center">
                        <div className="flex justify-center items-center">
                          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                          <span>Chargement...</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredDonnees.length === 0 ? (
                    <tr>
                      <td colSpan={colCount} className="px-6 py-4 text-center text-gray-500">
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
                        {isPartner && (
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-blue-600">
                            {donnee.tarif_lettre || '-'}
                          </td>
                        )}
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
                        <td className="px-6 py-4 text-sm text-gray-500">
                          {isPartner ? (
                            <div className="flex flex-wrap gap-1">
                              {(() => {
                                const recherche = (donnee.recherche || '').toUpperCase().trim();
                                if (!recherche || recherche === '-') return [<span key="none" className="text-gray-400 text-xs">-</span>];

                                // Détecter les patterns complets
                                const patterns = [
                                  { regex: /DATE\s+ET\s+LIEU\s+DE\s+NAISSANCE/g, label: 'DATE ET LIEU DE NAISSANCE', icon: '🎂' },
                                  { regex: /LIEU\s+DE\s+NAISSANCE/g, label: 'LIEU DE NAISSANCE', icon: '🎂' },
                                  { regex: /DATE\s+DE\s+NAISSANCE/g, label: 'DATE DE NAISSANCE', icon: '🎂' },
                                  { regex: /ADRESSE/g, label: 'ADRESSE', icon: '🏠' },
                                  { regex: /EMPLOYEUR/g, label: 'EMPLOYEUR', icon: '💼' },
                                  { regex: /BANQUE/g, label: 'BANQUE', icon: '🏦' },
                                  { regex: /TEL[EÉ]PHONE/g, label: 'TÉLÉPHONE', icon: '📞' }
                                ];

                                const found = [];
                                let remaining = recherche;

                                patterns.forEach(pattern => {
                                  if (pattern.regex.test(remaining)) {
                                    found.push({ label: pattern.label, icon: pattern.icon });
                                    remaining = remaining.replace(pattern.regex, '');
                                  }
                                });

                                // Ajouter les mots restants non reconnus
                                const otherWords = remaining.split(/\s+/).filter(w => w && w !== 'ET' && w !== 'DE');
                                otherWords.forEach(word => {
                                  if (!found.some(f => f.label.includes(word))) {
                                    found.push({ label: word, icon: '' });
                                  }
                                });

                                return found.map((item, idx) => (
                                  <span
                                    key={idx}
                                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-300"
                                  >
                                    {item.icon && <span>{item.icon}</span>}
                                    <span>{item.label}</span>
                                  </span>
                                ));
                              })()}
                            </div>
                          ) : (
                            <span className="whitespace-nowrap">{donnee.elements_retrouves || '-'}</span>
                          )}
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
                              onClick={() => handleSupprimerEnquete(donnee.id)}
                              className="text-red-500 hover:text-red-700"
                              title="Supprimer l'enquête"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          );
        })()}
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
                      className={`relative inline-flex items-center px-4 py-2 border ${currentPage === pageNum
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

      {/* Alerte Enquêteur Non Assigné */}
      {showInvestigatorAlert && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-[100] animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-sm w-full mx-4 transform animate-in zoom-in-95 duration-200 text-center border border-gray-100">
            <div className="w-20 h-20 bg-amber-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-10 h-10 text-amber-500" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Attention</h3>
            <p className="text-gray-600 mb-8 leading-relaxed">
              Il est impossible de valider ce dossier car <span className="font-semibold text-gray-900">aucun enquêteur n'est assigné</span>.
            </p>
            <button
              onClick={() => setShowInvestigatorAlert(false)}
              className="w-full py-3.5 px-6 bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl transition-all shadow-lg shadow-amber-200 active:scale-95"
            >
              D'accord, j'ai compris
            </button>
          </div>
        </div>
      )}
      {/* Modal pour assignation rapide d'enquêteur si nécessaire - non implémenté ici car séparé */}

      {/* Modale de Confirmation Personnalisée */}
      {confirmModal.show && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          {/* Overlay avec Glassmorphism */}
          <div
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300"
            onClick={() => setConfirmModal({ ...confirmModal, show: false })}
          />

          {/* Modal Content */}
          <div className="relative bg-white w-full max-w-md rounded-[32px] shadow-2xl border border-white/20 p-8 animate-in zoom-in-95 slide-in-from-bottom-4 duration-300">
            <div className="flex flex-col items-center text-center">
              <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
                <CheckCircle className="w-8 h-8 text-blue-600" />
              </div>

              <h3 className="text-xl font-bold text-slate-800 mb-3 tracking-tight">
                {confirmModal.title}
              </h3>

              <p className="text-slate-500 font-medium leading-relaxed mb-8">
                {confirmModal.message}
              </p>

              <div className="flex gap-3 w-full">
                <button
                  onClick={() => setConfirmModal({ ...confirmModal, show: false })}
                  className="flex-1 py-3.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl font-bold transition-all active:scale-[0.98]"
                >
                  Annuler
                </button>
                <button
                  onClick={() => confirmModal.action(confirmModal.enqueteId)}
                  className={`flex-1 py-3.5 text-white rounded-xl font-bold shadow-lg transition-all active:scale-[0.98] ${confirmModal.confirmColor}`}
                >
                  {confirmModal.confirmLabel}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataViewer;