import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Archive, RefreshCw, AlertCircle, 
  CheckCircle, Download, FileText, FileSpreadsheet
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnqueteExporter = () => {
  // State for validated enquetes (ready for export) - EOS
  const [enquetesValidees, setEnquetesValidees] = useState([]);
  const [loadingEnquetes, setLoadingEnquetes] = useState(true);
  const [creatingExport, setCreatingExport] = useState(false);
  
  // State for PARTNER exports
  const [partnerStats, setPartnerStats] = useState({
    enquetes_positives: 0,
    enquetes_negatives: 0,
    contestations_positives: 0,
    contestations_negatives: 0,
    total: 0
  });
  const [partnerEnquetes, setPartnerEnquetes] = useState([]);
  const [loadingPartnerStats, setLoadingPartnerStats] = useState(true);
  const [loadingPartnerEnquetes, setLoadingPartnerEnquetes] = useState(true);
  const [exportingPartner, setExportingPartner] = useState({});
  
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Charger les données au montage du composant
  useEffect(() => {
    fetchEnquetesValidees();
    fetchPartnerStats();
    fetchPartnerEnquetes();
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

  // Fonction pour charger les enquêtes validées EOS (prêtes pour export)
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

  // Fonction pour charger les statistiques PARTNER
  const fetchPartnerStats = async () => {
    try {
      setLoadingPartnerStats(true);
      const response = await axios.get(`${API_URL}/api/partner/exports/stats`);
      
      if (response.data.success) {
        setPartnerStats(response.data.data);
      }
    } catch (error) {
      console.error("Erreur stats PARTNER:", error);
      // Ne pas afficher d'erreur si PARTNER n'est pas configuré
    } finally {
      setLoadingPartnerStats(false);
    }
  };

  // Fonction pour charger la liste des enquêtes PARTNER validées
  const fetchPartnerEnquetes = async () => {
    try {
      setLoadingPartnerEnquetes(true);
      const response = await axios.get(`${API_URL}/api/partner/exports/validated`);
      
      if (response.data.success) {
        setPartnerEnquetes(response.data.data);
      }
    } catch (error) {
      console.error("Erreur enquêtes PARTNER:", error);
    } finally {
      setLoadingPartnerEnquetes(false);
    }
  };

  // Créer un nouvel export groupé EOS avec toutes les enquêtes validées
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

      setSuccess(`Export EOS créé avec succès ! ${enquetesValidees.length} enquête(s) ont été archivées.`);
      
      // Recharger la liste des enquêtes validées (devrait être vide maintenant)
      await fetchEnquetesValidees();

    } catch (error) {
      console.error("Erreur:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite lors de la création de l'export");
    } finally {
      setCreatingExport(false);
    }
  };

  // Gérer les exports PARTNER - Un seul fichier
  const handlePartnerExportSingle = async (exportType, endpoint, label) => {
    setExportingPartner(prev => ({ ...prev, [exportType]: true }));
    setError(null);
    setSuccess(null);

    try {
      const response = await axios.post(`${API_URL}${endpoint}`, {}, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Déterminer l'extension du fichier
      const contentType = response.headers['content-type'];
      let extension = '.xls';
      if (contentType && contentType.includes('wordprocessingml')) {
        extension = '.docx';
      } else if (contentType && contentType.includes('zip')) {
        extension = '.zip';
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T');
      const filename = `export_partner_${exportType}_${timestamp[0]}_${timestamp[1].split('-')[0]}${extension}`;
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Export PARTNER "${label}" créé avec succès !`);
      
      // Rafraîchir les statistiques et la liste
      setTimeout(() => {
        fetchPartnerStats();
        fetchPartnerEnquetes();
      }, 1000);

    } catch (error) {
      console.error("Erreur export PARTNER:", error);
      setError(error.response?.data?.error || `Erreur lors de l'export ${label}`);
    } finally {
      setExportingPartner(prev => ({ ...prev, [exportType]: false }));
    }
  };

  // Gérer les exports PARTNER - Word ET Excel (endpoint combiné)
  const handlePartnerExportBoth = async (exportType, endpointBoth, label) => {
    setExportingPartner(prev => ({ ...prev, [exportType]: true }));
    setError(null);
    setSuccess(null);

    try {
      // Appel à l'endpoint combiné qui retourne un ZIP avec Word + Excel
      const response = await axios.post(`${API_URL}${endpointBoth}`, {}, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T');
      const filename = `export_partner_${exportType}_${timestamp[0]}_${timestamp[1].split('-')[0]}.zip`;
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Export PARTNER "${label}" créé avec succès ! (Word + Excel dans un ZIP)`);
      
      // Rafraîchir les statistiques et la liste
      setTimeout(() => {
        fetchPartnerStats();
        fetchPartnerEnquetes();
      }, 1000);

    } catch (error) {
      console.error("Erreur export PARTNER:", error);
      setError(error.response?.data?.error || `Erreur lors de l'export ${label}`);
    } finally {
      setExportingPartner(prev => ({ ...prev, [exportType]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Download className="w-7 h-7 text-blue-500" />
            Export des Résultats
          </h2>
          <p className="text-sm text-gray-600 mt-1">
            Exports EOS et PARTNER - Enquêtes validées prêtes pour l'export
          </p>
        </div>
        <button
          onClick={() => {
            fetchEnquetesValidees();
            fetchPartnerStats();
            fetchPartnerEnquetes();
          }}
          disabled={loadingEnquetes || loadingPartnerStats || loadingPartnerEnquetes}
          className="flex items-center gap-1 px-3 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${(loadingEnquetes || loadingPartnerStats || loadingPartnerEnquetes) ? 'animate-spin' : ''}`} />
          <span>Actualiser</span>
        </button>
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

      {/* ========== SECTION EXPORT EOS ========== */}
      <div className="border-2 border-blue-300 rounded-lg bg-blue-50 p-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-500 text-white p-3 rounded-lg">
              <Download className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-blue-900">Export EOS</h3>
              <p className="text-sm text-blue-700">Format texte (.txt) - Longueur fixe</p>
            </div>
            {enquetesValidees.length > 0 && (
              <span className="ml-4 px-3 py-1 bg-red-500 text-white text-sm font-bold rounded-full animate-pulse">
                {enquetesValidees.length} enquête{enquetesValidees.length > 1 ? 's' : ''}
              </span>
            )}
          </div>
          <button
            onClick={handleCreateExport}
            disabled={creatingExport || enquetesValidees.length === 0}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md font-semibold"
          >
            {creatingExport ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Export en cours...</span>
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                <span>Exporter EOS ({enquetesValidees.length})</span>
              </>
            )}
          </button>
        </div>

        {/* Tableau des enquêtes EOS validées */}
        <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
          {loadingEnquetes ? (
            <div className="flex justify-center items-center p-8">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-500 mr-3" />
              <span className="text-gray-600">Chargement...</span>
            </div>
          ) : enquetesValidees.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-gray-500">
              <CheckCircle className="w-12 h-12 mb-3 text-gray-300" />
              <p className="font-medium">Aucune enquête EOS en attente</p>
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
      </div>

      {/* ========== SECTION EXPORT PARTNER ========== */}
      <div className="border-2 border-purple-300 rounded-lg bg-purple-50 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="bg-purple-500 text-white p-3 rounded-lg">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-purple-900">Export PARTNER</h3>
            <p className="text-sm text-purple-700">Formats Word (.docx) et Excel (.xls)</p>
          </div>
          {partnerStats.total > 0 && (
            <span className="ml-4 px-3 py-1 bg-red-500 text-white text-sm font-bold rounded-full animate-pulse">
              {partnerStats.total} dossier{partnerStats.total > 1 ? 's' : ''}
            </span>
          )}
        </div>

        {loadingPartnerStats || loadingPartnerEnquetes ? (
          <div className="bg-white rounded-lg p-8 flex justify-center items-center">
            <RefreshCw className="w-6 h-6 animate-spin text-purple-500 mr-3" />
            <span>Chargement des données PARTNER...</span>
          </div>
        ) : (
          <>
            {/* Tableau des enquêtes PARTNER validées */}
            {partnerEnquetes.length > 0 && (
              <div className="bg-white border rounded-lg overflow-hidden shadow-sm mb-4">
                <div className="bg-purple-100 px-4 py-2 border-b">
                  <h4 className="font-semibold text-purple-900">Enquêtes PARTNER prêtes à exporter ({partnerEnquetes.length})</h4>
                </div>
                <div className="overflow-x-auto max-h-64">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">N° Dossier</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Résultat</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {partnerEnquetes.map((enquete) => (
                        <tr key={enquete.id} className="hover:bg-gray-50">
                          <td className="px-4 py-2 whitespace-nowrap font-medium text-gray-900">
                            {enquete.numeroDossier || '-'}
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-gray-700">
                            {enquete.nom}
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              enquete.est_contestation ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                            }`}>
                              {enquete.type_export}
                            </span>
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              enquete.resultat === 'Positive' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {enquete.resultat}
                            </span>
                          </td>
                          <td className="px-4 py-2 whitespace-nowrap text-center">
                            <span className="font-mono text-xs font-bold">{enquete.code_resultat}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Boutons d'export en grille */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {/* Enquêtes Positives */}
            <div className="bg-white border-2 border-green-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-base font-bold text-green-800">📋 Enquêtes Positives</h4>
                {partnerStats.enquetes_positives > 0 && (
                  <span className="px-2 py-0.5 bg-green-500 text-white text-xs font-bold rounded-full">
                    {partnerStats.enquetes_positives}
                  </span>
                )}
              </div>
              <button
                onClick={() => handlePartnerExportBoth('enquetes_pos', '/api/partner/exports/enquetes/positives/both', 'Enquêtes Positives')}
                disabled={partnerStats.enquetes_positives === 0 || exportingPartner.enquetes_pos}
                className="w-full flex items-center justify-center gap-2 px-3 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
              >
                {exportingPartner.enquetes_pos ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Export en cours...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Exporter Word + Excel</span>
                  </>
                )}
              </button>
            </div>

            {/* Enquêtes Négatives */}
            <div className="bg-white border-2 border-red-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-base font-bold text-red-800">📋 Enquêtes Négatives</h4>
                {partnerStats.enquetes_negatives > 0 && (
                  <span className="px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full">
                    {partnerStats.enquetes_negatives}
                  </span>
                )}
              </div>
              <button
                onClick={() => handlePartnerExportBoth('enquetes_neg', '/api/partner/exports/enquetes/negatives/both', 'Enquêtes Négatives')}
                disabled={partnerStats.enquetes_negatives === 0 || exportingPartner.enquetes_neg}
                className="w-full flex items-center justify-center gap-2 px-3 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
              >
                {exportingPartner.enquetes_neg ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Export en cours...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Exporter Word + Excel</span>
                  </>
                )}
              </button>
            </div>

            {/* Contestations Positives */}
            <div className="bg-white border-2 border-blue-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-base font-bold text-blue-800">📋 Contestations Positives</h4>
                {partnerStats.contestations_positives > 0 && (
                  <span className="px-2 py-0.5 bg-blue-500 text-white text-xs font-bold rounded-full">
                    {partnerStats.contestations_positives}
                  </span>
                )}
              </div>
              <button
                onClick={() => handlePartnerExportBoth('contest_pos', '/api/partner/exports/contestations/positives/both', 'Contestations Positives')}
                disabled={partnerStats.contestations_positives === 0 || exportingPartner.contest_pos}
                className="w-full flex items-center justify-center gap-2 px-3 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
              >
                {exportingPartner.contest_pos ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Export en cours...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Exporter Word + Excel</span>
                  </>
                )}
              </button>
            </div>

            {/* Contestations Négatives */}
            <div className="bg-white border-2 border-orange-200 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-3">
                <h4 className="text-base font-bold text-orange-800">📋 Contestations Négatives</h4>
                {partnerStats.contestations_negatives > 0 && (
                  <span className="px-2 py-0.5 bg-orange-500 text-white text-xs font-bold rounded-full">
                    {partnerStats.contestations_negatives}
                  </span>
                )}
              </div>
              <button
                onClick={() => handlePartnerExportBoth('contest_neg', '/api/partner/exports/contestations/negatives/both', 'Contestations Négatives')}
                disabled={partnerStats.contestations_negatives === 0 || exportingPartner.contest_neg}
                className="w-full flex items-center justify-center gap-2 px-3 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold"
              >
                {exportingPartner.contest_neg ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Export en cours...</span>
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    <span>Exporter Word + Excel</span>
                  </>
                )}
              </button>
            </div>
          </div>
          </>
        )}
      </div>

      {/* Informations */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-start gap-2">
          <AlertCircle className="w-5 h-5 text-gray-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-gray-800 mb-1">ℹ️ Informations</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• <strong>EOS</strong> : Fichier texte (.txt) format longueur fixe - Toutes les enquêtes validées</li>
              <li>• <strong>PARTNER</strong> : Fichiers Word (.docx) pour rapports et Excel (.xls) pour tableaux</li>
              <li>• Les dossiers exportés sont automatiquement <strong>archivés</strong></li>
              <li>• Consultez l'onglet <strong>"Archives"</strong> pour retrouver vos exports</li>
              <li>• Les badges rouges <span className="inline-block px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full">avec animation</span> indiquent les dossiers en attente</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnqueteExporter;
