import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, Save, X, DollarSign } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const TarifsPartner = () => {
  const [clients, setClients] = useState([]);
  const [selectedClient, setSelectedClient] = useState(null);
  const [tarifs, setTarifs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [newTarif, setNewTarif] = useState({
    code_lettre: '',
    description: '',
    montant: ''
  });
  const [isAdding, setIsAdding] = useState(false);

  // Charger les clients
  useEffect(() => {
    loadClients();
  }, []);

  // Charger les tarifs quand un client est sélectionné
  useEffect(() => {
    if (selectedClient) {
      loadTarifs();
    }
  }, [selectedClient]);

  const loadClients = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/clients`);
      if (response.data.success) {
        // Filtrer pour ne garder que PARTNER
        const partnerClients = response.data.clients.filter(c => c.code !== 'EOS');
        setClients(partnerClients);
        if (partnerClients.length > 0) {
          setSelectedClient(partnerClients[0]);
        }
      }
    } catch (error) {
      console.error('Erreur lors du chargement des clients:', error);
      setError('Erreur lors du chargement des clients');
    }
  };

  const loadTarifs = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/api/tarifs-client?client_id=${selectedClient.id}`);
      if (response.data.success) {
        setTarifs(response.data.tarifs);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des tarifs:', error);
      setError('Erreur lors du chargement des tarifs');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newTarif.code_lettre || !newTarif.montant) {
      setError('Le code et le montant sont obligatoires');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_URL}/api/tarifs-client`, {
        client_id: selectedClient.id,
        code_lettre: newTarif.code_lettre.toUpperCase(),
        description: newTarif.description,
        montant: parseFloat(newTarif.montant),
        date_debut: new Date().toISOString().split('T')[0]
      });

      if (response.data.success) {
        setSuccess('Tarif ajouté avec succès');
        setNewTarif({ code_lettre: '', description: '', montant: '' });
        setIsAdding(false);
        loadTarifs();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      console.error('Erreur lors de l\'ajout du tarif:', error);
      setError(error.response?.data?.error || 'Erreur lors de l\'ajout du tarif');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async (tarif) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.put(`${API_URL}/api/tarifs-client/${tarif.id}`, {
        montant: parseFloat(tarif.montant),
        description: tarif.description
      });

      if (response.data.success) {
        setSuccess('Tarif modifié avec succès');
        setEditingId(null);
        loadTarifs();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      console.error('Erreur lors de la modification du tarif:', error);
      setError('Erreur lors de la modification du tarif');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (tarifId) => {
    if (!confirm('Êtes-vous sûr de vouloir désactiver ce tarif ?')) {
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.delete(`${API_URL}/api/tarifs-client/${tarifId}`);

      if (response.data.success) {
        setSuccess('Tarif désactivé avec succès');
        loadTarifs();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (error) {
      console.error('Erreur lors de la désactivation du tarif:', error);
      setError('Erreur lors de la désactivation du tarif');
    } finally {
      setIsLoading(false);
    }
  };

  const updateTarifValue = (tarifId, field, value) => {
    setTarifs(tarifs.map(t => 
      t.id === tarifId ? { ...t, [field]: value } : t
    ));
  };

  if (clients.length === 0) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">
          Aucun client non-EOS trouvé. Assurez-vous que PARTNER est bien créé.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <DollarSign className="w-6 h-6 text-green-600" />
            Gestion des tarifs {selectedClient?.nom}
          </h2>
          <p className="text-gray-600 mt-1">
            Configurez les tarifs par lettre pour {selectedClient?.nom}
          </p>
        </div>

        {selectedClient && (
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            {isAdding ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
            {isAdding ? 'Annuler' : 'Nouveau tarif'}
          </button>
        )}
      </div>

      {/* Messages */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          {error}
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
          {success}
        </div>
      )}

      {/* Formulaire d'ajout */}
      {isAdding && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Nouveau tarif</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Code lettre *
              </label>
              <input
                type="text"
                value={newTarif.code_lettre}
                onChange={(e) => setNewTarif({ ...newTarif, code_lettre: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="A, B, C..."
                maxLength="10"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <input
                type="text"
                value={newTarif.description}
                onChange={(e) => setNewTarif({ ...newTarif, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Description du tarif"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant (€) *
              </label>
              <input
                type="number"
                step="0.01"
                value={newTarif.montant}
                onChange={(e) => setNewTarif({ ...newTarif, montant: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="15.00"
              />
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={handleAdd}
              disabled={isLoading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Enregistrer
            </button>
            <button
              onClick={() => {
                setIsAdding(false);
                setNewTarif({ code_lettre: '', description: '', montant: '' });
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              Annuler
            </button>
          </div>
        </div>
      )}

      {/* Liste des tarifs */}
      {isLoading && <p className="text-center py-8">Chargement...</p>}

      {!isLoading && tarifs.length === 0 && !isAdding && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <p className="text-gray-600 mb-4">Aucun tarif défini pour ce client</p>
          <button
            onClick={() => setIsAdding(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 inline-flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Ajouter un tarif
          </button>
        </div>
      )}

      {!isLoading && tarifs.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
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
              {tarifs.map((tarif) => (
                <tr key={tarif.id} className={editingId === tarif.id ? 'bg-blue-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-3 py-1 text-lg font-bold text-blue-800 bg-blue-100 rounded-full">
                      {tarif.code_lettre}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {editingId === tarif.id ? (
                      <input
                        type="text"
                        value={tarif.description}
                        onChange={(e) => updateTarifValue(tarif.id, 'description', e.target.value)}
                        className="w-full px-2 py-1 border border-gray-300 rounded"
                      />
                    ) : (
                      <span className="text-gray-900">{tarif.description || '-'}</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {editingId === tarif.id ? (
                      <input
                        type="number"
                        step="0.01"
                        value={tarif.montant}
                        onChange={(e) => updateTarifValue(tarif.id, 'montant', e.target.value)}
                        className="w-24 px-2 py-1 border border-gray-300 rounded"
                      />
                    ) : (
                      <span className="text-lg font-semibold text-green-600">
                        {parseFloat(tarif.montant).toFixed(2)} €
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {tarif.date_debut}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {editingId === tarif.id ? (
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => handleUpdate(tarif)}
                          className="text-green-600 hover:text-green-900 flex items-center gap-1"
                        >
                          <Save className="w-4 h-4" />
                          Enregistrer
                        </button>
                        <button
                          onClick={() => {
                            setEditingId(null);
                            loadTarifs(); // Recharger pour annuler les modifications
                          }}
                          className="text-gray-600 hover:text-gray-900"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => setEditingId(tarif.id)}
                          className="text-blue-600 hover:text-blue-900 flex items-center gap-1"
                        >
                          <Edit2 className="w-4 h-4" />
                          Modifier
                        </button>
                        <button
                          onClick={() => handleDelete(tarif.id)}
                          className="text-red-600 hover:text-red-900 flex items-center gap-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          Désactiver
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TarifsPartner;


