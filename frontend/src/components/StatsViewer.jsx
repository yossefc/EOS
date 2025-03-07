import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { BarChart, RefreshCcw } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const StatsViewer = forwardRef((props, ref) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(`${API_URL}/api/stats`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err.message || 'Erreur lors de la récupération des statistiques');
        } finally {
            setLoading(false);
        }
    };

    // Expose fetchStats to parent components
    useImperativeHandle(ref, () => ({
        fetchStats
    }));

    useEffect(() => {
        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <span>Chargement des statistiques...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white shadow rounded-lg p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                    <BarChart className="w-6 h-6" />
                    Statistiques globales
                </h2>
                <button
                    onClick={fetchStats}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                    <RefreshCcw className="w-4 h-4" />
                    Actualiser
                </button>
            </div>

            {error ? (
                <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
                    {error}
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        <div className="bg-blue-50 p-4 rounded-lg">
                            <div className="text-blue-600 text-sm font-medium">
                                Fichiers importés
                            </div>
                            <div className="text-2xl font-bold mt-1">
                                {stats?.total_fichiers || 0}
                            </div>
                        </div>
                        <div className="bg-green-50 p-4 rounded-lg">
                            <div className="text-green-600 text-sm font-medium">
                                Données totales
                            </div>
                            <div className="text-2xl font-bold mt-1">
                                {stats?.total_donnees || 0}
                            </div>
                        </div>
                    </div>

                    <div className="border-t pt-4">
                        <h3 className="text-lg font-semibold mb-4">
                            Derniers fichiers traités
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead>
                                    <tr>
                                        <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Nom du fichier
                                        </th>
                                        <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Date import
                                        </th>
                                        <th className="px-6 py-3 bg-gray-50 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Données
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {stats?.derniers_fichiers?.map((fichier) => (
                                        <tr key={fichier.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                {fichier.nom}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {fichier.date_upload}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right">
                                                {fichier.nombre_donnees}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
});

StatsViewer.displayName = 'StatsViewer';

export default StatsViewer;