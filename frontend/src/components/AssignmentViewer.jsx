import React, { useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types'; // Ajout des PropTypes
import axios from 'axios';
import { Loader2, AlertCircle, UserPlus, Check, Search, Users, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { FixedSizeList as List } from 'react-window';

// Création d'une instance axios avec les configurations de base
const api = axios.create({
    baseURL: 'http://localhost:5000',
    withCredentials: false,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Composant de ligne d'enquête mémorisé avec PropTypes
const EnqueteRow = React.memo(({ enquete, index, enqueteurs, onAssign, isSelected }) => {
    return (
        <tr className={`hover:bg-gray-50 transition-colors duration-150 ease-in-out 
                      ${isSelected ? 'bg-blue-50' : ''}`}>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-500">
                {index}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {enquete.numeroDossier}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {enquete.nom}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                {enquete.prenom}
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                    {enquete.typeDemande}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap">
                <select
                    className="block w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-2 focus:ring-blue-500"
                    value={enquete.enqueteurId || ''}
                    onChange={(e) => onAssign(enquete.numeroDossier, e.target.value)}
                >
                    <option value="">Sélectionner un enquêteur</option>
                    {enqueteurs.map((enqueteur) => (
                        <option key={enqueteur.id} value={enqueteur.id}>
                            {enqueteur.nom} {enqueteur.prenom}
                        </option>
                    ))}
                </select>
            </td>
        </tr>
    );
});

// Définition du displayName pour résoudre le warning react/display-name
EnqueteRow.displayName = 'EnqueteRow';

// Définition des PropTypes pour résoudre les warnings react/prop-types
EnqueteRow.propTypes = {
    enquete: PropTypes.shape({
        numeroDossier: PropTypes.string,
        nom: PropTypes.string,
        prenom: PropTypes.string,
        typeDemande: PropTypes.string,
        enqueteurId: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }).isRequired,
    index: PropTypes.number.isRequired,
    enqueteurs: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
        nom: PropTypes.string.isRequired,
        prenom: PropTypes.string.isRequired
    })).isRequired,
    onAssign: PropTypes.func.isRequired,
    isSelected: PropTypes.bool.isRequired
};

// Composant de pagination avec PropTypes
const Pagination = ({ currentPage, totalPages, itemsPerPage, setItemsPerPage, handlePageChange }) => (
    <div className="flex justify-center items-center mt-4 gap-2">
        <button 
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
            className="px-2 py-1 border rounded disabled:opacity-50"
            title="Première page"
        >
            <ChevronLeft className="w-4 h-4" />
            <ChevronLeft className="w-4 h-4 -ml-2" />
        </button>
        <button 
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-1 border rounded disabled:opacity-50"
            title="Page précédente"
        >
            <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="px-3 py-1">
            Page {currentPage} sur {totalPages}
        </span>
        <button 
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="px-3 py-1 border rounded disabled:opacity-50"
            title="Page suivante"
        >
            <ChevronRight className="w-4 h-4" />
        </button>
        <button 
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage >= totalPages}
            className="px-2 py-1 border rounded disabled:opacity-50"
            title="Dernière page"
        >
            <ChevronRight className="w-4 h-4" />
            <ChevronRight className="w-4 h-4 -ml-2" />
        </button>
        <select
            value={itemsPerPage}
            onChange={(e) => {
                setItemsPerPage(Number(e.target.value));
                handlePageChange(1); // Revenir à la première page lors du changement d'items par page
            }}
            className="ml-4 px-2 py-1 border rounded"
        >
            {[10, 25, 50, 100].map(value => (
                <option key={value} value={value}>{value} par page</option>
            ))}
        </select>
    </div>
);

// PropTypes pour le composant Pagination
Pagination.propTypes = {
    currentPage: PropTypes.number.isRequired,
    totalPages: PropTypes.number.isRequired,
    itemsPerPage: PropTypes.number.isRequired,
    setItemsPerPage: PropTypes.func.isRequired,
    handlePageChange: PropTypes.func.isRequired
};

