import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { FileUp, RefreshCw, Check, AlertCircle, File, Trash2, ChevronRight, X, Database } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

// Définition des PropTypes séparément
const ImportHandlerPropTypes = {
  onImportComplete: PropTypes.func
};

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

  // MULTI-CLIENT: États pour les clients
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [loadingClients, setLoadingClients] = useState(true);

  // Charger les statistiques et clients au montage
  useEffect(() => {
    fetchStats();
    fetchClients();
  }, []);

  // MULTI-CLIENT: Récupérer la liste des clients actifs
  const fetchClients = async () => {
    try {
      setLoadingClients(true);
      const response = await axios.get(`${API_URL}/api/clients`);
      if (response.data.success) {
        setClients(response.data.clients);
        // Sélectionner automatiquement le client EOS par défaut
        const eosClient = response.data.clients.find(c => c.code === 'EOS');
        if (eosClient) {
          setSelectedClientId(eosClient.id);
        } else if (response.data.clients.length > 0) {
          setSelectedClientId(response.data.clients[0].id);
        }
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des clients:", error);
      // Ne pas afficher d'erreur si les clients ne sont pas disponibles
      // L'application fonctionnera avec EOS par défaut côté backend
    } finally {
      setLoadingClients(false);
    }
  };

  // Récupérer les statistiques depuis le serveur
  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Erreur lors de la récupération des statistiques:", error);
      setError("Erreur lors de la récupération des statistiques");
    } finally {
      setLoading(false);
    }
  };

  // Gestion de la sélection du fichier
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setFileExists(false); // Réinitialiser l'état fileExists
      setExistingFileInfo(null);
      setError(null);
      setSuccess(null);
    }
  };

  // Envoi du fichier au serveur
  const handleUpload = async (replace = false) => {
    if (!selectedFile) {
      setError("Veuillez sélectionner un fichier");
      return;
    }

    try {
      setUploading(true);

      const formData = new FormData();
      formData.append("file", selectedFile);

      // Ajouter la date butoir si elle est définie
      if (dateButoir) {
        formData.append("date_butoir", dateButoir);
      }

      // MULTI-CLIENT: Ajouter le client_id si sélectionné
      if (selectedClientId) {
        formData.append("client_id", selectedClientId);
      }

      // Utiliser l'URL appropriée selon que l'on remplace ou non un fichier existant
      const url = replace ? `${API_URL}/replace-file` : `${API_URL}/parse`;

      const response = await axios.post(url, formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      // Gestion des réponses
      if (response.data.status === "file_exists") {
        setFileExists(true);
        setExistingFileInfo(response.data.existing_file_info);
      } else {
        setSuccess(`Fichier importé avec succès. ${response.data.records_processed} enregistrements traités.`);
        setSelectedFile(null);
        setDateButoir(''); // Réinitialiser la date butoir

        // Rafraîchir les statistiques
        fetchStats();

        // Notification au parent que l'import est terminé
        if (onImportComplete) {
          onImportComplete();
        }
      }
    } catch (error) {
      console.error("Erreur lors de l'upload:", error);
      setError(error.response?.data?.error || "Erreur lors de l'envoi du fichier");
    } finally {
      setUploading(false);
    }
  };

  // Supprimer un fichier
  const handleDeleteFile = async (fileId) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce fichier et toutes ses données ?")) {
      return;
    }

    try {
      setLoading(true);

      const response = await axios.delete(`${API_URL}/api/files/${fileId}`);

      if (response.data.message) {
        setSuccess("Fichier supprimé avec succès");
        // Rafraîchir les statistiques
        fetchStats();
      }
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      setError("Erreur lors de la suppression du fichier");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Messages d'état */}
      <div className="fixed top-24 right-8 z-[60] flex flex-col gap-3 w-80">
        {error && (
          <div className="bg-white/80 backdrop-blur-md border-l-4 border-red-500 text-red-700 p-4 rounded-xl shadow-xl animate-in slide-in-from-right duration-300 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-bold">Erreur</p>
              <p className="text-xs opacity-80">{error}</p>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {success && (
          <div className="bg-white/80 backdrop-blur-md border-l-4 border-emerald-500 text-emerald-700 p-4 rounded-xl shadow-xl animate-in slide-in-from-right duration-300 flex items-start gap-3">
            <Check className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-bold">Succès</p>
              <p className="text-xs opacity-80">{success}</p>
            </div>
            <button onClick={() => setSuccess(null)} className="text-emerald-400 hover:text-emerald-600 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Colonne de gauche: Formulaire */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-white rounded-[32px] border border-slate-200/60 p-8 shadow-sm hover:shadow-md transition-shadow duration-500">
            <div className="flex items-center gap-4 mb-8">
              <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center">
                <FileUp className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-slate-800">Nouvel Import</h3>
                <p className="text-sm text-slate-500 font-medium">Glissez un fichier ou cliquez pour parcourir</p>
              </div>
            </div>

            <div className="space-y-8">
              {/* Sélection du Client (Boutons) */}
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 ml-1">
                  Client émetteur
                </label>
                <div className="flex flex-wrap gap-2">
                  {loadingClients ? (
                    <div className="animate-pulse flex gap-2 w-full">
                      <div className="h-10 w-24 bg-slate-100 rounded-xl" />
                      <div className="h-10 w-24 bg-slate-100 rounded-xl" />
                    </div>
                  ) : (
                    clients.map(client => (
                      <button
                        key={client.id}
                        onClick={() => setSelectedClientId(client.id)}
                        className={`
                          px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 flex items-center gap-2
                          ${selectedClientId === client.id
                            ? 'bg-slate-800 text-white shadow-md shadow-slate-200'
                            : 'bg-slate-50 text-slate-500 hover:bg-slate-100 border border-transparent hover:border-slate-200'}
                        `}
                      >
                        <div className={`w-1.5 h-1.5 rounded-full ${selectedClientId === client.id ? 'bg-blue-400' : 'bg-slate-300'}`} />
                        {client.nom}
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Zone d'upload Stylisée */}
              <div className="group relative">
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
                <div className={`
                  border-2 border-dashed rounded-[24px] p-10 text-center transition-all duration-500
                  ${selectedFile
                    ? 'border-blue-500/50 bg-blue-50/30'
                    : 'border-slate-200 group-hover:border-blue-400 group-hover:bg-slate-50/50'}
                `}>
                  <div className={`
                    w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 transition-all duration-500
                    ${selectedFile ? 'bg-blue-500 text-white scale-110' : 'bg-slate-100 text-slate-400 group-hover:scale-110 group-hover:text-blue-500 transform'}
                  `}>
                    {selectedFile ? <Check className="w-8 h-8" /> : <File className="w-8 h-8" />}
                  </div>
                  {selectedFile ? (
                    <div className="animate-in fade-in zoom-in-95 duration-300">
                      <p className="text-slate-800 font-bold text-lg mb-1">{selectedFile.name}</p>
                      <p className="text-slate-500 text-sm font-medium">
                        {(selectedFile.size / 1024).toFixed(1)} KB • Prêt pour l&apos;import
                      </p>
                      <button
                        onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                        className="mt-4 text-xs font-bold text-rose-500 hover:text-rose-600 transition-colors"
                      >
                        Changer de fichier
                      </button>
                    </div>
                  ) : (
                    <>
                      <p className="text-slate-900 font-bold text-lg mb-1">Sélectionner un fichier</p>
                      <p className="text-slate-500 text-sm font-medium">PDF, Excel ou Texte (format EOS)</p>
                    </>
                  )}
                </div>
              </div>

              {/* Date Butoir */}
              <div className="space-y-3">
                <label className="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2 ml-1">
                  Date Butoir <span className="text-[10px] font-bold text-blue-500 lowercase">(optionnel)</span>
                </label>
                <input
                  type="date"
                  value={dateButoir}
                  onChange={(e) => setDateButoir(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200/60 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                />
              </div>

              {/* Action Button */}
              {!fileExists ? (
                <button
                  onClick={() => handleUpload(false)}
                  disabled={!selectedFile || uploading}
                  className="w-full py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-200 text-white rounded-xl font-bold shadow-md shadow-blue-100 disabled:shadow-none transition-all active:scale-[0.98] flex items-center justify-center gap-2"
                >
                  {uploading ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      <span>Traitement en cours...</span>
                    </>
                  ) : (
                    <>
                      <FileUp className="w-5 h-5" />
                      <span>Lancer l&apos;importation</span>
                    </>
                  )}
                </button>
              ) : (
                <div className="p-6 bg-amber-50 rounded-2xl border border-amber-200 animate-in zoom-in-95 duration-300">
                  <div className="flex items-center gap-3 mb-4 text-amber-800">
                    <AlertCircle className="w-6 h-6" />
                    <h4 className="font-black">Fichier déjà existant</h4>
                  </div>
                  <p className="text-sm text-amber-700 mb-6 font-medium leading-relaxed">
                    Un fichier nommé <span className="font-bold text-slate-900">{existingFileInfo?.nom}</span> a été importé le {existingFileInfo?.date_upload}.
                    Voulez-vous écraser les données existantes ?
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleUpload(true)}
                      className="flex-1 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold transition-all shadow-lg shadow-amber-200/50"
                    >
                      Oui, remplacer
                    </button>
                    <button
                      onClick={() => { setFileExists(false); setSelectedFile(null); }}
                      className="flex-1 py-3 bg-white border border-amber-200 text-amber-800 rounded-xl font-bold hover:bg-amber-100 transition-all"
                    >
                      Annuler
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Colonne de droite: Stats & Historique */}
        <div className="lg:col-span-5 space-y-8">
          {/* Cartes Stats en Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white p-6 rounded-[24px] border border-slate-200/60 shadow-sm">
              <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
                <File className="w-5 h-5 text-indigo-600" />
              </div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-wider mb-1">Fichiers</p>
              <p className="text-3xl font-black text-slate-900 truncate">
                {stats?.total_fichiers || 0}
              </p>
            </div>

            <div className="bg-white p-6 rounded-[24px] border border-slate-200/60 shadow-sm">
              <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mb-4">
                <Database className="w-5 h-5 text-emerald-600" />
              </div>
              <p className="text-xs font-black text-slate-400 uppercase tracking-wider mb-1">Dossiers</p>
              <p className="text-3xl font-black text-slate-900 truncate">
                {stats?.total_donnees || 0}
              </p>
            </div>
          </div>

          {/* Liste des fichiers */}
          <div className="bg-white rounded-[32px] border border-slate-200/60 overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h3 className="font-bold text-slate-500 text-[10px] uppercase tracking-[0.2em]">Historique des imports</h3>
            </div>

            <div className="divide-y divide-slate-100">
              {loading ? (
                <div className="p-10 flex flex-col items-center gap-4 text-slate-400">
                  <RefreshCw className="w-8 h-8 animate-spin" />
                  <span className="text-xs font-bold uppercase tracking-widest">Synchronisation...</span>
                </div>
              ) : stats?.derniers_fichiers && stats.derniers_fichiers.length > 0 ? (
                <div className="max-h-[400px] overflow-y-auto hide-scrollbar">
                  {stats.derniers_fichiers.map((fichier) => (
                    <div
                      key={fichier.id}
                      className="group flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition-colors"
                    >
                      <div className="flex items-center gap-3 overflow-hidden">
                        <div className="w-8 h-8 bg-slate-100 rounded-lg flex items-center justify-center group-hover:bg-blue-100 transition-colors">
                          <File className="w-4 h-4 text-slate-400 group-hover:text-blue-600" />
                        </div>
                        <div className="overflow-hidden">
                          <p className="font-bold text-slate-900 text-sm truncate">{fichier.nom}</p>
                          <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">
                            {fichier.date_upload} • {fichier.nombre_donnees} rec.
                          </p>
                        </div>
                      </div>

                      <button
                        onClick={() => handleDeleteFile(fichier.id)}
                        className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-300 hover:text-rose-600 hover:bg-rose-50 transition-all opacity-0 group-hover:opacity-100"
                        title="Supprimer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-12 text-center text-slate-400">
                  <p className="text-xs font-black uppercase tracking-widest">Aucun historique</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Aide et documentation */}
      {/* MULTI-CLIENT: Aide pour CLIENT_X */}
      {selectedClientId && clients.find(c => c.id === selectedClientId && c.code === 'CLIENT_X') && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium mb-2 flex items-center gap-2 text-blue-900">
            <ChevronRight className="w-5 h-5 text-blue-500" />
            Format de fichier CLIENT_X
          </h3>

          <div className="space-y-3 text-sm text-blue-900">
            <div>
              <p className="font-medium mb-1">📋 ENQUÊTES</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800 ml-2">
                <li>Format: Excel (.xlsx ou .xls)</li>
                <li>Onglet requis: <span className="font-mono bg-blue-100 px-1">Worksheet</span></li>
                <li>Colonnes: NUM, NOM, PRENOM, JOUR, MOIS, ANNEE NAISSANCE, LIEUNAISSANCE, DATE ENVOI, DATE BUTOIR, ADRESSE, CP, VILLE, TEL, TARIF, RECHERCHE</li>
                <li>Le code postal sera automatiquement formaté sur 5 chiffres</li>
                <li>Les téléphones à "0" seront ignorés</li>
              </ul>
            </div>

            <div>
              <p className="font-medium mb-1">⚠️ CONTESTATIONS</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800 ml-2">
                <li>Format: Excel (.xlsx ou .xls)</li>
                <li>Onglet requis: <span className="font-mono bg-blue-100 px-1">FICHIER 1 CONTRE</span></li>
                <li>Colonnes: DATE DU JOUR, NOM, PRENOM (URGENT si urgence), MOTIF, DATE BUTOIR</li>
                <li>Si PRENOM contient "URGENT", la contestation sera marquée comme urgente</li>
              </ul>
            </div>

            <p className="text-xs text-blue-700 mt-2">
              💡 Les lignes vides sont automatiquement ignorées lors de l&apos;import
            </p>
          </div>
        </div>
      )}


    </div>
  );
};

// Assigner les PropTypes après la définition du composant
ImportHandler.propTypes = ImportHandlerPropTypes;

export default ImportHandler;