import React, { useState, useEffect } from 'react';
import { FileUp, Trash2 } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const FileViewer = () => {
    const [files, setFiles] = useState([]);
    const [selectedFileData, setSelectedFileData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [importing, setImporting] = useState(false);

    const fetchFiles = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/api/stats`);
            const data = await response.json();
            setFiles(data.derniers_fichiers || []);
            setError(null);
        } catch (err) {
            console.error('Error fetching files:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setImporting(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/parse`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Erreur lors de l\'import du fichier');
            }

            await fetchFiles(); // Rafraîchir la liste des fichiers
            setError(null);
        } catch (err) {
            console.error('Import error:', err);
            setError('Erreur lors de l\'import: ' + err.message);
        } finally {
            setImporting(false);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    return (
        <div className="space-y-6">
            {/* Section Import */}
            <div className="bg-white shadow rounded-lg p-6">
                <div className="mb-6">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                        <FileUp className="w-6 h-6" />
                        Import de fichier
                    </h2>
                    <input
                        type="file"
                        onChange={handleFileUpload}
                        accept=".txt"
                        className="block w-full text-sm text-gray-500
                            file:mr-4 file:py-2 file:px-4
                            file:rounded-md file:border-0
                            file:text-sm file:font-semibold
                            file:bg-blue-50 file:text-blue-700
                            hover:file:bg-blue-100"
                    />
                </div>
                {importing && (
                    <div className="text-center py-2">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                        <div className="mt-2">Import en cours...</div>
                    </div>
                )}
                {error && (
                    <div className="text-red-500 bg-red-50 p-4 rounded mt-4">
                        {error}
                    </div>
                )}
            </div>

            {/* Liste des fichiers */}
            <div className="bg-white shadow rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Fichiers importés ({files.length})</h2>
                    <button
                        onClick={fetchFiles}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Actualiser
                    </button>
                </div>

                {loading ? (
                    <div className="text-center py-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                        <div className="mt-2">Chargement des fichiers...</div>
                    </div>
                ) : files.length > 0 ? (
                    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                        {files.map((file) => (
                            <div
                                key={file.id}
                                className="border rounded-lg p-4 hover:border-blue-500 transition-colors"
                            >
                                <div className="font-medium">{file.nom}</div>
                                <div className="text-sm text-gray-500">
                                    Importé le: {file.date_upload}
                                </div>
                                <div className="text-sm text-gray-500">
                                    {file.nombre_donnees} enregistrements
                                </div>
                                <div className="mt-2 flex space-x-2">
                                    <button
                                        onClick={() => loadFileData(file.id)}
                                        className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                                    >
                                        Voir les données
                                    </button>
                                    <button
                                        onClick={() => handleDeleteFile(file.id)}
                                        className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm flex items-center gap-1"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-4 text-gray-500">
                        Aucun fichier importé
                    </div>
                )}
            </div>

            {/* Données du fichier sélectionné */}
            {selectedFileData && (
                <div className="bg-white shadow rounded-lg p-6">
                    <h2 className="text-xl font-bold mb-4">
                        Données du fichier : {selectedFileData.fichier.nom}
                    </h2>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">N° Dossier</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prénom</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date Naissance</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {selectedFileData.donnees.map((donnee, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{donnee.numeroDossier}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{donnee.nom}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{donnee.prenom}</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm">{donnee.dateNaissance}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FileViewer;