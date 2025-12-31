import { useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import {
    BarChart2, RefreshCw, AlertCircle,
    Download, DollarSign, TrendingUp, FileText, Users
} from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    ResponsiveContainer, PieChart as RPieChart, Pie, Cell, LineChart, Line,
    AreaChart, Area
} from 'recharts';
import config from '../config';

const API_URL = config.API_URL;

// Couleurs pour les graphiques
const COLORS = {
    facture: '#3B82F6',   // Bleu
    enqueteur: '#10B981', // Vert
    marge: '#6366F1',     // Indigo
    paye: '#F59E0B',      // Ambre
    impaye: '#EF4444'     // Rouge
};

const FinancialReports = () => {
    const [periodeStats, setPeriodeStats] = useState([]);
    const [tarifStats, setTarifStats] = useState([]);
    const [enqueteurStats, setEnqueteurStats] = useState([]);
    const [globalStats, setGlobalStats] = useState(null);
    const [statsEOS, setStatsEOS] = useState(null);
    const [statsPartner, setStatsPartner] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');

    // Période sélectionnée pour les filtres
    const [selectedPeriod, setSelectedPeriod] = useState('12months');

    // MULTI-CLIENT: États pour les clients
    const [clients, setClients] = useState([]);
    const [selectedClientId, setSelectedClientId] = useState(null);
    const [loadingClients, setLoadingClients] = useState(true);

    // État pour l'actualisation automatique
    const [autoRefresh, setAutoRefresh] = useState(false);

    // MULTI-CLIENT: Récupérer la liste des clients
    const fetchClients = useCallback(async () => {
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
    }, []);

    // Fonction pour récupérer toutes les données
    const fetchAllData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // 📊 Récupérer les statistiques par période (1, 12 ou 24 mois)
            let periodCount;
            if (selectedPeriod === '1month') periodCount = 1;
            else if (selectedPeriod === '12months') periodCount = 12;
            else if (selectedPeriod === '24months') periodCount = 24;
            else periodCount = 12; // Fallback pour 'current' ou autre (à adapter selon besoin réel)
            const clientParam = selectedClientId ? `&client_id=${selectedClientId}` : '';
            const periodRes = await axios.get(`${API_URL}/api/paiement/stats/periodes?mois=${periodCount}${clientParam}`);

            if (periodRes.data.success) {
                setPeriodeStats(periodRes.data.data);
            }

            // 📈 Récupérer les statistiques globales
            const globalRes = await axios.get(`${API_URL}/api/tarification/stats/global${selectedClientId ? `?client_id=${selectedClientId}` : ''}`);

            if (globalRes.data.success) {
                setGlobalStats(globalRes.data.data);
            }

            // 📊 Si "Tous les clients" est sélectionné, récupérer aussi EOS et PARTNER séparément
            if (!selectedClientId && clients.length > 0) {
                const clientEOS = clients.find(c => c.code === 'EOS');
                const clientPartner = clients.find(c => c.code !== 'EOS');

                if (clientEOS) {
                    const eosRes = await axios.get(`${API_URL}/api/tarification/stats/global?client_id=${clientEOS.id}`);
                    if (eosRes.data.success) {
                        setStatsEOS(eosRes.data.data);
                    }
                }

                if (clientPartner) {
                    const partnerRes = await axios.get(`${API_URL}/api/tarification/stats/global?client_id=${clientPartner.id}`);
                    if (partnerRes.data.success) {
                        setStatsPartner(partnerRes.data.data);
                    }
                }
            } else {
                setStatsEOS(null);
                setStatsPartner(null);
            }

            // 🧪 Statistiques simulées par type de tarif
            const mockTarifStats = [
                { code: 'A', description: 'Adresse seule', count: 124, montant: 992.00 },
                { code: 'AT', description: 'Adresse et téléphone', count: 248, montant: 5456.00 },
                { code: 'ATB', description: 'Adresse, téléphone et banque', count: 76, montant: 1824.00 },
                { code: 'D', description: 'Décès', count: 12, montant: 120.00 },
                { code: 'ATBE', description: 'Adresse, téléphone, banque et employeur', count: 42, montant: 1092.00 }
            ];
            setTarifStats(mockTarifStats);

            // 🧪 Statistiques simulées par enquêteur
            const mockEnqueteurStats = [
                { id: 1, nom: 'Dupont', prenom: 'Jean', count: 87, montant: 1914.00, status: { positive: 68, negative: 19 } },
                { id: 2, nom: 'Martin', prenom: 'Sophie', count: 124, montant: 2728.00, status: { positive: 102, negative: 22 } },
                { id: 3, nom: 'Bernard', prenom: 'Philippe', count: 56, montant: 1232.00, status: { positive: 48, negative: 8 } },
                { id: 4, nom: 'Petit', prenom: 'Marie', count: 103, montant: 2266.00, status: { positive: 85, negative: 18 } },
                { id: 5, nom: 'Lefebvre', prenom: 'Thomas', count: 132, montant: 2904.00, status: { positive: 112, negative: 20 } }
            ];
            setEnqueteurStats(mockEnqueteurStats);

        } catch (err) {
            console.error("Erreur lors de la récupération des données:", err);
            setError("Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    }, [selectedPeriod, selectedClientId, clients]);

    useEffect(() => {
        fetchClients();
    }, [fetchClients]);

    useEffect(() => {
        if (!loadingClients) {
            fetchAllData();
        }
    }, [fetchAllData, loadingClients]);

    // Effet pour l'actualisation automatique
    useEffect(() => {
        let interval;
        if (autoRefresh) {
            interval = setInterval(() => {
                fetchAllData();
            }, 30000); // Actualisation toutes les 30 secondes
        }
        return () => clearInterval(interval);
    }, [autoRefresh, fetchAllData]);


    // Générer un rapport PDF (exemple)
    const handleGenerateReport = () => {
        // Dans une implémentation réelle, cette fonction ferait un appel API pour générer un PDF
        alert("Fonctionnalité de génération de rapport PDF à implémenter");
    };

    // Mise en forme des données pour les graphiques
    const prepareChartData = () => {
        // Pour le graphique d'évolution mensuelle
        const monthlyData = periodeStats.map(stat => ({
            name: stat.periode,
            facturé: stat.montant_facture,
            payé: stat.montant_paye,
            marge: stat.marge
        }));

        // Pour le camembert des types de tarifs
        const tarifData = tarifStats.map(tarif => ({
            name: tarif.code,
            value: tarif.montant,
            count: tarif.count,
            description: tarif.description
        }));

        // Pour la répartition par enquêteur
        const enqueteurData = enqueteurStats.map(enq => ({
            name: `${enq.prenom} ${enq.nom}`,
            montant: enq.montant,
            count: enq.count,
            positive: enq.status.positive,
            negative: enq.status.negative
        }));

        return { monthlyData, tarifData, enqueteurData };
    };

    const { monthlyData, tarifData, enqueteurData } = prepareChartData();

    // Affichage du chargement
    if (loading && !periodeStats.length) {
        return (
            <div className="flex justify-center items-center h-64">
                <RefreshCw className="w-10 h-10 animate-spin text-blue-500" />
            </div>
        );
    }

    // Affichage de l'erreur
    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <div>
                    <h3 className="font-medium">Erreur de chargement</h3>
                    <p>{error}</p>
                </div>
                <button
                    onClick={fetchAllData}
                    className="ml-auto px-3 py-1 border border-red-300 rounded hover:bg-red-100"
                >
                    Réessayer
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* En-tête avec titre et contrôles */}
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <BarChart2 className="w-6 h-6 text-blue-500" />
                    Rapports Financiers
                </h2>

                <div className="flex gap-3 items-center">
                    {/* Switch Auto-refresh */}
                    <div className="flex items-center gap-2 mr-2">
                        <button
                            onClick={() => setAutoRefresh(!autoRefresh)}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${autoRefresh ? 'bg-blue-600' : 'bg-gray-200'
                                }`}
                        >
                            <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${autoRefresh ? 'translate-x-6' : 'translate-x-1'
                                    }`}
                            />
                        </button>
                        <span className="text-sm text-gray-600">Auto</span>
                    </div>
                    {/* MULTI-CLIENT: Sélecteur de client */}
                    {!loadingClients && clients.length > 0 && (
                        <div>
                            <select
                                value={selectedClientId || ''}
                                onChange={(e) => setSelectedClientId(e.target.value ? parseInt(e.target.value) : null)}
                                className="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
                            >
                                <option value="">Tous les clients</option>
                                {clients.map(client => (
                                    <option key={client.id} value={client.id}>
                                        {client.nom} ({client.code})
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div>
                        <select
                            value={selectedPeriod}
                            onChange={(e) => setSelectedPeriod(e.target.value)}
                            className="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
                        >
                            <option value="1month">Dernier mois</option>
                            <option value="12months">12 derniers mois</option>
                            <option value="24months">24 derniers mois</option>
                            <option value="current">Année en cours</option>
                        </select>
                    </div>
                    <button
                        onClick={handleGenerateReport}
                        className="flex items-center gap-1 px-3 py-1.5 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                    >
                        <Download className="w-4 h-4" />
                        <span>Exporter PDF</span>
                    </button>
                    <button
                        onClick={fetchAllData}
                        className={`flex items-center gap-1 px-3 py-1.5 border border-gray-300 rounded-md hover:bg-gray-50 text-sm ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                        disabled={loading}
                    >
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                        <span>Actualiser</span>
                    </button>
                </div>
            </div>

            {/* Contenu principal */}
            <div className="space-y-6">
                {/* Statistiques globales en cartes */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Total facturé (EOS)</p>
                                <p className="text-2xl font-bold text-blue-700 mt-1">
                                    {globalStats?.total_eos.toFixed(2) || 0} €
                                </p>
                            </div>
                            <div className="p-2 bg-blue-100 rounded-full">
                                <DollarSign className="w-5 h-5 text-blue-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Pour {globalStats?.enquetes_positives || 0} enquêtes positives
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Payé aux enquêteurs</p>
                                <p className="text-2xl font-bold text-green-700 mt-1">
                                    {globalStats?.total_enqueteurs.toFixed(2) || 0} €
                                </p>
                            </div>
                            <div className="p-2 bg-green-100 rounded-full">
                                <Users className="w-5 h-5 text-green-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Représente {globalStats ? (globalStats.total_enqueteurs / globalStats.total_eos * 100).toFixed(1) : 0}% du CA
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Marge brute</p>
                                <p className="text-2xl font-bold text-indigo-700 mt-1">
                                    {globalStats?.marge.toFixed(2) || 0} €
                                </p>
                            </div>
                            <div className="p-2 bg-indigo-100 rounded-full">
                                <TrendingUp className="w-5 h-5 text-indigo-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Taux de marge: {globalStats?.pourcentage_marge.toFixed(1) || 0}%
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Enquêtes traitées</p>
                                <p className="text-2xl font-bold text-gray-700 mt-1">
                                    {globalStats?.enquetes_traitees || 0}
                                </p>
                            </div>
                            <div className="p-2 bg-gray-100 rounded-full">
                                <FileText className="w-5 h-5 text-gray-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Dont {globalStats?.enquetes_positives || 0} positives ({globalStats ? (globalStats.enquetes_positives / globalStats.enquetes_traitees * 100).toFixed(1) : 0}%)
                        </p>
                    </div>
                </div>

                {/* Comparaison EOS vs PARTNER (uniquement si "Tous" est sélectionné) */}
                {!selectedClientId && statsEOS && statsPartner && (
                    <div className="bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg border-2 border-blue-200">
                        <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <TrendingUp className="w-6 h-6 text-blue-600" />
                            Comparaison EOS vs PARTNER
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Carte EOS */}
                            <div className="bg-white rounded-lg shadow-md p-5 border-2 border-blue-300">
                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="text-lg font-semibold text-blue-900">Client EOS</h4>
                                    <div className="bg-blue-100 rounded-full p-2">
                                        <DollarSign className="w-5 h-5 text-blue-600" />
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div>
                                        <p className="text-sm text-gray-600">Total Facturé</p>
                                        <p className="text-2xl font-bold text-blue-700">
                                            {statsEOS.total_eos.toFixed(2)} €
                                        </p>
                                    </div>

                                    <div>
                                        <p className="text-sm text-gray-600">Payé Enquêteurs</p>
                                        <p className="text-xl font-semibold text-gray-700">
                                            {statsEOS.total_enqueteurs.toFixed(2)} €
                                        </p>
                                    </div>

                                    <div className="pt-3 border-t border-blue-200">
                                        <p className="text-sm text-gray-600">Marge EOS</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {statsEOS.marge.toFixed(2)} €
                                        </p>
                                        <p className="text-sm text-gray-500 mt-1">
                                            Taux: {statsEOS.pourcentage_marge.toFixed(1)}%
                                        </p>
                                    </div>

                                    <div className="pt-2">
                                        <p className="text-xs text-gray-500">
                                            {statsEOS.enquetes_positives} enquêtes positives / {statsEOS.enquetes_traitees} traitées
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Carte PARTNER */}
                            <div className="bg-white rounded-lg shadow-md p-5 border-2 border-green-300">
                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="text-lg font-semibold text-green-900">Client PARTNER</h4>
                                    <div className="bg-green-100 rounded-full p-2">
                                        <DollarSign className="w-5 h-5 text-green-600" />
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <div>
                                        <p className="text-sm text-gray-600">Total Facturé</p>
                                        <p className="text-2xl font-bold text-green-700">
                                            {statsPartner.total_eos.toFixed(2)} €
                                        </p>
                                    </div>

                                    <div>
                                        <p className="text-sm text-gray-600">Payé Enquêteurs</p>
                                        <p className="text-xl font-semibold text-gray-700">
                                            {statsPartner.total_enqueteurs.toFixed(2)} €
                                        </p>
                                    </div>

                                    <div className="pt-3 border-t border-green-200">
                                        <p className="text-sm text-gray-600">Marge PARTNER</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {statsPartner.marge.toFixed(2)} €
                                        </p>
                                        <p className="text-sm text-gray-500 mt-1">
                                            Taux: {statsPartner.pourcentage_marge.toFixed(1)}%
                                        </p>
                                    </div>

                                    <div className="pt-2">
                                        <p className="text-xs text-gray-500">
                                            {statsPartner.enquetes_positives} enquêtes positives / {statsPartner.enquetes_traitees} traitées
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Résumé comparatif */}
                        <div className="mt-4 bg-white rounded-lg p-4 border border-gray-200">
                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div>
                                    <p className="text-xs text-gray-600 mb-1">Différence de Marge</p>
                                    <p className="text-lg font-bold text-indigo-600">
                                        {Math.abs(statsEOS.marge - statsPartner.marge).toFixed(2)} €
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        {statsEOS.marge > statsPartner.marge ? 'EOS gagne plus' : 'PARTNER gagne plus'}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-600 mb-1">Part EOS du Total</p>
                                    <p className="text-lg font-bold text-blue-600">
                                        {(statsEOS.total_eos / (statsEOS.total_eos + statsPartner.total_eos) * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs text-gray-600 mb-1">Part PARTNER du Total</p>
                                    <p className="text-lg font-bold text-green-600">
                                        {(statsPartner.total_eos / (statsEOS.total_eos + statsPartner.total_eos) * 100).toFixed(1)}%
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Graphiques de la vue d'ensemble */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Graphique d'évolution mensuelle */}
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <h3 className="font-medium mb-4">Évolution mensuelle</h3>
                        <div style={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={monthlyData}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="facturé" fill={COLORS.facture} name="Facturé" />
                                    <Bar dataKey="payé" fill={COLORS.enqueteur} name="Payé aux enquêteurs" />
                                    <Bar dataKey="marge" fill={COLORS.marge} name="Marge" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Répartition par type de tarif */}
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <h3 className="font-medium mb-4">Répartition par type de tarif</h3>
                        <div style={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <RPieChart>
                                    <Pie
                                        data={tarifData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {tarifData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={`hsl(${index * 30}, 70%, 50%)`} />
                                        ))}
                                    </Pie>
                                    <Tooltip formatter={(value) => `${value.toFixed(2)} €`} />
                                    <Legend />
                                </RPieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Tableau des données mensuelles */}
                <div className="bg-white p-4 rounded-lg shadow border">
                    <h3 className="font-medium mb-4">Données mensuelles détaillées</h3>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Période
                                    </th>
                                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Enquêtes
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Facturé (EOS)
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Payé (Enquêteurs)
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Marge
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Taux de marge
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {periodeStats.map((stat, index) => (
                                    <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {stat.periode}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                                            {stat.nb_enquetes}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                            {stat.montant_facture.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                                            {stat.montant_enqueteurs.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600">
                                            {stat.marge.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                                            {(stat.marge / stat.montant_facture * 100).toFixed(1)}%
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot className="bg-gray-50">
                                <tr>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        TOTAL
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-gray-900">
                                        {periodeStats.reduce((sum, stat) => sum + stat.nb_enquetes, 0)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                        {periodeStats.reduce((sum, stat) => sum + stat.montant_facture, 0).toFixed(2)} €
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                        {periodeStats.reduce((sum, stat) => sum + stat.montant_enqueteurs, 0).toFixed(2)} €
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600">
                                        {periodeStats.reduce((sum, stat) => sum + stat.marge, 0).toFixed(2)} €
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                        {(periodeStats.reduce((sum, stat) => sum + stat.marge, 0) /
                                            periodeStats.reduce((sum, stat) => sum + stat.montant_facture, 0) * 100).toFixed(1)}%
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FinancialReports;