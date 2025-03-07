import React, { useState } from 'react';
import axios from 'axios';
import { Download, AlertCircle, Check, FileDown } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const ExportHandler = ({ enquetes = [], onExportComplete }) => {
    const [exporting, setExporting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [exportType, setExportType] = useState('all'); // 'all', 'completed', 'pending'

    const resetStatus = () => {
        setError(null);
        setSuccess(null);
    };

    const handleExport = async () => {
        if (enquetes.length === 0) {
            setError("Aucune enquête à exporter");
            return;
        }

        setExporting(true);
        resetStatus();

        try {
            // Préparer les données à exporter selon le filtre choisi
            let dataToExport = [];

            switch (exportType) {
                case 'completed':
                    dataToExport = enquetes.filter(e => e.code_resultat && (e.code_resultat === 'P' || e.code_resultat === 'H' || e.code_resultat === 'D'));
                    break;
                case 'pending':
                    dataToExport = enquetes.filter(e => !e.code_resultat || e.code_resultat === '');
                    break;
                default:
                    dataToExport = [...enquetes];
            }

            if (dataToExport.length === 0) {
                setError(`Aucune enquête correspondant au filtre "${exportType}" à exporter`);
                setExporting(false);
                return;
            }

            // Appel à l'API pour générer le fichier
            const response = await axios.post(
                `${API_URL}/api/export-enquetes`,
                { enquetes: dataToExport },
                {
                    responseType: 'blob',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            // Créer un lien de téléchargement pour le fichier généré
            const blob = new Blob([response.data], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');

            // Nom du fichier au format XXXExp_AAAAMMJJ.txt selon le cahier des charges
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');

            // XXX = code du prestataire (utilisation de EOS par défaut)
            const fileName = `EOSExp_${year}${month}${day}.txt`;

            a.href = url;
            a.download = fileName;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            setSuccess(`Fichier "${fileName}" généré avec succès (${dataToExport.length} enquêtes)`);

            // Notifier le composant parent
            if (onExportComplete) {
                onExportComplete();
            }
        } catch (err) {
            console.error('Erreur lors de l\'export:', err);
            setError(err.response?.data?.error || 'Erreur lors de l\'export des données');
        } finally {
            setExporting(false);
        }
    };

    const getExportTypeLabel = (type) => {
        switch (type) {
            case 'completed': return 'Enquêtes terminées';
            case 'pending': return 'Enquêtes en attente';
            default: return 'Toutes les enquêtes';
        }
    };

    const completedCount = enquetes.filter(e => e.code_resultat && (e.code_resultat === 'P' || e.code_resultat === 'H' || e.code_resultat === 'D')).length;
    const pendingCount = enquetes.filter(e => !e.code_resultat || e.code_resultat === '').length;

    return (
        <div className="bg-white shadow-md rounded-lg p-6">
            <div className="flex items-center gap-2 mb-6">
                <FileDown className="w-6 h-6 text-green-500" />
                <h2 className="text-xl font-bold">Export des résultats d'enquête</h2>
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
                    Type d'export
                </label>
                <div className="grid grid-cols-3 gap-3">
                    <div
                        className={`p-3 border rounded-lg cursor-pointer text-center ${exportType === 'all' ? 'bg-blue-50 border-blue-200' : 'hover:bg-gray-50'
                            }`}
                        onClick={() => setExportType('all')}
                    >
                        <div className="font-medium">Toutes</div>
                        <div className="text-sm text-gray-500">{enquetes.length} enquêtes</div>
                    </div>
                    <div
                        className={`p-3 border rounded-lg cursor-pointer text-center ${exportType === 'completed' ? 'bg-green-50 border-green-200' : 'hover:bg-gray-50'
                            }`}
                        onClick={() => setExportType('completed')}
                    >
                        <div className="font-medium">Terminées</div>
                        <div className="text-sm text-gray-500">{completedCount} enquêtes</div>
                    </div>
                    <div
                        className={`p-3 border rounded-lg cursor-pointer text-center ${exportType === 'pending' ? 'bg-amber-50 border-amber-200' : 'hover:bg-gray-50'
                            }`}
                        onClick={() => setExportType('pending')}
                    >
                        <div className="font-medium">En attente</div>
                        <div className="text-sm text-gray-500">{pendingCount} enquêtes</div>
                    </div>
                </div>
            </div>

            {/* Bouton d'export */}
            <button
                onClick={handleExport}
                disabled={exporting || enquetes.length === 0}
                className={`w-full flex items-center justify-center gap-2 px-4 py-2 text-white rounded-md 
                    ${exporting || enquetes.length === 0
                        ? 'bg-green-300 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700'}`}
            >
                {exporting ? (
                    <>
                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Exportation en cours...
                    </>
                ) : (
                    <>
                        <Download className="w-5 h-5" />
                        Exporter {getExportTypeLabel(exportType)}
                    </>
                )}
            </button>

            {/* Informations sur le format de fichier */}
            <div className="mt-6 p-4 bg-green-50 rounded-lg text-sm text-green-800">
                <h3 className="font-medium mb-2">Informations sur l'export</h3>
                <p>
                    Le fichier d'export sera généré selon le format spécifié dans le cahier des charges EOS :
                </p>
                <ul className="mt-2 list-disc pl-5 space-y-1">
                    <li>Format texte à longueur fixe</li>
                    <li>Nom du fichier : EOSExp_AAAAMMJJ.txt</li>
                    <li>Encodage UTF-8</li>
                    <li>Structure conforme aux spécifications du cahier des charges</li>
                </ul>
            </div>
        </div>
    );
};

export default ExportHandler;