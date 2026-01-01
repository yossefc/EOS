import { useState, useEffect, useCallback } from 'react';
import { Archive, Download, FileText, Search, ChevronLeft, ChevronRight, RefreshCw, Layers } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const ArchivesViewer = ({ title = 'Archives des Exports' }) => {
  const [exportBatches, setExportBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalBatches, setTotalBatches] = useState(0);
  const [downloadingId, setDownloadingId] = useState(null);
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [loadingClients, setLoadingClients] = useState(false);
  const perPage = 20;

  const fetchClients = useCallback(async () => {
    try {
      setLoadingClients(true);
      const response = await fetch(`${API_BASE_URL}/api/clients`);
      const data = await response.json();
      if (data.success) {
        setClients(data.clients);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération des clients:', err);
    } finally {
      setLoadingClients(false);
    }
  }, []);

  const fetchExportBatches = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `${API_BASE_URL}/api/exports/batches?page=${currentPage}&per_page=${perPage}`;
      if (selectedClientId !== null) {
        url += `&client_id=${selectedClientId}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des exports archivés');
      }

      const data = await response.json();

      if (data.success) {
        setExportBatches(data.data);
        setTotalPages(data.pages);
        setTotalBatches(data.total);
      } else {
        throw new Error(data.error || 'Erreur inconnue');
      }
    } catch (err) {
      console.error('Erreur:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [currentPage, selectedClientId]);

  useEffect(() => {
    fetchClients();
  }, [fetchClients]);

  useEffect(() => {
    fetchExportBatches();
  }, [fetchExportBatches]);

  const handleDownload = async (batchId, filename) => {
    setDownloadingId(batchId);
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/exports/batches/${batchId}/download`
      );

      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Erreur:', err);
      alert(`Erreur lors du téléchargement: ${err.message}`);
    } finally {
      setDownloadingId(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };

  const filteredBatches = exportBatches.filter(batch => {
    const searchLower = searchTerm.toLowerCase();
    return (
      batch.filename?.toLowerCase().includes(searchLower) ||
      batch.utilisateur?.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-3">
            <Archive className="w-8 h-8 text-purple-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
              <p className="text-sm text-gray-600">
                {totalBatches} export{totalBatches > 1 ? 's' : ''} archivé{totalBatches > 1 ? 's' : ''}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex bg-gray-100 p-1 rounded-xl">
              <button
                onClick={() => { setSelectedClientId(null); setCurrentPage(1); }}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${selectedClientId === null
                  ? 'bg-white text-purple-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
                  }`}
              >
                Tous les clients
              </button>
              {clients.map(client => (
                <button
                  key={client.id}
                  onClick={() => { setSelectedClientId(client.id); setCurrentPage(1); }}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${selectedClientId === client.id
                    ? 'bg-white text-purple-600 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                  {client.nom}
                </button>
              ))}
            </div>

            <button
              onClick={fetchExportBatches}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 transition-colors shadow-sm"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Actualiser</span>
            </button>
          </div>
        </div>

        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Rechercher par nom de fichier ou utilisateur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm"
            />
          </div>
        </div>
      </div>

      {loading && exportBatches.length === 0 ? (
        <div className="flex flex-col justify-center items-center p-12 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mb-4"></div>
          <span className="text-gray-600 font-medium">Chargement des archives...</span>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl flex items-center gap-3">
          <Layers className="w-5 h-5" />
          <p><strong>Erreur:</strong> {error}</p>
        </div>
      ) : filteredBatches.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="bg-gray-50 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Archive className="w-10 h-10 text-gray-300" />
          </div>
          <p className="text-gray-600 text-lg font-medium">Aucun export archivé trouvé</p>
          <p className="text-sm text-gray-500 mt-2">
            {selectedClientId
              ? `Aucun export pour ce client n'a encore été réalisé.`
              : 'Les exports créés depuis l\'onglet "Export des résultats" apparaîtront ici.'}
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white shadow-sm rounded-xl overflow-hidden border border-gray-100">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Nom du fichier
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Client
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Nb Enquêtes
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Taille
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Date création
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Utilisateur
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredBatches.map((batch) => (
                    <tr key={batch.id} className="hover:bg-purple-50/30 transition-colors group">
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                            <FileText className="w-4 h-4 text-purple-600" />
                          </div>
                          <span className="font-mono text-xs font-medium text-gray-700">{batch.filename}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${clients.find(c => c.id === batch.client_id)?.code === 'PARTNER'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-green-100 text-green-800'
                          }`}>
                          {clients.find(c => c.id === batch.client_id)?.nom || 'Inconnu'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <span className="font-semibold text-purple-700">
                          {batch.enquete_count}
                        </span>
                        <span className="text-gray-500 ml-1 text-xs uppercase font-medium">dossiers</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatFileSize(batch.file_size)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex flex-col">
                          <span className="font-medium text-gray-700">
                            {batch.created_at ? new Date(batch.created_at).toLocaleDateString('fr-FR', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric'
                            }) : 'N/A'}
                          </span>
                          <span className="text-xs text-gray-400">
                            {batch.created_at ? new Date(batch.created_at).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            }) : ''}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-medium">
                        {batch.utilisateur || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleDownload(batch.id, batch.filename)}
                          disabled={downloadingId === batch.id}
                          className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
                          title="Télécharger"
                        >
                          {downloadingId === batch.id ? (
                            <>
                              <RefreshCw className="w-4 h-4 animate-spin" />
                              <span className="hidden sm:inline">...</span>
                            </>
                          ) : (
                            <>
                              <Download className="w-4 h-4" />
                              <span className="hidden sm:inline">Télécharger</span>
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-sm font-medium text-gray-500">
              Affichage de la page <span className="text-gray-900">{currentPage}</span> sur <span className="text-gray-900">{totalPages}</span>
              <span className="mx-2">•</span>
              <span className="text-gray-900">{totalBatches}</span> résultats au total
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white hover:border-purple-300 hover:text-purple-600 transition-all shadow-sm bg-gray-50"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <div className="flex gap-1">
                {[...Array(Math.min(5, totalPages))].map((_, i) => {
                  let pageNum;
                  if (totalPages <= 5) pageNum = i + 1;
                  else if (currentPage <= 3) pageNum = i + 1;
                  else if (currentPage >= totalPages - 2) pageNum = totalPages - 4 + i;
                  else pageNum = currentPage - 2 + i;

                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`w-9 h-9 rounded-lg text-sm font-bold transition-all ${currentPage === pageNum
                        ? 'bg-purple-600 text-white shadow-md'
                        : 'bg-white border border-gray-200 text-gray-600 hover:border-purple-300 hover:text-purple-600'
                        }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}
              </div>
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-200 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white hover:border-purple-300 hover:text-purple-600 transition-all shadow-sm bg-gray-50"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ArchivesViewer;
