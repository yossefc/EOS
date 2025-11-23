import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  FileDown, RefreshCw, AlertCircle, 
  CheckCircle, Filter, Calendar, AlertTriangle, Download
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteExporter = () => { // Removed enquetes prop
  // State for managing enquetes list
  const [enquetes, setEnquetes] = useState([]);
  const [loading, setLoading] = useState(true); // Initial loading state
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [exportURL, setExportURL] = useState(null);
  const [exportingIndividual, setExportingIndividual] = useState(null);
  
  // State for filtering
  const [dateRange, setDateRange] = useState({
    start: '',
    end: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState({
    ENQ: true,
    CON: true
  });
  const [selectedResults, setSelectedResults] = useState({
    P: true,  // Positive
    N: true,  // Negative
    H: true,  // Confirmed
    Z: true,  // Canceled (agency)
    I: true,  // Untreatable
    Y: true   // Canceled (EOS)
  });

  // Fetch validated enquetes
  const fetchValidatedEnquetes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/api/enquetes/validees`);
      if (response.data.success) {
        setEnquetes(response.data.data);
      } else {
        setError(response.data.error || "Erreur lors du chargement des enquêtes validées.");
      }
    } catch (err) {
      console.error("Erreur lors du chargement des enquêtes validées:", err);
      setError(err.response?.data?.error || err.message || "Une erreur s'est produite.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchValidatedEnquetes();
  }, [fetchValidatedEnquetes]);

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

  // Generate export file (Word format)
  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      
      // Préparer les enquêtes à exporter
      const enquetesToExport = enquetes.map(enquete => ({ id: enquete.id }));
      
      if (enquetesToExport.length === 0) {
        setError("Aucune enquête à exporter");
        setLoading(false);
        return;
      }
      
      // Faire la requête d'export
      const response = await axios.post(`${API_URL}/api/export-enquetes`, {
        enquetes: enquetesToExport
      }, {
        responseType: 'blob' // Important pour recevoir un fichier binaire
      });
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Export_Enquetes_${new Date().toISOString().split('T')[0]}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      setSuccess(`${enquetesToExport.length} enquête(s) exportée(s) avec succès en format Word`);
      fetchValidatedEnquetes(); // Reload list to remove exported items
      
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors de l'export");
    } finally {
      setLoading(false);
    }
  };

  // Export individual enquete
  const handleExportIndividual = async (enqueteId) => {
    setExportingIndividual(enqueteId);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post(`${API_URL}/api/export/enquete/${enqueteId}`, {}, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Export_Enquete_${enqueteId}_${new Date().toISOString().split('T')[0]}.txt`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Enquête ${enqueteId} exportée et archivée avec succès !`);
      fetchValidatedEnquetes(); // Reload list to remove exported item

    } catch (err) {
      console.error(`Erreur lors de l'export de l'enquête ${enqueteId}:`, err);
      setError(err.response?.data?.error || err.message || "Une erreur s'est produite lors de l'export.");
    } finally {
      setExportingIndividual(null);
    }
  };

  // Download the generated file
  const handleDownload = () => {
    if (exportURL) {
      window.open(exportURL, '_blank');
    }
  };

  // Get filtered count based on current filters
  const getFilteredCount = () => {
    // In a real implementation, this would filter the enquetes array based on the selected filters
    // For simplicity, we'll just return the total count of enquetes
    return enquetes.length;
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <FileDown className="w-6 h-6 text-blue-500" />
          Export des Résultats (Word)
        </h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1 px-3 py-1.5 border rounded hover:bg-gray-50"
          >
            <Filter className="w-4 h-4" />
            <span>Filtres</span>
          </button>
          <button
            onClick={handleExport}
            disabled={loading}
            className="flex items-center gap-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Génération...</span>
              </>
            ) : (
              <>
                <FileDown className="w-4 h-4" />
                <span>Exporter en Word & archiver</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Messages de succès et d'erreur */}
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

      {/* Filtres */}
      {showFilters && (
        <div className="bg-gray-50 border rounded-lg p-4 space-y-4">
          <h3 className="font-medium">Filtres d&#39;export</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
                <Calendar className="w-4 h-4 text-gray-500" />
                Période
              </h4>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Date de début</label>
                  <input
                    type="date"
                    value={dateRange.start}
                    onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                    className="w-full border rounded p-2"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Date de fin</label>
                  <input
                    type="date"
                    value={dateRange.end}
                    onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                    className="w-full border rounded p-2"
                  />
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-sm font-medium mb-2">Type de demande</h4>
              <div className="flex gap-3">
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={selectedTypes.ENQ}
                    onChange={() => setSelectedTypes({ ...selectedTypes, ENQ: !selectedTypes.ENQ })}
                    className="rounded text-blue-500"
                  />
                  <span className="text-sm">Enquêtes</span>
                </label>
                <label className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={selectedTypes.CON}
                    onChange={() => setSelectedTypes({ ...selectedTypes, CON: !selectedTypes.CON })}
                    className="rounded text-blue-500"
                  />
                  <span className="text-sm">Contestations</span>
                </label>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium mb-2">Codes résultat</h4>
            <div className="flex flex-wrap gap-3">
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.P}
                  onChange={() => setSelectedResults({ ...selectedResults, P: !selectedResults.P })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Positif (P)</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.N}
                  onChange={() => setSelectedResults({ ...selectedResults, N: !selectedResults.N })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Négatif (N)</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.H}
                  onChange={() => setSelectedResults({ ...selectedResults, H: !selectedResults.H })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Confirmé (H)</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.Z}
                  onChange={() => setSelectedResults({ ...selectedResults, Z: !selectedResults.Z })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Annulé agence (Z)</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.I}
                  onChange={() => setSelectedResults({ ...selectedResults, I: !selectedResults.I })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Intraitable (I)</span>
              </label>
              <label className="flex items-center gap-1">
                <input
                  type="checkbox"
                  checked={selectedResults.Y}
                  onChange={() => setSelectedResults({ ...selectedResults, Y: !selectedResults.Y })}
                  className="rounded text-blue-500"
                />
                <span className="text-sm">Annulé EOS (Y)</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Tableau des enquêtes validées */}
      <div className="bg-white border rounded-lg overflow-hidden">
        <div className="p-4 border-b bg-gray-50">
          <h3 className="font-medium">Enquêtes validées prêtes pour l&#39;export</h3>
          <p className="text-sm text-gray-600 mt-1">
            {enquetes.length} enquête(s) confirmée(s) non archivée(s)
          </p>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
            <p className="text-gray-600">Chargement des enquêtes...</p>
          </div>
        ) : enquetes.length === 0 ? (
          <div className="p-8 text-center">
            <AlertCircle className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-600">Aucune enquête validée disponible pour l&#39;export</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">N° Dossier</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Nom</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Prénom</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Enquêteur</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Résultat</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-700 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {enquetes.map((enquete) => (
                  <tr key={enquete.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm">{enquete.numeroDossier}</td>
                    <td className="px-4 py-3 text-sm">{enquete.nom}</td>
                    <td className="px-4 py-3 text-sm">{enquete.prenom}</td>
                    <td className="px-4 py-3 text-sm">{enquete.typeDemande}</td>
                    <td className="px-4 py-3 text-sm">{enquete.enqueteurNom}</td>
                    <td className="px-4 py-3 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        enquete.code_resultat === 'P' ? 'bg-green-100 text-green-800' :
                        enquete.code_resultat === 'N' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {enquete.code_resultat}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {enquete.updated_at ? new Date(enquete.updated_at).toLocaleDateString('fr-FR') : '-'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => handleExportIndividual(enquete.id)}
                        disabled={exportingIndividual === enquete.id}
                        className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center gap-1 text-sm mx-auto"
                      >
                        {exportingIndividual === enquete.id ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            <span>Export...</span>
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            <span>Exporter</span>
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

      {/* Instructions d'export */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-800 mb-1">Informations importantes</h3>
            <p className="text-sm text-blue-700">
              Chaque enquête sera exportée sur une page séparée du document Word. Le document inclura un tableau détaillé des informations, les notes et commentaires. Les enquêtes seront automatiquement archivées après l&#39;export.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnqueteExporter;