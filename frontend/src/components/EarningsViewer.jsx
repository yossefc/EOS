import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  DollarSign, Calendar, RefreshCw, AlertCircle, CheckSquare, FileDown, 
  AlertTriangle, BarChart2, TrendingUp, Filter, ArrowDownCircle, ArrowUpCircle
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const EnhancedEarningsViewer = ({ enqueteurId }) => {
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState(new Date().getMonth() + 1); // Mois actuel (1-12)
  const [year, setYear] = useState(new Date().getFullYear()); // Année actuelle
  const [viewAll, setViewAll] = useState(false);
  const [activeView, setActiveView] = useState('summary'); // 'summary' ou 'details'
  const [csvDownloading, setCsvDownloading] = useState(false);
  // Historique de revenus (pour le graphique)
  const [revenueHistory, setRevenueHistory] = useState([]);

  useEffect(() => {
    if (enqueteurId) {
      fetchEarnings();
      fetchEarningsHistory();
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

  // Nouvelle fonction pour récupérer l'historique des revenus sur 6 mois
  const fetchEarningsHistory = async () => {
    try {
      const now = new Date();
      const history = [];
      
      // Récupérer les données des 6 derniers mois
      for (let i = 0; i < 6; i++) {
        const targetDate = new Date(now);
        targetDate.setMonth(now.getMonth() - i);
        
        const month = targetDate.getMonth() + 1;
        const year = targetDate.getFullYear();
        
        const url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}?month=${month}&year=${year}`;
        
        try {
          const response = await axios.get(url);
          if (response.data.success) {
            history.push({
              month: month,
              year: year,
              label: getMonthName(month) + ' ' + year,
              total: response.data.data.total_gagne || 0,
              count: response.data.data.nombre_enquetes || 0
            });
          }
        } catch (e) {
          // Continuer même si une requête échoue
          history.push({
            month: month,
            year: year,
            label: getMonthName(month) + ' ' + year,
            total: 0,
            count: 0
          });
        }
      }
      
      // Trier du plus ancien au plus récent
      history.sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year;
        return a.month - b.month;
      });
      
      setRevenueHistory(history);
      
    } catch (error) {
      console.error("Erreur lors de la récupération de l'historique:", error);
    }
  };

  // Fonction pour exporter les données en CSV
  const handleExportCSV = () => {
    if (!earnings || !earnings.facturations) return;
    
    setCsvDownloading(true);
    
    try {
      // Créer les entêtes du CSV
      const headers = ["Date", "N° Dossier", "Éléments trouvés", "Montant", "Statut"];
      
      // Créer les lignes de données
      const rows = earnings.facturations.map(facturation => [
        formatDate(facturation.created_at),
        facturation.donnee_id,
        facturation.tarif_enqueteur_code || '-',
        facturation.resultat_enqueteur_montant.toFixed(2),
        facturation.paye ? 'Payé' : 'En attente'
      ]);
      
      // Ajouter une ligne de total
      rows.push(['', '', 'TOTAL', earnings.total_gagne.toFixed(2), '']);
      
      // Convertir en CSV
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');
      
      // Créer un blob et un lien de téléchargement
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      // Configurer le lien de téléchargement
      const period = viewAll ? 'tous' : `${getMonthName(month)}-${year}`;
      link.setAttribute('href', url);
      link.setAttribute('download', `revenus-${period}.csv`);
      document.body.appendChild(link);
      
      // Déclencher le téléchargement
      link.click();
      
      // Nettoyer
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error("Erreur lors de l'export CSV:", error);
      setError("Erreur lors de l'export CSV");
    } finally {
      setCsvDownloading(false);
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

  // Obtenir le nom du mois en français
  const getMonthName = (monthNumber) => {
    const monthNames = [
      'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ];
    return monthNames[monthNumber - 1];
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

  // Rendus des différentes sections
  const renderHeader = () => (
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <DollarSign className="w-6 h-6 text-green-500" />
        Mes Revenus
      </h2>
      <div className="flex gap-2">
        <button
          onClick={() => setActiveView(activeView === 'summary' ? 'details' : 'summary')}
          className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200"
        >
          {activeView === 'summary' ? (
            <>
              <Table className="w-4 h-4" />
              <span>Voir détails</span>
            </>
          ) : (
            <>
              <BarChart2 className="w-4 h-4" />
              <span>Voir résumé</span>
            </>
          )}
        </button>
        <button
          onClick={fetchEarnings}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Actualiser</span>
        </button>
      </div>
    </div>
  );

  const renderFilters = () => (
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
  );

  const renderSummaryCards = () => (
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
  );

  const renderRevenueChart = () => {
    // Calcul de la hauteur maximale des barres (pour l'échelle)
    const maxRevenue = Math.max(...revenueHistory.map(item => item.total), 10);
    
    return (
      <div className="bg-white border rounded-lg p-4 mb-6">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-500" />
          Évolution de vos revenus sur 6 mois
        </h3>
        
        <div className="h-64 flex items-end justify-between gap-2 mt-4 pl-8 pb-8 relative">
          {/* Axe Y (montants) */}
          <div className="absolute left-0 top-0 bottom-8 w-8 flex flex-col justify-between text-xs text-gray-500">
            <span>{maxRevenue.toFixed(0)}€</span>
            <span>{(maxRevenue/2).toFixed(0)}€</span>
            <span>0€</span>
          </div>
          
          {/* Lignes horizontales de la grille */}
          <div className="absolute left-8 right-0 top-0 bottom-8 flex flex-col justify-between">
            <div className="border-t border-gray-100 w-full"></div>
            <div className="border-t border-gray-100 w-full"></div>
            <div className="border-t border-gray-100 w-full"></div>
          </div>
          
          {/* Barres du graphique */}
          {revenueHistory.map((item, index) => (
            <div key={index} className="flex flex-col items-center gap-1 flex-1">
              <div className="relative w-full flex justify-center">
                <div 
                  className="w-16 bg-blue-500 rounded-t-md transition-all duration-500 ease-in-out"
                  style={{ 
                    height: `${(item.total / maxRevenue) * 100}%`,
                    minHeight: item.total > 0 ? '4px' : '0px'
                  }}
                ></div>
              </div>
              <div className="text-xs font-medium -rotate-45 origin-top-left translate-y-6 translate-x-3">
                {item.label}
              </div>
            </div>
          ))}
          
          {/* Axe X (mois) */}
          <div className="absolute left-8 right-0 bottom-0 h-8 border-t border-gray-300"></div>
        </div>
        
        {/* Légende */}
        <div className="flex justify-center mt-8 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 rounded-sm"></div>
            <span>Revenus mensuels</span>
          </div>
        </div>
      </div>
    );
  };

  const renderFacturationsTable = () => (
    <div className="bg-white border rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-gray-50 border-b flex justify-between items-center">
        <h3 className="font-medium">Détail des enquêtes</h3>
        <button 
          onClick={handleExportCSV}
          className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800"
          disabled={csvDownloading}
        >
          {csvDownloading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Exportation...</span>
            </>
          ) : (
            <>
              <FileDown className="w-4 h-4" />
              <span>Exporter en CSV</span>
            </>
          )}
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
          <tfoot className="bg-gray-50">
            <tr>
              <td colSpan="3" className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                Total
              </td>
              <td className="px-4 py-3 text-right text-sm font-medium text-gray-900">
                {earnings.total_gagne.toFixed(2)} €
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );

  const renderEmptyState = () => (
    <div className="bg-gray-50 border rounded-lg p-8 text-center">
      <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
      <p className="text-gray-600 mb-2">Aucune facturation trouvée pour cette période</p>
      <p className="text-sm text-gray-500">Essayez de modifier les filtres ou de sélectionner "Toutes les périodes"</p>
    </div>
  );

  const renderNonNumericalStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-base font-medium text-gray-900 mb-3">Performance par type d'enquête</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse et téléphone (AT)</span>
              <span className="font-medium">12 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{width: '75%'}}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse, téléphone et banque (ATB)</span>
              <span className="font-medium">8 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{width: '50%'}}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse et employeur (AE)</span>
              <span className="font-medium">5 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{width: '30%'}}></div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-white border rounded-lg p-4">
        <h3 className="text-base font-medium text-gray-900 mb-3">Répartition par résultat</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Positif (P)</span>
              <span className="font-medium">18 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-green-500 h-2 rounded-full" style={{width: '80%'}}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Négatif (N)</span>
              <span className="font-medium">5 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-red-500 h-2 rounded-full" style={{width: '20%'}}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Autres résultats</span>
              <span className="font-medium">2 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-gray-500 h-2 rounded-full" style={{width: '10%'}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Rendu principal
  return (
    <div className="space-y-4">
      {/* En-tête avec titre et bouton d'actualisation */}
      {renderHeader()}

      {/* Message d'erreur */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Filtres de date */}
      {renderFilters()}

      {/* Affichage du chargement */}
      {loading ? (
        <div className="text-center p-8 bg-white rounded-lg border">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-4" />
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      ) : earnings ? (
        <>
          {/* Vue résumé avec graphiques */}
          {activeView === 'summary' ? (
            <>
              {/* Cartes de résumé */}
              {renderSummaryCards()}
              
              {/* Graphique d'évolution */}
              {renderRevenueChart()}
              
              {/* Statistiques non numériques */}
              {renderNonNumericalStats()}
              
              {/* Appel à action pour voir plus de détails */}
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 text-center">
                <p className="text-blue-700 mb-2">Vous voulez voir le détail de toutes vos enquêtes?</p>
                <button
                  onClick={() => setActiveView('details')}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 inline-flex items-center gap-2"
                >
                  <Table className="w-4 h-4" />
                  Voir le tableau détaillé
                </button>
              </div>
            </>
          ) : (
            <>
              {/* Vue détaillée avec tableau */}
              {/* Mini résumé en haut de la vue détaillée */}
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <DollarSign className="w-5 h-5 text-blue-500" />
                  <div>
                    <div className="text-sm font-medium">Total pour cette période</div>
                    <div className="text-lg font-bold text-blue-700">{earnings.total_gagne.toFixed(2)} €</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div className="text-xs text-gray-600">Nombre d'enquêtes</div>
                    <div className="text-sm font-medium">{earnings.nombre_enquetes}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-600">À recevoir</div>
                    <div className="text-sm font-medium">{earnings.total_a_payer.toFixed(2)} €</div>
                  </div>
                </div>
              </div>
              
              {/* Liste des enquêtes/facturations */}
              {earnings.facturations.length > 0 ? renderFacturationsTable() : renderEmptyState()}
            </>
          )}
        </>
      ) : (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-lg">
          <p>Aucune donnée disponible. Veuillez actualiser.</p>
        </div>
      )}
      
      {/* Guide d'information */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-6">
        <h3 className="font-medium text-gray-900 mb-2">Comment suis-je rémunéré?</h3>
        <p className="text-sm text-gray-600 mb-3">
          Votre rémunération est calculée par enquête traitée, selon le barème suivant:
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 text-left">Code</th>
                <th className="px-4 py-2 text-left">Description</th>
                <th className="px-4 py-2 text-right">Montant</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-4 py-2">A</td>
                <td className="px-4 py-2">Adresse seule</td>
                <td className="px-4 py-2 text-right">5.60 €</td>
              </tr>
              <tr>
                <td className="px-4 py-2">AT</td>
                <td className="px-4 py-2">Adresse et téléphone</td>
                <td className="px-4 py-2 text-right">15.40 €</td>
              </tr>
              <tr>
                <td className="px-4 py-2">ATB</td>
                <td className="px-4 py-2">Adresse, téléphone et banque</td>
                <td className="px-4 py-2 text-right">16.80 €</td>
              </tr>
              <tr>
                <td className="px-4 py-2">D</td>
                <td className="px-4 py-2">Décès</td>
                <td className="px-4 py-2 text-right">7.00 €</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-600 mt-3">
          Les paiements sont effectués chaque mois pour toutes les enquêtes traitées le mois précédent.
        </p>
      </div>
    </div>
  );
};

export default EnhancedEarningsViewer;