import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { DollarSign, Calendar, RefreshCw, AlertCircle, CheckSquare, FileDown, AlertTriangle } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EarningsViewer = ({ enqueteurId }) => {
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState(new Date().getMonth() + 1); // Mois actuel (1-12)
  const [year, setYear] = useState(new Date().getFullYear()); // Année actuelle
  const [viewAll, setViewAll] = useState(false);

  useEffect(() => {
    if (enqueteurId) {
      fetchEarnings();
    }
  }, [enqueteurId, month, year, viewAll]);

  const fetchEarnings = async () => {
    try {
      setLoading(true);
      setError(null);

      let url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}`;
      
      // Ajouter les paramètres de filtrage par date si viewAll est false
      if (!viewAll) {
        url += `?month=${month}&year=${year}`;
      }

      const response = await axios.get(url);

      if (response.data.success) {
        setEarnings(response.data.data);
      } else {
        throw new Error(response.data.error || "Erreur lors de la récupération des gains");
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des gains:", error);
      setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
    } finally {
      setLoading(false);
    }
  };

  // Formater une date au format français
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Générer un array des mois
  const months = [
    { value: 1, label: 'Janvier' },
    { value: 2, label: 'Février' },
    { value: 3, label: 'Mars' },
    { value: 4, label: 'Avril' },
    { value: 5, label: 'Mai' },
    { value: 6, label: 'Juin' },
    { value: 7, label: 'Juillet' },
    { value: 8, label: 'Août' },
    { value: 9, label: 'Septembre' },
    { value: 10, label: 'Octobre' },
    { value: 11, label: 'Novembre' },
    { value: 12, label: 'Décembre' }
  ];

  // Générer un array d'années (de l'année actuelle à 2 ans en arrière)
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 3 }, (_, i) => currentYear - i);

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <DollarSign className="w-6 h-6 text-green-500" />
          Mes Revenus
        </h2>
        <button
          onClick={fetchEarnings}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Actualiser</span>
        </button>
      </div>

      {/* Filtres de date */}
      <div className="flex items-center gap-4 mb-6 bg-gray-50 p-3 rounded-lg">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-600">Période :</span>
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={viewAll}
              onChange={(e) => setViewAll(e.target.checked)}
              className="rounded text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Toutes les périodes</span>
          </label>
          
          {!viewAll && (
            <>
              <select
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
                className="py-1 px-2 border rounded-md text-sm"
                disabled={viewAll}
              >
                {months.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
              
              <select
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value))}
                className="py-1 px-2 border rounded-md text-sm"
                disabled={viewAll}
              >
                {years.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>
      </div>

      {/* Message d'erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Affichage du chargement */}
      {loading ? (
        <div className="text-center p-8">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-4" />
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      ) : earnings ? (
        <>
          {/* Cartes de résumé */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 border border-green-100 rounded-lg p-4">
              <div className="text-green-600 text-sm font-medium mb-1">Total gagné</div>
              <div className="text-2xl font-bold text-green-700">{earnings.total_gagne.toFixed(2)} €</div>
              <div className="text-green-600 text-xs">{earnings.nombre_enquetes} enquêtes</div>
            </div>
            
            <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
              <div className="text-blue-600 text-sm font-medium mb-1">Déjà payé</div>
              <div className="text-2xl font-bold text-blue-700">{earnings.total_paye.toFixed(2)} €</div>
            </div>
            
            <div className="bg-amber-50 border border-amber-100 rounded-lg p-4">
              <div className="text-amber-600 text-sm font-medium mb-1">Reste à payer</div>
              <div className="text-2xl font-bold text-amber-700">{earnings.total_a_payer.toFixed(2)} €</div>
            </div>
          </div>

          {/* Liste des enquêtes/facturations */}
          {earnings.facturations.length > 0 ? (
            <div className="bg-white border rounded-lg overflow-hidden">
              <div className="px-4 py-3 bg-gray-50 border-b flex justify-between items-center">
                <h3 className="font-medium">Détail des enquêtes</h3>
                <button 
                  className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
                  title="Télécharger en CSV"
                >
                  <FileDown className="w-4 h-4" />
                  <span>Exporter</span>
                </button>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Date
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        N° Dossier
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Éléments trouvés
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                        Montant
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                        Statut
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {earnings.facturations.map((facturation) => (
                      <tr key={facturation.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(facturation.created_at)}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                          {facturation.donnee_id}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                          {facturation.tarif_enqueteur_code || '-'}
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium">
                          {facturation.resultat_enqueteur_montant.toFixed(2)} €
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                          {facturation.paye ? (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              <CheckSquare className="w-3 h-3 mr-1" />
                              Payé
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
                              En attente
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 border rounded-lg p-8 text-center">
              <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
              <p className="text-gray-600 mb-2">Aucune facturation trouvée pour cette période</p>
              <p className="text-sm text-gray-500">Essayez de modifier les filtres ou de sélectionner "Toutes les périodes"</p>
            </div>
          )}
        </>
      ) : (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-lg">
          <p>Aucune donnée disponible. Veuillez actualiser.</p>
        </div>
      )}
    </div>
  );
};

export default EarningsViewer;