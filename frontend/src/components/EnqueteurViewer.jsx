import React, { useState, useEffect } from "react";
import { Users, Plus, Trash2, Download, RefreshCw } from "lucide-react";
import VPNTemplateManager from "./VPNTemplateManager";
import config from '../config';

const API_URL = config.API_URL;

function EnqueteurViewer() {
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showTemplateManager, setShowTemplateManager] = useState(false);

    const fetchEnqueteurs = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/enqueteurs`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (data.success) {
                setEnqueteurs(data.data);
            } else {
                throw new Error(data.error || 'Erreur lors de la récupération des enquêteurs');
            }
        } catch (error) {
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchEnqueteurs();
    }, []);

    const handleRefresh = () => {
        fetchEnqueteurs();
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
                    <Users className="w-6 h-6" />
                    Enquêteurs ({enqueteurs.length})
                </h2>

                <div className="flex items-center gap-4">
                    <button
                        onClick={handleRefresh}
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
                                Nom
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Prénom
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Email
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Téléphone
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {enqueteurs.map((enqueteur) => (
                            <tr key={enqueteur.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {enqueteur.nom}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {enqueteur.prenom}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {enqueteur.email}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {enqueteur.telephone}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {enqueteurs.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                    Aucun enquêteur disponible
                </div>
            )}
        </div>
    );
}

export default EnqueteurViewer;