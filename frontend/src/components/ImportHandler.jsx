import  { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { FileUp, RefreshCw, Check, AlertCircle, File, Trash2, ChevronRight, X } from 'lucide-react';
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
    <div className="space-y-6">
      {/* En-tête */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <FileUp className="w-6 h-6 text-blue-500" />
          Import de fichiers
        </h2>
        
        <button
          onClick={fetchStats}
          className="flex items-center gap-1 px-3 py-1.5 rounded-md border border-gray-300 hover:bg-gray-50"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Actualiser</span>
        </button>
      </div>
      
      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
          <button 
            onClick={() => setError(null)}
            className="ml-auto text-red-700 hover:text-red-900"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-center gap-2">
          <Check className="w-5 h-5 flex-shrink-0" />
          <p>{success}</p>
          <button 
            onClick={() => setSuccess(null)}
            className="ml-auto text-green-700 hover:text-green-900"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      {/* Formulaire d'upload */}
      <div className="bg-white rounded-lg border p-6">
        <h3 className="text-lg font-medium mb-4">Importer un nouveau fichier</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fichier à importer
            </label>
            <div className="flex items-center gap-2">
              <input
                type="file"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              {selectedFile && (
                <span className="text-sm text-gray-600">
                  {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
              )}
            </div>
          </div>
          
          {/* MULTI-CLIENT: Sélecteur de client (masqué si un seul client) */}
          {!loadingClients && clients.length > 1 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Client
              </label>
              <select
                value={selectedClientId || ''}
                onChange={(e) => setSelectedClientId(parseInt(e.target.value))}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                {clients.map(client => (
                  <option key={client.id} value={client.id}>
                    {client.nom} ({client.code})
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Sélectionnez le client pour lequel importer les données
              </p>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date butoir (optionnelle)
            </label>
            <input
              type="date"
              value={dateButoir}
              onChange={(e) => setDateButoir(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Sélectionner une date butoir"
            />
            <p className="mt-1 text-xs text-gray-500">
              Si définie, cette date sera appliquée à toutes les enquêtes du fichier importé
            </p>
          </div>
          
          {!fileExists ? (
            <button
              onClick={() => handleUpload(false)}
              disabled={!selectedFile || uploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Importation en cours...</span>
                </>
              ) : (
                <>
                  <FileUp className="w-4 h-4" />
                  <span>Importer le fichier</span>
                </>
              )}
            </button>
          ) : (
            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
              <h4 className="font-medium text-yellow-800 mb-2">Ce fichier existe déjà</h4>
              
              {existingFileInfo && (
                <div className="mb-3 text-sm">
                  <p>Nom: <span className="font-medium">{existingFileInfo.nom}</span></p>
                  <p>Date d&apos;upload: <span className="font-medium">{existingFileInfo.date_upload}</span></p>
                  <p>Nombre d&apos;enregistrements: <span className="font-medium">{existingFileInfo.nombre_donnees}</span></p>
                </div>
              )}
              
              <p className="text-sm text-yellow-700 mb-3">
                Que souhaitez-vous faire ?
              </p>
              
              <div className="flex gap-2">
                <button
                  onClick={() => handleUpload(true)}
                  className="px-3 py-1.5 bg-yellow-600 text-white rounded-md hover:bg-yellow-700"
                >
                  Remplacer
                </button>
                
                <button
                  onClick={() => {
                    setFileExists(false);
                    setSelectedFile(null);
                    setDateButoir('');
                  }}
                  className="px-3 py-1.5 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Annuler
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Statistiques et liste des fichiers */}
      <div className="bg-white rounded-lg border overflow-hidden">
        <div className="p-4 bg-gray-50 border-b">
          <h3 className="font-medium">Statistiques des fichiers importés</h3>
        </div>
        
        {loading ? (
          <div className="p-12 flex justify-center">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        ) : stats ? (
          <div>
            {/* Statistiques */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-700">Nombre total de fichiers</p>
                <p className="text-2xl font-bold text-blue-900">{stats.total_fichiers}</p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-green-700">Nombre total d&apos;enregistrements</p>
                <p className="text-2xl font-bold text-green-900">{stats.total_donnees}</p>
              </div>
            </div>
            
            {/* Liste des fichiers */}
            <div className="p-4 border-t">
              <h4 className="font-medium mb-3">Derniers fichiers importés</h4>
              
              {stats.derniers_fichiers && stats.derniers_fichiers.length > 0 ? (
                <div className="space-y-2">
                  {stats.derniers_fichiers.map((fichier) => (
                    <div 
                      key={fichier.id}
                      className="flex items-center justify-between bg-gray-50 p-3 rounded-lg border hover:bg-gray-100"
                    >
                      <div className="flex items-center gap-3">
                        <File className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="font-medium">{fichier.nom}</p>
                          <p className="text-xs text-gray-500">{fichier.date_upload} • {fichier.nombre_donnees} enregistrements</p>
                        </div>
                      </div>
                      
                      <div>
                        <button
                          onClick={() => handleDeleteFile(fichier.id)}
                          className="text-red-600 hover:text-red-800"
                          title="Supprimer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center p-4">
                  Aucun fichier importé
                </p>
              )}
            </div>
          </div>
        ) : (
          <p className="p-6 text-center text-gray-500">
            Aucune statistique disponible
          </p>
        )}
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
      
      <div className="bg-gray-50 border rounded-lg p-4">
        <h3 className="font-medium mb-2 flex items-center gap-2">
          <ChevronRight className="w-5 h-5 text-blue-500" />
          Format de fichier requis (EOS)
        </h3>
        
        <p className="text-sm text-gray-600 mb-3">
          Le fichier importé doit respecter le format spécifié dans le cahier des charges EOS France.
          Il s&apos;agit d&apos;un fichier texte avec des champs de longueur fixe selon la spécification suivante :
        </p>
        
        <div className="overflow-x-auto">
          <table className="min-w-full text-xs sm:text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-2 py-1 text-left">Nom du champ</th>
                <th className="px-2 py-1 text-center">Position</th>
                <th className="px-2 py-1 text-center">Longueur</th>
                <th className="px-2 py-1 text-left">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-2 py-1 font-medium">numeroDossier</td>
                <td className="px-2 py-1 text-center">1-10</td>
                <td className="px-2 py-1 text-center">10</td>
                <td className="px-2 py-1">Identifiant unique du dossier</td>
              </tr>
              <tr>
                <td className="px-2 py-1 font-medium">referenceDossier</td>
                <td className="px-2 py-1 text-center">11-25</td>
                <td className="px-2 py-1 text-center">15</td>
                <td className="px-2 py-1">Référence externe</td>
              </tr>
              <tr>
                <td className="px-2 py-1 font-medium">typeDemande</td>
                <td className="px-2 py-1 text-center">73-75</td>
                <td className="px-2 py-1 text-center">3</td>
                <td className="px-2 py-1">Type (ENQ ou CON)</td>
              </tr>
              <tr>
                <td className="px-2 py-1 font-medium">nom</td>
                <td className="px-2 py-1 text-center">145-174</td>
                <td className="px-2 py-1 text-center">30</td>
                <td className="px-2 py-1">Nom de la personne</td>
              </tr>
              <tr>
                <td colSpan="4" className="px-2 py-1 text-center text-gray-500">
                  ... autres champs selon le cahier des charges
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Assigner les PropTypes après la définition du composant
ImportHandler.propTypes = ImportHandlerPropTypes;

export default ImportHandler;