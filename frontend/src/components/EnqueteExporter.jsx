import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Archive, RefreshCw, AlertCircle, 
  CheckCircle, Download
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteExporter = () => {
  // State for archives
  const [archives, setArchives] = useState([]);
  const [loadingArchives, setLoadingArchives] = useState(true);
  const [downloadingArchiveId, setDownloadingArchiveId] = useState(null);
  const [creatingExport, setCreatingExport] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Charger les archives au montage du composant
  useEffect(() => {
    fetchArchives();
  }, []);

  // Clear messages after a timeout
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // Fonction pour charger les archives
  const fetchArchives = async () => {
    try {
      setLoadingArchives(true);
      const response = await axios.get(`${API_URL}/api/archives`);
      
      if (response.data.success) {
        setArchives(response.data.data);
      } else {
        throw new Error(response.data.error || 'Erreur lors du chargement');
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Erreur lors du chargement des archives");
    } finally {
      setLoadingArchives(false);
    }
  };

  // Créer un nouvel export avec toutes les enquêtes non archivées
  const handleCreateExport = async () => {
    setCreatingExport(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/export-enquetes`, {
        utilisateur: 'Administrateur'
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `Export_Enquetes_${new Date().toISOString().split('T')[0]}.docx`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess("Toutes les enquêtes validées ont été exportées et archivées avec succès !");
      
      // Recharger la liste des archives
      await fetchArchives();

    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors de la création de l'export");
    } finally {
      setCreatingExport(false);
    }
  };

  // Télécharger un fichier archivé
  const handleDownloadArchive = async (archiveId, filename) => {
    setDownloadingArchiveId(archiveId);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await axios.get(`${API_URL}/api/archives/${archiveId}`, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Fichier "${filename}" téléchargé avec succès !`);

    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors du téléchargement");
    } finally {
      setDownloadingArchiveId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Archive className="w-6 h-6 text-purple-500" />
            Archives des Exports
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Créez un nouvel export ou téléchargez les fichiers déjà exportés
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCreateExport}
            disabled={creatingExport}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {creatingExport ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Création en cours...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Créer un nouvel export</span>
              </>
            )}
          </button>
          <button
            onClick={fetchArchives}
            disabled={loadingArchives}
            className="flex items-center gap-1 px-3 py-1.5 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loadingArchives ? 'animate-spin' : ''}`} />
            <span>Actualiser</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-center gap-2">
          <CheckCircle className="w-5 h-5 flex-shrink-0" />
          <p>{success}</p>
        </div>
      )}

      {/* Tableau des archives */}
      <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
        {loadingArchives ? (
          <div className="flex justify-center items-center p-12">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-500 mr-3" />
            <span className="text-gray-600">Chargement des archives...</span>
          </div>
        ) : archives.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-gray-500">
            <Archive className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-lg font-medium">Aucune archive disponible</p>
            <p className="text-sm mt-2">Les fichiers exportés apparaîtront ici</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    N° Dossier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nom
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Prénom
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Nom du fichier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date d'export
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Utilisateur
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {archives.map((archive) => (
                  <tr key={archive.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {archive.numeroDossier}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {archive.nom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {archive.prenom}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      <span className="font-mono text-xs bg-gray-100 px-2 py-1 rounded">
                        {archive.nom_fichier}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {archive.date_export ? new Date(archive.date_export).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      }) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {archive.utilisateur || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleDownloadArchive(archive.id, archive.nom_fichier)}
                        disabled={downloadingArchiveId === archive.id}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                        title="Télécharger le fichier"
                      >
                        {downloadingArchiveId === archive.id ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span>Téléchargement...</span>
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            <span>Télécharger</span>
                          </>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Informations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-800 mb-1">Comment ça marche ?</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Cliquez sur <strong>"Créer un nouvel export"</strong> pour générer un fichier Word avec toutes les enquêtes validées non archivées</li>
              <li>• Les enquêtes exportées sont automatiquement archivées et apparaissent dans le tableau ci-dessus</li>
              <li>• Chaque enquête est présentée sur une page séparée avec un design professionnel</li>
              <li>• Vous pouvez re-télécharger n'importe quel fichier archivé à tout moment</li>
              <li>• Total des archives : <strong>{archives.length}</strong></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnqueteExporter;
