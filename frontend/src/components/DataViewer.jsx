import  { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import { Table, RefreshCw, Search, Filter, Calendar, FileText, FileUp } from 'lucide-react';
import UpdateModal from './UpdateModal';
import config from '../config';
import EnqueteExporter from './EnqueteExporter';
import EnqueteBatchExporter from './EnqueteBatchExporter';
import HistoryModal from './HistoryModal';


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
    // Définition des états
    const [donnees, setDonnees] = useState([]);
    const [enqueteToExport, setEnqueteToExport] = useState(null);
    const [selectedDonnees, setSelectedDonnees] = useState([]);
    const [showBatchExport, setShowBatchExport] = useState(false);
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [fichiers, setFichiers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedData, setSelectedData] = useState(null);
    const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
    const [statusFilter, setStatusFilter] = useState('all');
    const [dateFilter, setDateFilter] = useState('all');
    const [fichierFilter, setFichierFilter] = useState('all');
    const [selectedHistoryData, setSelectedHistoryData] = useState(null);
    const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

    // Utiliser useMemo pour filtrer les données
    const filteredDonnees = useMemo(() => {
        let filtered = [...donnees];
        
        // Appliquer les filtres
        if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            filtered = filtered.filter(donnee => 
                (donnee.numeroDossier && donnee.numeroDossier.toLowerCase().includes(searchLower)) ||
                (donnee.nom && donnee.nom.toLowerCase().includes(searchLower)) ||
                (donnee.prenom && donnee.prenom.toLowerCase().includes(searchLower)) ||
                (donnee.ville && donnee.ville.toLowerCase().includes(searchLower))
            );
        }
        
        // Filtre par statut
        if (statusFilter !== 'all') {
            if (statusFilter === 'pending') {
                filtered = filtered.filter(donnee => !donnee.code_resultat);
            } else {
                filtered = filtered.filter(donnee => donnee.code_resultat === statusFilter);
            }
        }
        
        // Filtre par date
        if (dateFilter !== 'all') {
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
                
                switch (dateFilter) {
                    case 'today':
                        return enqueteDate.getTime() === today.getTime();
                    case 'overdue':
                        return enqueteDate < today;
                    case 'week':{
                                                const oneWeek = new Date(today);
                        oneWeek.setDate(today.getDate() + 7);
                        return enqueteDate >= today && enqueteDate <= oneWeek;
                    }
                    default:
                        return true;
                }
            });
        }
        
        // Filtre par fichier d'importation
        if (fichierFilter !== 'all') {
            filtered = filtered.filter(donnee => donnee.fichier_id === parseInt(fichierFilter));
        }
        
        return filtered;
    }, [donnees, searchTerm, statusFilter, dateFilter, fichierFilter]);

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

    const handleSelectAll = (e) => {
        if (e.target.checked) {
            setSelectedDonnees([...filteredDonnees]);
        } else {
            setSelectedDonnees([]);
        }
    };
    
    const handleSelectDonnee = (donnee, checked) => {
        if (checked) {
            setSelectedDonnees([...selectedDonnees, donnee]);
        } else {
            setSelectedDonnees(selectedDonnees.filter(d => d.id !== donnee.id));
        }
    };

    const handleExport = (donnee) => {
        setEnqueteToExport(donnee);
    };

    // Définir fetchData avec useCallback pour éviter des re-rendus inutiles
    const fetchData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // Faire une seule requête optimisée pour récupérer toutes les données avec leurs détails
            const response = await axios.get(`${API_URL}/api/donnees`);

            if (response.data.success && Array.isArray(response.data.data)) {
                // Récupérer les données de l'enquêteur en utilisant Promise.all pour paralléliser les requêtes
                const donneesWithDetails = await Promise.all(
                    response.data.data.map(async (donnee) => {
                        try {
                            const detailsResponse = await axios.get(`${API_URL}/api/donnees-enqueteur/${donnee.id}`);
                            if (detailsResponse.data.success && detailsResponse.data.data) {
                                // Fusionner les informations
                                return {
                                    ...donnee,
                                    ...detailsResponse.data.data
                                };
                            }
                            return donnee;
                        } catch (err) {
                            // Ignorer l'erreur et retourner l'objet donnee sans modifications
                            console.warn(`Impossible de récupérer les détails pour l'ID ${donnee.id}:`, err);
                            return donnee;
                        }
                    })
                );

                setDonnees(donneesWithDetails);
            } else {
                throw new Error("Format de données invalide");
            }

            // Charger les enquêteurs dans une requête séparée
            const enqueteursResponse = await axios.get(`${API_URL}/api/enqueteurs`);
            if (enqueteursResponse.data.success && Array.isArray(enqueteursResponse.data.data)) {
                setEnqueteurs(enqueteursResponse.data.data);
            }
            
            // Charger la liste des fichiers importés
            const statsResponse = await axios.get(`${API_URL}/api/stats`);
            if (statsResponse.data && statsResponse.data.derniers_fichiers) {
                setFichiers(statsResponse.data.derniers_fichiers);
            }

        } catch (err) {
            console.error("Erreur lors du chargement des données:", err);
            setError(`Erreur: ${err.response?.data?.error || err.message}`);
        } finally {
            setLoading(false);
        }
    }, []);

    // Charger les données au montage du composant
    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Fonctions utilitaires
    const getEnqueteurName = useCallback((enqueteurId) => {
        if (!enqueteurId) return 'Non assigné';
        const enqueteur = enqueteurs.find(e => e.id === enqueteurId);
        return enqueteur ? `${enqueteur.nom} ${enqueteur.prenom}` : 'Non trouvé';
    }, [enqueteurs]);
    
    // Fonction pour obtenir le nom du fichier d'importation
    const getFichierName = useCallback((fichierId) => {
        if (!fichierId) return 'Inconnu';
        const fichier = fichiers.find(f => f.id === fichierId);
        return fichier ? fichier.nom : 'Inconnu';
    }, [fichiers]);

    const handleSearch = useCallback((e) => {
        setSearchTerm(e.target.value);
    }, []);

    const handleDelete = useCallback(async (id) => {
        if (window.confirm('Voulez-vous vraiment supprimer cet enregistrement ?')) {
            try {
                const response = await axios.delete(`${API_URL}/api/donnees/${id}`);
                if (response.status === 200) {
                    setDonnees(prevDonnees => prevDonnees.filter(donnee => donnee.id !== id));
                    alert('Enregistrement supprimé avec succès.');
                } else {
                    alert('Erreur lors de la suppression de l\'enregistrement.');
                }
            } catch (err) {
                console.error('Erreur lors de la suppression :', err);
                alert('Une erreur est survenue.');
            }
        }
    }, []);

    const handleUpdate = useCallback(async (donnee) => {
        try {
            setLoading(true);
            // Récupérer les données enquêteur en même temps
            const response = await axios.get(`${API_URL}/api/donnees-enqueteur/${donnee.id}`);
            if (response.data.success && response.data.data) {
                // Fusionner les données
                setSelectedData({
                    ...donnee,
                    enqueteur_data: response.data.data
                });
            } else {
                setSelectedData(donnee);
            }
            setIsUpdateModalOpen(true);
        } catch (err) {
            console.error("Erreur lors de la récupération des données:", err);
            setSelectedData(donnee);
            setIsUpdateModalOpen(true);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleModalClose = useCallback((shouldRefresh) => {
        setIsUpdateModalOpen(false);
        setSelectedData(null);
        if (shouldRefresh) {
            fetchData();
        }
    }, [fetchData]);

    const handleHistory = useCallback((id) => {
        setSelectedHistoryData(id);
        setIsHistoryModalOpen(true);
    }, []);

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

                <div className="flex flex-wrap items-center gap-2">
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
                                <option value="today">Aujourd&apos;hui</option>
                                <option value="week">Cette semaine</option>
                                <option value="overdue">En retard</option>
                            </select>
                            <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        </div>
                        {/* Nouveau filtre par fichier */}
                        <div className="relative">
                            <select
                                value={fichierFilter}
                                onChange={(e) => setFichierFilter(e.target.value)}
                                className="appearance-none pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            >
                                <option value="all">Tous les fichiers</option>
                                {fichiers.map(fichier => (
                                    <option key={fichier.id} value={fichier.id}>
                                        {fichier.nom}
                                    </option>
                                ))}
                            </select>
                            <FileUp className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        </div>
                        <button
                            onClick={fetchData}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Actualiser
                        </button>
                    </div>
                    {/* Bouton d'export par lot */}
                    {selectedDonnees.length > 0 && (
                        <button
                            onClick={() => setShowBatchExport(true)}
                            className="flex items-center gap-1 px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                        >
                            <FileText className="w-4 h-4" />
                            <span>Exporter {selectedDonnees.length} enquête{selectedDonnees.length > 1 ? 's' : ''}</span>
                        </button>
                    )}
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-2 py-3 text-left">
                                <input
                                    type="checkbox"
                                    onChange={handleSelectAll}
                                    checked={selectedDonnees.length === filteredDonnees.length && filteredDonnees.length > 0}
                                    className="rounded text-blue-600 focus:ring-blue-500"
                                />
                            </th>
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
                                Fichier source
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
                            <tr 
                                key={index} 
                                className={`hover:bg-gray-50 ${isDateOverdue(donnee.dateRetourEspere) ? 'bg-red-50' : ''}`}
                            >
                                <td className="px-2 py-2 text-center">
                                    <input
                                        type="checkbox"
                                        checked={selectedDonnees.some(d => d.id === donnee.id)}
                                        onChange={(e) => handleSelectDonnee(donnee, e.target.checked)}
                                        className="rounded text-blue-600 focus:ring-blue-500"
                                    />
                                </td>
                                <td className="px-2 py-2 text-xs">
                                    <div className="flex space-x-1">
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
                                        <button
                                            onClick={() => handleExport(donnee)}
                                            className="px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-xs"
                                        >
                                            Export
                                        </button>
                                    </div>
                                </td>
                                <td className="px-2 py-2 text-xs">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                                        ${STATUS_COLORS[donnee.code_resultat] || 'bg-yellow-100 text-yellow-800'}`}
                                    >
                                        {STATUS_LABELS[donnee.code_resultat] || 'En attente'}
                                    </span>
                                </td>
                                <td className="px-2 py-2 text-xs">{getEnqueteurName(donnee.enqueteurId)}</td>
                                <td className="px-2 py-2 text-xs">{getFichierName(donnee.fichier_id)}</td>
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

            {/* Composant d'export individuel */}
            {enqueteToExport && (
                <EnqueteExporter
                    data={enqueteToExport}
                    onClose={() => setEnqueteToExport(null)}
                />
            )}

            {/* Composant d'export par lot */}
            {showBatchExport && (
                <EnqueteBatchExporter
                    data={selectedDonnees}
                    onClose={() => setShowBatchExport(false)}
                />
            )}

            {isHistoryModalOpen && selectedHistoryData && (
                <HistoryModal
                    isOpen={isHistoryModalOpen}
                    onClose={() => {
                        setIsHistoryModalOpen(false);
                        setSelectedHistoryData(null);
                    }}
                    donneeId={selectedHistoryData}
                />
            )}
        </div>
    );
};

export default DataViewer;