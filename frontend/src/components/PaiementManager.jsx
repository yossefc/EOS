import  { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Users, ArrowLeft, DollarSign, Calendar,  RefreshCw, CheckCircle, 
    AlertCircle, FileDown, Check, X, AlertTriangle, Clock, Search
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_URL;

const PaiementManager = () => {
    // États
    const [enqueteursAPayer, setEnqueteursAPayer] = useState([]);
    const [facturations, setFacturations] = useState([]);
    const [selectedEnqueteur, setSelectedEnqueteur] = useState(null);
    const [selectedFacturations, setSelectedFacturations] = useState([]);
    const [allFacturationsSelected, setAllFacturationsSelected] = useState(false);
    
    const [reference, setReference] = useState('');
    const [datePaiement, setDatePaiement] = useState(new Date().toISOString().split('T')[0]);
    
    const [view, setView] = useState('list'); // 'list', 'detail', 'history', 'stats'
    const [loading, setLoading] = useState(true);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    
    // Historique des paiements
    const [historiquePaiements, setHistoriquePaiements] = useState([]);
    const [loadingHistory, setLoadingHistory] = useState(false);
    
    // Statistiques par période
    const [statsPeriodes, setStatsPeriodes] = useState([]);
    const [loadingStats, setLoadingStats] = useState(false);
    
    // Filtres
    const [searchTerm, setSearchTerm] = useState('');
    
    // Chargement initial
    useEffect(() => {
        fetchEnqueteursAPayer();
    }, []);
    
    // Récupérer la liste des enquêteurs avec des paiements en attente
    const fetchEnqueteursAPayer = async () => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await axios.get(`${API_URL}/api/paiement/enqueteurs-a-payer`);
            
            if (response.data.success) {
                setEnqueteursAPayer(response.data.data);
            } else {
                throw new Error(response.data.error || "Erreur lors de la récupération des enquêteurs à payer");
            }
        } catch (error) {
            console.error("Erreur:", error);
            setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
            setLoading(false);
        }
    };
    
    // Récupérer les facturations non payées d'un enquêteur
    const fetchFacturationsEnqueteur = async (enqueteurId) => {
        try {
            setLoadingDetail(true);
            setError(null);
            
            const response = await axios.get(`${API_URL}/api/paiement/enqueteur/${enqueteurId}/facturations`);
            
            if (response.data.success) {
                setFacturations(response.data.data.facturations);
                setSelectedEnqueteur(response.data.data.enqueteur);
                setSelectedFacturations([]);
                setAllFacturationsSelected(false);
                setView('detail');
            } else {
                throw new Error(response.data.error || "Erreur lors de la récupération des facturations");
            }
        } catch (error) {
            console.error("Erreur:", error);
            setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
            setLoadingDetail(false);
        }
    };
    
    // Récupérer l'historique des paiements
    const fetchHistoriquePaiements = async () => {
        try {
            setLoadingHistory(true);
            setError(null);
            
            const response = await axios.get(`${API_URL}/api/paiement/historique`);
            
            if (response.data.success) {
                setHistoriquePaiements(response.data.data);
                setView('history');
            } else {
                throw new Error(response.data.error || "Erreur lors de la récupération de l'historique");
            }
        } catch (error) {
            console.error("Erreur:", error);
            setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
            setLoadingHistory(false);
        }
    };
    
    // Récupérer les statistiques par période
    const fetchStatsPeriodes = async () => {
        try {
            setLoadingStats(true);
            setError(null);
            
            const response = await axios.get(`${API_URL}/api/paiement/stats/periodes`);
            
            if (response.data.success) {
                setStatsPeriodes(response.data.data);
                setView('stats');
            } else {
                throw new Error(response.data.error || "Erreur lors de la récupération des statistiques");
            }
        } catch (error) {
            console.error("Erreur:", error);
            setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
            setLoadingStats(false);
        }
    };
    
    // Marquer les facturations sélectionnées comme payées
    const handleMarkAsPaid = async () => {
        if (selectedFacturations.length === 0) {
            setError("Veuillez sélectionner au moins une facturation");
            return;
        }
        
        try {
            setSubmitting(true);
            setError(null);
            
            const response = await axios.post(`${API_URL}/api/paiement/marquer-payes`, {
                facturation_ids: selectedFacturations,
                reference_paiement: reference,
                date_paiement: datePaiement
            });
            
            if (response.data.success) {
                setSuccess(`${response.data.count} facturations marquées comme payées`);
                
                // Mettre à jour la liste des facturations
                const updatedFacturations = facturations.filter(
                    f => !selectedFacturations.includes(f.id)
                );
                
                setFacturations(updatedFacturations);
                setSelectedFacturations([]);
                
                // Si toutes les facturations ont été payées, retourner à la liste
                if (updatedFacturations.length === 0) {
                    setTimeout(() => {
                        setView('list');
                        fetchEnqueteursAPayer();
                    }, 1500);
                }
            } else {
                throw new Error(response.data.error || "Erreur lors du marquage des paiements");
            }
        } catch (error) {
            console.error("Erreur:", error);
            setError(error.response?.data?.error || error.message || "Une erreur s'est produite");
        } finally {
            setSubmitting(false);
        }
    };
    
    // Générer un relevé PDF
    const handleGeneratePDF = () => {
        if (!selectedEnqueteur) return;
        
        // Ouvrir un nouvel onglet pour télécharger le PDF
        window.open(`${API_URL}/api/paiement/generer-pdf/${selectedEnqueteur.id}`, '_blank');
    };
    
    // Sélectionner/désélectionner toutes les facturations
    const handleSelectAll = (checked) => {
        if (checked) {
            setSelectedFacturations(facturations.map(f => f.id));
        } else {
            setSelectedFacturations([]);
        }
        setAllFacturationsSelected(checked);
    };
    
    // Sélectionner/désélectionner une facturation
    const handleSelectFacturation = (id, checked) => {
        if (checked) {
            setSelectedFacturations(prev => [...prev, id]);
        } else {
            setSelectedFacturations(prev => prev.filter(fId => fId !== id));
        }
    };
    
    // Effet pour mettre à jour l'état de sélection globale
    useEffect(() => {
        if (facturations.length > 0 && selectedFacturations.length === facturations.length) {
            setAllFacturationsSelected(true);
        } else {
            setAllFacturationsSelected(false);
        }
    }, [selectedFacturations, facturations]);
    
    // Filtrer les enquêteurs selon le terme de recherche
    const filteredEnqueteurs = enqueteursAPayer.filter(enqueteur => 
        searchTerm === '' || 
        enqueteur.nom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        enqueteur.prenom.toLowerCase().includes(searchTerm.toLowerCase()) ||
        enqueteur.email.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // Calculer le montant total sélectionné
    const montantTotalSelected = facturations
        .filter(f => selectedFacturations.includes(f.id))
        .reduce((sum, f) => sum + f.montant, 0);
    
    // Rendu de la liste des enquêteurs à payer
    const renderEnqueteurList = () => (
        <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                <h3 className="font-medium">Enquêteurs avec des paiements en attente</h3>
                <div className="flex gap-2">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Rechercher un enquêteur..."
                            className="pl-9 pr-4 py-2 border rounded-md"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={fetchEnqueteursAPayer}
                        className="flex items-center gap-1 px-3 py-2 border rounded hover:bg-gray-50"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Actualiser</span>
                    </button>
                </div>
            </div>
            
            {loading ? (
                <div className="flex justify-center items-center p-8">
                    <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                </div>
            ) : filteredEnqueteurs.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                    <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                    <p className="text-lg font-medium mb-2">Tous les paiements sont à jour!</p>
                    <p>Il n&apos;y a aucun paiement en attente pour le moment.</p>
                </div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Enquêteur
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Email
                                </th>
                                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Enquêtes à payer
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Montant total
                                </th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {filteredEnqueteurs.map((enqueteur) => (
                                <tr key={enqueteur.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="text-sm font-medium text-gray-900">
                                            {enqueteur.nom} {enqueteur.prenom}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {enqueteur.email}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                            {enqueteur.nombre_facturations}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">
                                        {enqueteur.montant_total.toFixed(2)} €
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                        <button
                                            onClick={() => fetchFacturationsEnqueteur(enqueteur.id)}
                                            className="text-blue-600 hover:text-blue-900 px-3 py-1 border border-blue-400 rounded-md hover:bg-blue-50"
                                        >
                                            Voir détail
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
    
    // Rendu du détail des facturations d'un enquêteur
    const renderFacturationsDetail = () => (
        <div className="space-y-4">
            <button
                onClick={() => setView('list')}
                className="flex items-center gap-1 px-3 py-1 text-blue-600 hover:underline"
            >
                <ArrowLeft className="w-4 h-4" />
                <span>Retour à la liste</span>
            </button>
            
            <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b">
                    <h3 className="font-medium text-lg mb-2">
                        Facturations en attente pour {selectedEnqueteur?.prenom} {selectedEnqueteur?.nom}
                    </h3>
                    <p className="text-gray-600 text-sm">{selectedEnqueteur?.email}</p>
                </div>
                
                {loadingDetail ? (
                    <div className="flex justify-center items-center p-8">
                        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : facturations.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                        <p>Toutes les facturations ont été payées!</p>
                    </div>
                ) : (
                    <div className="p-4">
                        <div className="flex justify-between items-center mb-4">
                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    checked={allFacturationsSelected}
                                    onChange={(e) => handleSelectAll(e.target.checked)}
                                    className="rounded text-blue-600 focus:ring-blue-500 h-4 w-4"
                                />
                                <span className="text-sm">
                                    Sélectionner toutes les facturations ({facturations.length})
                                </span>
                            </div>
                            
                            <div className="flex items-center gap-4">
                                <div className="text-sm">
                                    <span className="text-gray-600">Sélectionnés: </span>
                                    <span className="font-medium">{selectedFacturations.length} facturations</span>
                                    {selectedFacturations.length > 0 && (
                                        <span className="ml-2 font-medium text-green-600">
                                            {montantTotalSelected.toFixed(2)} €
                                        </span>
                                    )}
                                </div>
                                
                                <button
                                    onClick={handleGeneratePDF}
                                    className="flex items-center gap-1 px-3 py-1 border border-gray-300 rounded-md hover:bg-gray-50"
                                >
                                    <FileDown className="w-4 h-4" />
                                    <span>Générer PDF</span>
                                </button>
                            </div>
                        </div>
                        
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-4 py-3 w-12"></th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            N° Dossier
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Éléments
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Résultat
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Date
                                        </th>
                                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Montant
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {facturations.map((facturation) => (
                                        <tr key={facturation.id} className="hover:bg-gray-50">
                                            <td className="px-4 py-3 text-center">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedFacturations.includes(facturation.id)}
                                                    onChange={(e) => handleSelectFacturation(facturation.id, e.target.checked)}
                                                    className="rounded text-blue-600 focus:ring-blue-500 h-4 w-4"
                                                />
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {facturation.numeroDossier}
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                {facturation.elements_retrouves || '-'}
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                    {facturation.code_resultat === 'P' ? 'Positif' : 
                                                     facturation.code_resultat === 'N' ? 'Négatif' : 
                                                     facturation.code_resultat === 'H' ? 'Confirmé' : 
                                                     facturation.code_resultat || '-'}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                                                {facturation.date}
                                            </td>
                                            <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium">
                                                {facturation.montant.toFixed(2)} €
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
            
            {/* Formulaire de paiement */}
            {selectedFacturations.length > 0 && (
                <div className="bg-white rounded-lg shadow p-4">
                    <h3 className="font-medium mb-4">Marquer comme payé</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Référence du paiement
                            </label>
                            <input
                                type="text"
                                value={reference}
                                onChange={(e) => setReference(e.target.value)}
                                placeholder="Ex: VIREMENT-2023-03"
                                className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Date du paiement
                            </label>
                            <input
                                type="date"
                                value={datePaiement}
                                onChange={(e) => setDatePaiement(e.target.value)}
                                className="w-full px-3 py-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <div className="text-sm">
                            <span className="text-gray-700">Total à payer: </span>
                            <span className="font-medium text-green-600">{montantTotalSelected.toFixed(2)} €</span>
                        </div>
                        <button
                            onClick={handleMarkAsPaid}
                            disabled={submitting}
                            className="flex items-center gap-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        >
                            {submitting ? (
                                <>
                                    <RefreshCw className="w-4 h-4 animate-spin" />
                                    <span>Traitement...</span>
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="w-4 h-4" />
                                    <span>Marquer comme payé</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
    
    // Rendu de l'historique des paiements
    const renderHistoriquePaiements = () => (
        <div className="space-y-4">
            <button
                onClick={() => setView('list')}
                className="flex items-center gap-1 px-3 py-1 text-blue-600 hover:underline"
            >
                <ArrowLeft className="w-4 h-4" />
                <span>Retour à la liste</span>
            </button>
            
            <div className="bg-white rounded-lg shadow">
                <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                    <h3 className="font-medium">Historique des paiements</h3>
                    <button
                        onClick={fetchHistoriquePaiements}
                        className="flex items-center gap-1 px-3 py-1 border rounded hover:bg-gray-50"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Actualiser</span>
                    </button>
                </div>
                
                {loadingHistory ? (
                    <div className="flex justify-center items-center p-8">
                        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : historiquePaiements.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <Clock className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>Aucun historique de paiement disponible.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Référence
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Date
                                    </th>
                                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Nombre d&apos;enquêtes
                                    </th>
                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Montant total
                                    </th>
                                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Période
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {historiquePaiements.map((paiement, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {paiement.reference}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {paiement.date}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {paiement.nombre_facturations}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">
                                            {paiement.montant_total.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                                            {paiement.periode.debut} au {paiement.periode.fin}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
    
    // Rendu des statistiques par période
    const renderStatsPeriodes = () => (
        <div className="space-y-4">
            <button
                onClick={() => setView('list')}
                className="flex items-center gap-1 px-3 py-1 text-blue-600 hover:underline"
            >
                <ArrowLeft className="w-4 h-4" />
                <span>Retour à la liste</span>
            </button>
            
            <div className="bg-white rounded-lg shadow">
                <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                    <h3 className="font-medium">Statistiques par période</h3>
                    <button
                        onClick={fetchStatsPeriodes}
                        className="flex items-center gap-1 px-3 py-1 border rounded hover:bg-gray-50"
                    >
                        <RefreshCw className="w-4 h-4" />
                        <span>Actualiser</span>
                    </button>
                </div>
                
                {loadingStats ? (
                    <div className="flex justify-center items-center p-8">
                        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                ) : statsPeriodes.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>Aucune statistique disponible.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Période
                                    </th>
                                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Enquêtes terminées
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
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {statsPeriodes.map((stat, index) => (
                                    <tr key={index} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {stat.periode}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {stat.nb_enquetes}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">
                                            {stat.montant_facture.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium">
                                            {stat.montant_paye.toFixed(2)} €
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600">
                                            {stat.marge.toFixed(2)} €
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            
            {/* Graphique des tendances */}
            {statsPeriodes.length > 0 && (
                <div className="bg-white rounded-lg shadow p-4">
                    <h3 className="font-medium mb-4">Tendances sur les 12 derniers mois</h3>
                    
                    <div className="h-64 mt-4">
                        {/* Graphique simple (on pourrait utiliser recharts pour plus de sophistication) */}
                        <div className="h-full flex items-end space-x-1">
                            {statsPeriodes.map((stat, index) => {
                                const maxMontant = Math.max(...statsPeriodes.map(s => s.montant_facture));
                                const height = (stat.montant_facture / maxMontant) * 100;
                                
                                return (
                                    <div key={index} className="flex-1 flex flex-col items-center h-full pt-8">
                                        <div className="flex-1 w-full flex items-end">
                                            <div 
                                                className="w-full bg-blue-500 rounded-t"
                                                style={{ height: `${height}%` }}
                                            ></div>
                                        </div>
                                        <div className="text-xs mt-2 -rotate-45 origin-top-left translate-y-6 translate-x-2">
                                            {stat.periode}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
    
    // Messages d'erreur et de succès
    const renderMessages = () => (
        <>
            {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                    <span>{error}</span>
                    <button onClick={() => setError(null)} className="ml-auto text-red-700 hover:text-red-900">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}
            
            {success && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md flex items-center gap-2">
                    <Check className="w-5 h-5 flex-shrink-0" />
                    <span>{success}</span>
                    <button onClick={() => setSuccess(null)} className="ml-auto text-green-700 hover:text-green-900">
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}
        </>
    );
    
    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <DollarSign className="w-6 h-6 text-green-500" />
                    Gestion des Paiements
                </h2>
                
                <div className="flex gap-2">
                    <button
                        onClick={() => setView('list')}
                        className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                            view === 'list' ? 'bg-gray-100 text-gray-800' : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <Users className="w-4 h-4" />
                        <span>Enquêteurs</span>
                    </button>
                    <button
                        onClick={fetchHistoriquePaiements}
                        className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                            view === 'history' ? 'bg-gray-100 text-gray-800' : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <Clock className="w-4 h-4" />
                        <span>Historique</span>
                    </button>
                    <button
                        onClick={fetchStatsPeriodes}
                        className={`px-3 py-1 rounded text-sm flex items-center gap-1 ${
                            view === 'stats' ? 'bg-gray-100 text-gray-800' : 'text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                        <Calendar className="w-4 h-4" />
                        <span>Statistiques</span>
                    </button>
                </div>
            </div>
            
            {renderMessages()}
            
            {view === 'list' && renderEnqueteurList()}
            {view === 'detail' && renderFacturationsDetail()}
            {view === 'history' && renderHistoriquePaiements()}
            {view === 'stats' && renderStatsPeriodes()}
        </div>
    );
};

export default PaiementManager;