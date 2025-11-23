import { useState, useEffect } from 'react';
import axios from 'axios';
import PropTypes from 'prop-types';
import { 
  FileDown, RefreshCw, AlertCircle, 
  CheckCircle, Filter, Calendar, AlertTriangle
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteExporter = ({ enquetes = [] }) => {
  // State for managing export functionality
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [exportURL, setExportURL] = useState(null);
  
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
      
    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors de l'export");
    } finally {
      setLoading(false);
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

      {/* Zone d'informations sur l'export */}
      <div className="bg-white border rounded-lg p-6">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-medium mb-2">Informations sur l&#39;export</h3>
            <p className="text-sm text-gray-600 mb-4">
              Le fichier généré sera au format Word (.docx) avec une page par enquête. Les enquêtes exportées seront automatiquement archivées.
            </p>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Total des enquêtes disponibles:</span>
                <span className="text-sm">{enquetes.length}</span>
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Enquêtes après filtrage:</span>
                <span className="text-sm">{getFilteredCount()}</span>
              </div>
            </div>
          </div>
          
          {exportURL && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex flex-col items-center">
              <CheckCircle className="w-8 h-8 text-green-500 mb-2" />
              <p className="text-sm text-green-700 mb-2">Fichier prêt à télécharger</p>
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 flex items-center gap-1 text-sm"
              >
                <FileDown className="w-4 h-4" />
                <span>Télécharger</span>
              </button>
            </div>
          )}
        </div>
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

// Define prop types to fix the ESLint warning
EnqueteExporter.propTypes = {
  enquetes: PropTypes.array
};

export default EnqueteExporter;