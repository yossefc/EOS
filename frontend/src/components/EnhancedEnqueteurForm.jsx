import  { useState } from "react";
import PropTypes from 'prop-types'; // Import PropTypes
import { User, Plus, Download, Mail, Phone, Shield, Check, X } from "lucide-react";
import axios from 'axios';
import config from '../config';

const API_URL = config.API_URL;

const EnhancedEnqueteurForm = ({ onEnqueteurAdded, onClose }) => {
    const [formData, setFormData] = useState({
        nom: '',
        prenom: '',
        email: '',
        telephone: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [newEnqueteur, setNewEnqueteur] = useState(null);
    const [downloadingVpn, setDownloadingVpn] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccess(null);

        try {
            // Validation basique
            if (!formData.nom || !formData.prenom || !formData.email) {
                throw new Error("Les champs nom, prénom et email sont obligatoires");
            }

            // Validation email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(formData.email)) {
                throw new Error("L'adresse email n'est pas valide");
            }

            // Envoyer la demande
            const response = await axios.post(`${API_URL}/api/enqueteurs`, formData);

            if (response.data.success) {
                // Afficher le message de succès
                setSuccess(`Enquêteur ${formData.prenom} ${formData.nom} créé avec succès!`);
                setNewEnqueteur(response.data.data);
                
                // Réinitialiser le formulaire
                setFormData({
                    nom: '',
                    prenom: '',
                    email: '',
                    telephone: ''
                });
                
                // Informer le parent du succès
                onEnqueteurAdded(response.data.data);
            } else {
                throw new Error(response.data.error || "Erreur lors de la création de l'enquêteur");
            }
        } catch (err) {
            setError(err.message || "Une erreur s'est produite");
            console.error("Erreur:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadVpnConfig = async (id) => {
        try {
            setDownloadingVpn(true);
            
            // Vérifier si la configuration VPN est disponible
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
                
                setSuccess(prev => `${prev} Configuration VPN téléchargée.`);
            } else {
                throw new Error(response.data.error || "Erreur lors de la génération de la config VPN");
            }
        } catch (error) {
            console.error("Erreur lors du téléchargement de la config VPN:", error);
            setError(error.message);
        } finally {
            setDownloadingVpn(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <User className="w-5 h-5" />
                Nouvel enquêteur
            </h2>

            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-md flex items-center gap-2">
                    <X className="w-5 h-5 text-red-500" />
                    {error}
                </div>
            )}

            {success && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-600 rounded-md flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-500" />
                    {success}
                </div>
            )}

            {newEnqueteur ? (
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
                    <h3 className="font-semibold text-blue-700 mb-2">Enquêteur ajouté avec succès</h3>
                    <div className="mb-4">
                        <p><span className="font-medium">Nom:</span> {newEnqueteur.nom} {newEnqueteur.prenom}</p>
                        <p><span className="font-medium">Email:</span> {newEnqueteur.email}</p>
                        {newEnqueteur.telephone && <p><span className="font-medium">Téléphone:</span> {newEnqueteur.telephone}</p>}
                    </div>
                    
                    <div className="flex gap-2">
                        <button
                            onClick={() => handleDownloadVpnConfig(newEnqueteur.id)}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            disabled={downloadingVpn}
                        >
                            {downloadingVpn ? (
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            ) : (
                                <Download className="w-4 h-4" />
                            )}
                            <span>Télécharger config VPN</span>
                        </button>
                        <button
                            onClick={() => {
                                setNewEnqueteur(null);
                                setSuccess(null);
                            }}
                            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                        >
                            Ajouter un autre enquêteur
                        </button>
                    </div>
                </div>
            ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Nom*
                            </label>
                            <input
                                type="text"
                                name="nom"
                                value={formData.nom}
                                onChange={handleChange}
                                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Prénom*
                            </label>
                            <input
                                type="text"
                                name="prenom"
                                value={formData.prenom}
                                onChange={handleChange}
                                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Email*
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full pl-10 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <p className="mt-1 text-xs text-gray-500">
                                Cet email sera utilisé par l&apos;enquêteur pour se connecter
                            </p>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Téléphone
                            </label>
                            <div className="relative">
                                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                                <input
                                    type="tel"
                                    name="telephone"
                                    value={formData.telephone}
                                    onChange={handleChange}
                                    className="w-full pl-10 p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                        </div>
                    </div>
                    
                    <div className="p-4 bg-blue-50 rounded-md mt-4">
                        <div className="flex items-start gap-2">
                            <Shield className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-medium text-blue-700">Accès OpenVPN</p>
                                <p className="text-xs text-blue-600">
                                    Une configuration OpenVPN sera automatiquement générée pour cet enquêteur. 
                                    Vous pourrez la télécharger après la création ou plus tard depuis la liste des enquêteurs.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="flex justify-end space-x-4 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                        >
                            Annuler
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                    <span>Création...</span>
                                </>
                            ) : (
                                <>
                                    <Plus className="w-5 h-5" />
                                    <span>Créer l&apos;enquêteur</span>
                                </>
                            )}
                        </button>
                    </div>
                </form>
            )}
        </div>
    );
};

// Add PropTypes validation
EnhancedEnqueteurForm.propTypes = {
    onEnqueteurAdded: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired
};

export default EnhancedEnqueteurForm;