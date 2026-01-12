import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { RefreshCw, TrendingUp, Archive, CheckCircle, Database, FileText, Calendar, Users, AlertCircle, Loader } from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

/**
 * StatsViewer - Tableau de bord des statistiques
 * Design clair avec typographie soignée
 */
const StatsViewer = forwardRef((props, ref) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchStats = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await fetch(`${API_URL}/api/stats`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) throw new Error(`Erreur HTTP: ${response.status}`);
            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err.message || 'Erreur lors de la récupération des statistiques');
        } finally {
            setLoading(false);
        }
    };

    useImperativeHandle(ref, () => ({ fetchStats }));
    useEffect(() => { fetchStats(); }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-16 gap-3">
                <Loader className="w-6 h-6 text-blue-500 animate-spin" />
                <p className="text-slate-500 text-sm">Chargement des statistiques...</p>
            </div>
        );
    }

    const totalArchived = stats?.clients_stats?.reduce((acc, c) => acc + c.archived, 0) || 0;
    const totalPositifs = stats?.clients_stats?.reduce((acc, c) => acc + c.bon, 0) || 0;
    const priorityClient = stats?.clients_stats?.length > 0
        ? stats.clients_stats.sort((a, b) => (b.imported - b.treated) - (a.imported - a.treated))[0]
        : null;

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-6">

            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-blue-500" />
                        Tableau de bord
                    </h1>
                    <p className="text-sm text-slate-500 mt-0.5">Vue d'ensemble des performances</p>
                </div>
                <button
                    onClick={fetchStats}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 
                     bg-white border border-slate-200 rounded-lg hover:bg-slate-50 
                     transition-colors shadow-sm"
                >
                    <RefreshCw className="w-4 h-4" />
                    Actualiser
                </button>
            </div>

            {/* Error */}
            {error && (
                <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <p className="text-sm font-medium text-red-700">{error}</p>
                </div>
            )}

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

                {/* Total Dossiers */}
                <div className="bg-white rounded-lg border border-slate-200 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
                            <Database className="w-5 h-5 text-blue-600" />
                        </div>
                        <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            +{stats?.total_fichiers || 0} fichiers
                        </span>
                    </div>
                    <p className="text-sm font-medium text-slate-500 mb-1">Total dossiers</p>
                    <p className="text-3xl font-bold text-slate-800 tracking-tight">
                        {stats?.total_donnees?.toLocaleString() || 0}
                    </p>
                </div>

                {/* Archivés */}
                <div className="bg-white rounded-lg border border-slate-200 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                        <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                            <Archive className="w-5 h-5 text-slate-600" />
                        </div>
                    </div>
                    <p className="text-sm font-medium text-slate-500 mb-1">Dossiers archivés</p>
                    <p className="text-3xl font-bold text-slate-800 tracking-tight">
                        {totalArchived.toLocaleString()}
                    </p>
                </div>

                {/* Positifs */}
                <div className="bg-white rounded-lg border border-slate-200 p-5 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                        <div className="w-10 h-10 bg-green-50 rounded-lg flex items-center justify-center">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                        </div>
                    </div>
                    <p className="text-sm font-medium text-slate-500 mb-1">Résultats positifs</p>
                    <p className="text-3xl font-bold text-green-600 tracking-tight">
                        {totalPositifs.toLocaleString()}
                    </p>
                </div>
            </div>

            {/* Performance par Client */}
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
                    <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                        <Users className="w-4 h-4 text-blue-500" />
                        Performance par client
                    </h2>
                    <span className="text-xs font-medium text-blue-700 bg-blue-100 px-2.5 py-1 rounded-full">
                        {stats?.clients_stats?.length || 0} clients
                    </span>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-slate-50/50 border-b border-slate-100">
                                <th className="px-5 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Client</th>
                                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wide">Importés</th>
                                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wide">Traités</th>
                                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wide">Archivés</th>
                                <th className="px-4 py-3 text-center text-xs font-semibold text-green-600 uppercase tracking-wide">Positifs</th>
                                <th className="px-5 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wide">Taux réussite</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {stats?.clients_stats?.map((client) => (
                                <tr key={client.id} className="hover:bg-slate-50/50 transition-colors">
                                    <td className="px-5 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-9 h-9 bg-slate-100 rounded-lg flex items-center justify-center">
                                                <span className="text-xs font-bold text-slate-600">{client.code}</span>
                                            </div>
                                            <span className="font-medium text-slate-800">{client.nom}</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-4 text-center">
                                        <span className="text-sm font-semibold text-slate-700">{client.imported}</span>
                                    </td>
                                    <td className="px-4 py-4 text-center">
                                        <span className="inline-flex px-2.5 py-1 bg-blue-50 text-blue-700 rounded text-xs font-semibold">
                                            {client.treated}
                                        </span>
                                    </td>
                                    <td className="px-4 py-4 text-center">
                                        <span className="text-sm text-slate-500">{client.archived}</span>
                                    </td>
                                    <td className="px-4 py-4 text-center">
                                        <span className="inline-flex items-center gap-1 text-green-600 font-semibold text-sm">
                                            <CheckCircle className="w-3.5 h-3.5" />
                                            {client.bon}
                                        </span>
                                    </td>
                                    <td className="px-5 py-4 text-right">
                                        <div className="inline-flex flex-col items-end gap-1.5">
                                            <span className={`text-sm font-bold ${client.success_rate >= 50 ? 'text-green-600' : 'text-slate-600'}`}>
                                                {client.success_rate}%
                                            </span>
                                            <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full transition-all ${client.success_rate >= 50 ? 'bg-green-500' : 'bg-slate-400'}`}
                                                    style={{ width: `${Math.min(client.success_rate, 100)}%` }}
                                                />
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Bottom Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

                {/* Derniers Imports */}
                <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 overflow-hidden">
                    <div className="px-5 py-4 border-b border-slate-100 bg-slate-50">
                        <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                            <FileText className="w-4 h-4 text-slate-500" />
                            Derniers imports
                        </h2>
                    </div>
                    <div className="divide-y divide-slate-100">
                        {stats?.derniers_fichiers?.length > 0 ? (
                            stats.derniers_fichiers.map((fichier) => (
                                <div key={fichier.id} className="px-5 py-3 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className="w-9 h-9 bg-slate-50 rounded-lg flex items-center justify-center">
                                            <FileText className="w-4 h-4 text-slate-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-slate-800">{fichier.nom}</p>
                                            <div className="flex items-center gap-2 mt-0.5">
                                                <span className="text-xs text-slate-400">{fichier.client_nom}</span>
                                                <span className="text-slate-300">•</span>
                                                <span className="text-xs text-slate-400 flex items-center gap-1">
                                                    <Calendar className="w-3 h-3" />
                                                    {fichier.date_upload}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-bold text-slate-800">{fichier.nombre_donnees}</p>
                                        <p className="text-xs text-slate-400">entrées</p>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="px-5 py-8 text-center">
                                <p className="text-sm text-slate-400">Aucun fichier importé récemment</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Recommandation */}
                <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                    <div className="px-5 py-4 border-b border-slate-100 bg-slate-50">
                        <h2 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-blue-500" />
                            Recommandation
                        </h2>
                    </div>
                    <div className="p-5 space-y-4">
                        {priorityClient ? (
                            <>
                                <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                                    <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-1">
                                        Priorité d'action
                                    </p>
                                    <p className="text-lg font-bold text-slate-800">{priorityClient.nom}</p>
                                    <p className="text-xs text-slate-500 mt-1">
                                        {priorityClient.imported - priorityClient.treated} dossier(s) en attente
                                    </p>
                                </div>
                                <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                    <span className="text-sm font-medium text-green-700">Système opérationnel</span>
                                </div>
                            </>
                        ) : (
                            <div className="py-6 text-center">
                                <p className="text-sm text-slate-400">Aucune donnée disponible</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
});

StatsViewer.displayName = 'StatsViewer';

export default StatsViewer;