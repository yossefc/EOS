import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Archive, RefreshCw, AlertCircle, 
  CheckCircle, Download
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteExporter = () => {
  // State for validated enquetes (ready for export)
  const [enquetesValidees, setEnquetesValidees] = useState([]);
  const [loadingEnquetes, setLoadingEnquetes] = useState(true);
  const [creatingExport, setCreatingExport] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Charger les enquêtes validées au montage du composant
  useEffect(() => {
    fetchEnquetesValidees();
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

  // Fonction pour charger les enquêtes validées (prêtes pour export)
  const fetchEnquetesValidees = async () => {
    try {
      setLoadingEnquetes(true);
      const response = await axios.get(`${API_URL}/api/exports/validated`);
      
      if (response.data.success) {
        setEnquetesValidees(response.data.data);
      } else {
        throw new Error(response.data.error || 'Erreur lors du chargement');
      }
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Erreur lors du chargement des enquêtes validées");
    } finally {
      setLoadingEnquetes(false);
    }
  };

  // Créer un nouvel export groupé avec toutes les enquêtes validées
  const handleCreateExport = async () => {
    if (enquetesValidees.length === 0) {
      setError("Aucune enquête validée à exporter");
      return;
    }

    if (!window.confirm(`Vous allez créer un export de ${enquetesValidees.length} enquête(s) validée(s). Ces enquêtes seront archivées. Continuer ?`)) {
      return;
    }

    setCreatingExport(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/exports/create-batch`, {
        utilisateur: 'Administrateur'
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Extraire le nom du fichier depuis les headers si disponible
      const contentDisposition = response.headers['content-disposition'];
      let filename = `XXXExp_${new Date().toISOString().split('T')[0].replace(/-/g, '')}.txt`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Export créé avec succès ! ${enquetesValidees.length} enquête(s) ont été archivées.`);
      
      // Recharger la liste des enquêtes validées (devrait être vide maintenant)
      await fetchEnquetesValidees();

    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors de la création de l'export");
    } finally {
      setCreatingExport(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <Download className="w-6 h-6 text-blue-500" />
            Export des Résultats
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Enquêtes validées prêtes pour l'export - {enquetesValidees.length} enquête(s)
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleCreateExport}
            disabled={creatingExport || enquetesValidees.length === 0}
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
                <span>Créer un nouvel export ({enquetesValidees.length})</span>
              </>
            )}
          </button>
          <button
            onClick={fetchEnquetesValidees}
            disabled={loadingEnquetes}
            className="flex items-center gap-1 px-3 py-1.5 border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loadingEnquetes ? 'animate-spin' : ''}`} />
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

      {/* Tableau des enquêtes validées */}
      <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
        {loadingEnquetes ? (
          <div className="flex justify-center items-center p-12">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mr-3" />
            <span className="text-gray-600">Chargement des enquêtes validées...</span>
          </div>
        ) : enquetesValidees.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-gray-500">
            <CheckCircle className="w-16 h-16 mb-4 text-gray-300" />
            <p className="text-lg font-medium">Aucune enquête validée en attente d'export</p>
            <p className="text-sm mt-2">Les enquêtes validées depuis l'onglet "Données" apparaîtront ici</p>
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
                    Type Demande
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Enquêteur
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code Résultat
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date Validation
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {enquetesValidees.map((enquete) => (
                  <tr key={enquete.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {enquete.numeroDossier}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {enquete.nom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {enquete.prenom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {enquete.typeDemande}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {enquete.enqueteurNom}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        enquete.code_resultat === 'P' ? 'bg-green-100 text-green-800' :
                        enquete.code_resultat === 'N' ? 'bg-red-100 text-red-800' :
                        enquete.code_resultat === 'H' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {enquete.code_resultat}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {enquete.updated_at ? new Date(enquete.updated_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      }) : '-'}
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
              <li>• Les enquêtes validées depuis l'onglet <strong>"Données"</strong> apparaissent dans ce tableau</li>
              <li>• Cliquez sur <strong>"Créer un nouvel export"</strong> pour générer un fichier texte (.txt) au format EOS avec toutes les enquêtes validées</li>
              <li>• Les enquêtes exportées sont automatiquement <strong>archivées</strong> et disparaissent de ce tableau</li>
              <li>• Le fichier généré est au format longueur fixe conforme au cahier des charges EOS FRANCE</li>
              <li>• Les fichiers exportés sont accessibles dans l'onglet <strong>"Archives"</strong> pour re-téléchargement</li>
              <li>• Enquêtes en attente d'export : <strong>{enquetesValidees.length}</strong></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnqueteExporter;
