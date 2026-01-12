import React, { useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {
    Loader2, AlertCircle, UserPlus, Check, Search, Users,
    RefreshCw, ChevronLeft, ChevronRight, Download, X
} from 'lucide-react';
import { FixedSizeList as List } from 'react-window';
import config from '../config';

const api = axios.create({
    baseURL: config.API_URL,
    withCredentials: false,
    headers: { 'Content-Type': 'application/json' }
});

/**
 * Ligne d'enquête mémorisée
 */
const EnqueteRow = React.memo(({ enquete, index, enqueteurs, onAssign, isSelected }) => (
    <tr className={`hover:bg-slate-50 transition-colors ${isSelected ? 'bg-blue-50' : ''}`}>
        <td className="px-4 py-3 text-sm text-slate-500 font-medium">{index}</td>
        <td className="px-4 py-3 text-sm font-semibold text-slate-800">{enquete.numeroDossier}</td>
        <td className="px-4 py-3 text-sm text-slate-700">{enquete.nom}</td>
        <td className="px-4 py-3 text-sm text-slate-700">{enquete.prenom}</td>
        <td className="px-4 py-3">
            <span className={`px-2 py-1 text-xs font-semibold rounded
        ${enquete.typeDemande === 'ENQ'
                    ? 'bg-blue-50 text-blue-700'
                    : 'bg-amber-50 text-amber-700'}`}>
                {enquete.typeDemande}
            </span>
        </td>
        <td className="px-4 py-3">
            <select
                className="w-full px-2 py-1.5 text-sm border border-slate-200 rounded-lg bg-white
                   focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                value={enquete.enqueteurId || ''}
                onChange={(e) => onAssign(enquete.numeroDossier, e.target.value)}
            >
                <option value="">Sélectionner...</option>
                {enqueteurs.map((enq) => (
                    <option key={enq.id} value={enq.id}>{enq.nom} {enq.prenom}</option>
                ))}
            </select>
        </td>
    </tr>
));

EnqueteRow.displayName = 'EnqueteRow';
EnqueteRow.propTypes = {
    enquete: PropTypes.shape({
        numeroDossier: PropTypes.string,
        nom: PropTypes.string,
        prenom: PropTypes.string,
        typeDemande: PropTypes.string,
        enqueteurId: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    }).isRequired,
    index: PropTypes.number.isRequired,
    enqueteurs: PropTypes.array.isRequired,
    onAssign: PropTypes.func.isRequired,
    isSelected: PropTypes.bool.isRequired
};

/**
 * Composant de pagination
 */
const Pagination = ({ currentPage, totalPages, itemsPerPage, setItemsPerPage, handlePageChange }) => (
    <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-slate-200">
        <div className="text-sm text-slate-500">
            Page <span className="font-medium text-slate-700">{currentPage}</span> sur{' '}
            <span className="font-medium text-slate-700">{totalPages}</span>
        </div>

        <div className="flex items-center gap-2">
            <button
                onClick={() => handlePageChange(1)}
                disabled={currentPage === 1}
                className="p-1.5 rounded border border-slate-200 text-slate-500 hover:bg-slate-50 
                   disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <ChevronLeft className="w-4 h-4" />
                <ChevronLeft className="w-4 h-4 -ml-2" />
            </button>
            <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="p-1.5 rounded border border-slate-200 text-slate-500 hover:bg-slate-50 
                   disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <ChevronLeft className="w-4 h-4" />
            </button>

            <span className="px-3 py-1 text-sm text-slate-600">{currentPage}</span>

            <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages}
                className="p-1.5 rounded border border-slate-200 text-slate-500 hover:bg-slate-50 
                   disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <ChevronRight className="w-4 h-4" />
            </button>
            <button
                onClick={() => handlePageChange(totalPages)}
                disabled={currentPage >= totalPages}
                className="p-1.5 rounded border border-slate-200 text-slate-500 hover:bg-slate-50 
                   disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <ChevronRight className="w-4 h-4" />
                <ChevronRight className="w-4 h-4 -ml-2" />
            </button>

            <select
                value={itemsPerPage}
                onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    handlePageChange(1);
                }}
                className="ml-2 px-2 py-1.5 text-sm border border-slate-200 rounded-lg"
            >
                {[10, 25, 50, 100].map(value => (
                    <option key={value} value={value}>{value} / page</option>
                ))}
            </select>
        </div>
    </div>
);

Pagination.propTypes = {
    currentPage: PropTypes.number.isRequired,
    totalPages: PropTypes.number.isRequired,
    itemsPerPage: PropTypes.number.isRequired,
    setItemsPerPage: PropTypes.func.isRequired,
    handlePageChange: PropTypes.func.isRequired
};

/**
 * AssignmentViewer - Gestion des assignations d'enquêtes
 */
