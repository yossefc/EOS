import { useState, useEffect, useCallback } from 'react';
import { 
    X, Clock, AlertCircle, FileText, 
    RefreshCw, Archive, User, Hash, History,
    Users
} from 'lucide-react';
import PropTypes from 'prop-types';

// Configuration API - remplacez par votre URL d'API
const API_URL = 'http://localhost:5000';

const HistoryModal = ({ isOpen, onClose, donneeId, donnee }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [historyData, setHistoryData] = useState(null);
    const [isUsingNewAPI, setIsUsingNewAPI] = useState(false);
    
    // Nouveaux états pour les données complètes
    const [archivesEnquetes, setArchivesEnquetes] = useState(null);
    const [archivesEnqueteurs, setArchivesEnqueteurs] = useState(null);
    const [motifContestationDetail, setMotifContestationDetail] = useState(null);
    const [loadingArchives, setLoadingArchives] = useState(true);

    // Messages d'interface utilisateur avec apostrophes corrigées
    const messages = {
        noHistoryData: "Aucune donnée d&apos;historique disponible",
        noArchiveFound: "Aucune archive d&apos;enquête trouvée",
        noEnqueteurArchiveFound: "Aucune archive d&apos;enquêteur trouvée",
        noHistoryAvailable: "Aucun historique disponible"
    };

    // Charger les données des archives et motifs
    const fetchArchivesData = useCallback(async () => {
        try {
            setLoadingArchives(true);
            
            // Initialiser les états à des tableaux vides pour permettre l'affichage des sections
            setArchivesEnquetes([]);
            setArchivesEnqueteurs([]);
            setMotifContestationDetail(null);
            
            // Récupérer toutes les données des archives pour cette enquête
            const promises = [
                fetch(`${API_URL}/api/archives-enquetes/${donneeId}`).catch(() => ({ ok: false })),
                fetch(`${API_URL}/api/archives-enqueteurs/${donneeId}`).catch(() => ({ ok: false })),
                fetch(`${API_URL}/api/donnees-complete/${donneeId}`).catch(() => ({ ok: false }))
            ];
            
            // Si on a un numéro de dossier, essayer aussi de récupérer par numéro de dossier
            if (donnee?.numeroDossier) {
                promises.push(
                    fetch(`${API_URL}/api/historique-enquete/${donnee.numeroDossier}`).catch(() => ({ ok: false }))
                );
            }
            
            const [archivesEnquetesResponse, archivesEnqueteursResponse, motifsResponse, historiqueResponse] = await Promise.all(promises);
            
            let archivesEnquetesFound = [];
            let archivesEnqueteursFound = [];
            
            // Archives enquêtes - Route directe
            if (archivesEnquetesResponse.ok) {
                const archivesEnquetesData = await archivesEnquetesResponse.json();
                if (archivesEnquetesData.success && archivesEnquetesData.data) {
                    archivesEnquetesFound = Array.isArray(archivesEnquetesData.data) ? archivesEnquetesData.data : [archivesEnquetesData.data];
                }
            }
            
            // Archives enquêteurs - Route directe
            if (archivesEnqueteursResponse.ok) {
                const archivesEnqueteursData = await archivesEnqueteursResponse.json();
                if (archivesEnqueteursData.success && archivesEnqueteursData.data) {
                    archivesEnqueteursFound = Array.isArray(archivesEnqueteursData.data) ? archivesEnqueteursData.data : [archivesEnqueteursData.data];
                }
            }
            
            // Motifs contestation detail
            if (motifsResponse.ok) {
                const motifsData = await motifsResponse.json();
                if (motifsData.success && motifsData.data) {
                    setMotifContestationDetail({
                        motif_contestation_detail: motifsData.data.motif_contestation_detail,
                        motif_contestation_code: motifsData.data.motif_contestation_code,
                        motifDeContestation: motifsData.data.motifDeContestation,
                        codeMotif: motifsData.data.codeMotif, // Ajouter le codeMotif comme fallback
                        date_contestation: motifsData.data.date_contestation,
                        statut_validation: motifsData.data.statut_validation
                    });
                }
            }
            
            // NOUVELLES DONNÉES d'historique via numéro de dossier - UTILISER TOUTES LES DONNÉES
            if (historiqueResponse && historiqueResponse.ok) {
                const historiqueData = await historiqueResponse.json();
                if (historiqueData.success && historiqueData.data) {
                    console.log('Données historique complètes:', historiqueData.data);
                    
                    // Ajouter les archives depuis l'historique si disponibles
                    if (historiqueData.data.archives_info) {
                        console.log('Archives trouvées via historique:', historiqueData.data.archives_info);
                        
                        // Archives enquêtes depuis l'historique
                        if (historiqueData.data.archives_info.enquete) {
                            const archiveEnquete = {
                                ...historiqueData.data.archives_info.enquete,
                                // Ajouter des données de l'enquête principale si disponibles
                                ...(historiqueData.data.enquete_origine || {}),
                                source: 'historique_enquete'
                            };
                            archivesEnquetesFound.push(archiveEnquete);
                        }
                        
                        // Archives enquêteurs depuis l'historique
                        if (historiqueData.data.archives_info.enqueteur) {
                            const archiveEnqueteur = {
                                ...historiqueData.data.archives_info.enqueteur,
                                // Ajouter les données enquêteur détaillées si disponibles
                                ...(historiqueData.data.archives_enqueteur || {}),
                                source: 'historique_enqueteur'
                            };
                            archivesEnqueteursFound.push(archiveEnqueteur);
                        }
                    }
                    
                    // Ajouter TOUTES les données d'archive enquêteur détaillées si disponibles
                    if (historiqueData.data.archives_enqueteur) {
                        const archiveEnqueteurComplete = {
                            ...historiqueData.data.archives_enqueteur,
                            source: 'archives_enqueteur_detaillees',
                            numero_dossier_recherche: donnee?.numeroDossier
                        };
                        archivesEnqueteursFound.push(archiveEnqueteurComplete);
                    }
                    
                    // Ajouter les données d'enquête origine si c'est une archive
                    if (historiqueData.data.enquete_origine && historiqueData.data.est_archive) {
                        const enqueteOriginArchive = {
                            ...historiqueData.data.enquete_origine,
                            source: 'enquete_origine_archivee',
                            numero_dossier_recherche: donnee?.numeroDossier
                        };
                        archivesEnquetesFound.push(enqueteOriginArchive);
                    }
                }
            }
            
            // Nettoyer et dédupliquer les archives (éviter les doublons)
            const archivesEnquetesUniques = archivesEnquetesFound.filter((archive, index, self) => 
                index === self.findIndex(a => a.id === archive.id || (a.original_id === archive.original_id && a.archived_at === archive.archived_at))
            );
            
            const archivesEnqueteursUniques = archivesEnqueteursFound.filter((archive, index, self) => 
                index === self.findIndex(a => a.id === archive.id || (a.original_id === archive.original_id && a.archived_at === archive.archived_at))
            );
            
            // Définir les données finales
            setArchivesEnquetes(archivesEnquetesUniques);
            setArchivesEnqueteurs(archivesEnqueteursUniques);
            
            console.log(`ARCHIVES FINALES - Enquêtes: ${archivesEnquetesUniques.length}, Enquêteurs: ${archivesEnqueteursUniques.length}`);
            
        } catch (error) {
            console.error('Erreur lors du chargement des archives:', error);
            // Même en cas d'erreur, on initialise à des tableaux vides
            setArchivesEnquetes([]);
            setArchivesEnqueteurs([]);
        } finally {
            setLoadingArchives(false);
        }
    }, [donneeId, donnee]);

    const fetchHistoryData = useCallback(async () => {
        try {
          setLoading(true);
          setError(null);
          
          // Détecter si c'est une contestation et si on a le numeroDossier
          const isContestation = donnee?.typeDemande === 'CON' && donnee?.numeroDossier;
          
          let response;
          if (isContestation) {
            // Utiliser la nouvelle API pour les contestations
            setIsUsingNewAPI(true);
            response = await fetch(`${API_URL}/api/historique-enquete/${donnee.numeroDossier}`);
          } else {
            // Utiliser l'ancienne API pour les autres cas
            setIsUsingNewAPI(false);
            response = await fetch(`${API_URL}/api/donnees/${donneeId}/historique`);
          }
          
          const data = await response.json();
          
          if (data.success) {
            setHistoryData(data.data);
          } else {
            throw new Error(data.error || "Erreur lors de la récupération de l'historique");
          }
        } catch (error) {
          console.error("Erreur:", error);
          setError(error.message || "Une erreur s'est produite");
        } finally {
          setLoading(false);
        }
    }, [donneeId, donnee]);
      
    useEffect(() => {
        if (isOpen && donneeId) {
            fetchHistoryData();
            fetchArchivesData();
        }
    }, [isOpen, donneeId, fetchHistoryData, fetchArchivesData]);

    // Formater la date
    const formatDate = (dateString) => {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('fr-FR');
    };

    // Helper pour obtenir le libellé du motif de contestation
    const getMotifContestationLabel = (code) => {
        const motifs = {
            'A01': 'Adresse incorrecte ou incomplète',
            'A02': 'Personne déménagée sans laisser d&apos;adresse',
            'A03': 'Adresse introuvable',
            'T01': 'Téléphone incorrect ou non attribué',
            'T02': 'Personne injoignable par téléphone',
            'E01': 'Employeur incorrect',
            'E02': 'Personne ne travaille plus chez cet employeur',
            'D01': 'Personne décédée',
            'D02': 'Date de décès incorrecte',
            'I01': 'Informations personnelles incorrectes',
            'I02': 'Identité non confirmée',
            'R01': 'Résultats insuffisants',
            'R02': 'Informations manquantes',
            'F01': 'Fraude suspectée',
            'F02': 'Fausse déclaration',
            'AUT': 'Autre motif',
            '1': 'Courriers reviennent NPAI',
            '2': 'Adresse facturée est celle d&apos;un tiers qui ne connaît pas le client',
            '3': 'Adresse facturée est celle d&apos;un tiers chez qui n&apos;est plus le client',
            '4': 'Téléphone hors service/pas attribué',
            '5': 'Client inconnu à ce numéro',
            '6': 'Téléphone ne connaît pas la personne recherchée',
            '7': 'Adresse non conforme',
            '8': 'Personne non domiciliée à cette adresse',
            '9': 'Informations partielles ou insuffisantes',
            '10': 'Refus de communiquer les informations'
        };
        return motifs[code] || code || 'Motif non spécifié';
    };

    // Helper pour afficher le statut de validation
    const getValidationStatusDisplay = (status) => {
        const colors = {
            'confirmee': 'bg-green-100 text-green-800',
            'refusee': 'bg-red-100 text-red-800',
            'en_attente': 'bg-orange-100 text-orange-800',
            'validee': 'bg-blue-100 text-blue-800'
        };
        
        const labels = {
            'confirmee': 'Confirmée',
            'refusee': 'Refusée',
            'en_attente': 'En attente',
            'validee': 'Validée'
        };
        
        return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full ${colors[status] || 'bg-gray-100 text-gray-500'}`}>
                {labels[status] || status || 'Non défini'}
            </span>
        );
    };

    // Composant pour afficher les motifs de contestation complets
    const MotifContestationSection = ({ motifs, title = "Motifs de contestation" }) => {
        if (!motifs || (!motifs.motif_contestation_code && !motifs.motif_contestation_detail && !motifs.motifDeContestation)) {
            return null;
        }

        return (
            <div className="bg-white border border-amber-200 rounded-lg overflow-hidden">
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 px-4 py-3 border-b border-amber-200">
                    <h4 className="font-medium text-amber-800 flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        {title}
                    </h4>
                </div>
                
                <div className="p-4 space-y-4">
                    {/* Codes de motif */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Code principal */}
                        {motifs.motif_contestation_code && (
                            <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                                <h5 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                    <Hash className="w-4 h-4" />
                                    Code principal
                                </h5>
                                <div className="bg-white p-3 rounded-lg border border-amber-200">
                                    <p className="font-mono text-lg text-center font-bold text-amber-900 mb-2">
                                        {motifs.motif_contestation_code}
                                    </p>
                                    <p className="text-sm text-gray-600 text-center">
                                        {getMotifContestationLabel(motifs.motif_contestation_code)}
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Code legacy */}
                        {motifs.codeMotif && (
                            <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                                <h5 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                    <Hash className="w-4 h-4" />
                                    Code legacy
                                </h5>
                                <div className="bg-white p-3 rounded-lg border border-amber-200">
                                    <p className="font-mono text-lg text-center font-bold text-amber-900 mb-2">
                                        {motifs.codeMotif}
                                    </p>
                                    <p className="text-sm text-gray-600 text-center">
                                        {getMotifContestationLabel(motifs.codeMotif)}
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Détails du motif */}
                    {(motifs.motif_contestation_detail || motifs.motifDeContestation) && (
                        <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                            <h5 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                <FileText className="w-4 h-4" />
                                Détails du motif
                            </h5>
                            <div className="space-y-3">
                                {motifs.motif_contestation_detail && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Description détaillée</p>
                                        <p className="text-gray-800 whitespace-pre-wrap">
                                            {motifs.motif_contestation_detail}
                                        </p>
                                    </div>
                                )}
                                {motifs.motifDeContestation && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Motif legacy</p>
                                        <p className="text-gray-800">
                                            {motifs.motifDeContestation}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Informations de suivi */}
                    {(motifs.date_contestation || motifs.statut_validation || motifs.validee_par || motifs.date_validation) && (
                        <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                            <h5 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                <Clock className="w-4 h-4" />
                                Informations de suivi
                            </h5>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                                {motifs.date_contestation && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Date contestation</p>
                                        <p className="text-gray-800">
                                            {formatDate(motifs.date_contestation)}
                                        </p>
                                    </div>
                                )}
                                {motifs.statut_validation && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Statut</p>
                                        {getValidationStatusDisplay(motifs.statut_validation)}
                                    </div>
                                )}
                                {motifs.validee_par && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Validée par</p>
                                        <p className="text-gray-800">{motifs.validee_par}</p>
                                    </div>
                                )}
                                {motifs.date_validation && (
                                    <div className="bg-white p-3 rounded-lg border border-amber-200">
                                        <p className="text-sm text-amber-600 mb-1">Date validation</p>
                                        <p className="text-gray-800">
                                            {formatDate(motifs.date_validation)}
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        );
    };

    // Validation des props pour MotifContestationSection
    MotifContestationSection.propTypes = {
        motifs: PropTypes.shape({
            motif_contestation_code: PropTypes.string,
            motif_contestation_detail: PropTypes.string,
            motifDeContestation: PropTypes.string,
            codeMotif: PropTypes.string,
            date_contestation: PropTypes.string,
            statut_validation: PropTypes.string,
            validee_par: PropTypes.string,
            date_validation: PropTypes.string
        }),
        title: PropTypes.string
    };
    
    if (!isOpen) return null;
    
    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-auto">
            <div className="bg-white rounded-xl w-full max-w-7xl max-h-[90vh] overflow-y-auto">
                {/* En-tête fixe */}
                <div className="bg-gradient-to-r from-indigo-600 to-indigo-800 p-4 rounded-t-xl sticky top-0 z-10 shadow-md">
                    <div className="flex justify-between items-start">
                        <div className="text-white">
                            <h2 className="text-xl font-bold flex items-center gap-2">
                                <History className="w-5 h-5" />
                                {isUsingNewAPI ? 'Historique complet de l\'enquête' : 'Historique détaillé du dossier'}
                            </h2>
                            <p className="text-sm text-indigo-100 mt-1">
                                {isUsingNewAPI 
                                    ? 'Données complètes depuis les archives et contestations'
                                    : 'Suivi des modifications, motifs de contestation et archives'
                                }
                            </p>
                        </div>
                        <button 
                            onClick={onClose} 
                            className="text-white/70 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>
                </div>

                {/* Contenu principal */}
                <div className="p-6">
                    {loading ? (
                        <div className="flex justify-center items-center py-20">
                            <RefreshCw className="w-8 h-8 animate-spin text-indigo-500" />
                        </div>
                    ) : error ? (
                        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                            <div className="flex items-center gap-2">
                                <AlertCircle className="w-5 h-5" />
                                <span>{error}</span>
                            </div>
                        </div>
                    ) : historyData ? (
                        <div className="space-y-6">
                            {/* Grille principale en 2 colonnes */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Colonne de gauche - Informations principales */}
                                <div className="space-y-6">
                                    {/* Section 1: Informations de base */}
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200">
                                            <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                                                <User className="w-5 h-5 text-gray-600" />
                                                Informations de base
                                            </h3>
                                        </div>
                                        <div className="p-4">
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <p className="text-sm text-gray-500">Numéro dossier</p>
                                                    <p className="font-medium">{historyData.numero_dossier || '-'}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-500">Type demande</p>
                                                    <p className="font-medium">{historyData.type_demande || '-'}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-500">Date création</p>
                                                    <p className="font-medium">{formatDate(historyData.created_at)}</p>
                                                </div>
                                                <div>
                                                    <p className="text-sm text-gray-500">Dernière mise à jour</p>
                                                    <p className="font-medium">{formatDate(historyData.updated_at)}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Section 2: Motifs de contestation */}
                                    {motifContestationDetail && (
                                        <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                                            <div className="bg-gradient-to-r from-amber-50 to-orange-50 px-4 py-3 border-b border-amber-200">
                                                <h3 className="font-semibold text-amber-800 flex items-center gap-2">
                                                    <AlertCircle className="w-5 h-5" />
                                                    Motifs de contestation
                                                </h3>
                                            </div>
                                            <div className="p-4 space-y-4">
                                                {/* Code motif */}
                                                {(motifContestationDetail.motif_contestation_code || motifContestationDetail.codeMotif) && (
                                                    <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                                                        <h4 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                                            <Hash className="w-4 h-4" />
                                                            Code(s) motif
                                                        </h4>
                                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                            {motifContestationDetail.motif_contestation_code && (
                                                                <div>
                                                                    <p className="text-sm text-amber-600 mb-1">Code principal</p>
                                                                    <div className="bg-white p-2 rounded border border-amber-200">
                                                                        <p className="font-mono text-lg text-center font-bold text-amber-900">
                                                                            {motifContestationDetail.motif_contestation_code}
                                                                        </p>
                                                                        <p className="text-sm text-gray-600 mt-1 text-center">
                                                                            {getMotifContestationLabel(motifContestationDetail.motif_contestation_code)}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {motifContestationDetail.codeMotif && (
                                                                <div>
                                                                    <p className="text-sm text-amber-600 mb-1">Code legacy</p>
                                                                    <div className="bg-white p-2 rounded border border-amber-200">
                                                                        <p className="font-mono text-lg text-center font-bold text-amber-900">
                                                                            {motifContestationDetail.codeMotif}
                                                                        </p>
                                                                        <p className="text-sm text-gray-600 mt-1 text-center">
                                                                            {getMotifContestationLabel(motifContestationDetail.codeMotif)}
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Détails du motif */}
                                                {(motifContestationDetail.motif_contestation_detail || motifContestationDetail.motifDeContestation) && (
                                                    <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                                                        <h4 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                                            <FileText className="w-4 h-4" />
                                                            Détails du motif
                                                        </h4>
                                                        <div className="space-y-3">
                                                            {motifContestationDetail.motif_contestation_detail && (
                                                                <div className="bg-white p-3 rounded border border-amber-200">
                                                                    <p className="text-sm text-amber-600 mb-1">Description détaillée</p>
                                                                    <p className="text-gray-800 whitespace-pre-wrap">
                                                                        {motifContestationDetail.motif_contestation_detail}
                                                                    </p>
                                                                </div>
                                                            )}
                                                            {motifContestationDetail.motifDeContestation && (
                                                                <div className="bg-white p-3 rounded border border-amber-200">
                                                                    <p className="text-sm text-amber-600 mb-1">Motif legacy</p>
                                                                    <p className="text-gray-800">
                                                                        {motifContestationDetail.motifDeContestation}
                                                                    </p>
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* Statut et dates */}
                                                <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                                                    <h4 className="text-amber-800 font-semibold mb-3 flex items-center gap-2">
                                                        <Clock className="w-4 h-4" />
                                                        Suivi
                                                    </h4>
                                                    <div className="grid grid-cols-2 gap-4">
                                                        {motifContestationDetail.date_contestation && (
                                                            <div>
                                                                <p className="text-sm text-amber-600 mb-1">Date contestation</p>
                                                                <p className="text-gray-800">
                                                                    {formatDate(motifContestationDetail.date_contestation)}
                                                                </p>
                                                            </div>
                                                        )}
                                                        {motifContestationDetail.statut_validation && (
                                                            <div>
                                                                <p className="text-sm text-amber-600 mb-1">Statut</p>
                                                                {getValidationStatusDisplay(motifContestationDetail.statut_validation)}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Section 3: Archives enquêtes */}
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <div className="bg-gradient-to-r from-cyan-50 to-blue-50 px-4 py-3 border-b border-cyan-200">
                                            <h3 className="font-semibold text-cyan-800 flex items-center gap-2">
                                                <Archive className="w-5 h-5" />
                                                Archives enquêtes
                                                <span className="text-sm font-normal text-cyan-600">
                                                    ({archivesEnquetes?.length || 0} enregistrement{archivesEnquetes?.length > 1 ? 's' : ''})
                                                </span>
                                            </h3>
                                        </div>
                                        <div className="p-4">
                                            {loadingArchives ? (
                                                <div className="flex justify-center py-4">
                                                    <RefreshCw className="w-6 h-6 animate-spin text-cyan-600" />
                                                </div>
                                            ) : archivesEnquetes?.length > 0 ? (
                                                <div className="space-y-4">
                                                    {archivesEnquetes.map((archive, index) => (
                                                        <div key={index} className="bg-cyan-50 border border-cyan-200 rounded-lg p-4">
                                                            <div className="flex items-center justify-between mb-3">
                                                                <h4 className="font-semibold text-cyan-800">
                                                                    Archive #{index + 1}
                                                                </h4>
                                                                <span className="text-sm text-cyan-600">
                                                                    {formatDate(archive.archived_at)}
                                                                </span>
                                                            </div>
                                                            <div className="grid grid-cols-2 gap-3 text-sm">
                                                                {Object.entries(archive).map(([key, value]) => (
                                                                    <div key={key} className="bg-white p-2 rounded border border-cyan-100">
                                                                        <p className="text-cyan-700 font-medium mb-1">{key}</p>
                                                                        <p className="text-gray-800 break-all">
                                                                            {value !== null && value !== undefined 
                                                                                ? (typeof value === 'object' ? JSON.stringify(value) : String(value))
                                                                                : '-'}
                                                                        </p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-4 text-gray-500">
                                                    {messages.noArchiveFound}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Colonne de droite - Historique et archives enquêteurs */}
                                <div className="space-y-6">
                                    {/* Section 4: Historique chronologique */}
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-4 py-3 border-b border-blue-200">
                                            <h3 className="font-semibold text-blue-800 flex items-center gap-2">
                                                <Clock className="w-5 h-5" />
                                                Historique chronologique
                                            </h3>
                                        </div>
                                        <div className="p-4">
                                            {historyData.historique?.length > 0 ? (
                                                <div className="space-y-4">
                                                    {historyData.historique.map((event, index) => (
                                                        <div key={index} className="flex gap-4 pb-4 border-b last:border-0">
                                                            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                                                                <Clock className="w-5 h-5 text-blue-600" />
                                                            </div>
                                                            <div className="flex-1">
                                                                <div className="flex items-center gap-2">
                                                                    <h4 className="font-medium text-blue-900">{event.type}</h4>
                                                                    <span className="text-sm text-gray-500">{formatDate(event.date)}</span>
                                                                </div>
                                                                <p className="text-gray-600 mt-1">{event.description}</p>
                                                                {event.user && (
                                                                    <div className="text-sm text-gray-500 mt-1">
                                                                        Par: {event.user}
                                                                    </div>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-4 text-gray-500">
                                                    {messages.noHistoryAvailable}
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Section 5: Archives enquêteurs */}
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
                                        <div className="bg-gradient-to-r from-emerald-50 to-green-50 px-4 py-3 border-b border-emerald-200">
                                            <h3 className="font-semibold text-emerald-800 flex items-center gap-2">
                                                <Users className="w-5 h-5" />
                                                Archives enquêteurs
                                                <span className="text-sm font-normal text-emerald-600">
                                                    ({archivesEnqueteurs?.length || 0} enregistrement{archivesEnqueteurs?.length > 1 ? 's' : ''})
                                                </span>
                                            </h3>
                                        </div>
                                        <div className="p-4">
                                            {loadingArchives ? (
                                                <div className="flex justify-center py-4">
                                                    <RefreshCw className="w-6 h-6 animate-spin text-emerald-600" />
                                                </div>
                                            ) : archivesEnqueteurs?.length > 0 ? (
                                                <div className="space-y-4">
                                                    {archivesEnqueteurs.map((archive, index) => (
                                                        <div key={index} className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                                                            <div className="flex items-center justify-between mb-3">
                                                                <h4 className="font-semibold text-emerald-800">
                                                                    Archive #{index + 1}
                                                                </h4>
                                                                <span className="text-sm text-emerald-600">
                                                                    {formatDate(archive.archived_at)}
                                                                </span>
                                                            </div>
                                                            <div className="grid grid-cols-2 gap-3 text-sm">
                                                                {Object.entries(archive).map(([key, value]) => (
                                                                    <div key={key} className="bg-white p-2 rounded border border-emerald-100">
                                                                        <p className="text-emerald-700 font-medium mb-1">{key}</p>
                                                                        <p className="text-gray-800 break-all">
                                                                            {value !== null && value !== undefined 
                                                                                ? (typeof value === 'object' ? JSON.stringify(value) : String(value))
                                                                                : '-'}
                                                                        </p>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-4 text-gray-500">
                                                    {messages.noEnqueteurArchiveFound}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-8 text-gray-500">
                            {messages.noHistoryData}
                        </div>
                    )}
                </div>

                {/* Pied de page */}
                <div className="p-4 border-t bg-gray-50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>
    );
};

// PropTypes
HistoryModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  donneeId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  donnee: PropTypes.object,
};

export default HistoryModal;