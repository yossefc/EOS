import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, Save, X, AlertCircle, CheckCircle, Euro } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

/**
 * Interface d'administration des tarifs PARTNER
 * Permet de gérer les tarifs selon la lettre et la combinaison de demandes
 */
const PartnerTarifsAdmin = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // État du formulaire
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    tarif_lettre: 'A',
    request_codes: ['ADDRESS'],
    amount: ''
  });
  
  // Client PARTNER (hardcodé, à adapter si besoin)
  const PARTNER_CLIENT_ID = 11;
  
  const REQUEST_CODES = [
    { code: 'ADDRESS', label: 'Adresse', icon: '🏠', color: 'blue' },
    { code: 'PHONE', label: 'Téléphone', icon: '📞', color: 'green' },
    { code: 'EMPLOYER', label: 'Employeur', icon: '🏢', color: 'purple' },
    { code: 'BANK', label: 'Banque', icon: '🏦', color: 'indigo' },
    { code: 'BIRTH', label: 'Date et lieu de naissance', icon: '🎂', color: 'pink' }
  ];
  
  const LETTRES_TARIF = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
  
  // Charger les règles
  useEffect(() => {
    fetchRules();
  }, []);
  
  const fetchRules = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/partner/admin/tarif-rules`, {
        params: { client_id: PARTNER_CLIENT_ID }
      });
      if (response.data.success) {
        setRules(response.data.rules);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAdd = () => {
    setIsAdding(true);
    setEditingId(null);
    setFormData({
      tarif_lettre: 'A',
      request_codes: ['ADDRESS'],
      amount: ''
    });
  };
  
  const handleEdit = (rule) => {
    setEditingId(rule.id);
    setIsAdding(false);
    // Extraire les codes depuis request_key
    const codes = rule.request_key.split('+');
    setFormData({
      tarif_lettre: rule.tarif_lettre,
      request_codes: codes,
      amount: rule.amount.toString()
    });
  };
  
  const handleCancel = () => {
    setIsAdding(false);
    setEditingId(null);
    setFormData({
      tarif_lettre: 'A',
      request_codes: ['ADDRESS'],
      amount: ''
    });
  };
  
  const toggleRequestCode = (code) => {
    const newCodes = formData.request_codes.includes(code)
      ? formData.request_codes.filter(c => c !== code)
      : [...formData.request_codes, code];
    
    if (newCodes.length === 0) {
      setError('Au moins une demande doit être sélectionnée');
      return;
    }
    
    setFormData({ ...formData, request_codes: newCodes });
  };
  
  const handleSave = async () => {
    try {
      setError(null);
      
      if (!formData.amount || parseFloat(formData.amount) < 0) {
        setError('Le montant est obligatoire et doit être positif');
        return;
      }
      
      if (formData.request_codes.length === 0) {
        setError('Au moins une demande doit être sélectionnée');
        return;
      }
      
      if (editingId) {
        // Mise à jour (montant uniquement)
        await axios.put(`${API_URL}/api/partner/admin/tarif-rules/${editingId}`, {
          amount: parseFloat(formData.amount)
        });
        setSuccess('Règle de tarif mise à jour avec succès');
      } else {
        // Création
        await axios.post(`${API_URL}/api/partner/admin/tarif-rules`, {
          client_id: PARTNER_CLIENT_ID,
          tarif_lettre: formData.tarif_lettre,
          request_codes: formData.request_codes,
          amount: parseFloat(formData.amount)
        });
        setSuccess('Règle de tarif créée avec succès');
      }
      
      handleCancel();
      fetchRules();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la sauvegarde');
    }
  };
  
  const handleDelete = async (id) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette règle ?')) {
      return;
    }
    
    try {
      setError(null);
      await axios.delete(`${API_URL}/api/partner/admin/tarif-rules/${id}`);
      setSuccess('Règle de tarif supprimée avec succès');
      fetchRules();
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la suppression');
    }
  };
  
  // Grouper les règles par lettre
  const groupedRules = LETTRES_TARIF.map(lettre => ({
    lettre,
    rules: rules.filter(r => r.tarif_lettre === lettre)
  })).filter(g => g.rules.length > 0);
  
  // Formatter request_key pour affichage
  const formatRequestKey = (key) => {
    return key.split('+').map(code => {
      const found = REQUEST_CODES.find(r => r.code === code);
      return found ? found.label : code;
    }).join(' + ');
  };
  
  // Formatter avec icônes
  const formatRequestKeyWithIcons = (key) => {
    return key.split('+').map(code => {
      const found = REQUEST_CODES.find(r => r.code === code);
      return found ? { icon: found.icon, label: found.label, color: found.color } : null;
    }).filter(Boolean);
  };
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Euro className="w-7 h-7 text-blue-600" />
            Tarifs combinés PARTNER
          </h2>
          <p className="text-gray-600 mt-1">
            Gestion des tarifs selon la lettre et la combinaison de demandes
          </p>
        </div>
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm hover:shadow-md"
        >
          <Plus className="w-5 h-5" />
          Ajouter une règle
        </button>
      </div>
      
      {/* Messages */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-red-800">{error}</div>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-green-800">{success}</div>
        </div>
      )}
      
      {/* Formulaire d'ajout/édition */}
      {(isAdding || editingId) && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {editingId ? 'Modifier la règle' : 'Nouvelle règle'}
          </h3>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Lettre de tarif
              </label>
              <select
                value={formData.tarif_lettre}
                onChange={(e) => setFormData({ ...formData, tarif_lettre: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                disabled={!!editingId}
              >
                {LETTRES_TARIF.map(lettre => (
                  <option key={lettre} value={lettre}>{lettre}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant (€)
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="50.00"
                />
                <Euro className="absolute right-3 top-2.5 w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
          
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Demandes <span className="text-red-500">*</span>
            </label>
            <div className="grid grid-cols-2 gap-3">
              {REQUEST_CODES.map(({ code, label, icon, color }) => (
                <label
                  key={code}
                  className={`flex items-center gap-3 p-3 border-2 rounded-lg cursor-pointer transition-all ${
                    formData.request_codes.includes(code)
                      ? `bg-${color}-50 border-${color}-400 shadow-sm`
                      : 'bg-white border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                  } ${editingId ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <input
                    type="checkbox"
                    checked={formData.request_codes.includes(code)}
                    onChange={() => !editingId && toggleRequestCode(code)}
                    disabled={!!editingId}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-xl">{icon}</span>
                  <span className="text-sm font-medium text-gray-900">{label}</span>
                </label>
              ))}
            </div>
            {editingId && (
              <p className="text-xs text-gray-500 mt-2">
                Les demandes ne peuvent pas être modifiées. Supprimez et recréez la règle si nécessaire.
              </p>
            )}
          </div>
          
          <div className="flex gap-3 mt-6">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Save className="w-4 h-4" />
              Enregistrer
            </button>
            <button
              onClick={handleCancel}
              className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              <X className="w-4 h-4" />
              Annuler
            </button>
          </div>
        </div>
      )}
      
      {/* Liste des règles groupées par lettre */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-gray-600 mt-2">Chargement...</p>
        </div>
      ) : groupedRules.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 border rounded-lg">
          <p className="text-gray-600">Aucune règle de tarif configurée</p>
        </div>
      ) : (
        <div className="space-y-6">
          {groupedRules.map(({ lettre, rules: rls }) => (
            <div key={lettre} className="bg-white border rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b">
                <h3 className="font-semibold text-gray-900">
                  Lettre {lettre} <span className="text-gray-500 text-sm">({rls.length} règles)</span>
                </h3>
              </div>
              
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Demandes</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Montant</th>
                    <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {rls.map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-2">
                          {formatRequestKeyWithIcons(rule.request_key).map((item, idx) => (
                            <span
                              key={idx}
                              className={`inline-flex items-center gap-1.5 px-3 py-1 bg-${item.color}-50 border border-${item.color}-200 rounded-full text-sm`}
                            >
                              <span>{item.icon}</span>
                              <span className="font-medium text-gray-700">{item.label}</span>
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-lg font-bold text-green-600">
                          {parseFloat(rule.amount).toFixed(2)} €
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={() => handleEdit(rule)}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            title="Modifier le montant"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(rule.id)}
                            className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                            title="Supprimer"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PartnerTarifsAdmin;

