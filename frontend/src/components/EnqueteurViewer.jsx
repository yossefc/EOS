import React, { useState, useEffect } from "react";
import { Users, Plus, Trash2, Download, RefreshCw, Mail, Phone, Key, Shield } from "lucide-react";
import VPNTemplateManager from "./VPNTemplateManager";
import EnqueteurForm from "./EnqueteurForm";
import axios from 'axios';
import config from '../config';

const API_URL = config.API_URL;

function EnqueteurViewer() {
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showTemplateManager, setShowTemplateManager] = useState(false);
    const [downloadingVpn, setDownloadingVpn] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const fetchEnqueteurs = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_URL}/api/enqueteurs`);
            if (response.data.success) {
                setEnqueteurs(response.data.data);
            } else {
                throw new Error(response.data.error || 'Erreur lors de la récupération des enquêteurs');
            }
        } catch (error) {
            console.error("Erreur lors de la récupération des enquêteurs:", error);
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

    const handleEnqueteurAdded = (newEnqueteur) => {
        setSuccessMessage(`Enquêteur ${newEnqueteur.prenom} ${newEnqueteur.nom} ajouté avec succès`);
        setTimeout(() => setSuccessMessage(null), 5000);
        fetchEnqueteurs();
    };

    const handleDeleteEnqueteur = async (id) => {
        if (window.confirm("Êtes-vous sûr de vouloir supprimer cet enquêteur?")) {
            try {
                const response = await axios.delete(`${API_URL}/api/enqueteurs/${id}`);
                if (response.data.success) {
                    setSuccessMessage("Enquêteur supprimé avec succès");
                    setTimeout(() => setSuccessMessage(null), 5000);
                    fetchEnqueteurs();
                } else {
                    throw new Error(response.data.error || "Erreur lors de la suppression");
                }
            } catch (error) {
                console.error("Erreur lors de la suppression:", error);
                setError(error.message);
            }
        }
    };

    const handleDownloadVpnConfig = async (id) => {
        try {
            setDownloadingVpn(id);
            const response = await axios.get(`${API_URL}/api/enqueteurs/${id}/vpn-config`);
            
            if (response.data.success) {
                // Créer un lien de téléchargement pour le fichier
                const downloadUrl = `${API_URL}/api/download/vpn-config/${id}`;
                
                // Créer un élément <a> temporaire et cliquer dessus pour démarrer le téléchargement
                const link = document.createElement('a');
                link.href = downloadUrl;
                link.setAttribute('download', `client${id}.ovpn`);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                setSuccessMessage("Configuration VPN prête à être téléchargée");
                setTimeout(() => setSuccessMessage(null), 5000);
            } else {
                throw new Error(response.data.error || "Erreur lors de la génération de la config VPN");
            }
        } catch (error) {
            console.error("Erreur lors du téléchargement de la config VPN:", error);
            setError(error.message);
        } finally {
            setDownloadingVpn(null);
        }
    };

    if (loading && enqueteurs.length === 0) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

    if (error && enqueteurs.length === 0) {
        return (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                Erreur: {error}
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Messages de succès */}
            {successMessage && (
                <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg">
                    {successMessage}
                </div>
            )}

            {/* Affichage du formulaire ou du template manager */}
            {showAddForm ? (
                <EnqueteurForm 
                    onEnqueteurAdded={handleEnqueteurAdded} 
                    onClose={() => setShowAddForm(false)} 
                />
            ) : showTemplateManager ? (
                <VPNTemplateManager />
            ) : (
                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Users className="w-6 h-6" />
                            Enquêteurs ({enqueteurs.length})
                        </h2>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setShowTemplateManager(true)}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                            >
                                <Shield className="w-4 h-4" />
                                Template VPN
                            </button>
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                            >
                                <Plus className="w-4 h-4" />
                                Ajouter
                            </button>
                            <button
                                onClick={handleRefresh}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
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
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        VPN
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Actions
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
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <div className="flex items-center gap-2">
                                                <Mail className="w-4 h-4 text-blue-500" />
                                                {enqueteur.email}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {enqueteur.telephone ? (
                                                <div className="flex items-center gap-2">
                                                    <Phone className="w-4 h-4 text-green-500" />
                                                    {enqueteur.telephone}
                                                </div>
                                            ) : (
                                                <span className="text-gray-400">Non renseigné</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                                            <button
                                                onClick={() => handleDownloadVpnConfig(enqueteur.id)}
                                                className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-md hover:bg-blue-200"
                                                disabled={downloadingVpn === enqueteur.id}
                                            >
                                                {downloadingVpn === enqueteur.id ? (
                                                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                                ) : (
                                                    <Download className="w-4 h-4" />
                                                )}
                                                <span>Config VPN</span>
                                            </button>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <button
                                                onClick={() => handleDeleteEnqueteur(enqueteur.id)}
                                                className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 rounded-md hover:bg-red-200"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                                <span>Supprimer</span>
                                            </button>
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
            )}

            {/* Bouton de retour si on affiche un formulaire/manager */}
            {(showAddForm || showTemplateManager) && (
                <div className="mt-4">
                    <button
                        onClick={() => {
                            setShowAddForm(false);
                            setShowTemplateManager(false);
                        }}
                        className="px-4 py-2 text-blue-600 hover:underline font-medium"
                    >
                        ← Retour à la liste des enquêteurs
                    </button>
                </div>
            )}
        </div>
    );
}

export default EnqueteurViewer;