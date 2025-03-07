import React, { useState } from 'react';
import axios from 'axios';
import { FileUp, AlertCircle, Check, Calendar } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const ImportHandler = ({ onImportComplete }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [stats, setStats] = useState(null);
    const [confirmReplace, setConfirmReplace] = useState(false);
    const [existingFileInfo, setExistingFileInfo] = useState(null);
    const [deadlineDate, setDeadlineDate] = useState('');
    const [showDatePicker, setShowDatePicker] = useState(false);

    const resetStatus = () => {
        setError(null);
        setSuccess(null);
        setConfirmReplace(false);
        setExistingFileInfo(null);
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            // Vérifier le type et l'extension du fichier
            if (selectedFile.name.endsWith('.txt')) {
                setFile(selectedFile);
                resetStatus();
            } else {
                setError("Seuls les fichiers texte (.txt) sont acceptés selon le cahier des charges");
                setFile(null);
                e.target.value = '';
            }
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Veuillez sélectionner un fichier");
            return;
        }

        setUploading(true);
        resetStatus();

        const formData = new FormData();
        formData.append("file", file);
        
        // Ajouter la date butoir si elle est définie
        if (deadlineDate) {
            formData.append("deadline_date", deadlineDate);
        }

        try {
            const response = await axios.post(`${API_URL}/parse`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                // Ne pas lever d'exception pour l'erreur 409
                validateStatus: function (status) {
                    return status < 500; // Considère les statuts 2xx, 3xx et 4xx comme des succès
                }
            });

            if (response.status === 409) {
                // Fichier existe déjà
                setExistingFileInfo(response.data.existing_file_info);
                setConfirmReplace(true);
            } else if (response.status === 200 || response.status === 201) {
                // Import réussi
                setSuccess(`Fichier ${file.name} importé avec succès! ${response.data.records_processed || 0} enregistrements traités.${deadlineDate ? ` Date butoir fixée au ${formatDate(deadlineDate)}.` : ''}`);
                setStats({
                    fileId: response.data.file_id,
                    recordsProcessed: response.data.records_processed || 0,
                    deadlineDate: deadlineDate || null
                });

                // Notifier le composant parent
                if (onImportComplete) {
                    onImportComplete();
                }

                // Réinitialiser le champ de fichier et la date
                setFile(null);
                setDeadlineDate('');
                setShowDatePicker(false);
                const fileInput = document.getElementById('file-import');
                if (fileInput) fileInput.value = '';
            } else {
                // Autres erreurs (400, 401, 403, etc.)
                throw new Error(response.data?.error || `Erreur ${response.status} lors de l'import`);
            }
        } catch (err) {
            console.error('Erreur lors de l\'import:', err);
            setError(err.response?.data?.error || err.message || 'Erreur lors de l\'import du fichier');
        } finally {
            setUploading(false);
        }
    };

    const handleReplaceFile = async () => {
        if (!file) return;

        setUploading(true);
        resetStatus();

        const formData = new FormData();
        formData.append("file", file);
        
        // Ajouter la date butoir si elle est définie
        if (deadlineDate) {
            formData.append("deadline_date", deadlineDate);
        }

        try {
            const response = await axios.post(`${API_URL}/replace-file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                // Ne pas lever d'exception pour les codes de statut < 500
                validateStatus: function (status) {
                    return status < 500;
                }
            });

            if (response.status === 200 || response.status === 201) {
                setSuccess(`Fichier ${file.name} remplacé avec succès! ${response.data.records_processed || 0} enregistrements traités.${deadlineDate ? ` Date butoir fixée au ${formatDate(deadlineDate)}.` : ''}`);

                // Notifier le composant parent
                if (onImportComplete) {
                    onImportComplete();
                }

                // Réinitialiser
                setFile(null);
                setDeadlineDate('');
                setShowDatePicker(false);
                const fileInput = document.getElementById('file-import');
                if (fileInput) fileInput.value = '';
            } else {
                // Autres erreurs (400, 401, 403, etc.)
                throw new Error(response.data?.error || `Erreur ${response.status} lors du remplacement`);
            }
        } catch (err) {
            console.error('Erreur lors du remplacement:', err);
            setError(err.response?.data?.error || err.message || 'Erreur lors du remplacement du fichier');
        } finally {
            setUploading(false);
        }
    };

    const handleCancelReplace = () => {
        setConfirmReplace(false);
        setExistingFileInfo(null);
        setFile(null);
        // Réinitialiser le champ de fichier
        const fileInput = document.getElementById('file-import');
        if (fileInput) fileInput.value = '';
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    };

    const handleDateToggle = () => {
        setShowDatePicker(!showDatePicker);
        if (!showDatePicker && !deadlineDate) {
            // Si on ouvre le picker et qu'aucune date n'est définie, proposer une date par défaut (J+30)
            const defaultDate = new Date();
            defaultDate.setDate(defaultDate.getDate() + 30);
            setDeadlineDate(defaultDate.toISOString().split('T')[0]);
        }
    };

    return (
        <div className="bg-white shadow-md rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
                <FileUp className="w-6 h-6 text-blue-500" />
                <h2 className="text-xl font-bold">Import de fichiers EOS</h2>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-start gap-2">
                    <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>{error}</div>
                </div>
            )}

            {success && (
                <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-start gap-2">
                    <Check className="w-5 h-5 mt-0.5 flex-shrink-0" />
                    <div>{success}</div>
                </div>
            )}

            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sélectionner un fichier au format texte
                </label>
                <p className="text-sm text-gray-500 mb-2">
                    Format attendu: fichier texte (.txt) contenant des données à longueur fixe selon le cahier des charges EOS.
                </p>
                <input
                    id="file-import"
                    type="file"
                    onChange={handleFileChange}
                    accept=".txt"
                    className="block w-full text-sm text-gray-500
                        file:mr-4 file:py-2 file:px-4
                        file:rounded-md file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100"
                    disabled={uploading || confirmReplace}
                />
            </div>

            {/* Bouton et champ pour la date butoir */}
            <div className="mb-6">
                <button
                    type="button"
                    onClick={handleDateToggle}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                    <Calendar className="w-5 h-5 mr-2 text-gray-500" />
                    {showDatePicker 
                        ? (deadlineDate ? `Date butoir: ${formatDate(deadlineDate)}` : "Définir une date butoir") 
                        : (deadlineDate ? `Date butoir: ${formatDate(deadlineDate)}` : "Définir une date butoir")}
                </button>
                
                {showDatePicker && (
                    <div className="mt-2">
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Date butoir pour le traitement
                        </label>
                        <div className="flex items-center gap-2">
                            <input
                                type="date"
                                value={deadlineDate}
                                onChange={(e) => setDeadlineDate(e.target.value)}
                                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                            />
                            {deadlineDate && (
                                <button
                                    type="button"
                                    onClick={() => setDeadlineDate('')}
                                    className="inline-flex items-center px-2 py-1 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                                >
                                    Effacer
                                </button>
                            )}
                        </div>
                        <p className="mt-1 text-sm text-gray-500">
                            Cette date sera appliquée comme date limite de retour pour toutes les enquêtes du fichier
                        </p>
                    </div>
                )}
            </div>

            {/* Message de confirmation pour remplacer un fichier existant */}
            {confirmReplace && existingFileInfo && (
                <div className="mb-4 p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg">
                    <h3 className="font-medium mb-2">Le fichier existe déjà</h3>
                    <ul className="mb-4 text-sm space-y-1">
                        <li><span className="font-medium">Nom:</span> {existingFileInfo.nom}</li>
                        <li><span className="font-medium">Importé le:</span> {existingFileInfo.date_upload}</li>
                        <li><span className="font-medium">Nombre de données:</span> {existingFileInfo.nombre_donnees}</li>
                    </ul>
                    <div className="flex gap-3">
                        <button
                            onClick={handleReplaceFile}
                            className="px-3 py-1.5 bg-amber-500 text-white rounded hover:bg-amber-600 text-sm"
                            disabled={uploading}
                        >
                            Remplacer
                        </button>
                        <button
                            onClick={handleCancelReplace}
                            className="px-3 py-1.5 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 text-sm"
                            disabled={uploading}
                        >
                            Annuler
                        </button>
                    </div>
                </div>
            )}

            {/* Bouton d'envoi */}
            {!confirmReplace && (
                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className={`w-full flex items-center justify-center gap-2 px-4 py-2 text-white rounded-md 
                        ${!file || uploading
                            ? 'bg-blue-300 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'}`}
                >
                    {uploading ? (
                        <>
                            <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Importation en cours...
                        </>
                    ) : (
                        <>
                            <FileUp className="w-5 h-5" />
                            Importer le fichier
                        </>
                    )}
                </button>
            )}

            {/* Informations sur le format de fichier */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg text-sm text-blue-800">
                <h3 className="font-medium mb-2">À propos du format de fichier</h3>
                <p>
                    Selon le cahier des charges EOS, les fichiers doivent être au format texte à longueur fixe.
                    Assurez-vous que votre fichier respecte ce format avant de l'importer.
                </p>
                <ul className="mt-2 list-disc pl-5 space-y-1">
                    <li>Format Windows (pas Unix)</li>
                    <li>Extension .txt</li>
                    <li>Champs à longueur fixe selon la structure définie</li>
                    <li>Encodage UTF-8</li>
                </ul>
            </div>
        </div>
    );
};

export default ImportHandler;