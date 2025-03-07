import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Loader2, AlertCircle, UserPlus, Check, Search, Users } from 'lucide-react';

const api = axios.create({
    baseURL: 'http://localhost:5000',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

const AssignmentViewer = () => {
    const [enquetes, setEnquetes] = useState([]);
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [startRange, setStartRange] = useState(1);
    const [endRange, setEndRange] = useState(1);
    const [selectedEnqueteur, setSelectedEnqueteur] = useState('');
    const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const [enquetesResponse, enqueteursResponse] = await Promise.all([
                    api.get('/api/donnees'),
                    api.get('/api/enqueteurs')
                ]);

                if (enquetesResponse.data.success && Array.isArray(enquetesResponse.data.data)) {
                    setEnquetes(enquetesResponse.data.data);
                }

                if (enqueteursResponse.data.success && Array.isArray(enqueteursResponse.data.data)) {
                    setEnqueteurs(enqueteursResponse.data.data);
                }
                
            } catch (error) {
                setError('Erreur lors du chargement des données: ' + (error.response?.data?.error || error.message));
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleAssignment = async (enqueteId, enqueteurId) => {
        try {
            setError(null);
            const response = await api.post('/api/assign-enquete', {
                enqueteId,
                enqueteurId: enqueteurId || null
            });
            
            if (response.data.success) {
                const donnees = await api.get('/api/donnees');
                if (donnees.data.success) {
                    setEnquetes(donnees.data.data);
                    setSuccessMessage('Assignation réussie!');
                    setTimeout(() => setSuccessMessage(''), 3000);
                }
            }
        } catch (error) {
            setError('Erreur lors de l\'assignation: ' + (error.response?.data?.error || error.message));
        }
    };

    const handleBulkAssignment = async () => {
        try {
            if (!selectedEnqueteur) {
                setError("Veuillez sélectionner un enquêteur");
                return;
            }

            const start = Math.max(0, startRange - 1);
            const end = Math.min(endRange, filteredEnquetes.length);
            
            const selectedEnquetes = filteredEnquetes.slice(start, end);
            
            for (const enquete of selectedEnquetes) {
                await handleAssignment(enquete.numeroDossier, selectedEnqueteur);
            }
            
            setSuccessMessage(`Assignation en masse réussie pour ${selectedEnquetes.length} enquête(s)!`);
            setShowBulkAssignModal(false);
            setSelectedEnqueteur('');
            
        } catch (error) {
            setError('Erreur lors de l\'assignation en masse: ' + error.message);
        }
    };

    const filteredEnquetes = enquetes.filter(enquete => 
        enquete.numeroDossier?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        enquete.nom?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        enquete.prenom?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="bg-gray-50 min-h-screen p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header Section */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        Assignation des Enquêtes
                    </h1>
                    <p className="text-gray-600">
                        Gérez les assignations des enquêtes aux enquêteurs
                    </p>
                </div>

                {/* Search and Bulk Assignment */}
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
                    <button
                        onClick={() => setShowBulkAssignModal(true)}
                        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Users className="w-5 h-5 mr-2" />
                        Assignation en masse
                    </button>
                </div>

                {successMessage && (
                    <div className="mb-4 flex items-center bg-green-100 text-green-700 px-4 py-2 rounded-lg">
                        <Check className="w-5 h-5 mr-2" />
                        {successMessage}
                    </div>
                )}

                {/* Main Content */}
                {loading ? (
                    <div className="flex justify-center items-center h-64">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : error ? (
                    <div className="flex items-center justify-center h-64 bg-red-50 rounded-lg">
                        <AlertCircle className="w-6 h-6 text-red-500 mr-2" />
                        <p className="text-red-600">{error}</p>
                    </div>
                ) : !filteredEnquetes.length ? (
                    <div className="flex flex-col items-center justify-center h-64 bg-white rounded-lg border border-gray-200">
                        <UserPlus className="w-12 h-12 text-gray-400 mb-2" />
                        <p className="text-gray-600">Aucune enquête trouvée</p>
                    </div>
                ) : (
                    <div className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-200">
                        <div className="overflow-x-auto">
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
                                        <tr 
                                            key={enquete.numeroDossier || enquete.id}
                                            className={`hover:bg-gray-50 transition-colors duration-150 ease-in-out 
                                                ${index + 1 >= startRange && index + 1 <= endRange && showBulkAssignModal 
                                                    ? 'bg-blue-50' 
                                                    : ''}`}
                                        >
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-500">
                                                {index + 1}
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
                                                    onChange={(e) => handleAssignment(enquete.numeroDossier, e.target.value)}
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
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}

                {/* Modal d'assignation en masse */}
                {showBulkAssignModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
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
                                            onChange={(e) => setStartRange(parseInt(e.target.value))}
                                            className="w-24 px-3 py-2 border rounded-lg"
                                        />
                                        <span className="flex items-center">à</span>
                                        <input
                                            type="number"
                                            min={startRange}
                                            max={filteredEnquetes.length}
                                            value={endRange}
                                            onChange={(e) => setEndRange(parseInt(e.target.value))}
                                            className="w-24 px-3 py-2 border rounded-lg"
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Sélectionner l'enquêteur
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