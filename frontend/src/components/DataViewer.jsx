import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Table, RefreshCw, Search, Filter, Calendar, AlertCircle } from 'lucide-react';
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

const DataViewer = () => {
    const [donnees, setDonnees] = useState([]);
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [filteredDonnees, setFilteredDonnees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedData, setSelectedData] = useState(null);
    const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
    const [statusFilter, setStatusFilter] = useState('all');
    const [dateFilter, setDateFilter] = useState('all');

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Charger les données
            const dataResponse = await axios.get(`${API_URL}/api/donnees`);

            if (dataResponse.data.success && Array.isArray(dataResponse.data.data)) {
                // Pour chaque donnée, récupérer les infos enquêteur (résultat, etc.)
                const data = dataResponse.data.data;
                const dataWithDetails = await Promise.all(
                    data.map(async (donnee) => {
                        try {
                            const detailsResponse = await axios.get(`${API_URL}/api/donnees-enqueteur/${donnee.id}`);
                            if (detailsResponse.data.success && detailsResponse.data.data) {
                                return { ...donnee, ...detailsResponse.data.data };
                            }
                            return donnee;
                        } catch (error) {
                            return donnee;
                        }
                    })
                );

                setDonnees(dataWithDetails);
                applyFilters(dataWithDetails, searchTerm, statusFilter, dateFilter);
            } else {
                throw new Error('Format de données invalide');
            }

            // Charger les enquêteurs
            const enqueteursResponse = await axios.get(`${API_URL}/api/enqueteurs`);
            if (enqueteursResponse.data.success && Array.isArray(enqueteursResponse.data.data)) {
                setEnqueteurs(enqueteursResponse.data.data);
            }

            setLoading(false);
        } catch (error) {
            console.error('Erreur lors du chargement des données:', error);
            setError('Erreur lors du chargement des données: ' + (error.response?.data?.error || error.message));
            setLoading(false);
        }
    };

    // Appliquer les filtres
    const applyFilters = (data, search, status, date) => {
        let filtered = [...data];

        // Filtre de recherche
        if (search) {
            const searchLower = search.toLowerCase();
            filtered = filtered.filter(donnee =>
                (donnee.numeroDossier && donnee.numeroDossier.toLowerCase().includes(searchLower)) ||
                (donnee.nom && donnee.nom.toLowerCase().includes(searchLower)) ||
                (donnee.prenom && donnee.prenom.toLowerCase().includes(searchLower)) ||
                (donnee.ville && donnee.ville.toLowerCase().includes(searchLower))
            );
        }

        // Filtre par statut
        if (status !== 'all') {
            if (status === 'pending') {
                filtered = filtered.filter(donnee => !donnee.code_resultat);
            } else {
                filtered = filtered.filter(donnee => donnee.code_resultat === status);
            }
        }

        // Filtre par date
        if (date !== 'all') {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

            filtered = filtered.filter(donnee => {
                if (!donnee.dateRetourEspere) return false;

                // Convertir la date au format français (DD/MM/YYYY) en objet Date
                const parts = donnee.dateRetourEspere.split('/');
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

        setFilteredDonnees(filtered);
    };

    useEffect(() => {
        fetchData();
    }, []);

    // Effet pour appliquer les filtres lorsqu'ils changent
    useEffect(() => {
        applyFilters(donnees, searchTerm, statusFilter, dateFilter);
    }, [searchTerm, statusFilter, dateFilter]);

    const getEnqueteurName = (enqueteurId) => {
        if (!enqueteurId) return 'Non assigné';
        const enqueteur = enqueteurs.find(e => e.id === enqueteurId);
        return enqueteur ? `${enqueteur.nom} ${enqueteur.prenom}` : 'Non trouvé';
    };

    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Voulez-vous vraiment supprimer cet enregistrement ?')) {
            try {
                const response = await axios.delete(`${API_URL}/api/donnees/${id}`);
                if (response.status === 200) {
                    const updatedDonnees = donnees.filter((donnee) => donnee.id !== id);
                    setDonnees(updatedDonnees);
                    setFilteredDonnees(updatedDonnees);
                    alert('Enregistrement supprimé avec succès.');
                } else {
                    alert('Erreur lors de la suppression de l\'enregistrement.');
                }
            } catch (error) {
                console.error('Erreur lors de la suppression :', error);
                alert('Une erreur est survenue.');
            }
        }
    };

    const handleUpdate = (donnee) => {
        console.log("Ouverture du modal pour:", donnee);
        setSelectedData(donnee);
        setIsUpdateModalOpen(true);
    };

    const handleModalClose = (shouldRefresh) => {
        setIsUpdateModalOpen(false);
        setSelectedData(null);
        if (shouldRefresh) {
            fetchData();
        }
    };

    // Fonction pour l'historique (à implémenter plus tard)
    const handleHistory = (id) => {
        console.log('Historique pour ID:', id);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                Erreur: {error}
            </div>
        );
    }

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                    <Table className="w-6 h-6" />
                    Données importées ({filteredDonnees.length})
                </h2>

                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="relative">
                        <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={handleSearch}
                            placeholder="Rechercher..."
                            className="pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
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
                            onClick={fetchData}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Actualiser
                        </button>
                    </div>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Actions
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Statut
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Enquêteur
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Date limite
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                N° Dossier
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Type
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Nom
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Prénom
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Date Naissance
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Ville
                            </th>
                            <th className="px-2 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Éléments demandés
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredDonnees.map((donnee, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                <td className="px-2 py-2 text-xs flex space-x-1">
                                    <button
                                        onClick={() => handleDelete(donnee.id)}
                                        className="px-2 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs"
                                    >
                                        Supp
                                    </button>
                                    <button
                                        onClick={() => handleUpdate(donnee)}
                                        className="px-2 py-1 bg-green-500 text-white rounded hover:bg-blue-600 text-xs"
                                    >
                                        Traiter
                                    </button>
                                    <button
                                        onClick={() => handleHistory(donnee.id)}
                                        className="px-2 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-xs"
                                    >
                                        Histo
                                    </button>
                                </td>
                                <td className="px-2 py-2 text-xs">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                        ${STATUS_COLORS[donnee.code_resultat] || 'bg-yellow-100 text-yellow-800'}`}
                                    >
                                        {STATUS_LABELS[donnee.code_resultat] || 'En attente'}
                                    </span>
                                </td>
                                <td className="px-2 py-2 text-xs">{getEnqueteurName(donnee.enqueteurId)}</td>
                                <td className="px-2 py-2 text-xs">{donnee.dateRetourEspere}</td>
                                <td className="px-2 py-2 text-xs">{donnee.numeroDossier}</td>
                                <td className="px-2 py-2 text-xs">{donnee.typeDemande}</td>
                                <td className="px-2 py-2 text-xs">{donnee.nom}</td>
                                <td className="px-2 py-2 text-xs">{donnee.prenom}</td>
                                <td className="px-2 py-2 text-xs">{donnee.dateNaissance}</td>
                                <td className="px-2 py-2 text-xs">{donnee.ville}</td>
                                <td className="px-2 py-2 text-xs">
                                    <div className="flex flex-wrap gap-1">
                                        {donnee.elementDemandes?.split('').map((element, idx) => (
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
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {filteredDonnees.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    Aucune donnée disponible
                </div>
            )}

            {isUpdateModalOpen && (
                <UpdateModal
                    isOpen={isUpdateModalOpen}
                    onClose={handleModalClose}
                    data={selectedData}
                />
            )}
        </div>
    );
};

export default DataViewer;