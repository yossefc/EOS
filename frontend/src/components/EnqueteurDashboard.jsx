import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    FileUp, FileDown, Table, User, Search, Filter, Calendar, Clock,
    AlertTriangle, CheckCircle, BarChart2, AlertCircle, RefreshCw
} from 'lucide-react';
import ImportHandler from './ImportHandler';
import ExportHandler from './ExportHandler';
import UpdateModal from './UpdateModal';
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

const EnqueteurDashboard = () => {
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

    // Stats
    const [stats, setStats] = useState({
        total: 0,
        pending: 0,
        positive: 0,
        negative: 0,
        byType: {}
    });

    const fetchEnquetes = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await axios.get(`${API_URL}/api/donnees`);

            if (response.data.success && Array.isArray(response.data.data)) {
                const enquetesData = response.data.data;

                // Pour chaque enquête, récupérer les données enquêteur si elles existent
                const enquetesWithDetails = await Promise.all(
                    enquetesData.map(async (enquete) => {
                        try {
                            const detailsResponse = await axios.get(`${API_URL}/api/donnees-enqueteur/${enquete.id}`);
                            if (detailsResponse.data.success && detailsResponse.data.data) {
                                return { ...enquete, ...detailsResponse.data.data };
                            }
                            return enquete;
                        } catch (error) {
                            return enquete;
                        }
                    })
                );

                setEnquetes(enquetesWithDetails);
                applyFilters(enquetesWithDetails, searchTerm, statusFilter, dateFilter);
                calculateStats(enquetesWithDetails);
            } else {
                throw new Error("Format de données invalide");
            }
        } catch (error) {
            console.error("Erreur lors du chargement des enquêtes:", error);
            setError(`Erreur: ${error.response?.data?.error || error.message}`);
        } finally {
            setLoading(false);
        }
    };
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
    // Calculer les statistiques
    const calculateStats = (enquetesData) => {
        const total = enquetesData.length;
        const pending = enquetesData.filter(e => !e.code_resultat).length;
        const positive = enquetesData.filter(e => e.code_resultat === 'P').length;
        const negative = enquetesData.filter(e => e.code_resultat === 'N').length;

        // Compter par type de demande
        const byType = enquetesData.reduce((acc, enquete) => {
            const type = enquete.typeDemande || 'Inconnu';
            acc[type] = (acc[type] || 0) + 1;
            return acc;
        }, {});

        setStats({
            total,
            pending,
            positive,
            negative,
            byType
        });
    };

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

    // Effet pour charger les enquêtes au montage
    useEffect(() => {
        fetchEnquetes();
    }, []);

    // Effet pour appliquer les filtres lorsqu'ils changent
    useEffect(() => {
        applyFilters(enquetes, searchTerm, statusFilter, dateFilter);
    }, [searchTerm, statusFilter, dateFilter]);

    // Gérer la recherche
    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
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
        }
    };

    // Formater l'âge à partir de la date de naissance
    const calculateAge = (dateNaissance) => {
        if (!dateNaissance) return "";

        // Convertir la date au format français (DD/MM/YYYY) en objet Date
        const parts = dateNaissance.split('/');
        if (parts.length !== 3) return "";

        const day = parseInt(parts[0], 10);
        const month = parseInt(parts[1], 10) - 1; // Les mois commencent à 0
        const year = parseInt(parts[2], 10);

        const birthDate = new Date(year, month, day);
        const today = new Date();

        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();

        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }

        return age;
    };

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto">
                {/* En-tête */}
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-gray-900">
                        Tableau de bord EOS - Interface Enquêteur
                    </h1>
                    <p className="mt-1 text-sm text-gray-600">
                        Gérez vos enquêtes et traitez les dossiers selon les exigences du cahier des charges
                    </p>
                </div>

                {/* Cartes de statistiques */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
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

                {/* Navigation par onglets */}
                <div className="mb-6 border-b border-gray-200">
                    <div className="flex -mb-px space-x-8">
                        <button
                            onClick={() => setActiveTab('enquetes')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                                ${activeTab === 'enquetes'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <Table className="w-5 h-5" />
                            <span>Liste des enquêtes</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('import')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                                ${activeTab === 'import'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <FileUp className="w-5 h-5" />
                            <span>Import de fichiers</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('export')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                                ${activeTab === 'export'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <FileDown className="w-5 h-5" />
                            <span>Export des résultats</span>
                        </button>
                        <button
                            onClick={() => setActiveTab('stats')}
                            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                                ${activeTab === 'stats'
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                            `}
                        >
                            <BarChart2 className="w-5 h-5" />
                            <span>Statistiques</span>
                        </button>
                    </div>
                </div>

                {/* Contenu des onglets */}
                <div>
                    {/* Onglet Liste des enquêtes */}
                    {activeTab === 'enquetes' && (
                        <div className="bg-white shadow-md rounded-lg overflow-hidden">
                            {/* Barre de recherche et filtres */}
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
                                                onChange={(e) => setStatusFilter(e.target.value)}
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
                                                onChange={(e) => setDateFilter(e.target.value)}
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
                            {loading ? (
                                <div className="flex justify-center items-center p-8">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                                </div>
                            ) : error ? (
                                <div className="p-8 text-center">
                                    <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                                    <p className="text-red-500">{error}</p>
                                </div>
                            ) : filteredEnquetes.length === 0 ? (
                                <div className="p-8 text-center">
                                    <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                                    <p className="text-gray-500">Aucune enquête ne correspond aux critères de recherche</p>
                                </div>
                            ) : (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    N° Dossier
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Date limite
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Nom & Prénom
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Âge
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Type
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Éléments demandés
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Statut
                                                </th>
                                                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                                                    Actions
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {filteredEnquetes.map((enquete) => (
                                                <tr 
  key={enquete.id} 
  className={`hover:bg-gray-50 ${isDateOverdue(enquete.dateRetourEspere) ? 'bg-red-100 border-l-4 border-red-500' : ''}`}
>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {enquete.numeroDossier}
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        {enquete.dateRetourEspere}
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-gray-900">
                                                        <div className="font-medium">{enquete.nom}</div>
                                                        <div className="text-gray-500">{enquete.prenom}</div>
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        {calculateAge(enquete.dateNaissance)} ans
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                        {enquete.typeDemande || "-"}
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm">
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
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                                            ${STATUS_COLORS[enquete.code_resultat] || 'bg-yellow-100 text-yellow-800'}`}
                                                        >
                                                            {STATUS_LABELS[enquete.code_resultat] || 'En attente'}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 whitespace-nowrap text-sm">
                                                        <button
                                                            onClick={() => handleUpdate(enquete)}
                                                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                                                        >
                                                            Traiter
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Onglet Import */}
                    {activeTab === 'import' && (
                        <ImportHandler
                            onImportComplete={fetchEnquetes}
                        />
                    )}

                    {/* Onglet Export */}
                    {activeTab === 'export' && (
                        <ExportHandler
                            enquetes={filteredEnquetes}
                            onExportComplete={() => { }}
                        />
                    )}

                    {/* Onglet Statistiques */}
                    {activeTab === 'stats' && (
                        <div className="bg-white shadow-md rounded-lg p-6">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <BarChart2 className="w-6 h-6 text-blue-500" />
                                Statistiques détaillées
                            </h2>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Statistiques par statut */}
                                <div className="border rounded-lg p-4">
                                    <h3 className="font-medium text-lg mb-4">Répartition par statut</h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">En attente</span>
                                            <div className="flex items-center">
                                                <div className="w-32 bg-gray-200 rounded-full h-2.5 mr-2">
                                                    <div className="bg-yellow-500 h-2.5 rounded-full" style={{ width: `${stats.total ? (stats.pending / stats.total * 100) : 0}%` }}></div>
                                                </div>
                                                <span className="text-sm">{stats.pending}</span>
                                            </div>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Positifs</span>
                                            <div className="flex items-center">
                                                <div className="w-32 bg-gray-200 rounded-full h-2.5 mr-2">
                                                    <div className="bg-green-500 h-2.5 rounded-full" style={{ width: `${stats.total ? (stats.positive / stats.total * 100) : 0}%` }}></div>
                                                </div>
                                                <span className="text-sm">{stats.positive}</span>
                                            </div>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm">Négatifs</span>
                                            <div className="flex items-center">
                                                <div className="w-32 bg-gray-200 rounded-full h-2.5 mr-2">
                                                    <div className="bg-red-500 h-2.5 rounded-full" style={{ width: `${stats.total ? (stats.negative / stats.total * 100) : 0}%` }}></div>
                                                </div>
                                                <span className="text-sm">{stats.negative}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Statistiques par type */}
                                <div className="border rounded-lg p-4">
                                    <h3 className="font-medium text-lg mb-4">Répartition par type</h3>
                                    <div className="space-y-4">
                                        {Object.entries(stats.byType).map(([type, count]) => (
                                            <div key={type} className="flex justify-between items-center">
                                                <span className="text-sm">{type}</span>
                                                <div className="flex items-center">
                                                    <div className="w-32 bg-gray-200 rounded-full h-2.5 mr-2">
                                                        <div className="bg-blue-500 h-2.5 rounded-full" style={{ width: `${stats.total ? (count / stats.total * 100) : 0}%` }}></div>
                                                    </div>
                                                    <span className="text-sm">{count}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
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

export default EnqueteurDashboard;