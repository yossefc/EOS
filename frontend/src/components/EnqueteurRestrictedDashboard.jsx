import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
    RefreshCw, Search, Filter, Calendar, AlertCircle, CheckCircle, LogOut,
    User, Clock, Table, ArrowDownToLine, DollarSign
} from 'lucide-react';
import UpdateModal from './UpdateModal';
import EnhancedEarningsViewer from './EnhancedEarningsViewer'; // Utiliser le composant amélioré
import config from '../config';

const API_URL = config.API_URL;

// Status colors
const STATUS_COLORS = {
    'P': 'bg-green-100 text-green-800',
    'N': 'bg-red-100 text-red-800',
    'H': 'bg-blue-100 text-blue-800',
    'Z': 'bg-yellow-100 text-yellow-800',
    'I': 'bg-purple-100 text-purple-800',
    'Y': 'bg-gray-100 text-gray-800'
};

// Status labels
const STATUS_LABELS = {
    'P': 'Positif',
    'N': 'Négatif / NPA',
    'H': 'Confirmé',
    'Z': 'Annulé (agence)',
    'I': 'Intraitable',
    'Y': 'Annulé (EOS)',
    '': 'En attente'
};

const EnqueteurRestrictedDashboard = ({ onLogout }) => {
    // Récupérer les infos de l'enquêteur
    const enqueteurId = localStorage.getItem('enqueteurId');
    const enqueteurNom = localStorage.getItem('enqueteurNom');
    const enqueteurPrenom = localStorage.getItem('enqueteurPrenom');
    
    // State pour les données
    const [enquetes, setEnquetes] = useState([]);
    const [filteredEnquetes, setFilteredEnquetes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [dateFilter, setDateFilter] = useState('all');
    const [selectedEnquete, setSelectedEnquete] = useState(null);
    const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('enquetes');
    const [earningsSummary, setEarningsSummary] = useState(null);
    
    // Stats
    const [stats, setStats] = useState({
        total: 0,
        pending: 0,
        positive: 0,
        negative: 0
    });

    // Fonction pour récupérer les enquêtes de l'enquêteur connecté
    const fetchEnquetes = useCallback(async () => {
        if (!enqueteurId) {
            setError("Aucun enquêteur connecté");
            setLoading(false);
            return;
        }
        
        try {
            setLoading(true);
            setError(null);

            const response = await axios.get(`${API_URL}/api/enqueteur/${enqueteurId}/enquetes`);

            if (response.data.success && Array.isArray(response.data.data)) {
                setEnquetes(response.data.data);
                applyFilters(response.data.data, searchTerm, statusFilter, dateFilter);
                calculateStats(response.data.data);
            } else {
                throw new Error("Format de données invalide");
            }
        } catch (error) {
            console.error("Erreur lors du chargement des enquêtes:", error);
            setError(`Erreur: ${error.response?.data?.error || error.message}`);
        } finally {
            setLoading(false);
        }
    }, [enqueteurId, searchTerm, statusFilter, dateFilter]);
    // Fonction pour vérifier si la date est dépassée
    const isDateOverdue = (dateString) => {
        if (!dateString) return false;
        
        // Convertir la date au format français (DD/MM/YYYY) en objet Date
        const parts = dateString.split('/');
        if (parts.length !== 3) return false;
        
        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1; // Les mois commencent à 0
        const year = parseInt(parts[2], 10);
        
        const dateRetour = new Date(year, month, day);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Réinitialiser les heures pour comparer seulement les dates
        
        return dateRetour < today;
    };
    // Fonction pour récupérer un résumé des revenus
    const fetchEarningsSummary = useCallback(async () => {
        if (!enqueteurId) return;
        
        try {
            const response = await axios.get(`${API_URL}/api/facturation/enqueteur/${enqueteurId}`);
            if (response.data.success) {
                setEarningsSummary({
                    totalGagne: response.data.data.total_gagne || 0,
                    totalAPayer: response.data.data.total_a_payer || 0,
                    nombreEnquetes: response.data.data.nombre_enquetes || 0
                });
            }
        } catch (error) {
            console.error("Erreur lors du chargement du résumé des revenus:", error);
        }
    }, [enqueteurId]);

    // Appliquer les filtres
    const applyFilters = (data, search, status, date) => {
        let filtered = [...data];

        // Filtre de recherche
        if (search) {
            const searchLower = search.toLowerCase();
            filtered = filtered.filter(enquete =>
                (enquete.numeroDossier && enquete.numeroDossier.toLowerCase().includes(searchLower)) ||
                (enquete.nom && enquete.nom.toLowerCase().includes(searchLower)) ||
                (enquete.prenom && enquete.prenom.toLowerCase().includes(searchLower)) ||
                (enquete.ville && enquete.ville.toLowerCase().includes(searchLower))
            );
        }

        // Filtre par statut
        if (status !== 'all') {
            if (status === 'pending') {
                filtered = filtered.filter(enquete => !enquete.code_resultat);
            } else {
                filtered = filtered.filter(enquete => enquete.code_resultat === status);
            }
        }

        // Filtre par date
        if (date !== 'all') {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

            filtered = filtered.filter(enquete => {
                if (!enquete.dateRetourEspere) return false;

                // Convertir la date au format français (DD/MM/YYYY) en objet Date
                const parts = enquete.dateRetourEspere.split('/');
                if (parts.length !== 3) return false;

                // En France, le format est JJ/MM/AAAA
                const day = parseInt(parts[0], 10);
                const month = parseInt(parts[1], 10) - 1; // Les mois commencent à 0
                const year = parseInt(parts[2], 10);

                const enqueteDate = new Date(year, month, day);

                switch (date) {
                    case 'today':
                        return enqueteDate.getTime() === today.getTime();
                    case 'overdue':
                        return enqueteDate < today;
                    case 'week':
                        const oneWeek = new Date(today);
                        oneWeek.setDate(today.getDate() + 7);
                        return enqueteDate >= today && enqueteDate <= oneWeek;
                    default:
                        return true;
                }
            });
        }

        setFilteredEnquetes(filtered);
    };

    // Calculer les statistiques
    const calculateStats = (data) => {
        const total = data.length;
        const pending = data.filter(e => !e.code_resultat).length;
        const positive = data.filter(e => e.code_resultat === 'P').length;
        const negative = data.filter(e => e.code_resultat === 'N').length;

        setStats({
            total,
            pending,
            positive,
            negative
        });
    };

    // Charger les enquêtes au montage du composant
    useEffect(() => {
        fetchEnquetes();
        fetchEarningsSummary();
    }, [fetchEnquetes, fetchEarningsSummary]);

    // Gérer la recherche
    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
        applyFilters(enquetes, e.target.value, statusFilter, dateFilter);
    };

    // Ouvrir le modal de mise à jour
    const handleUpdate = (enquete) => {
        setSelectedEnquete(enquete);
        setIsUpdateModalOpen(true);
    };

    // Fermer le modal de mise à jour
    const handleModalClose = (shouldRefresh) => {
        setIsUpdateModalOpen(false);
        setSelectedEnquete(null);

        if (shouldRefresh) {
            fetchEnquetes();
            fetchEarningsSummary();
        }
    };

    // Fonctions pour la déconnexion
    const handleLogout = () => {
        // Supprimer les données de l'enquêteur du localStorage
        localStorage.removeItem('enqueteurId');
        localStorage.removeItem('enqueteurNom');
        localStorage.removeItem('enqueteurPrenom');
        localStorage.removeItem('enqueteurEmail');
        
        // Appeler la fonction de déconnexion
        onLogout();
    };
    
    // Télécharger la configuration OpenVPN
    const handleDownloadVpnConfig = () => {
        if (!enqueteurId) return;
        
        const downloadUrl = `${API_URL}/api/download/vpn-config/${enqueteurId}`;
        
        // Créer un élément <a> temporaire et cliquer dessus pour démarrer le téléchargement
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.setAttribute('download', `client${enqueteurId}.ovpn`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    // Si chargement en cours
    if (loading && !enquetes.length) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    // Si erreur
    if (error && !enquetes.length) {
        return (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                <div className="flex items-center gap-2">
                    <AlertCircle className="w-5 h-5" />
                    <span>{error}</span>
                </div>
                <button
                    onClick={handleLogout}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Retour à la connexion
                </button>
            </div>
        );
    }

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto">
                {/* Header avec infos de l'enquêteur */}
                <div className="mb-6">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-2">
                                <User className="w-6 h-6 text-blue-500" />
                                Bonjour, {enqueteurPrenom} {enqueteurNom}
                            </h1>
                            <p className="text-gray-600">
                                Voici les enquêtes qui vous sont assignées
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={handleDownloadVpnConfig}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 bg-white rounded-lg hover:bg-gray-50"
                            >
                                <ArrowDownToLine className="w-4 h-4" />
                                Config VPN
                            </button>
                            <button
                                onClick={handleLogout}
                                className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                            >
                                <LogOut className="w-4 h-4" />
                                Déconnexion
                            </button>
                        </div>
                    </div>
                    
                    {/* Alerte de revenus en attente */}
                    {earningsSummary && earningsSummary.totalAPayer > 0 && (
                        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex justify-between items-center">
                            <div className="flex items-center gap-2">
                                <DollarSign className="w-5 h-5 text-blue-500" />
                                <div>
                                    <span className="font-medium text-blue-800">
                                        Vous avez {earningsSummary.totalAPayer.toFixed(2)}€ de revenus en attente
                                    </span>
                                    <p className="text-sm text-blue-600">
                                        Vos revenus correspondent à {earningsSummary.nombreEnquetes} enquêtes traitées
                                    </p>
                                </div>
                            </div>
                            <button 
                                onClick={() => setActiveTab('earnings')}
                                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                            >
                                Voir mes revenus
                            </button>
                        </div>
                    )}
                </div>

                {/* Navigation par onglets */}
                <div className="mb-6 border-b border-gray-200">
                    <div className="flex -mb-px space-x-8">
                        <button
                            onClick={() => setActiveTab('enquetes')}
                            className={`py-4 px-4 border-b-2 font-medium text-sm flex items-center gap-2
                                ${activeTab === 'enquetes'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <Table className="w-5 h-5" />
                            <span>Mes enquêtes</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('earnings')}
                            className={`py-4 px-4 border-b-2 font-medium text-sm flex items-center gap-2
                                ${activeTab === 'earnings'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <DollarSign className="w-5 h-5" />
                            <span>Mes revenus</span>
                            {earningsSummary && earningsSummary.totalAPayer > 0 && (
                                <span className="inline-flex items-center justify-center bg-blue-100 text-blue-800 text-xs font-medium rounded-full h-5 px-2 ml-1">
                                    {earningsSummary.totalAPayer.toFixed(0)}€
                                </span>
                            )}
                        </button>
                    </div>
                </div>

                {/* Cartes de statistiques - affichées seulement sur l'onglet enquêtes */}
                {activeTab === 'enquetes' && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white rounded-lg shadow p-4 flex items-center">
                            <div className="rounded-full p-3 bg-blue-100 mr-4">
                                <Table className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Total enquêtes</p>
                                <p className="text-2xl font-semibold">{stats.total}</p>
                            </div>
                        </div>
                        <div className="bg-white rounded-lg shadow p-4 flex items-center">
                            <div className="rounded-full p-3 bg-yellow-100 mr-4">
                                <Clock className="w-6 h-6 text-yellow-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">En attente</p>
                                <p className="text-2xl font-semibold">{stats.pending}</p>
                            </div>
                        </div>
                        <div className="bg-white rounded-lg shadow p-4 flex items-center">
                            <div className="rounded-full p-3 bg-green-100 mr-4">
                                <CheckCircle className="w-6 h-6 text-green-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Positifs</p>
                                <p className="text-2xl font-semibold">{stats.positive}</p>
                            </div>
                        </div>
                        <div className="bg-white rounded-lg shadow p-4 flex items-center">
                            <div className="rounded-full p-3 bg-red-100 mr-4">
                                <AlertCircle className="w-6 h-6 text-red-600" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Négatifs</p>
                                <p className="text-2xl font-semibold">{stats.negative}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Contenu des onglets */}
                {activeTab === 'enquetes' ? (
                    <>
                        {/* Filtres de recherche */}
                        <div className="bg-white shadow-md rounded-lg overflow-hidden">
                            <div className="p-4 bg-gray-50 border-b">
                                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                    <div className="relative flex-grow max-w-md">
                                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        <input
                                            type="text"
                                            placeholder="Rechercher par nom, dossier..."
                                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            value={searchTerm}
                                            onChange={handleSearch}
                                        />
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        <div className="relative">
                                            <select
                                                value={statusFilter}
                                                onChange={(e) => {
                                                    setStatusFilter(e.target.value);
                                                    applyFilters(enquetes, searchTerm, e.target.value, dateFilter);
                                                }}
                                                className="appearance-none pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                <option value="all">Tous les statuts</option>
                                                <option value="pending">En attente</option>
                                                <option value="P">Positif</option>
                                                <option value="N">Négatif</option>
                                                <option value="H">Confirmé</option>
                                                <option value="Z">Annulé (agence)</option>
                                                <option value="I">Intraitable</option>
                                                <option value="Y">Annulé (EOS)</option>
                                            </select>
                                            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        </div>
                                        <div className="relative">
                                            <select
                                                value={dateFilter}
                                                onChange={(e) => {
                                                    setDateFilter(e.target.value);
                                                    applyFilters(enquetes, searchTerm, statusFilter, e.target.value);
                                                }}
                                                className="appearance-none pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                <option value="all">Toutes les dates</option>
                                                <option value="today">Aujourd'hui</option>
                                                <option value="week">Cette semaine</option>
                                                <option value="overdue">En retard</option>
                                            </select>
                                            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                        </div>
                                        <button
                                            onClick={fetchEnquetes}
                                            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                                        >
                                            <RefreshCw className="w-4 h-4" />
                                            Actualiser
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Tableau des enquêtes */}
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                N° Dossier
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Date limite
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Nom & Prénom
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Type
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Éléments demandés
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Statut
                                            </th>
                                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                Actions
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {filteredEnquetes.length === 0 ? (
                                            <tr>
                                                <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                                                    Aucune enquête ne correspond aux critères de recherche
                                                </td>
                                            </tr>
                                        ) : (
                                            filteredEnquetes.map((enquete) => (
                                                <tr 
                                                key={enquete.id} 
                                                className={`hover:bg-gray-50 ${isDateOverdue(enquete.dateRetourEspere) ? 'bg-red-50' : ''}`}
                                              >
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {enquete.numeroDossier}
                                                    </td>
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {enquete.dateRetourEspere}
                                                    </td>
                                                    <td className="px-4 py-4 text-sm text-gray-900">
                                                        <div className="font-medium">{enquete.nom}</div>
                                                        <div className="text-gray-500">{enquete.prenom}</div>
                                                    </td>
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {enquete.typeDemande === 'ENQ' ? 'Enquête' : 
                                                        enquete.typeDemande === 'CON' ? 'Contestation' : 
                                                        enquete.typeDemande}
                                                    </td>
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                        <div className="flex flex-wrap gap-1">
                                                            {enquete.elementDemandes?.split('').map((element, idx) => (
                                                                <span key={idx} className="px-2 py-0.5 bg-gray-100 rounded-full text-xs"
                                                                    title={
                                                                        element === 'A' ? 'Adresse' :
                                                                            element === 'T' ? 'Téléphone' :
                                                                                element === 'D' ? 'Décès' :
                                                                                    element === 'B' ? 'Banque' :
                                                                                        element === 'E' ? 'Employeur' :
                                                                                            element === 'R' ? 'Revenus' : element
                                                                    }
                                                                >
                                                                    {element}
                                                                </span>
                                                            ))}
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                            ${STATUS_COLORS[enquete.code_resultat] || 'bg-yellow-100 text-yellow-800'}`}
                                                        >
                                                            {STATUS_LABELS[enquete.code_resultat] || 'En attente'}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                        <button
                                                            onClick={() => handleUpdate(enquete)}
                                                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                                                        >
                                                            Traiter
                                                        </button>
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
                    /* Affichage du composant EnhancedEarningsViewer */
                    <EnhancedEarningsViewer enqueteurId={enqueteurId} />
                )}
            </div>

            {/* Modal pour traiter une enquête */}
            {isUpdateModalOpen && selectedEnquete && (
                <UpdateModal
                    isOpen={isUpdateModalOpen}
                    onClose={handleModalClose}
                    data={selectedEnquete}
                />
            )}
        </div>
    );
};

export default EnqueteurRestrictedDashboard;