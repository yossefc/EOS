import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    BarChart2, PieChart, Calendar, RefreshCw, AlertCircle, 
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
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [activeTab, setActiveTab] = useState('overview');
    
    // Période sélectionnée pour les filtres
    const [selectedPeriod, setSelectedPeriod] = useState('12months');
    
    // Récupération des données
    useEffect(() => {
        fetchAllData();
    }, [selectedPeriod]);
    
    const fetchAllData = async () => {
        try {
            setLoading(true);
            setError(null);
            
            // Récupérer les statistiques par période
            const periodResponse = await axios.get(`${API_URL}/api/paiement/stats/periodes?mois=${selectedPeriod === '12months' ? 12 : 24}`);
            
            if (periodResponse.data.success) {
                setPeriodeStats(periodResponse.data.data);
            }
            
            // Récupérer les statistiques globales
            const globalResponse = await axios.get(`${API_URL}/api/tarification/stats/global`);
            
            if (globalResponse.data.success) {
                setGlobalStats(globalResponse.data.data);
            }
            
            // Récupérer les statistiques par tarif (simulation pour l'exemple)
            const mockTarifStats = [
                { code: 'A', description: 'Adresse seule', count: 124, montant: 992.00 },
                { code: 'AT', description: 'Adresse et téléphone', count: 248, montant: 5456.00 },
                { code: 'ATB', description: 'Adresse, téléphone et banque', count: 76, montant: 1824.00 },
                { code: 'D', description: 'Décès', count: 12, montant: 120.00 },
                { code: 'ATBE', description: 'Adresse, téléphone, banque et employeur', count: 42, montant: 1092.00 }
            ];
            
            setTarifStats(mockTarifStats);
            
            // Récupérer les statistiques par enquêteur (simulation pour l'exemple)
            const mockEnqueteurStats = [
                { id: 1, nom: 'Dupont', prenom: 'Jean', count: 87, montant: 1914.00, status: { positive: 68, negative: 19 } },
                { id: 2, nom: 'Martin', prenom: 'Sophie', count: 124, montant: 2728.00, status: { positive: 102, negative: 22 } },
                { id: 3, nom: 'Bernard', prenom: 'Philippe', count: 56, montant: 1232.00, status: { positive: 48, negative: 8 } },
                { id: 4, nom: 'Petit', prenom: 'Marie', count: 103, montant: 2266.00, status: { positive: 85, negative: 18 } },
                { id: 5, nom: 'Lefebvre', prenom: 'Thomas', count: 132, montant: 2904.00, status: { positive: 112, negative: 20 } }
            ];
            
            setEnqueteurStats(mockEnqueteurStats);
            
        } catch (error) {
            console.error("Erreur lors de la récupération des données:", error);
            setError("Erreur lors du chargement des données");
        } finally {
            setLoading(false);
        }
    };
    
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
                
                <div className="flex gap-3">
                    <div>
                        <select
                            value={selectedPeriod}
                            onChange={(e) => setSelectedPeriod(e.target.value)}
                            className="border border-gray-300 rounded-md px-3 py-1.5 text-sm"
                        >
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
                        className="flex items-center gap-1 px-3 py-1.5 border border-gray-300 rounded-md hover:bg-gray-50 text-sm"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Actualiser</span>
                    </button>
                </div>
            </div>
            
            {/* Navigation par onglets */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('overview')}
                        className={`py-3 px-1 border-b-2 font-medium text-sm ${
                            activeTab === 'overview'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                        Vue d'ensemble
                    </button>
                    <button
                        onClick={() => setActiveTab('trends')}
                        className={`py-3 px-1 border-b-2 font-medium text-sm ${
                            activeTab === 'trends'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                        Tendances
                    </button>
                    <button
                        onClick={() => setActiveTab('enqueteurs')}
                        className={`py-3 px-1 border-b-2 font-medium text-sm ${
                            activeTab === 'enqueteurs'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                    >
                        Par enquêteur
                    </button>
                </nav>
            </div>
            
            {/* Contenu des onglets */}
            {activeTab === 'overview' && (
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
            )}
            
            {activeTab === 'trends' && (
                <div className="space-y-6">
                    {/* Graphiques de tendances */}
                    <div className="grid grid-cols-1 gap-6">
                        {/* Évolution de la facturation */}
                        <div className="bg-white p-4 rounded-lg shadow border">
                            <h3 className="font-medium mb-4">Évolution de la facturation</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={monthlyData}>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Line type="monotone" dataKey="facturé" stroke={COLORS.facture} name="Facturé" />
                                        <Line type="monotone" dataKey="payé" stroke={COLORS.enqueteur} name="Payé aux enquêteurs" />
                                        <Line type="monotone" dataKey="marge" stroke={COLORS.marge} name="Marge" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                        
                        {/* Évolution cumulative */}
                        <div className="bg-white p-4 rounded-lg shadow border">
                            <h3 className="font-medium mb-4">Évolution cumulative des revenus</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={
                                        // Calculer les valeurs cumulatives
                                        monthlyData.map((item, index, array) => {
                                            // Calculer les sommes cumulatives
                                            const cumulFacture = array.slice(0, index + 1).reduce((sum, curr) => sum + curr.facturé, 0);
                                            const cumulPaye = array.slice(0, index + 1).reduce((sum, curr) => sum + curr.payé, 0);
                                            const cumulMarge = array.slice(0, index + 1).reduce((sum, curr) => sum + curr.marge, 0);
                                            
                                            return {
                                                ...item,
                                                cumulFacture,
                                                cumulPaye,
                                                cumulMarge
                                            };
                                        })
                                    }>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis />
                                        <Tooltip />
                                        <Legend />
                                        <Area type="monotone" dataKey="cumulFacture" stackId="1" stroke={COLORS.facture} fill={`${COLORS.facture}33`} name="Facturé (cumul)" />
                                        <Area type="monotone" dataKey="cumulPaye" stackId="2" stroke={COLORS.enqueteur} fill={`${COLORS.enqueteur}33`} name="Payé (cumul)" />
                                        <Area type="monotone" dataKey="cumulMarge" stackId="3" stroke={COLORS.marge} fill={`${COLORS.marge}33`} name="Marge (cumul)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                        
                        {/* Tendance du taux de marge */}
                        <div className="bg-white p-4 rounded-lg shadow border">
                            <h3 className="font-medium mb-4">Évolution du taux de marge</h3>
                            <div style={{ height: 300 }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={
                                        periodeStats.map(stat => ({
                                            name: stat.periode,
                                            "taux de marge": (stat.marge / stat.montant_facture * 100) || 0
                                        }))
                                    }>
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis dataKey="name" />
                                        <YAxis domain={[0, 100]} />
                                        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                                        <Legend />
                                        <Line type="monotone" dataKey="taux de marge" stroke="#8884d8" name="Taux de marge (%)" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            {activeTab === 'enqueteurs' && (
                <div className="space-y-6">
                    {/* Vue par enquêteur */}
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <h3 className="font-medium mb-4">Performance des enquêteurs</h3>
                        <div style={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={enqueteurData} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis type="number" />
                                    <YAxis dataKey="name" type="category" width={150} />
                                    <Tooltip />
                                    <Legend />
                                    <Bar dataKey="montant" fill="#3B82F6" name="Montant (€)" />
                                    <Bar dataKey="count" fill="#10B981" name="Nombre d'enquêtes" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    
                    {/* Taux de réussite des enquêteurs */}
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <h3 className="font-medium mb-4">Taux de réussite des enquêteurs</h3>
                        <div style={{ height: 300 }}>
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={
                                    enqueteurData.map(enq => ({
                                        name: enq.name,
                                        "taux de réussite": (enq.positive / (enq.positive + enq.negative) * 100) || 0,
                                        total: enq.positive + enq.negative
                                    }))
                                }>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis domain={[0, 100]} />
                                    <Tooltip formatter={(value, name) => name === "taux de réussite" ? `${value.toFixed(1)}%` : value} />
                                    <Legend />
                                    <Bar dataKey="taux de réussite" fill="#3B82F6" name="Taux de réussite (%)" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    
                    {/* Tableau des enquêteurs */}
                    <div className="bg-white p-4 rounded-lg shadow border">
                        <h3 className="font-medium mb-4">Détail par enquêteur</h3>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Enquêteur
                                        </th>
                                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Enquêtes
                                        </th>
                                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Positives
                                        </th>
                                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Négatives
                                        </th>
                                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Taux réussite
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Montant
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {enqueteurStats.map((enqueteur, index) => (
                                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {enqueteur.prenom} {enqueteur.nom}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                                                {enqueteur.count}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-green-600">
                                                {enqueteur.status.positive}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-red-600">
                                                {enqueteur.status.negative}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-gray-900">
                                                {((enqueteur.status.positive / enqueteur.count) * 100).toFixed(1)}%
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                                {enqueteur.montant.toFixed(2)} €
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
                                            {enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.count, 0)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-green-600">
                                            {enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.status.positive, 0)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-red-600">
                                            {enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.status.negative, 0)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center font-medium text-gray-900">
                                            {(enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.status.positive, 0) / 
                                              enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.count, 0) * 100).toFixed(1)}%
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                                            {enqueteurStats.reduce((sum, enqueteur) => sum + enqueteur.montant, 0).toFixed(2)} €
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FinancialReports;