import React, { useState, useEffect } from 'react';
import { Table, RefreshCw, Search } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const DataViewer = () => {
    const [donnees, setDonnees] = useState([]);
    const [filteredDonnees, setFilteredDonnees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchData = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(`${API_URL}/api/donnees`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                setDonnees(data.data);
                setFilteredDonnees(data.data);
            } else {
                throw new Error('Format de données invalide');
            }
        } catch (err) {
            console.error('Error fetching data:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = (value) => {
        setSearchTerm(value);
        if (!value.trim()) {
            setFilteredDonnees(donnees);
            return;
        }

        const searchTermLower = value.toLowerCase();
        const filtered = donnees.filter(donnee =>
            donnee.numeroDossier?.toLowerCase().includes(searchTermLower) ||
            donnee.nom?.toLowerCase().includes(searchTermLower) ||
            donnee.prenom?.toLowerCase().includes(searchTermLower) ||
            donnee.ville?.toLowerCase().includes(searchTermLower)
        );
        setFilteredDonnees(filtered);
    };

    useEffect(() => {
        fetchData();
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

                <div className="flex items-center gap-4">
                    <div className="relative">
                        <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => handleSearch(e.target.value)}
                            placeholder="Rechercher..."
                            className="pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
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
                                Date Naissance
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Ville
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Code Postal
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {filteredDonnees.map((donnee, index) => (
                            <tr key={index} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.numeroDossier}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.nom}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.prenom}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.dateNaissance}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.ville}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                    {donnee.codePostal}
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
        </div>
    );
};

export default DataViewer;