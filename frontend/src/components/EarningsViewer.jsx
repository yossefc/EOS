import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import {
  DollarSign, Calendar, RefreshCw, AlertCircle, CheckSquare, FileDown,
  AlertTriangle, BarChart2, TrendingUp, Table
} from 'lucide-react';
import PropTypes from 'prop-types';
import config from '../config';

const API_URL = config.API_URL;

/**
 * Enhanced Earnings Viewer Component
 * 
 * Displays detailed earnings information for an investigator, including:
 * - Monthly and yearly earnings overview
 * - Historical earnings visualization
 * - Detailed transaction list with CSV export
 * - Filtering and period selection
 * 
 * @param {Object} props - Component props
 * @param {string|number} props.enqueteurId - ID of the investigator
 */
const EnhancedEarningsViewer = ({ enqueteurId }) => {
  // State management
  const [earnings, setEarnings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [month, setMonth] = useState(new Date().getMonth() + 1); // Current month (1-12)
  const [year, setYear] = useState(new Date().getFullYear()); // Current year
  const [viewAll, setViewAll] = useState(false);
  const [activeView, setActiveView] = useState('summary'); // 'summary', 'details', or 'monthly-stats'
  const [csvDownloading, setCsvDownloading] = useState(false);
  // Revenue history for chart visualization
  const [revenueHistory, setRevenueHistory] = useState([]);
  // Monthly statistics
  const [monthsPeriod, setMonthsPeriod] = useState(12); // 12 or 24 months
  const [monthlyStats, setMonthlyStats] = useState([]);
  const [loadingMonthlyStats, setLoadingMonthlyStats] = useState(false);

  // MULTI-CLIENT: États pour les clients
  const [clients, setClients] = useState([]);
  const [selectedClientId, setSelectedClientId] = useState(null);
  const [loadingClients, setLoadingClients] = useState(true);

  /**
   * Fetch earnings data based on selected period
   */
  const fetchEarnings = async () => {
    try {
      setLoading(true);
      setError(null);

      let url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}`;

      // Add date filtering parameters if viewAll is false
      if (!viewAll) {
        url += `?month=${month}&year=${year}`;
      } else {
        url += '?';
      }

      // MULTI-CLIENT: Ajouter le filtre client si sélectionné
      if (selectedClientId) {
        url += `${url.includes('?') && !url.endsWith('?') ? '&' : ''}client_id=${selectedClientId}`;
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

  /**
   * Fetch earnings history for the last 6 months for chart visualization
   */
  const fetchEarningsHistory = async () => {
    try {
      const now = new Date();
      const history = [];

      // Get data for the last 6 months
      for (let i = 0; i < 6; i++) {
        const targetDate = new Date(now);
        targetDate.setMonth(now.getMonth() - i);

        const month = targetDate.getMonth() + 1;
        const year = targetDate.getFullYear();

        // MULTI-CLIENT: Ajouter le filtre client si sélectionné
        let url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}?month=${month}&year=${year}`;
        if (selectedClientId) {
          url += `&client_id=${selectedClientId}`;
        }

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
        } catch (error) {
          console.log(error)
          // Continue even if one request fails
          history.push({
            month: month,
            year: year,
            label: getMonthName(month) + ' ' + year,
            total: 0,
            count: 0
          });
        }
      }

      // Sort from oldest to newest
      history.sort((a, b) => {
        if (a.year !== b.year) return a.year - b.year;
        return a.month - b.month;
      });

      setRevenueHistory(history);

    } catch (error) {
      console.error("Erreur lors de la récupération de l'historique:", error);
    }
  };

  /**
   * Fetch monthly statistics for the selected period (12 or 24 months)
   */
  const fetchMonthlyStats = async () => {
    try {
      setLoadingMonthlyStats(true);
      const now = new Date();
      const stats = [];

      // Get data for the last N months
      for (let i = monthsPeriod - 1; i >= 0; i--) {
        const targetDate = new Date(now);
        targetDate.setMonth(now.getMonth() - i);

        const month = targetDate.getMonth() + 1;
        const year = targetDate.getFullYear();

        // Build URL with client filter if selected
        let url = `${API_URL}/api/facturation/enqueteur/${enqueteurId}?month=${month}\u0026year=${year}`;
        if (selectedClientId) {
          url += `\u0026client_id=${selectedClientId}`;
        }

        try {
          const response = await axios.get(url);
          if (response.data.success) {
            stats.push({
              month: month,
              year: year,
              label: getMonthName(month) + ' ' + year,
              total_gagne: response.data.data.total_gagne || 0,
              total_paye: response.data.data.total_paye || 0,
              total_a_payer: response.data.data.total_a_payer || 0,
              nombre_enquetes: response.data.data.nombre_enquetes || 0
            });
          }
        } catch (error) {
          console.log(`Erreur pour ${getMonthName(month)} ${year}:`, error);
          // Add empty entry for this month
          stats.push({
            month: month,
            year: year,
            label: getMonthName(month) + ' ' + year,
            total_gagne: 0,
            total_paye: 0,
            total_a_payer: 0,
            nombre_enquetes: 0
          });
        }
      }

      setMonthlyStats(stats);

    } catch (error) {
      console.error("Erreur lors de la récupération des statistiques mensuelles:", error);
    } finally {
      setLoadingMonthlyStats(false);
    }
  };

  /**
   * MULTI-CLIENT: Récupérer la liste des clients
   */
  const fetchClients = async () => {
    try {
      setLoadingClients(true);
      const response = await axios.get(`${API_URL}/api/clients`);
      if (response.data.success) {
        setClients(response.data.clients);
        // Sélectionner "Tous" par défaut (null = tous les clients)
        setSelectedClientId(null);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération des clients:", error);
    } finally {
      setLoadingClients(false);
    }
  };

  // Fetch clients on mount
  useEffect(() => {
    fetchClients();
  }, []);

  // Fetch data when component mounts or when filters change
  useEffect(() => {
    if (enqueteurId && !loadingClients) {
      fetchEarnings();
      fetchEarningsHistory();
    }
  }, [enqueteurId, month, year, viewAll, selectedClientId, loadingClients]);

  // Fetch monthly stats when switching to monthly-stats view or when period/client changes
  useEffect(() => {
    if (enqueteurId && activeView === 'monthly-stats' && !loadingClients) {
      fetchMonthlyStats();
    }
  }, [enqueteurId, activeView, monthsPeriod, selectedClientId, loadingClients]);


  /**
   * Export earnings data as CSV
   */
  const handleExportCSV = () => {
    if (!earnings || !earnings.facturations) return;

    setCsvDownloading(true);

    try {
      // Create CSV headers
      const headers = ["Date", "N° Dossier", "Éléments trouvés", "Montant", "Statut"];

      // Create data rows
      const rows = earnings.facturations.map(facturation => [
        formatDate(facturation.created_at),
        facturation.donnee_id,
        facturation.tarif_enqueteur_code || '-',
        facturation.resultat_enqueteur_montant.toFixed(2),
        facturation.paye ? 'Payé' : 'En attente'
      ]);

      // Add total row
      rows.push(['', '', 'TOTAL', earnings.total_gagne.toFixed(2), '']);

      // Convert to CSV content
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');

      // Configure the download link
      const period = viewAll ? 'tous' : `${getMonthName(month)}-${year}`;
      link.setAttribute('href', url);
      link.setAttribute('download', `revenus-${period}.csv`);
      document.body.appendChild(link);

      // Trigger download
      link.click();

      // Clean up
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Erreur lors de l'export CSV:", error);
      setError("Erreur lors de l'export CSV");
    } finally {
      setCsvDownloading(false);
    }
  };

  /**
   * Format a date string to French format (DD/MM/YYYY)
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-';

    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  /**
   * Get month name in French
   */
  const getMonthName = (monthNumber) => {
    const monthNames = [
      'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
      'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
    ];
    return monthNames[monthNumber - 1];
  };

  // Generate array of months for select dropdown
  const months = useMemo(() => [
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
  ], []);

  // Generate array of years (current year and 2 years back)
  const currentYear = new Date().getFullYear();
  const years = useMemo(() =>
    Array.from({ length: 3 }, (_, i) => currentYear - i),
    [currentYear]
  );

  // UI Section Renderers
  const renderHeader = () => (
    <div className="flex justify-between items-center mb-4">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <DollarSign className="w-6 h-6 text-green-500" />
        Mes Revenus
      </h2>
      <div className="flex gap-2">
        {activeView !== 'monthly-stats' && (
          <button
            onClick={() => setActiveView(activeView === 'summary' ? 'details' : 'summary')}
            className="flex items-center gap-1 px-3 py-1.5 bg-gray-100 text-gray-800 rounded-md hover:bg-gray-200 transition-colors">
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
        )}
        <button
          onClick={() => setActiveView(activeView === 'monthly-stats' ? 'summary' : 'monthly-stats')}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-md transition-colors ${activeView === 'monthly-stats'
            ? 'bg-green-500 text-white hover:bg-green-600'
            : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
            }`}>
          <BarChart2 className="w-4 h-4" />
          <span>Statistiques</span>
        </button>
        <button
          onClick={fetchEarnings}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors">
          <RefreshCw className="w-4 h-4" />
          <span>Actualiser</span>
        </button>
      </div>
    </div>
  );

  const renderFilters = () => (
    <div className="flex items-center gap-4 mb-6 bg-gray-50 p-3 rounded-lg flex-wrap">
      {/* MULTI-CLIENT: Sélecteur de client */}
      {!loadingClients && clients.length > 1 && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Client :</span>
          <select
            value={selectedClientId || ''}
            onChange={(e) => setSelectedClientId(e.target.value ? parseInt(e.target.value) : null)}
            className="py-1 px-2 border rounded-md text-sm"
          >
            <option value="">Tous</option>
            {clients.map(client => (
              <option key={client.id} value={client.id}>
                {client.nom}
              </option>
            ))}
          </select>
        </div>
      )}

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
      <div className="bg-green-50 border border-green-100 rounded-lg p-4 transition-all hover:shadow-md">
        <div className="text-green-600 text-sm font-medium mb-1">Total gagné</div>
        <div className="text-2xl font-bold text-green-700">{earnings.total_gagne.toFixed(2)} €</div>
        <div className="text-green-600 text-xs">{earnings.nombre_enquetes} enquêtes</div>
      </div>

      <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 transition-all hover:shadow-md">
        <div className="text-blue-600 text-sm font-medium mb-1">Déjà payé</div>
        <div className="text-2xl font-bold text-blue-700">{earnings.total_paye.toFixed(2)} €</div>
      </div>

      <div className="bg-amber-50 border border-amber-100 rounded-lg p-4 transition-all hover:shadow-md">
        <div className="text-amber-600 text-sm font-medium mb-1">Reste à payer</div>
        <div className="text-2xl font-bold text-amber-700">{earnings.total_a_payer.toFixed(2)} €</div>
      </div>
    </div>
  );

  const renderRevenueChart = () => {
    // Calculate maximum height for bars (for scaling)
    const maxRevenue = Math.max(...revenueHistory.map(item => item.total), 10);

    return (
      <div className="bg-white border rounded-lg p-4 mb-6 hover:shadow-md transition-all">
        <h3 className="font-medium mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-500" />
          Évolution de vos revenus sur 6 mois
        </h3>

        <div className="h-64 flex items-end justify-between gap-2 mt-4 pl-8 pb-8 relative">
          {/* Y-axis (amounts) */}
          <div className="absolute left-0 top-0 bottom-8 w-8 flex flex-col justify-between text-xs text-gray-500">
            <span>{maxRevenue.toFixed(0)}€</span>
            <span>{(maxRevenue / 2).toFixed(0)}€</span>
            <span>0€</span>
          </div>

          {/* Horizontal grid lines */}
          <div className="absolute left-8 right-0 top-0 bottom-8 flex flex-col justify-between">
            <div className="border-t border-gray-100 w-full"></div>
            <div className="border-t border-gray-100 w-full"></div>
            <div className="border-t border-gray-100 w-full"></div>
          </div>

          {/* Chart bars */}
          {revenueHistory.map((item, index) => (
            <div key={index} className="flex flex-col items-center gap-1 flex-1">
              <div className="relative w-full flex justify-center">
                <div
                  className="w-16 bg-blue-500 rounded-t-md transition-all duration-500 ease-in-out hover:bg-blue-600"
                  style={{
                    height: `${(item.total / maxRevenue) * 100}%`,
                    minHeight: item.total > 0 ? '4px' : '0px'
                  }}
                  title={`${item.label}: ${item.total.toFixed(2)}€`}
                ></div>
              </div>
              <div className="text-xs font-medium -rotate-45 origin-top-left translate-y-6 translate-x-3">
                {item.label}
              </div>
            </div>
          ))}

          {/* X-axis (months) */}
          <div className="absolute left-8 right-0 bottom-0 h-8 border-t border-gray-300"></div>
        </div>

        {/* Legend */}
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
    <div className="bg-white border rounded-lg overflow-hidden hover:shadow-md transition-all">
      <div className="px-4 py-3 bg-gray-50 border-b flex justify-between items-center">
        <h3 className="font-medium">Détail des enquêtes</h3>
        <button
          onClick={handleExportCSV}
          className="text-sm flex items-center gap-1 text-blue-600 hover:text-blue-800 transition-colors"
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
              <tr key={facturation.id} className="hover:bg-gray-50 transition-colors">
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
      <p className="text-sm text-gray-500">Essayez de modifier les filtres ou de sélectionner &quot;Toutes les périodes&quot;</p>
    </div>
  );

  const renderMonthlyStatsTable = () => {
    const totals = monthlyStats.reduce((acc, stat) => ({
      nombre_enquetes: acc.nombre_enquetes + stat.nombre_enquetes,
      total_gagne: acc.total_gagne + stat.total_gagne,
      total_paye: acc.total_paye + stat.total_paye,
      total_a_payer: acc.total_a_payer + stat.total_a_payer
    }), { nombre_enquetes: 0, total_gagne: 0, total_paye: 0, total_a_payer: 0 });

    return (
      <div className="bg-white border rounded-lg overflow-hidden hover:shadow-md transition-all">
        <div className="px-4 py-3 bg-gray-50 border-b flex justify-between items-center">
          <h3 className="font-medium flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-blue-500" />
            Statistiques des {monthsPeriod} derniers mois
          </h3>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Période:</span>
            <select
              value={monthsPeriod}
              onChange={(e) => setMonthsPeriod(parseInt(e.target.value))}
              className="py-1 px-2 border rounded-md text-sm">
              <option value={1}>1 mois</option>
              <option value={12}>12 mois</option>
              <option value={24}>24 mois</option>
            </select>
          </div>
        </div>

        {loadingMonthlyStats ? (
          <div className="text-center p-8">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-4" />
            <p className="text-gray-600">Chargement des statistiques...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Mois
                  </th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                    Nb enquêtes
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Total gagné
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Total payé
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                    Reste à payer
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {monthlyStats.map((stat, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                      {stat.label}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-center text-gray-600">
                      {stat.nombre_enquetes}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium text-green-700">
                      {stat.total_gagne.toFixed(2)} €
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-blue-700">
                      {stat.total_paye.toFixed(2)} €
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-right text-amber-700">
                      {stat.total_a_payer.toFixed(2)} €
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50 border-t-2 border-gray-300">
                <tr>
                  <td className="px-4 py-3 text-left text-sm font-bold text-gray-900">
                    TOTAL
                  </td>
                  <td className="px-4 py-3 text-center text-sm font-bold text-gray-900">
                    {totals.nombre_enquetes}
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-green-700">
                    {totals.total_gagne.toFixed(2)} €
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-blue-700">
                    {totals.total_paye.toFixed(2)} €
                  </td>
                  <td className="px-4 py-3 text-right text-sm font-bold text-amber-700">
                    {totals.total_a_payer.toFixed(2)} €
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </div>
    );
  };


  const renderNonNumericalStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div className="bg-white border rounded-lg p-4 hover:shadow-md transition-all">
        <h3 className="text-base font-medium text-gray-900 mb-3">Performance par type d&apos;enquête</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse et téléphone (AT)</span>
              <span className="font-medium">12 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '75%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse, téléphone et banque (ATB)</span>
              <span className="font-medium">8 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '50%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Adresse et employeur (AE)</span>
              <span className="font-medium">5 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '30%' }}></div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 hover:shadow-md transition-all">
        <h3 className="text-base font-medium text-gray-900 mb-3">Répartition par résultat</h3>
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Positif (P)</span>
              <span className="font-medium">18 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '80%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Négatif (N)</span>
              <span className="font-medium">5 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: '20%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Autres résultats</span>
              <span className="font-medium">2 enquêtes</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div className="bg-gray-500 h-2 rounded-full" style={{ width: '10%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Main render
  return (
    <div className="space-y-4">
      {/* Header with title and refresh button */}
      {renderHeader()}

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Date filters */}
      {renderFilters()}

      {/* Loading state */}
      {loading ? (
        <div className="text-center p-8 bg-white rounded-lg border">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-500 mb-4" />
          <p className="text-gray-600">Chargement des données...</p>
        </div>
      ) : earnings ? (
        <>
          {/* Summary view with charts */}
          {activeView === 'summary' ? (
            <>
              {/* Summary cards */}
              {renderSummaryCards()}

              {/* Evolution chart */}
              {renderRevenueChart()}

              {/* Non-numerical statistics */}
              {renderNonNumericalStats()}

              {/* Call to action for more details */}
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 text-center hover:shadow-md transition-all">
                <p className="text-blue-700 mb-2">Vous voulez voir le détail de toutes vos enquêtes?</p>
                <button
                  onClick={() => setActiveView('details')}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
                >
                  <Table className="w-4 h-4" />
                  Voir le tableau détaillé
                </button>
              </div>
            </>
          ) : activeView === 'monthly-stats' ? (
            <>
              {/* Monthly Statistics View */}
              {renderMonthlyStatsTable()}
            </>
          ) : (
            <>
              {/* Detailed view with table */}
              {/* Mini summary at the top of detailed view */}
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4 flex justify-between items-center hover:shadow-md transition-all">
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

              {/* Billing list/table */}
              {earnings.facturations.length > 0 ? renderFacturationsTable() : renderEmptyState()}
            </>
          )}
        </>
      ) : (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 p-4 rounded-lg">
          <p>Aucune donnée disponible. Veuillez actualiser.</p>
        </div>
      )}

      {/* Information guide */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-6 hover:shadow-md transition-all">
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

// Define prop types for better documentation and type checking
EnhancedEarningsViewer.propTypes = {
  enqueteurId: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number
  ]).isRequired
};

export default EnhancedEarningsViewer;