import  { useState } from 'react';
import { Mail, LogIn, AlertCircle } from 'lucide-react';
import axios from 'axios';
import config from '../config';
import PropTypes from 'prop-types';

EnqueteurLogin.propTypes = {
    onLoginSuccess: PropTypes.func.isRequired, // ou .isOptional si ce n’est pas obligatoire
  };

const API_URL = config.API_URL;

const EnqueteurLogin = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // EnqueteurLogin.jsx
const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
        // Valider l'email
        if (!email) {
            throw new Error("Veuillez saisir votre adresse email");
        }

        console.log("Tentative de connexion avec:", email);

        // Envoyer la demande d'authentification
        const response = await axios.post(`${API_URL}/api/enqueteur/auth`, { email });
        console.log("Réponse d'authentification:", response.data);

        if (response.data.success) {
            // Vérifier que l'ID est présent
            if (!response.data.data.id) {
                throw new Error("L'ID de l'enquêteur est manquant dans la réponse");
            }

            // Stocker les informations avec conversion explicite en chaîne
            const enqueteurId = String(response.data.data.id);
            localStorage.setItem('enqueteurId', enqueteurId);
            localStorage.setItem('enqueteurNom', response.data.data.nom || '');
            localStorage.setItem('enqueteurPrenom', response.data.data.prenom || '');
            localStorage.setItem('enqueteurEmail', response.data.data.email || '');
            
            console.log("Informations stockées dans localStorage:", {
                enqueteurId,
                nom: response.data.data.nom,
                prenom: response.data.data.prenom,
                email: response.data.data.email
            });
            
            // Informer le parent du succès
            onLoginSuccess(response.data.data);
        } else {
            throw new Error(response.data.error || "Erreur d'authentification");
        }
    } catch (err) {
        console.error("Erreur de connexion:", err);
        setError(err.response?.data?.error || err.message || "Erreur lors de la connexion");
    } finally {
        setLoading(false);
    }
};

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
            <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
                <div className="text-center mb-8">
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">
                        EOS France
                    </h1>
                    <p className="text-gray-600">
                        Accès enquêteur
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-center gap-2">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Adresse email
                        </label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="pl-10 w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                placeholder="votre.email@exemple.com"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow flex items-center justify-center gap-2"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                <span>Connexion en cours...</span>
                            </>
                        ) : (
                            <>
                                <LogIn className="w-5 h-5" />
                                <span>Se connecter</span>
                            </>
                        )}
                    </button>
                </form>

                <div className="mt-8 text-center text-sm text-gray-500">
                    Pour accéder à votre espace, utilisez l&apos;adresse email fournie par l&apos;administrateur.
                </div>
            </div>
        </div>
    );
};

export default EnqueteurLogin;