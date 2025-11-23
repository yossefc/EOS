import { useCallback, useState, useEffect } from "react";
import axios from 'axios';
import {
    Users, Plus, Trash2, Download, RefreshCw, Mail, Phone,  Shield,
    Search,  AlertTriangle, Check, User, ArrowUpRight
} from "lucide-react";
import VPNTemplateManager from "./VPNTemplateManager";
import EnhancedEnqueteurForm from "./EnhancedEnqueteurForm";
import config from '../config';

const API_URL = config.API_URL;

function ImprovedEnqueteurViewer() {
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [filteredEnqueteurs, setFilteredEnqueteurs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showTemplateManager, setShowTemplateManager] = useState(false);
    const [downloadingVpn, setDownloadingVpn] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statsVisible, setStatsVisible] = useState({});

    const fetchEnqueteurs = useCallback(async () => {
        try {
          setLoading(true);
          const response = await axios.get(`${API_URL}/api/enqueteurs-stats`);
          if (response.data.success) {
            setEnqueteurs(response.data.data);
          } else {
            throw new Error(response.data.error || 'Erreur lors de la récupération des enquêteurs');
          }
        } catch (error) {
          console.error("Erreur:", error);
          setError(error.message);
        } finally {
          setLoading(false);
        }
      }, []);
      

    // Appliquer les filtres
    const applyFilters = (data, search) => {
        if (!search) {
            setFilteredEnqueteurs(data);
            return;
        }
        
        const searchLower = search.toLowerCase();
        const filtered = data.filter(enqueteur =>
            (enqueteur.nom && enqueteur.nom.toLowerCase().includes(searchLower)) ||
            (enqueteur.prenom && enqueteur.prenom.toLowerCase().includes(searchLower)) ||
            (enqueteur.email && enqueteur.email.toLowerCase().includes(searchLower)) ||
            (enqueteur.telephone && enqueteur.telephone.includes(searchLower))
        );
        
        setFilteredEnqueteurs(filtered);
    };

    useEffect(() => {
        fetchEnqueteurs();
      }, [fetchEnqueteurs]);
      

    useEffect(() => {
        applyFilters(enqueteurs, searchTerm);
    }, [searchTerm, enqueteurs]);

    // Gérer la recherche
    const handleSearch = (e) => {
        setSearchTerm(e.target.value);
    };

    const handleRefresh = () => {
        fetchEnqueteurs();
    };

    const handleEnqueteurAdded = (newEnqueteur) => {
        setSuccessMessage(`Enquêteur ${newEnqueteur.prenom} ${newEnqueteur.nom} ajouté avec succès`);
        setTimeout(() => setSuccessMessage(null), 5000);
        fetchEnqueteurs();
    };

    const handleDeleteEnqueteur = async (id) => {
        if (window.confirm("Êtes-vous sûr de vouloir supprimer cet enquêteur? Cette action supprimera également toutes ses assignations d'enquêtes.")) {
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
                
                setSuccessMessage("Configuration VPN téléchargée avec succès");
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

    const toggleStats = (id) => {
        setStatsVisible(prev => ({
            ...prev,
            [id]: !prev[id]
        }));
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
                <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5" />
                    <span>{error}</span>
                </div>
                <button
                    onClick={handleRefresh}
                    className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    Réessayer
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Messages de succès */}
            {successMessage && (
                <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-500" />
                    <span>{successMessage}</span>
                </div>
            )}

            {/* Affichage du formulaire ou du template manager */}
            {showAddForm ? (
                <EnhancedEnqueteurForm 
                    onEnqueteurAdded={handleEnqueteurAdded} 
                    onClose={() => setShowAddForm(false)} 
                />
            ) : showTemplateManager ? (
                <VPNTemplateManager />
            ) : (
                <div className="bg-white shadow rounded-lg p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                            <Users className="w-6 h-6 text-blue-500" />
                            Enquêteurs ({filteredEnqueteurs.length})
                        </h2>

                        <div className="flex items-center gap-2">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                                <input
                                    type="text"
                                    placeholder="Rechercher un enquêteur..."
                                    className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                    value={searchTerm}
                                    onChange={handleSearch}
                                />
                            </div>
                            <button
                                onClick={() => setShowTemplateManager(true)}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                                title="Gérer le modèle de configuration OpenVPN"
                            >
                                <Shield className="w-4 h-4" />
                                <span className="hidden md:inline">Template VPN</span>
                            </button>
                            <button
                                onClick={() => setShowAddForm(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                            >
                                <Plus className="w-4 h-4" />
                                <span className="hidden md:inline">Ajouter un enquêteur</span>
                            </button>
                            <button
                                onClick={handleRefresh}
                                className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                                title="Actualiser la liste"
                            >
                                <RefreshCw className="w-4 h-4" />
                            </button>
                        </div>
                    </div>

                    {/* Instructions OpenVPN */}
                    <div className="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg">
                        <div className="flex items-start gap-3">
                            <div className="rounded-full p-2 bg-blue-100">
                                <Shield className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                                <h3 className="font-medium text-blue-800 mb-1">Configuration OpenVPN</h3>
                                <p className="text-sm text-blue-700">
                                    Chaque enquêteur peut se connecter à l&apos;interface restreinte avec son adresse email. 
                                    Pour un accès sécurisé, téléchargez et partagez avec lui sa configuration OpenVPN personnelle.
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Liste des enquêteurs */}
                    <div className="grid grid-cols-1 gap-4">
                        {filteredEnqueteurs.length === 0 ? (
                            <div className="bg-gray-50 rounded-lg p-8 text-center">
                                <User className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                                {searchTerm ? (
                                    <p className="text-gray-500">Aucun enquêteur ne correspond à votre recherche</p>
                                ) : (
                                    <p className="text-gray-500">Aucun enquêteur disponible. Ajoutez-en un pour commencer.</p>
                                )}
                            </div>
                        ) : (
                            filteredEnqueteurs.map((enqueteur) => (
                                <div key={enqueteur.id} className="border rounded-lg overflow-hidden bg-white">
                                    {/* En-tête avec les informations de base */}
                                    <div className="p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b">
                                        <div className="flex items-center gap-3">
                                            <div className="flex-shrink-0 h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                                                <span className="text-blue-700 font-bold text-lg">
                                                    {enqueteur.prenom?.[0]}{enqueteur.nom?.[0]}
                                                </span>
                                            </div>
                                            <div>
                                                <h3 className="font-medium text-lg">{enqueteur.prenom} {enqueteur.nom}</h3>
                                                <div className="flex flex-wrap items-center text-sm text-gray-500 gap-x-4">
                                                    <div className="flex items-center gap-1">
                                                        <Mail className="w-4 h-4 text-gray-400" />
                                                        <span>{enqueteur.email}</span>
                                                    </div>
                                                    {enqueteur.telephone && (
                                                        <div className="flex items-center gap-1">
                                                            <Phone className="w-4 h-4 text-gray-400" />
                                                            <span>{enqueteur.telephone}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 ml-auto">
                                            <button
                                                onClick={() => handleDownloadVpnConfig(enqueteur.id)}
                                                className="flex items-center gap-1 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100"
                                                disabled={downloadingVpn === enqueteur.id}
                                            >
                                                {downloadingVpn === enqueteur.id ? (
                                                    <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                                ) : (
                                                    <Download className="w-4 h-4" />
                                                )}
                                                <span>Config VPN</span>
                                            </button>
                                            <button
                                                onClick={() => toggleStats(enqueteur.id)}
                                                className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
                                            >
                                                <span>{statsVisible[enqueteur.id] ? "Masquer stats" : "Voir stats"}</span>
                                            </button>
                                            <button
                                                onClick={() => handleDeleteEnqueteur(enqueteur.id)}
                                                className="flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 rounded-md hover:bg-red-100"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                                <span>Supprimer</span>
                                            </button>
                                        </div>
                                    </div>
                                    
                                    {/* Statistiques d'enquêtes (affichées conditionnellement) */}
                                    {statsVisible[enqueteur.id] && (
                                        <div className="p-4 bg-gray-50">
                                            <h4 className="font-medium text-gray-700 mb-3">Statistiques des enquêtes</h4>
                                            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                                                <div className="bg-white p-3 rounded-lg border">
                                                    <div className="text-sm text-gray-500">Total</div>
                                                    <div className="text-xl font-semibold">{enqueteur.total_enquetes || 0}</div>
                                                </div>
                                                <div className="bg-white p-3 rounded-lg border">
                                                    <div className="text-sm text-gray-500">En attente</div>
                                                    <div className="text-xl font-semibold text-yellow-500">{enqueteur.statuts?.pending || 0}</div>
                                                </div>
                                                <div className="bg-white p-3 rounded-lg border">
                                                    <div className="text-sm text-gray-500">Positifs</div>
                                                    <div className="text-xl font-semibold text-green-500">{enqueteur.statuts?.P || 0}</div>
                                                </div>
                                                <div className="bg-white p-3 rounded-lg border">
                                                    <div className="text-sm text-gray-500">Négatifs</div>
                                                    <div className="text-xl font-semibold text-red-500">{enqueteur.statuts?.N || 0}</div>
                                                </div>
                                                <div className="bg-white p-3 rounded-lg border">
                                                    <div className="text-sm text-gray-500">Autres</div>
                                                    <div className="text-xl font-semibold text-gray-500">
                                                        {(enqueteur.statuts?.H || 0) + 
                                                         (enqueteur.statuts?.Z || 0) + 
                                                         (enqueteur.statuts?.I || 0) + 
                                                         (enqueteur.statuts?.Y || 0)}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>
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
                        className="px-4 py-2 text-blue-600 hover:underline font-medium flex items-center gap-1"
                    >
                        <ArrowUpRight className="w-4 h-4 rotate-180" />
                        Retour à la liste des enquêteurs
                    </button>
                </div>
            )}
        </div>
    );
}

export default ImprovedEnqueteurViewer;