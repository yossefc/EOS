import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  DollarSign, PlusCircle, RefreshCw, Check, AlertCircle, Edit, Trash2,
  FilePlus, Archive, Calculator, AlertTriangle, BarChart2, Users
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const TarificationViewer = () => {
  // États pour les données
  const [tarifsEOS, setTarifsEOS] = useState([]);
  const [tarifsEnqueteur, setTarifsEnqueteur] = useState([]);
  const [enqueteurs, setEnqueteurs] = useState([]);
  
  // États pour les formulaires
  const [showFormEOS, setShowFormEOS] = useState(false);
  const [showFormEnqueteur, setShowFormEnqueteur] = useState(false);
  const [formDataEOS, setFormDataEOS] = useState({ code: '', description: '', montant: '' });
  const [formDataEnqueteur, setFormDataEnqueteur] = useState({ code: '', description: '', montant: '', enqueteur_id: '' });
  
  // États pour l'édition
  const [editingEOS, setEditingEOS] = useState(null);
  const [editingEnqueteur, setEditingEnqueteur] = useState(null);
  
  // États pour le chargement et les erreurs
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // États pour l'onglet actif
  const [activeTab, setActiveTab] = useState('tarifsEOS');
  
  // Charger les données initiales
  useEffect(() => {
    fetchData();
  }, []);
  
  // Fonction pour récupérer toutes les données
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [tarifsEOSResponse, tarifsEnqueteurResponse, enqueteursResponse] = await Promise.all([
        axios.get(`${API_URL}/api/tarifs/eos`),
        axios.get(`${API_URL}/api/tarifs/enqueteur`),
        axios.get(`${API_URL}/api/enqueteurs`)
      ]);
      
      if (tarifsEOSResponse.data.success) {
        setTarifsEOS(tarifsEOSResponse.data.data);
      }
      
      if (tarifsEnqueteurResponse.data.success) {
        setTarifsEnqueteur(tarifsEnqueteurResponse.data.data);
      }
      
      if (enqueteursResponse.data.success) {
        setEnqueteurs(enqueteursResponse.data.data);
      }
      
    } catch (error) {
      console.error("Erreur lors du chargement des données:", error);
      setError("Erreur lors du chargement des données. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };
  
  // Fonction pour initialiser les tarifs par défaut
  const initializeTarifs = async () => {
    try {
      setLoading(true);
      
      const response = await axios.post(`${API_URL}/api/tarifs/initialiser`);
      
      if (response.data.success) {
        setSuccess("Tarifs initialisés avec succès");
        fetchData();
      } else {
        setError("Erreur lors de l'initialisation des tarifs");
      }
      
    } catch (error) {
      console.error("Erreur lors de l'initialisation:", error);
      setError("Erreur lors de l'initialisation des tarifs");
    } finally {
      setLoading(false);
    }
  };
  
  // Gestionnaires de formulaire EOS
  const handleSubmitEOS = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      if (!formDataEOS.code || !formDataEOS.montant) {
        setError("Le code et le montant sont obligatoires");
        setLoading(false);
        return;
      }
      
      let response;
      
      if (editingEOS) {
        // Mise à jour
        response = await axios.put(`${API_URL}/api/tarifs/eos/${editingEOS.id}`, formDataEOS);
      } else {
        // Création
        response = await axios.post(`${API_URL}/api/tarifs/eos`, formDataEOS);
      }
      
      if (response.data.success) {
        setSuccess(editingEOS ? "Tarif EOS mis à jour avec succès" : "Tarif EOS créé avec succès");
        setFormDataEOS({ code: '', description: '', montant: '' });
        setShowFormEOS(false);
        setEditingEOS(null);
        fetchData();
      } else {
        setError(response.data.error || "Une erreur s'est produite");
      }
      
    } catch (error) {
      console.error("Erreur lors de la soumission:", error);
      setError(error.response?.data?.error || "Erreur lors de la soumission du formulaire");
    } finally {
      setLoading(false);
    }
  };
  
  // Gestionnaires de formulaire Enquêteur
  const handleSubmitEnqueteur = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      if (!formDataEnqueteur.code || !formDataEnqueteur.montant) {
        setError("Le code et le montant sont obligatoires");
        setLoading(false);
        return;
      }
      
      let response;
      
      if (editingEnqueteur) {
        // Mise à jour
        response = await axios.put(`${API_URL}/api/tarifs/enqueteur/${editingEnqueteur.id}`, formDataEnqueteur);
      } else {
        // Création
        response = await axios.post(`${API_URL}/api/tarifs/enqueteur`, formDataEnqueteur);
      }
      
      if (response.data.success) {
        setSuccess(editingEnqueteur ? "Tarif Enquêteur mis à jour avec succès" : "Tarif Enquêteur créé avec succès");
        setFormDataEnqueteur({ code: '', description: '', montant: '', enqueteur_id: '' });
        setShowFormEnqueteur(false);
        setEditingEnqueteur(null);
        fetchData();
      } else {
        setError(response.data.error || "Une erreur s'est produite");
      }
      
    } catch (error) {
      console.error("Erreur lors de la soumission:", error);
      setError(error.response?.data?.error || "Erreur lors de la soumission du formulaire");
    } finally {
      setLoading(false);
    }
  };
  
  // Supprimer un tarif EOS
  const handleDeleteEOS = async (id) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce tarif ?")) {
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await axios.delete(`${API_URL}/api/tarifs/eos/${id}`);
      
      if (response.data.success) {
        setSuccess("Tarif EOS supprimé avec succès");
        fetchData();
      } else {
        setError(response.data.error || "Erreur lors de la suppression");
      }
      
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      setError(error.response?.data?.error || "Erreur lors de la suppression");
    } finally {
      setLoading(false);
    }
  };
  
  // Supprimer un tarif Enquêteur
  const handleDeleteEnqueteur = async (id) => {
    if (!window.confirm("Êtes-vous sûr de vouloir supprimer ce tarif ?")) {
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await axios.delete(`${API_URL}/api/tarifs/enqueteur/${id}`);
      
      if (response.data.success) {
        setSuccess("Tarif Enquêteur supprimé avec succès");
        fetchData();
      } else {
        setError(response.data.error || "Erreur lors de la suppression");
      }
      
    } catch (error) {
      console.error("Erreur lors de la suppression:", error);
      setError(error.response?.data?.error || "Erreur lors de la suppression");
    } finally {
      setLoading(false);
    }
  };
  
  // Éditer un tarif EOS
  const handleEditEOS = (tarif) => {
    setFormDataEOS({
      code: tarif.code,
      description: tarif.description,
      montant: tarif.montant
    });
    setEditingEOS(tarif);
    setShowFormEOS(true);
  };
  
  // Éditer un tarif Enquêteur
  const handleEditEnqueteur = (tarif) => {
    setFormDataEnqueteur({
      code: tarif.code,
      description: tarif.description,
      montant: tarif.montant,
      enqueteur_id: tarif.enqueteur_id || ''
    });
    setEditingEnqueteur(tarif);
    setShowFormEnqueteur(true);
  };

  // Rendu de l'interface
  return (
    <div className="space-y-4">
      {/* Titre et description */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-green-500" />
            Gestion des Tarifs
          </h1>
          <p className="text-gray-600 mt-1">
            Gérez les tarifs facturés par EOS et les tarifs payés aux enquêteurs
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchData}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md border border-gray-300 hover:bg-gray-50"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Actualiser</span>
          </button>
          <button
            onClick={initializeTarifs}
            className="flex items-center gap-1 px-3 py-1.5 rounded-md bg-blue-500 text-white hover:bg-blue-600"
          >
            <FilePlus className="w-4 h-4" />
            <span>Initialiser les tarifs</span>
          </button>
        </div>
      </div>

      {/* Messages de succès et d'erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
          <Check className="w-5 h-5 flex-shrink-0" />
          <p>{success}</p>
        </div>
      )}

      {/* Onglets */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('tarifsEOS')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tarifsEOS'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Tarifs EOS
          </button>
          <button
            onClick={() => setActiveTab('tarifsEnqueteur')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tarifsEnqueteur'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Tarifs Enquêteur
          </button>
          <button
            onClick={() => setActiveTab('rapports')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'rapports'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Rapports Financiers
          </button>
        </nav>
      </div>

      {/* Contenu des onglets */}
      <div className="p-4">
        {/* Tarifs EOS */}
        {activeTab === 'tarifsEOS' && (
          <div>
            {/* Bouton d'ajout */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Tarifs facturés par EOS France</h2>
              <button
                onClick={() => {
                  setFormDataEOS({ code: '', description: '', montant: '' });
                  setEditingEOS(null);
                  setShowFormEOS(!showFormEOS);
                }}
                className="flex items-center gap-1 px-3 py-2 rounded-md bg-green-500 text-white hover:bg-green-600"
              >
                <PlusCircle className="w-5 h-5" />
                <span>{showFormEOS ? 'Annuler' : 'Ajouter un tarif'}</span>
              </button>
            </div>

            {/* Formulaire d'ajout/édition */}
            {showFormEOS && (
              <div className="bg-gray-50 p-4 rounded-lg mb-4 border border-gray-200">
                <h3 className="font-medium mb-3">
                  {editingEOS ? 'Modifier le tarif' : 'Ajouter un nouveau tarif'}
                </h3>
                <form onSubmit={handleSubmitEOS} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Code des éléments*
                      </label>
                      <input
                        type="text"
                        value={formDataEOS.code}
                        onChange={(e) => setFormDataEOS({ ...formDataEOS, code: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        placeholder="Ex: A, AT, D..."
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <input
                        type="text"
                        value={formDataEOS.description}
                        onChange={(e) => setFormDataEOS({ ...formDataEOS, description: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        placeholder="Ex: Adresse et téléphone"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Montant (€)*
                      </label>
                      <input
                        type="number"
                        value={formDataEOS.montant}
                        onChange={(e) => setFormDataEOS({ ...formDataEOS, montant: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        step="0.01"
                        min="0"
                        required
                      />
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 flex items-center gap-1"
                    >
                      {loading ? (
                        <span className="flex items-center gap-1">
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Traitement...
                        </span>
                      ) : (
                        <span className="flex items-center gap-1">
                          <Check className="w-4 h-4" />
                          {editingEOS ? 'Mettre à jour' : 'Enregistrer'}
                        </span>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Tableau des tarifs */}
            <div className="bg-white rounded-lg border overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date début
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading && tarifsEOS.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center">
                        <div className="flex justify-center items-center">
                          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                          Chargement...
                        </div>
                      </td>
                    </tr>
                  ) : tarifsEOS.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                        Aucun tarif défini. Utilisez le bouton "Initialiser les tarifs" pour créer les tarifs par défaut.
                      </td>
                    </tr>
                  ) : (
                    tarifsEOS.map((tarif) => (
                      <tr key={tarif.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {tarif.code}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tarif.description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tarif.montant.toFixed(2)} €
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tarif.date_debut}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => handleEditEOS(tarif)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteEOS(tarif.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tarifs Enquêteur */}
        {activeTab === 'tarifsEnqueteur' && (
          <div>
            {/* Bouton d'ajout */}
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-medium">Tarifs payés aux enquêteurs</h2>
              <button
                onClick={() => {
                  setFormDataEnqueteur({ code: '', description: '', montant: '', enqueteur_id: '' });
                  setEditingEnqueteur(null);
                  setShowFormEnqueteur(!showFormEnqueteur);
                }}
                className="flex items-center gap-1 px-3 py-2 rounded-md bg-green-500 text-white hover:bg-green-600"
              >
                <PlusCircle className="w-5 h-5" />
                <span>{showFormEnqueteur ? 'Annuler' : 'Ajouter un tarif'}</span>
              </button>
            </div>

            {/* Formulaire d'ajout/édition */}
            {showFormEnqueteur && (
              <div className="bg-gray-50 p-4 rounded-lg mb-4 border border-gray-200">
                <h3 className="font-medium mb-3">
                  {editingEnqueteur ? 'Modifier le tarif' : 'Ajouter un nouveau tarif'}
                </h3>
                <form onSubmit={handleSubmitEnqueteur} className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Code des éléments*
                      </label>
                      <input
                        type="text"
                        value={formDataEnqueteur.code}
                        onChange={(e) => setFormDataEnqueteur({ ...formDataEnqueteur, code: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        placeholder="Ex: A, AT, D..."
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <input
                        type="text"
                        value={formDataEnqueteur.description}
                        onChange={(e) => setFormDataEnqueteur({ ...formDataEnqueteur, description: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        placeholder="Ex: Adresse et téléphone"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Montant (€)*
                      </label>
                      <input
                        type="number"
                        value={formDataEnqueteur.montant}
                        onChange={(e) => setFormDataEnqueteur({ ...formDataEnqueteur, montant: e.target.value })}
                        className="w-full p-2 border rounded-md"
                        step="0.01"
                        min="0"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Enquêteur (vide = tarif par défaut)
                      </label>
                      <select
                        value={formDataEnqueteur.enqueteur_id}
                        onChange={(e) => setFormDataEnqueteur({ ...formDataEnqueteur, enqueteur_id: e.target.value })}
                        className="w-full p-2 border rounded-md"
                      >
                        <option value="">Tarif par défaut (tous enquêteurs)</option>
                        {enqueteurs.map((enqueteur) => (
                          <option key={enqueteur.id} value={enqueteur.id}>
                            {enqueteur.nom} {enqueteur.prenom}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 flex items-center gap-1"
                    >
                      {loading ? (
                        <span className="flex items-center gap-1">
                          <RefreshCw className="w-4 h-4 animate-spin" />
                          Traitement...
                        </span>
                      ) : (
                        <span className="flex items-center gap-1">
                          <Check className="w-4 h-4" />
                          {editingEnqueteur ? 'Mettre à jour' : 'Enregistrer'}
                        </span>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Tableau des tarifs */}
            <div className="bg-white rounded-lg border overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Code
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Enquêteur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date début
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {loading && tarifsEnqueteur.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center">
                        <div className="flex justify-center items-center">
                          <RefreshCw className="w-5 h-5 animate-spin mr-2" />
                          Chargement...
                        </div>
                      </td>
                    </tr>
                  ) : tarifsEnqueteur.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                        Aucun tarif défini. Utilisez le bouton "Initialiser les tarifs" pour créer les tarifs par défaut.
                      </td>
                    </tr>
                  ) : (
                    tarifsEnqueteur.map((tarif) => (
                      <tr key={tarif.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {tarif.code}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tarif.description}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {tarif.montant.toFixed(2)} €
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tarif.enqueteur_id ? tarif.enqueteur_nom : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Tarif par défaut
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {tarif.date_debut}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex justify-end gap-2">
                            <button
                              onClick={() => handleEditEnqueteur(tarif)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteEnqueteur(tarif.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Rapports financiers */}
        {activeTab === 'rapports' && (
          <div>
            <h2 className="text-lg font-medium mb-4">Rapports Financiers</h2>
            
            <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-4 mb-4 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-medium text-yellow-800">Fonctionnalité en développement</h3>
                <p className="text-yellow-700 text-sm mt-1">
                  Cette section permettra de visualiser et d'exporter des rapports financiers détaillés sur les enquêtes, les facturations EOS et les paiements aux enquêteurs.
                </p>
                <p className="text-yellow-700 text-sm mt-2">
                  En attendant, vous pouvez utiliser les fonctionnalités partielles ci-dessous.
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-lg border p-4">
                <h3 className="font-medium mb-3 flex items-center gap-2">
                  <BarChart2 className="w-5 h-5 text-blue-500" />
                  Statistiques Globales
                </h3>
                <p className="text-gray-500 text-sm mb-4">
                  Récapitulatif des montants facturés et à payer
                </p>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total facturé EOS:</span>
                    <span className="font-semibold">Calcul en cours...</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total à payer aux enquêteurs:</span>
                    <span className="font-semibold">Calcul en cours...</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Marge totale:</span>
                    <span className="font-semibold text-green-600">Calcul en cours...</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Pourcentage de marge:</span>
                    <span className="font-semibold text-green-600">Calcul en cours...</span>
                  </div>
                </div>
                
                <button className="w-full mt-4 flex items-center justify-center gap-1 px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
                  <Calculator className="w-4 h-4" />
                  <span>Générer un rapport détaillé</span>
                </button>
              </div>
              
              <div className="bg-white rounded-lg border p-4">
                <h3 className="font-medium mb-3 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-500" />
                  Paiements Enquêteurs
                </h3>
                <p className="text-gray-500 text-sm mb-4">
                  Gestion des paiements aux enquêteurs
                </p>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Montant total à payer:</span>
                    <span className="font-semibold">Calcul en cours...</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Dernière date de paiement:</span>
                    <span className="font-semibold">-</span>
                  </div>
                </div>
                
                <button className="w-full mt-4 flex items-center justify-center gap-1 px-3 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600">
                  <DollarSign className="w-4 h-4" />
                  <span>Voir le détail par enquêteur</span>
                </button>
              </div>
            </div>
            
            <div className="bg-white rounded-lg border">
              <div className="p-4 border-b">
                <h3 className="font-medium">Liste des enquêtes à facturer</h3>
              </div>
              <div className="p-4 text-center text-gray-500">
                <p>Cette section affichera la liste des enquêtes terminées avec leurs montants</p>
                <p className="text-sm mt-2">Fonctionnalité en cours de développement</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TarificationViewer;