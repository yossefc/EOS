import { useState, useEffect } from 'react';
import axios from 'axios';
import { Plus, Edit2, Trash2, Save, X, AlertCircle, CheckCircle, HelpCircle, ArrowUp, ArrowDown } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

/**
 * Interface d'administration des mots-clés PARTNER
 * Design visuel et intuitif pour gérer les patterns de détection
 */
const PartnerKeywordsAdmin = () => {
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isAdding, setIsAdding] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    request_code: 'ADDRESS',
    pattern: '',
    is_regex: false,
    priority: 10
  });
  
  const PARTNER_CLIENT_ID = 11;
  
  const REQUEST_TYPES = [
    { 
      code: 'ADDRESS', 
      label: 'Adresse', 
      icon: '🏠',
      color: 'blue',
      example: 'ADRESSE',
      description: 'Détecte les demandes de recherche d\'adresse'
    },
    { 
      code: 'PHONE', 
      label: 'Téléphone', 
      icon: '📞',
      color: 'green',
      example: 'TELEPHONE ou TEL',
      description: 'Détecte les demandes de numéro de téléphone'
    },
    { 
      code: 'EMPLOYER', 
      label: 'Employeur', 
      icon: '💼',
      color: 'purple',
      example: 'EMPLOYEUR',
      description: 'Détecte les demandes d\'informations sur l\'employeur'
    },
    { 
      code: 'BANK', 
      label: 'Banque', 
      icon: '🏦',
      color: 'indigo',
      example: 'BANQUE',
      description: 'Détecte les demandes d\'informations bancaires'
    },
    { 
      code: 'BIRTH', 
      label: 'Naissance', 
      icon: '🎂',
      color: 'pink',
      example: 'LIEU DE NAISSANCE',
      description: 'Détecte les demandes de date/lieu de naissance'
    }
  ];
  
  // Charger les keywords
  useEffect(() => {
    fetchKeywords();
  }, []);
  
  const fetchKeywords = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_URL}/api/partner/admin/keywords`, {
        params: { client_id: PARTNER_CLIENT_ID }
      });
      if (response.data.success) {
        setKeywords(response.data.keywords);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };
  
  const handleAdd = (requestCode) => {
    setIsAdding(true);
    setEditingId(null);
    setFormData({
      request_code: requestCode,
      pattern: '',
      is_regex: false,
      priority: 10
    });
  };
  
  const handleEdit = (keyword) => {
    setEditingId(keyword.id);
    setIsAdding(false);
    setFormData({
      request_code: keyword.request_code,
      pattern: keyword.pattern,
      is_regex: keyword.is_regex,
      priority: keyword.priority
    });
  };
  
  const handleCancel = () => {
    setIsAdding(false);
    setEditingId(null);
    setFormData({
      request_code: 'ADDRESS',
      pattern: '',
      is_regex: false,
      priority: 10
    });
  };
  
  const handleSave = async () => {
    try {
      setError(null);
      
      if (!formData.pattern.trim()) {
        setError('Le pattern est obligatoire');
        return;
      }
      
      if (editingId) {
        await axios.put(`${API_URL}/api/partner/admin/keywords/${editingId}`, formData);
        setSuccess('✓ Modifié');
      } else {
        await axios.post(`${API_URL}/api/partner/admin/keywords`, {
          ...formData,
          client_id: PARTNER_CLIENT_ID
        });
        setSuccess('✓ Ajouté');
      }
      
      handleCancel();
      fetchKeywords();
      setTimeout(() => setSuccess(null), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la sauvegarde');
    }
  };
  
  const handleDelete = async (id) => {
    if (!confirm('Supprimer ce mot-clé ?')) return;
    
    try {
      setError(null);
      await axios.delete(`${API_URL}/api/partner/admin/keywords/${id}`);
      setSuccess('✓ Supprimé');
      fetchKeywords();
      setTimeout(() => setSuccess(null), 2000);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur');
    }
  };

  const getTypeInfo = (code) => REQUEST_TYPES.find(t => t.code === code);
  
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header visuel avec gradient */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white shadow-xl">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              🔍 Détection automatique des demandes
            </h1>
            <p className="text-blue-100 mt-2">
              Configurez les mots-clés pour détecter automatiquement les demandes dans le champ RECHERCHE
            </p>
          </div>
          <div className="bg-white/20 backdrop-blur rounded-lg px-4 py-2">
            <div className="text-sm text-blue-100">Total</div>
            <div className="text-3xl font-bold">{keywords.length}</div>
          </div>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
          <span className="text-red-800 font-medium">{error}</span>
        </div>
      )}
      
      {success && (
        <div className="bg-green-50 border-l-4 border-green-500 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
          <span className="text-green-800 font-medium">{success}</span>
        </div>
      )}
      
      {/* Modal d'ajout/édition */}
      {(isAdding || editingId) && (
        <>
          <div className="fixed inset-0 bg-black/50 z-40" onClick={handleCancel}></div>
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-gray-900">
                  {editingId ? '✏️ Modifier' : '➕ Nouveau mot-clé'}
                </h3>
                <button onClick={handleCancel} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                {/* Type */}
                {!editingId && (
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Type de demande
                    </label>
                    <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                      <span className="text-3xl">{getTypeInfo(formData.request_code)?.icon}</span>
                      <div>
                        <div className="font-medium text-gray-900">{getTypeInfo(formData.request_code)?.label}</div>
                        <div className="text-xs text-gray-500">Exemple : {getTypeInfo(formData.request_code)?.example}</div>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Pattern */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Mot-clé à détecter
                  </label>
                  <input
                    type="text"
                    value={formData.pattern}
                    onChange={(e) => setFormData({ ...formData, pattern: e.target.value.toUpperCase() })}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg font-mono"
                    placeholder="Ex: ADRESSE"
                    autoFocus
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Ce mot sera cherché dans le champ RECHERCHE du fichier importé
                  </p>
                </div>
                
                {/* Priorité */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Priorité {formData.priority}
                  </label>
                  <input
                    type="range"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                    className="w-full"
                    min="1"
                    max="20"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Basse</span>
                    <span>Haute (testé en premier)</span>
                  </div>
                </div>
                
                {/* Regex */}
                <label className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100">
                  <input
                    type="checkbox"
                    checked={formData.is_regex}
                    onChange={(e) => setFormData({ ...formData, is_regex: e.target.checked })}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">Mode avancé (Regex)</span>
                    <p className="text-xs text-gray-500">Pour patterns complexes uniquement</p>
                  </div>
                </label>
              </div>
              
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleSave}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors"
                >
                  <Save className="w-4 h-4" />
                  Enregistrer
                </button>
                <button
                  onClick={handleCancel}
                  className="px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-semibold transition-colors"
                >
                  Annuler
                </button>
              </div>
            </div>
          </div>
        </>
      )}
      
      {/* Cartes par type de demande */}
      {loading ? (
        <div className="text-center py-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-gray-600 mt-4 font-medium">Chargement...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {REQUEST_TYPES.map((type) => {
            const typeKeywords = keywords.filter(kw => kw.request_code === type.code);
            const colorClasses = {
              blue: 'from-blue-500 to-blue-600 border-blue-200',
              green: 'from-green-500 to-green-600 border-green-200',
              purple: 'from-purple-500 to-purple-600 border-purple-200',
              indigo: 'from-indigo-500 to-indigo-600 border-indigo-200',
              pink: 'from-pink-500 to-pink-600 border-pink-200'
            };
            
            return (
              <div key={type.code} className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-gray-100 hover:shadow-xl transition-shadow">
                {/* Header coloré */}
                <div className={`bg-gradient-to-r ${colorClasses[type.color]} p-4 text-white`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-4xl">{type.icon}</span>
                      <div>
                        <h3 className="text-xl font-bold">{type.label}</h3>
                        <p className="text-sm text-white/80">Exemple : {type.example}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleAdd(type.code)}
                      className="bg-white/20 hover:bg-white/30 backdrop-blur rounded-lg p-2 transition-colors"
                      title="Ajouter un mot-clé"
                    >
                      <Plus className="w-5 h-5" />
                    </button>
                  </div>
                </div>
                
                {/* Liste des mots-clés */}
                <div className="p-4">
                  {typeKeywords.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <HelpCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">Aucun mot-clé configuré</p>
                      <button
                        onClick={() => handleAdd(type.code)}
                        className="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        + Ajouter le premier
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {typeKeywords
                        .sort((a, b) => b.priority - a.priority)
                        .map((kw) => (
                        <div
                          key={kw.id}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
                        >
                          <div className="flex items-center gap-3 flex-1">
                            <div className="flex items-center gap-1">
                              {kw.priority > 15 ? <ArrowUp className="w-4 h-4 text-red-500" /> : 
                               kw.priority < 8 ? <ArrowDown className="w-4 h-4 text-gray-400" /> : 
                               <span className="w-4 h-4 flex items-center justify-center text-gray-400">·</span>}
                              <span className="text-xs font-bold text-gray-500 w-6">{kw.priority}</span>
                            </div>
                            <div className="flex-1">
                              <div className="font-mono font-bold text-gray-900">{kw.pattern}</div>
                              {kw.is_regex && (
                                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded mt-1 inline-block">
                                  Regex
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={() => handleEdit(kw)}
                              className="p-2 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                              title="Modifier"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(kw.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Supprimer"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {/* Aide visuelle en bas */}
      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 border-2 border-amber-200">
        <div className="flex items-start gap-4">
          <div className="text-4xl">💡</div>
          <div>
            <h4 className="font-bold text-gray-900 mb-2">Comment ça marche ?</h4>
            <div className="text-sm text-gray-700 space-y-1">
              <p>1️⃣ Vous importez un fichier avec <span className="font-mono bg-white px-2 py-0.5 rounded">RECHERCHE = "ADRESSE EMPLOYEUR"</span></p>
              <p>2️⃣ Le système détecte automatiquement : 🏠 Adresse + 💼 Employeur</p>
              <p>3️⃣ Ces demandes apparaissent dans le tableau et dans la fiche de l'enquête</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PartnerKeywordsAdmin;