// Composant principal
const AssignmentViewer = () => {
    // États pour les données
    const [enquetes, setEnquetes] = useState([]);
    const [enqueteurs, setEnqueteurs] = useState([]);
    
    // États pour la pagination
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(50);
    const [totalPages, setTotalPages] = useState(1);
    
    // États pour les filtres et la recherche
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
    
    // États pour l'UI et les opérations
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');
    
    // États pour l'assignation en masse
    const [startRange, setStartRange] = useState(1);
    const [endRange, setEndRange] = useState(1);
    const [selectedEnqueteur, setSelectedEnqueteur] = useState('');
    const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);
    
    // Effet pour le debounce sur la recherche
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearchTerm(searchTerm.toLowerCase());
        }, 300);
        
        return () => clearTimeout(timer);
    }, [searchTerm]);
    
    // Fonction pour charger les données - réutilisable
    const fetchData = useCallback(async (resetPage = false) => {
        try {
            setLoading(true);
            setError(null);
            setRefreshing(true);
            
            const page = resetPage ? 1 : currentPage;
            if (resetPage) {
                setCurrentPage(1);
            }
            
            const [enquetesResponse, enqueteursResponse] = await Promise.all([
                api.get(`/api/donnees?page=${page}&per_page=${itemsPerPage}`),
                api.get('/api/enqueteurs')
            ]);
            
            if (enquetesResponse.data.success && Array.isArray(enquetesResponse.data.data)) {
                setEnquetes(enquetesResponse.data.data);
                // Utilisez `total` pour le nombre total d'items, et calculez les pages si nécessaire
                if (enquetesResponse.data.pages) {
                    setTotalPages(enquetesResponse.data.pages);
                } else if (enquetesResponse.data.total) {
                    setTotalPages(Math.ceil(enquetesResponse.data.total / itemsPerPage));
                } else {
                    setTotalPages(Math.ceil(enquetesResponse.data.data.length / itemsPerPage));
                }
            }
            
            if (enqueteursResponse.data.success && Array.isArray(enqueteursResponse.data.data)) {
                setEnqueteurs(enqueteursResponse.data.data);
            }
            
        } catch (error) {
            setError('Erreur lors du chargement des données: ' + (error.response?.data?.error || error.message));
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [currentPage, itemsPerPage]);
    
    // Chargement initial des données
    useEffect(() => {
        fetchData();
    }, [fetchData, currentPage]);
    
    // Filtrer les enquêtes avec useMemo
    const filteredEnquetes = useMemo(() => {
        if (!debouncedSearchTerm) return enquetes;
        
        return enquetes.filter(enquete => 
            (enquete.numeroDossier?.toLowerCase() || '').includes(debouncedSearchTerm) ||
            (enquete.nom?.toLowerCase() || '').includes(debouncedSearchTerm) ||
            (enquete.prenom?.toLowerCase() || '').includes(debouncedSearchTerm)
        );
    }, [enquetes, debouncedSearchTerm]);
    
    // Fonction optimisée pour l'assignation individuelle
    const handleAssignment = useCallback(async (enqueteId, enqueteurId) => {
        try {
            setError(null);
            
            // Mise à jour optimiste de l'état
            setEnquetes(prevEnquetes => 
                prevEnquetes.map(enquete => 
                    enquete.numeroDossier === enqueteId 
                        ? { ...enquete, enqueteurId: enqueteurId || null }
                        : enquete
                )
            );
            
            const response = await api.post('/api/assign-enquete', {
                enqueteId,
                enqueteurId: enqueteurId || null
            });
            
            if (response.data.success) {
                setSuccessMessage('Assignation réussie!');
                setTimeout(() => setSuccessMessage(''), 3000);
            } else {
                // En cas d'échec, recharger les données pour corriger l'état
                fetchData();
            }
        } catch (error) {
            // Recharger les données en cas d'erreur pour corriger l'état
            fetchData();
            setError('Erreur lors de l\'assignation: ' + (error.response?.data?.error || error.message));
        }
    }, [fetchData]);
    
    // Fonction optimisée pour l'assignation en masse
    const handleBulkAssignment = useCallback(async () => {
        try {
            if (!selectedEnqueteur) {
                setError("Veuillez sélectionner un enquêteur");
                return;
            }
            
            const start = Math.max(0, startRange - 1);
            const end = Math.min(endRange, filteredEnquetes.length);
            
            // Vérifier que la plage est valide
            if (start >= end || start < 0) {
                setError("Plage d'assignation invalide");
                return;
            }
            
            const selectedEnquetes = filteredEnquetes.slice(start, end);
            
            // Création de promesses pour toutes les assignations
            const assignPromises = selectedEnquetes.map(enquete => 
                api.post('/api/assign-enquete', {
                    enqueteId: enquete.numeroDossier,
                    enqueteurId: selectedEnqueteur
                })
            );
            
            // Mise à jour optimiste de l'état
            setEnquetes(prevEnquetes => 
                prevEnquetes.map(enquete => {
                    const isInRange = selectedEnquetes.some(
                        e => e.numeroDossier === enquete.numeroDossier
                    );
                    return isInRange 
                        ? { ...enquete, enqueteurId: selectedEnqueteur } 
                        : enquete;
                })
            );
            
            // Exécution de toutes les assignations en parallèle
            await Promise.all(assignPromises);
            
            setSuccessMessage(`Assignation en masse réussie pour ${selectedEnquetes.length} enquête(s)!`);
            setShowBulkAssignModal(false);
            setSelectedEnqueteur('');
            
            // Rafraîchir les données pour confirmer les changements
            fetchData();
            
        } catch (error) {
            fetchData(); // Recharger les données en cas d'erreur
            setError('Erreur lors de l\'assignation en masse: ' + (error.response?.data?.error || error.message));
        }
    }, [fetchData, filteredEnquetes, startRange, endRange, selectedEnqueteur]);
    
    // Fonction pour gérer le changement de page
    const handlePageChange = useCallback((newPage) => {
        setCurrentPage(newPage);
    }, []);
    
    return (
        <div className="bg-gray-50 min-h-screen p-6">
            <div className="max-w-7xl mx-auto">
                {/* En-tête */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        Assignation des Enquêtes
                    </h1>
                    <p className="text-gray-600">
                        Gérez les assignations des enquêtes aux enquêteurs
                    </p>
                </div>

                {/* Barre de recherche et boutons d'action */}
                <div className="mb-6 flex flex-col sm:flex-row justify-between items-center gap-4">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Rechercher par numéro, nom ou prénom..."
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => fetchData(true)}
                            disabled={refreshing}
                            className="flex items-center px-4 py-2 border border-gray-300 bg-white rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <RefreshCw className={`w-5 h-5 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                            {refreshing ? 'Actualisation...' : 'Actualiser'}
                        </button>
                        <button
                            onClick={() => setShowBulkAssignModal(true)}
                            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            <Users className="w-5 h-5 mr-2" />
                            Assignation en masse
                        </button>
                    </div>
                </div>

                {/* Messages d'erreur et de succès */}
                {successMessage && (
                    <div className="mb-4 flex items-center bg-green-100 text-green-700 px-4 py-3 rounded-lg">
                        <Check className="w-5 h-5 mr-2" />
                        {successMessage}
                    </div>
                )}
                
                {error && (
                    <div className="mb-4 flex items-center bg-red-100 text-red-700 px-4 py-3 rounded-lg">
                        <AlertCircle className="w-5 h-5 mr-2" />
                        {error}
                    </div>
                )}

                {/* Contenu principal */}
                {loading && !refreshing ? (
                    <div className="flex justify-center items-center h-64">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : filteredEnquetes.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 bg-white rounded-lg border border-gray-200">
                        <UserPlus className="w-12 h-12 text-gray-400 mb-2" />
                        <p className="text-gray-600">Aucune enquête trouvée</p>
                    </div>
                ) : (
                    <>
                        {/* Tableau des enquêtes */}
                        <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
                            <div className="overflow-x-auto">
                                {filteredEnquetes.length > 100 ? (
                                    // Utilisation de la virtualisation pour les grandes listes
                                    <div style={{ height: '600px' }} className="overflow-y-auto">
                                        <List
                                            height={600}
                                            width="100%"
                                            itemCount={filteredEnquetes.length}
                                            itemSize={60}
                                        >
                                            {({ index, style }) => {
                                                const enquete = filteredEnquetes[index];
                                                const isSelected = index + 1 >= startRange && 
                                                                index + 1 <= endRange && 
                                                                showBulkAssignModal;
                                                
                                                return (
                                                    <div style={style} className={`flex items-center ${isSelected ? 'bg-blue-50' : ''}`}>
                                                        <div className="px-6 whitespace-nowrap text-sm font-medium text-gray-500">{index + 1}</div>
                                                        <div className="px-6 whitespace-nowrap text-sm font-medium text-gray-900">{enquete.numeroDossier}</div>
                                                        <div className="px-6 whitespace-nowrap text-sm text-gray-700">{enquete.nom}</div>
                                                        <div className="px-6 whitespace-nowrap text-sm text-gray-700">{enquete.prenom}</div>
                                                        <div className="px-6 whitespace-nowrap">
                                                            <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                                                                {enquete.typeDemande}
                                                            </span>
                                                        </div>
                                                        <div className="px-6 whitespace-nowrap">
                                                            <select
                                                                className="block w-full max-w-xs rounded-lg border border-gray-300 px-3 py-2 text-sm"
                                                                value={enquete.enqueteurId || ''}
                                                                onChange={(e) => handleAssignment(enquete.numeroDossier, e.target.value)}
                                                            >
                                                                <option value="">Sélectionner un enquêteur</option>
                                                                {enqueteurs.map((enqueteur) => (
                                                                    <option key={enqueteur.id} value={enqueteur.id}>
                                                                        {enqueteur.nom} {enqueteur.prenom}
                                                                    </option>
                                                                ))}
                                                            </select>
                                                        </div>
                                                    </div>
                                                );
                                            }}
                                        </List>
                                    </div>
                                ) : (
                                    // Table normale pour les petites listes
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead>
                                            <tr className="bg-gray-50">
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    #
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Numéro Dossier
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Nom
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Prénom
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Type Demande
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Assignation
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {filteredEnquetes.map((enquete, index) => (
                                                <EnqueteRow 
                                                    key={enquete.numeroDossier || enquete.id}
                                                    enquete={enquete}
                                                    index={index + 1}
                                                    enqueteurs={enqueteurs}
                                                    onAssign={handleAssignment}
                                                    isSelected={index + 1 >= startRange && 
                                                              index + 1 <= endRange && 
                                                              showBulkAssignModal}
                                                />
                                            ))}
                                        </tbody>
                                    </table>
                                )}
                            </div>
                        </div>
                        
                        {/* Pagination */}
                        <Pagination 
                            currentPage={currentPage}
                            totalPages={totalPages}
                            itemsPerPage={itemsPerPage}
                            setItemsPerPage={setItemsPerPage}
                            handlePageChange={handlePageChange}
                        />
                    </>
                )}

                {/* Modal d'assignation en masse */}
                {showBulkAssignModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                            <h3 className="text-lg font-semibold mb-4">Assignation en masse</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Plage de lignes (1-{filteredEnquetes.length})
                                    </label>
                                    <div className="flex gap-2">
                                        <input
                                            type="number"
                                            min="1"
                                            max={filteredEnquetes.length}
                                            value={startRange}
                                            onChange={(e) => setStartRange(parseInt(e.target.value) || 1)}
                                            className="w-24 px-3 py-2 border rounded-lg"
                                        />
                                        <span className="flex items-center">à</span>
                                        <input
                                            type="number"
                                            min={startRange}
                                            max={filteredEnquetes.length}
                                            value={endRange}
                                            onChange={(e) => setEndRange(
                                                Math.max(
                                                    startRange, 
                                                    Math.min(parseInt(e.target.value) || startRange, filteredEnquetes.length)
                                                )
                                            )}
                                            className="w-24 px-3 py-2 border rounded-lg"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Sélectionner l&apos;enquêteur
                                    </label>
                                    <select
                                        className="w-full px-3 py-2 border rounded-lg"
                                        value={selectedEnqueteur}
                                        onChange={(e) => setSelectedEnqueteur(e.target.value)}
                                    >
                                        <option value="">Choisir un enquêteur</option>
                                        {enqueteurs.map((enqueteur) => (
                                            <option key={enqueteur.id} value={enqueteur.id}>
                                                {enqueteur.nom} {enqueteur.prenom}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="flex gap-2 justify-end mt-6">
                                    <button
                                        onClick={() => setShowBulkAssignModal(false)}
                                        className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                                    >
                                        Annuler
                                    </button>
                                    <button
                                        onClick={handleBulkAssignment}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                                    >
                                        Assigner
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssignmentViewer;