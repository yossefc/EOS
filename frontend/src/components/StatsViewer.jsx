import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import { BarChart2, RefreshCcw, TrendingUp, Archive, CheckCircle, Database, FileText, Calendar, Users } from 'lucide-react';

const API_URL = 'http://localhost:5000';

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

            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            const data = await response.json();
            setStats(data);
        } catch (err) {
            setError(err.message || 'Erreur lors de la récupération des statistiques');
        } finally {
            setLoading(false);
        }
    };

    useImperativeHandle(ref, () => ({
        fetchStats
    }));

    useEffect(() => {
        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center p-20 gap-4">
                <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
                <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">Analyse des données en cours...</p>
            </div>
        );
    }

    return (
        <div className="space-y-10 max-w-7xl mx-auto pb-10">
            {/* Header Performance */}
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-slate-800 tracking-tight flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-blue-500" />
                        Tableau de Bord Performance
                    </h2>
                    <p className="text-slate-500 font-medium mt-1">Surveillance en temps réel de l&apos;activité par client</p>
                </div>
                <button
                    onClick={fetchStats}
                    className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-xl font-semibold text-slate-600 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm active:scale-95 group"
                >
                    <RefreshCcw className="w-3.5 h-3.5 group-active:rotate-180 transition-transform duration-500" />
                    Actualiser
                </button>
            </div>

            {error && (
                <div className="bg-rose-50 border border-rose-100 text-rose-700 p-6 rounded-3xl flex items-center gap-4 animate-in fade-in slide-in-from-top-4">
                    <CheckCircle className="w-6 h-6 text-rose-500 rotate-180" />
                    <p className="font-bold">{error}</p>
                </div>
            )}

            {/* Global KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-200/60 shadow-sm hover:shadow-md transition-all duration-300">
                    <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center mb-6">
                        <Database className="w-6 h-6 text-blue-600" />
                    </div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Total Dossiers</p>
                    <div className="flex items-baseline gap-2">
                        <p className="text-3xl font-extrabold text-slate-800 leading-none">{stats?.total_donnees || 0}</p>
                        <span className="text-emerald-500 text-xs font-semibold leading-none">+ {stats?.total_fichiers || 0} fichiers</span>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-[32px] border border-slate-200/60 shadow-sm hover:shadow-md transition-all duration-300">
                    <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center mb-6">
                        <Archive className="w-6 h-6 text-indigo-600" />
                    </div>
                    <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Total Archivés</p>
                    <p className="text-4xl font-[900] text-slate-900 leading-none">
                        {stats?.clients_stats?.reduce((acc, c) => acc + c.archived, 0) || 0}
                    </p>
                </div>

                <div className="bg-white p-8 rounded-[32px] border border-slate-200/60 shadow-sm hover:shadow-md transition-all duration-300">
                    <div className="w-12 h-12 bg-emerald-50 rounded-2xl flex items-center justify-center mb-6">
                        <CheckCircle className="w-6 h-6 text-emerald-600" />
                    </div>
                    <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Dossiers Positifs</p>
                    <p className="text-4xl font-[900] text-slate-900 leading-none">
                        {stats?.clients_stats?.reduce((acc, c) => acc + c.bon, 0) || 0}
                    </p>
                </div>
            </div>

            {/* Client Breakdown Section */}
            <div className="bg-white rounded-[40px] border border-slate-200/60 shadow-sm overflow-hidden">
                <div className="px-10 py-8 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <h3 className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-2">
                        <Users className="w-6 h-6 text-blue-500" />
                        Performance par Client
                    </h3>
                    <div className="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-xs font-black uppercase tracking-widest">
                        {stats?.clients_stats?.length || 0} Clients Actifs
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50/30 text-slate-400">
                                <th className="px-10 py-5 text-xs font-black uppercase tracking-widest">Client</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest">Importés</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest">Traités</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest">Archivés</th>
                                <th className="px-6 py-5 text-xs font-black uppercase tracking-widest text-emerald-600">Bons (P)</th>
                                <th className="px-10 py-5 text-xs font-black uppercase tracking-widest text-right">Taux de Réussite</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {stats?.clients_stats?.map((client) => (
                                <tr key={client.id} className="hover:bg-slate-50 group transition-colors">
                                    <td className="px-10 py-6">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-700 font-bold text-xs border border-slate-200">
                                                {client.code}
                                            </div>
                                            <span className="font-semibold text-slate-800">{client.nom}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-6 font-bold text-slate-700">{client.imported}</td>
                                    <td className="px-6 py-6">
                                        <span className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg font-black text-xs">
                                            {client.treated}
                                        </span>
                                    </td>
                                    <td className="px-6 py-6 font-bold text-slate-400">{client.archived}</td>
                                    <td className="px-6 py-6">
                                        <div className="flex items-center gap-2 text-emerald-600 font-black">
                                            <CheckCircle className="w-4 h-4" />
                                            {client.bon}
                                        </div>
                                    </td>
                                    <td className="px-10 py-6 text-right">
                                        <div className="inline-flex flex-col items-end">
                                            <span className={`text-xl font-bold ${client.success_rate > 50 ? 'text-blue-600' : 'text-slate-800'}`}>
                                                {client.success_rate}%
                                            </span>
                                            <div className="w-24 h-1.5 bg-slate-100 rounded-full mt-2 overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full ${client.success_rate > 50 ? 'bg-blue-600' : 'bg-slate-400'}`}
                                                    style={{ width: `${client.success_rate}%` }}
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

            {/* Bottom Grid: Recent Activity & Global Health */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Last Files */}
                <div className="lg:col-span-8 bg-white rounded-[40px] border border-slate-200/60 shadow-sm overflow-hidden">
                    <div className="px-10 py-6 border-b border-slate-100 flex justify-between items-center">
                        <h3 className="font-black text-slate-900 text-sm uppercase tracking-widest flex items-center gap-2">
                            <FileText className="w-5 h-5 text-slate-400" />
                            Derniers Imports
                        </h3>
                    </div>
                    <div className="divide-y divide-slate-100">
                        {stats?.derniers_fichiers?.map((fichier) => (
                            <div key={fichier.id} className="px-10 py-5 hover:bg-slate-50 flex justify-between items-center transition-colors group">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center group-hover:bg-white transition-colors">
                                        <FileText className="w-5 h-5 text-slate-400" />
                                    </div>
                                    <div>
                                        <p className="font-bold text-slate-900">{fichier.nom}</p>
                                        <div className="flex items-center gap-3 mt-1">
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{fichier.client_nom}</span>
                                            <div className="w-1 h-1 bg-slate-300 rounded-full" />
                                            <span className="text-[10px] font-black text-slate-400 flex items-center gap-1">
                                                <Calendar className="w-3 h-3" />
                                                {fichier.date_upload}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="font-black text-slate-900">{fichier.nombre_donnees}</p>
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Entrées</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Priority Alert Box */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-white rounded-3xl p-8 text-slate-800 border border-slate-200 shadow-sm">
                        <h3 className="text-lg font-bold mb-6 tracking-tight flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-blue-500" />
                            Recommandation
                        </h3>
                        <div className="space-y-6">
                            {stats?.clients_stats?.length > 0 && (
                                <>
                                    <div className="p-5 bg-slate-50 rounded-2xl border border-slate-100">
                                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Priorité d&apos;action</p>
                                        <p className="text-xl font-bold text-slate-800">
                                            {stats.clients_stats.sort((a, b) => (a.imported - a.treated) - (b.imported - b.treated))[0].nom}
                                        </p>
                                        <p className="text-sm text-slate-500 mt-2 font-medium italic">Accumulation de dossiers non traités détectée.</p>
                                    </div>
                                    <div className="flex items-center gap-3 text-emerald-400 text-sm font-bold">
                                        <CheckCircle className="w-5 h-5" />
                                        Système optimisé à 100%
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
});

StatsViewer.displayName = 'StatsViewer';

export default StatsViewer;