const AssignmentViewer = () => {
    const [enquetes, setEnquetes] = useState([]);
    const [enqueteurs, setEnqueteurs] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(50);
    const [totalPages, setTotalPages] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');
    const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [startRange, setStartRange] = useState(1);
    const [endRange, setEndRange] = useState(1);
    const [selectedEnqueteur, setSelectedEnqueteur] = useState('');
    const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);
    const [exportingData, setExportingData] = useState(false);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm.toLowerCase()), 300);
        return () => clearTimeout(timer);
    }, [searchTerm]);

    // Fetch data
    const fetchData = useCallback(async (resetPage = false) => {
        try {
            setLoading(true);
            setError(null);
            setRefreshing(true);

            const page = resetPage ? 1 : currentPage;
            if (resetPage) setCurrentPage(1);

            const [enquetesRes, enqueteursRes] = await Promise.all([
                api.get(`/api/donnees?page=${page}&per_page=${itemsPerPage}`),
                api.get('/api/enqueteurs')
            ]);

            if (enquetesRes.data.success && Array.isArray(enquetesRes.data.data)) {
                setEnquetes(enquetesRes.data.data);
                setTotalPages(enquetesRes.data.pages || Math.ceil(enquetesRes.data.total / itemsPerPage) || 1);
            }
            if (enqueteursRes.data.success) {
                setEnqueteurs(enqueteursRes.data.data);
            }
        } catch (err) {
            setError('Erreur de chargement: ' + (err.response?.data?.error || err.message));
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, [currentPage, itemsPerPage]);

    useEffect(() => { fetchData(); }, [fetchData, currentPage]);

    // Filtered list
    const filteredEnquetes = useMemo(() => {
        if (!debouncedSearchTerm) return enquetes;
        return enquetes.filter(e =>
            (e.numeroDossier?.toLowerCase() || '').includes(debouncedSearchTerm) ||
            (e.nom?.toLowerCase() || '').includes(debouncedSearchTerm) ||
            (e.prenom?.toLowerCase() || '').includes(debouncedSearchTerm)
        );
    }, [enquetes, debouncedSearchTerm]);

    // Assignment handler
    const handleAssignment = useCallback(async (enqueteId, enqueteurId) => {
        try {
            setError(null);
            setEnquetes(prev => prev.map(e =>
                e.numeroDossier === enqueteId ? { ...e, enqueteurId: enqueteurId || null } : e
            ));

            const response = await api.post('/api/assign-enquete', {
                enqueteId,
                enqueteurId: enqueteurId || null
            });

            if (response.data.success) {
                setSuccessMessage('Assignation réussie');
                setTimeout(() => setSuccessMessage(''), 3000);
            } else {
                fetchData();
            }
        } catch (err) {
            fetchData();
            setError('Erreur: ' + (err.response?.data?.error || err.message));
        }
    }, [fetchData]);

    // Bulk assignment
    const handleBulkAssignment = useCallback(async () => {
        try {
            if (!selectedEnqueteur) {
                setError("Sélectionnez un enquêteur");
                return;
            }

            const start = Math.max(0, startRange - 1);
            const end = Math.min(endRange, filteredEnquetes.length);
            if (start >= end) {
                setError("Plage invalide");
                return;
            }

            const selected = filteredEnquetes.slice(start, end);

            setEnquetes(prev => prev.map(e => {
                const isInRange = selected.some(s => s.numeroDossier === e.numeroDossier);
                return isInRange ? { ...e, enqueteurId: selectedEnqueteur } : e;
            }));

            await Promise.all(selected.map(e =>
                api.post('/api/assign-enquete', {
                    enqueteId: e.numeroDossier,
                    enqueteurId: selectedEnqueteur
                })
            ));

            setSuccessMessage(`${selected.length} enquête(s) assignée(s)`);
            setShowBulkAssignModal(false);
            setSelectedEnqueteur('');
            fetchData();
        } catch (err) {
            fetchData();
            setError('Erreur: ' + (err.response?.data?.error || err.message));
        }
    }, [fetchData, filteredEnquetes, startRange, endRange, selectedEnqueteur]);


    // Export Word
    const handleExportWord = useCallback(async () => {
        try {
            setExportingData(true);
            const toExport = filteredEnquetes.map(e => ({ id: e.id }));
            if (toExport.length === 0) {
                setError("Aucune enquête à exporter");
                return;
            }

            const response = await api.post('/api/export-enquetes', { enquetes: toExport }, { responseType: 'blob' });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Export_${new Date().toISOString().split('T')[0]}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            setSuccessMessage(`${toExport.length} enquête(s) exportée(s)`);
        } catch (err) {
            setError(err.response?.data?.error || "Erreur d'export");
        } finally {
            setExportingData(false);
        }
    }, [filteredEnquetes]);

    const handlePageChange = useCallback((newPage) => setCurrentPage(newPage), []);

    return (
        <div className="min-h-screen bg-slate-50 p-6">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div>
                        <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                            <Users className="w-5 h-5 text-blue-500" />
                            Assignation des enquêtes
                        </h1>
                        <p className="text-sm text-slate-500 mt-0.5">
                            {filteredEnquetes.length} enquête(s) affichée(s)
                        </p>
                    </div>

                    <div className="flex flex-wrap gap-2">
                        <button
                            onClick={handleExportWord}
                            disabled={exportingData || filteredEnquetes.length === 0}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white 
                         bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                        >
                            {exportingData ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                            Word
                        </button>
                        <button
                            onClick={() => fetchData(true)}
                            disabled={refreshing}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 
                         bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                            Actualiser
                        </button>
                        <button
                            onClick={() => setShowBulkAssignModal(true)}
                            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white 
                         bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            <Users className="w-4 h-4" />
                            Assignation en masse
                        </button>
                    </div>
                </div>

                {/* Search bar */}
                <div className="relative max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Rechercher par numéro, nom ou prénom..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2.5 text-sm border border-slate-200 rounded-lg 
                       bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>

                {/* Messages */}
                {successMessage && (
                    <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                        <Check className="w-4 h-4 text-green-500" />
                        <span className="text-sm font-medium text-green-700">{successMessage}</span>
                    </div>
                )}
                {error && (
                    <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                        <AlertCircle className="w-4 h-4 text-red-500" />
                        <span className="text-sm font-medium text-red-700">{error}</span>
                        <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-600">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                )}

                {/* Content */}
                {loading && !refreshing ? (
                    <div className="flex justify-center items-center h-64 bg-white rounded-lg border border-slate-200">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : filteredEnquetes.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 bg-white rounded-lg border border-slate-200">
                        <UserPlus className="w-12 h-12 text-slate-300 mb-2" />
                        <p className="text-slate-500">Aucune enquête trouvée</p>
                    </div>
                ) : (
                    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="bg-slate-50 border-b border-slate-200">
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">#</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">N° Dossier</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Nom</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Prénom</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Type</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">Assignation</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {filteredEnquetes.map((enquete, index) => (
                                        <EnqueteRow
                                            key={enquete.numeroDossier || enquete.id}
                                            enquete={enquete}
                                            index={index + 1}
                                            enqueteurs={enqueteurs}
                                            onAssign={handleAssignment}
                                            isSelected={showBulkAssignModal && index + 1 >= startRange && index + 1 <= endRange}
                                        />
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <Pagination
                            currentPage={currentPage}
                            totalPages={totalPages}
                            itemsPerPage={itemsPerPage}
                            setItemsPerPage={setItemsPerPage}
                            handlePageChange={handlePageChange}
                        />
                    </div>
                )}

                {/* Modal assignation en masse */}
                {showBulkAssignModal && (
                    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-slate-800">Assignation en masse</h3>
                                <button onClick={() => setShowBulkAssignModal(false)} className="text-slate-400 hover:text-slate-600">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Plage de lignes (1 à {filteredEnquetes.length})
                                    </label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="number"
                                            min="1"
                                            max={filteredEnquetes.length}
                                            value={startRange}
                                            onChange={(e) => setStartRange(parseInt(e.target.value) || 1)}
                                            className="w-20 px-3 py-2 text-sm border border-slate-200 rounded-lg"
                                        />
                                        <span className="text-slate-500">à</span>
                                        <input
                                            type="number"
                                            min={startRange}
                                            max={filteredEnquetes.length}
                                            value={endRange}
                                            onChange={(e) => setEndRange(Math.min(parseInt(e.target.value) || startRange, filteredEnquetes.length))}
                                            className="w-20 px-3 py-2 text-sm border border-slate-200 rounded-lg"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Enquêteur
                                    </label>
                                    <select
                                        value={selectedEnqueteur}
                                        onChange={(e) => setSelectedEnqueteur(e.target.value)}
                                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg"
                                    >
                                        <option value="">Sélectionner un enquêteur...</option>
                                        {enqueteurs.map((enq) => (
                                            <option key={enq.id} value={enq.id}>{enq.nom} {enq.prenom}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="flex gap-2 pt-2">
                                    <button
                                        onClick={() => setShowBulkAssignModal(false)}
                                        className="flex-1 py-2.5 text-sm font-medium text-slate-600 bg-white border 
                               border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                                    >
                                        Annuler
                                    </button>
                                    <button
                                        onClick={handleBulkAssignment}
                                        className="flex-1 py-2.5 text-sm font-medium text-white bg-blue-600 
                               rounded-lg hover:bg-blue-700 transition-colors"
                                    >
                                        Assigner
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AssignmentViewer;