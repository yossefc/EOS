import React, { useState, useEffect } from 'react';
import { FileUp, Trash2, RefreshCw } from 'lucide-react';

const API_URL = 'http://localhost:5000';

const FileViewer = () => {
    const [files, setFiles] = useState([]);
    const [selectedFileData, setSelectedFileData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [importing, setImporting] = useState(false);
    const [error, setError] = useState(null);

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
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/parse`, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.status === 409) {  // Fichier existe déjà
                const confirmReplace = window.confirm(
                    `Le fichier ${data.existing_file_info.nom} existe déjà.\n` +
                    `Importé le: ${data.existing_file_info.date_upload}\n` +
                    `Nombre de données: ${data.existing_file_info.nombre_donnees}\n\n` +
                    `Voulez-vous le remplacer ?`
                );

                if (confirmReplace) {
                    // Remplacer le fichier
                    const replaceResponse = await fetch(`${API_URL}/replace-file`, {
                        method: 'POST',
                        body: formData
                    });

                    if (!replaceResponse.ok) {
                        throw new Error('Erreur lors du remplacement du fichier');
                    }

                    alert('Fichier remplacé avec succès');
                } else {
                    event.target.value = '';
                    return;
                }
            } else if (!response.ok) {
                throw new Error(data.error || 'Erreur lors de l\'import');
            }

            // Rafraîchir la liste des fichiers
            await fetchFiles();
            alert('Fichier importé avec succès');

        } catch (err) {
            setError(err.message);
            console.error('Erreur:', err);
        } finally {
            setImporting(false);
            event.target.value = ''; // Reset input
        }
    };

    const handleDeleteFile = async (fileId) => {
        if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce fichier ?')) {
            return;
        }

        try {
            const response = await fetch(`${API_URL}/api/files/${fileId}`, {
                method: 'DELETE',
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors de la suppression');
            }

            setFiles(prevFiles => prevFiles.filter(f => f.id !== fileId));

            if (selectedFileData?.fichier.id === fileId) {
                setSelectedFileData(null);
            }

            await fetchFiles();
            alert('Fichier supprimé avec succès');
        } catch (err) {
            setError(err.message);
        }
    };

    useEffect(() => {
        fetchFiles();
    }, []);

    if (loading) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
        );
    }

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
                        disabled={importing}
                    />
                </div>

                {importing && (
                    <div className="flex items-center gap-2 text-blue-600">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                        Import en cours...
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-600 rounded-md">
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
                        className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        <RefreshCw className="w-4 h-4" />
                        Actualiser
                    </button>
                </div>

                {files.length > 0 ? (
                    <div className="grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
                        {files.map((file) => (
                            <div
                                key={file.id}
                                className="border rounded-lg p-4 hover:border-blue-500 transition-colors"
                            >
                                <div className="font-medium truncate">{file.nom}</div>
                                <div className="text-sm text-gray-500">
                                    Importé le: {file.date_upload}
                                </div>
                                <div className="text-sm text-gray-500">
                                    {file.nombre_donnees} enregistrements
                                </div>
                                <div className="mt-4 flex justify-end gap-2">
                                    <button
                                        onClick={() => handleDeleteFile(file.id)}
                                        className="flex items-center gap-1 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-8 text-gray-500">
                        Aucun fichier importé
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileViewer;