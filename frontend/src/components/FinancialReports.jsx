import { useCallback, useState, useEffect } from 'react';
import axios from 'axios';
import {
    BarChart2, RefreshCw, AlertCircle,
    Download, DollarSign, TrendingUp, FileText, Users
} from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    ResponsiveContainer, PieChart as RPieChart, Pie, Cell
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
    const [globalStats, setGlobalStats] = useState(null);
    const [statsEOS, setStatsEOS] = useState(null);
    const [statsPartner, setStatsPartner] = useState(null);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Dates personnalisées
    const todayStr = new Date().toISOString().split('T')[0];
    const [dateDebut, setDateDebut] = useState(() => {
        const d = new Date();
        d.setFullYear(d.getFullYear() - 1);
        return d.toISOString().split('T')[0];
    });
    const [dateFin, setDateFin] = useState(todayStr);
    // Garde une trace du preset actif pour le surlignage des boutons
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

    // Applique un preset et met à jour les dates
    const applyPreset = useCallback((preset) => {
        const now = new Date();
        const fmt = (d) => d.toISOString().split('T')[0];
        let debut, fin = fmt(now);
        if (preset === '1month') {
            debut = fmt(new Date(now.getFullYear(), now.getMonth() - 1, 1));
            fin = fmt(new Date(now.getFullYear(), now.getMonth(), 0));
        } else if (preset === '12months') {
            const d = new Date(now); d.setFullYear(d.getFullYear() - 1);
            debut = fmt(d);
        } else if (preset === '24months') {
            const d = new Date(now); d.setFullYear(d.getFullYear() - 2);
            debut = fmt(d);
        } else if (preset === 'current') {
            debut = fmt(new Date(now.getFullYear(), 0, 1));
        } else if (preset === 'all') {
            debut = '2024-01-01';
        }
        setDateDebut(debut);
        setDateFin(fin);
        setSelectedPeriod(preset);
    }, []);

    // Fonction pour récupérer toutes les données
    const fetchAllData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            // 📊 Récupérer les statistiques par période (dates personnalisées)
            const clientParam = selectedClientId ? `&client_id=${selectedClientId}` : '';
            const dateParams = `date_debut=${dateDebut}&date_fin=${dateFin}`;
            const periodRes = await axios.get(
                `${API_URL}/api/paiement/stats/periodes?${dateParams}${clientParam}`
            );

            if (periodRes.data.success) {
                setPeriodeStats(periodRes.data.data);
            }

            // 📈 Récupérer les statistiques globales
            const globalRes = await axios.get(
                `${API_URL}/api/tarification/stats/global?${dateParams}${selectedClientId ? `&client_id=${selectedClientId}` : ''}`
            );

            if (globalRes.data.success) {
                setGlobalStats(globalRes.data.data);
            }

            const tarifRes = await axios.get(
                `${API_URL}/api/tarification/stats/tarifs?${dateParams}${selectedClientId ? `&client_id=${selectedClientId}` : ''}`
            );

            if (tarifRes.data.success) {
                setTarifStats(tarifRes.data.data);
            } else {
                setTarifStats([]);
            }

            // 📊 Si "Tous les clients" est sélectionné, récupérer aussi EOS et PARTNER séparément
            if (!selectedClientId && clients.length > 0) {
                const clientEOS = clients.find(c => c.code === 'EOS');
                const clientPartner = clients.find(c => c.code !== 'EOS');

                if (clientEOS) {
                    const eosRes = await axios.get(
                        `${API_URL}/api/tarification/stats/global?${dateParams}&client_id=${clientEOS.id}`
                    );
                    if (eosRes.data.success) {
                        setStatsEOS(eosRes.data.data);
                    }
                }

                if (clientPartner) {
                    const partnerRes = await axios.get(
                        `${API_URL}/api/tarification/stats/global?${dateParams}&client_id=${clientPartner.id}`
                    );
                    if (partnerRes.data.success) {
                        setStatsPartner(partnerRes.data.data);
                    }
                }
            } else {
                setStatsEOS(null);
                setStatsPartner(null);
            }

        } catch (err) {
            console.error("Erreur lors de la récupération des données:", err);
            setError("Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    }, [dateDebut, dateFin, selectedClientId, clients]);

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


    // Générer un PDF de facturation client
    const handleGenerateReport = () => {
        if (!selectedClientId) {
            alert("Veuillez sélectionner un client (EOS ou PARTNER) pour exporter le PDF de facturation.");
            return;
        }
        let url = `${API_URL}/api/paiement/facturation-client-pdf/${selectedClientId}`;
        url += `?date_debut=${dateDebut}&date_fin=${dateFin}`;
        window.open(url, '_blank');
    };

    // Statistiques agrégées sur la période sélectionnée (depuis periodeStats)
    const periodeTotaux = periodeStats.reduce(
        (acc, stat) => ({
            total_eos: acc.total_eos + (stat.montant_facture || 0),
            total_enqueteurs: acc.total_enqueteurs + (stat.montant_enqueteurs || 0),
            marge: acc.marge + (stat.marge || 0),
            nb_enquetes: acc.nb_enquetes + (stat.nb_enquetes || 0),
        }),
        { total_eos: 0, total_enqueteurs: 0, marge: 0, nb_enquetes: 0 }
    );

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
        return { monthlyData, tarifData };
    };

    const { monthlyData, tarifData } = prepareChartData();

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

                    {/* Sélection de période par date */}
                    <div className="flex items-center gap-2 flex-wrap">
                        {/* Presets rapides */}
                        {[
                            { key: '1month', label: '1M' },
                            { key: '12months', label: '12M' },
                            { key: '24months', label: '24M' },
                            { key: 'current', label: 'Année' },
                            { key: 'all', label: 'Tout' },
                        ].map(p => (
                            <button
                                key={p.key}
                                onClick={() => applyPreset(p.key)}
                                className={`px-2.5 py-1 rounded text-xs font-medium border transition-colors ${
                                    selectedPeriod === p.key
                                        ? 'bg-blue-600 text-white border-blue-600'
                                        : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'
                                }`}
                            >
                                {p.label}
                            </button>
                        ))}
                        {/* Séparateur */}
                        <span className="text-gray-300 text-sm">|</span>
                        {/* De */}
                        <div className="flex items-center gap-1">
                            <span className="text-xs text-gray-500">De</span>
                            <input
                                type="date"
                                value={dateDebut}
                                onChange={(e) => { setDateDebut(e.target.value); setSelectedPeriod('custom'); }}
                                className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                            />
                        </div>
                        {/* À */}
                        <div className="flex items-center gap-1">
                            <span className="text-xs text-gray-500">À</span>
                            <input
                                type="date"
                                value={dateFin}
                                onChange={(e) => { setDateFin(e.target.value); setSelectedPeriod('custom'); }}
                                className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                            />
                        </div>
                        {/* Bouton appliquer quand custom */}
                        {selectedPeriod === 'custom' && (
                            <button
                                onClick={fetchAllData}
                                className="px-3 py-1 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700"
                            >
                                Appliquer
                            </button>
                        )}
                    </div>
                    <button
                        onClick={handleGenerateReport}
                        className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm ${
                            selectedClientId
                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                : 'border border-gray-300 hover:bg-gray-50 text-gray-500'
                        }`}
                        title={selectedClientId ? 'Télécharger le PDF de facturation client' : 'Sélectionnez un client pour exporter'}
                    >
                        <Download className="w-4 h-4" />
                        <span>PDF Facturation</span>
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
                {/* Statistiques sur la période sélectionnée (en cartes) */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Total facturé (EOS)</p>
                                <p className="text-2xl font-bold text-blue-700 mt-1">
                                    {periodeTotaux.total_eos.toFixed(2)} €
                                </p>
                            </div>
                            <div className="p-2 bg-blue-100 rounded-full">
                                <DollarSign className="w-5 h-5 text-blue-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Sur la période sélectionnée
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Payé aux enquêteurs</p>
                                <p className="text-2xl font-bold text-green-700 mt-1">
                                    {periodeTotaux.total_enqueteurs.toFixed(2)} €
                                </p>
                            </div>
                            <div className="p-2 bg-green-100 rounded-full">
                                <Users className="w-5 h-5 text-green-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            {periodeTotaux.total_eos > 0
                                ? `Représente ${(periodeTotaux.total_enqueteurs / periodeTotaux.total_eos * 100).toFixed(1)}% du CA`
                                : 'Sur la période sélectionnée'}
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Marge brute</p>
                                <p className="text-2xl font-bold text-indigo-700 mt-1">
                                    {periodeTotaux.marge.toFixed(2)} €
                                </p>
                            </div>
                            <div className="p-2 bg-indigo-100 rounded-full">
                                <TrendingUp className="w-5 h-5 text-indigo-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Taux: {periodeTotaux.total_eos > 0
                                ? `${(periodeTotaux.marge / periodeTotaux.total_eos * 100).toFixed(1)}%`
                                : '0%'}
                        </p>
                    </div>

                    <div className="bg-white p-4 rounded-lg shadow border">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-sm text-gray-500">Enquêtes traitées</p>
                                <p className="text-2xl font-bold text-gray-700 mt-1">
                                    {periodeTotaux.nb_enquetes}
                                </p>
                            </div>
                            <div className="p-2 bg-gray-100 rounded-full">
                                <FileText className="w-5 h-5 text-gray-600" />
                            </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            Sur la période sélectionnée
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
                                            {stat.montant_facture > 0 ? (stat.marge / stat.montant_facture * 100).toFixed(1) : '0.0'}%
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
                                        {(() => {
                                            const totalMarge = periodeStats.reduce((sum, stat) => sum + stat.marge, 0);
                                            const totalFacture = periodeStats.reduce((sum, stat) => sum + stat.montant_facture, 0);
                                            return totalFacture > 0 ? (totalMarge / totalFacture * 100).toFixed(1) : '0.0';
                                        })()}%
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
