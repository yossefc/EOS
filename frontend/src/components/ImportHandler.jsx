import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {
  FileUp, RefreshCw, Check, AlertCircle, File, Trash2,
  X, Database, Calendar, Upload, HardDrive
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

/**
 * ImportHandler - Gestion des imports de fichiers
 * Design clair et professionnel
 */
const ImportHandler = ({ onImportComplete }) => {
  // États
  const [selectedFile, setSelectedFile] = useState(null);
  const [dateButoir, setDateButoir] = useState('');
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [fileExists, setFileExists] = useState(false);
  const [existingFileInfo, setExistingFileInfo] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Multi-client
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [loadingClients, setLoadingClients] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoadingClients(true);
      const response = await axios.get(`${API_URL}/api/clients`);
      if (response.data.success) {
        setClients(response.data.clients);
        const eosClient = response.data.clients.find(c => c.code === 'EOS');
        if (eosClient) {
          setSelectedClientId(eosClient.id);
        } else if (response.data.clients.length > 0) {
          setSelectedClientId(response.data.clients[0].id);
        }
      }
    } catch (error) {
      console.error("Erreur clients:", error);
    } finally {
      setLoadingClients(false);
    }
  };

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Erreur stats:", error);
      setError("Erreur lors de la récupération des statistiques");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setFileExists(false);
      setExistingFileInfo(null);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async (replace = false) => {
    if (!selectedFile) {
      setError("Veuillez sélectionner un fichier");
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append("file", selectedFile);
      if (dateButoir) formData.append("date_butoir", dateButoir);
      if (selectedClientId) formData.append("client_id", selectedClientId);

      const url = replace ? `${API_URL}/replace-file` : `${API_URL}/parse`;
      const response = await axios.post(url, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      if (response.data.status === "file_exists") {
        setFileExists(true);
        setExistingFileInfo(response.data.existing_file_info);
      } else {
        setSuccess(`Import réussi : ${response.data.records_processed} enregistrements traités.`);
        setSelectedFile(null);
        setDateButoir('');
        fetchStats();
        if (onImportComplete) onImportComplete();
      }
    } catch (error) {
      console.error("Erreur upload:", error);
      setError(error.response?.data?.error || "Erreur lors de l'envoi du fichier");
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm("Supprimer ce fichier et toutes ses données ?")) return;

    try {
      setLoading(true);
      const response = await axios.delete(`${API_URL}/api/files/${fileId}`);
      if (response.data.message) {
        setSuccess("Fichier supprimé");
        fetchStats();
      }
    } catch (error) {
      console.error("Erreur suppression:", error);
      setError("Erreur lors de la suppression");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">

      {/* Notifications */}
      <div className="fixed top-4 right-4 z-50 space-y-2 w-80">
        {error && (
          <div className="bg-white border border-red-200 rounded-lg p-4 shadow-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-red-700">Erreur</p>
              <p className="text-xs text-red-600 mt-0.5">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
        {success && (
          <div className="bg-white border border-green-200 rounded-lg p-4 shadow-lg flex items-start gap-3">
            <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-green-700">Succès</p>
              <p className="text-xs text-green-600 mt-0.5">{success}</p>
            </div>
            <button onClick={() => setSuccess(null)} className="text-green-400 hover:text-green-600">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-500" />
            Import de fichiers
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">Importez vos fichiers d'enquêtes</p>
        </div>
        <button
          onClick={fetchStats}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 
                     bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Actualiser
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Formulaire d'import */}
        <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
              <FileUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-800">Nouvel import</h2>
              <p className="text-xs text-slate-500">Sélectionnez un fichier à importer</p>
            </div>
          </div>

          <div className="space-y-5">

            {/* Sélection du client */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">
                Client émetteur
              </label>
              <div className="flex flex-wrap gap-2">
                {loadingClients ? (
                  <div className="flex gap-2">
                    <div className="h-9 w-20 bg-slate-100 rounded-lg animate-pulse" />
                    <div className="h-9 w-20 bg-slate-100 rounded-lg animate-pulse" />
                  </div>
                ) : (
                  clients.map(client => (
                    <button
                      key={client.id}
                      onClick={() => setSelectedClientId(client.id)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all
                        ${selectedClientId === client.id
                          ? 'bg-blue-600 text-white shadow-sm'
                          : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'}`}
                    >
                      {client.nom}
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Zone de drop */}
            <div className="relative">
              <input
                type="file"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              />
              <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all
                ${selectedFile
                  ? 'border-blue-400 bg-blue-50/50'
                  : 'border-slate-200 hover:border-blue-400 hover:bg-slate-50'}`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-3
                  ${selectedFile ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-400'}`}
                >
                  {selectedFile ? <Check className="w-6 h-6" /> : <File className="w-6 h-6" />}
                </div>

                {selectedFile ? (
                  <div>
                    <p className="font-semibold text-slate-800">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Prêt pour l'import
                    </p>
                    <button
                      onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                      className="mt-3 text-xs font-medium text-red-500 hover:text-red-600"
                    >
                      Changer de fichier
                    </button>
                  </div>
                ) : (
                  <div>
                    <p className="font-medium text-slate-700">Glissez un fichier ici</p>
                    <p className="text-xs text-slate-500 mt-1">ou cliquez pour parcourir</p>
                  </div>
                )}
              </div>
            </div>

            {/* Date butoir */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wide mb-2">
                Date butoir <span className="text-slate-400 font-normal normal-case">(optionnel)</span>
              </label>
              <input
                type="date"
                value={dateButoir}
                onChange={(e) => setDateButoir(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white
                           focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Bouton d'action */}
            {!fileExists ? (
              <button
                onClick={() => handleUpload(false)}
                disabled={!selectedFile || uploading}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-200 
                           text-white rounded-lg font-medium transition-colors flex items-center 
                           justify-center gap-2 disabled:cursor-not-allowed"
              >
                {uploading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Traitement en cours...
                  </>
                ) : (
                  <>
                    <FileUp className="w-4 h-4" />
                    Lancer l'importation
                  </>
                )}
              </button>
            ) : (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                  <span className="font-semibold text-amber-800">Fichier existant</span>
                </div>
                <p className="text-sm text-amber-700 mb-4">
                  <strong>{existingFileInfo?.nom}</strong> a été importé le {existingFileInfo?.date_upload}.
                  Voulez-vous le remplacer ?
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleUpload(true)}
                    className="flex-1 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg 
                               font-medium transition-colors"
                  >
                    Remplacer
                  </button>
                  <button
                    onClick={() => { setFileExists(false); setSelectedFile(null); }}
                    className="flex-1 py-2 bg-white border border-amber-300 text-amber-700 
                               rounded-lg font-medium hover:bg-amber-50 transition-colors"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Stats */}
        <div className="space-y-4">

          {/* Stats cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-white rounded-lg border border-slate-200 p-4">
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center mb-3">
                <File className="w-4 h-4 text-blue-600" />
              </div>
              <p className="text-xs font-medium text-slate-500">Fichiers</p>
              <p className="text-2xl font-bold text-slate-800">{stats?.total_fichiers || 0}</p>
            </div>
            <div className="bg-white rounded-lg border border-slate-200 p-4">
              <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center mb-3">
                <Database className="w-4 h-4 text-green-600" />
              </div>
              <p className="text-xs font-medium text-slate-500">Dossiers</p>
              <p className="text-2xl font-bold text-slate-800">{stats?.total_donnees || 0}</p>
            </div>
          </div>

          {/* Historique */}
          <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100 bg-slate-50">
              <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wide flex items-center gap-2">
                <HardDrive className="w-3.5 h-3.5" />
                Historique des imports
              </h3>
            </div>

            <div className="divide-y divide-slate-100 max-h-80 overflow-y-auto">
              {loading ? (
                <div className="p-6 flex flex-col items-center gap-2 text-slate-400">
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span className="text-xs">Chargement...</span>
                </div>
              ) : stats?.derniers_fichiers?.length > 0 ? (
                stats.derniers_fichiers.map((fichier) => (
                  <div key={fichier.id} className="px-4 py-3 flex items-center justify-between hover:bg-slate-50 group">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 bg-slate-50 rounded flex items-center justify-center flex-shrink-0">
                        <File className="w-4 h-4 text-slate-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-800 truncate">{fichier.nom}</p>
                        <p className="text-xs text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {fichier.date_upload} • {fichier.nombre_donnees} entrées
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteFile(fichier.id)}
                      className="p-1.5 rounded text-slate-300 hover:text-red-500 hover:bg-red-50 
                                 opacity-0 group-hover:opacity-100 transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))
              ) : (
                <div className="p-6 text-center text-slate-400">
                  <p className="text-xs">Aucun fichier importé</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

ImportHandler.propTypes = {
  onImportComplete: PropTypes.func
};

export default ImportHandler;