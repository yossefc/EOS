import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  User, Phone, MapPin, Building2, Calendar, Info,
  CreditCard, MessageSquare, Briefcase, CircleDollarSign,
  Check, AlertCircle, X, Search, Building
} from 'lucide-react';
import { COUNTRIES } from './countryData';
import config from '../config';

const API_URL = config.API_URL;

// Types de recherche selon le cahier des charges
const TYPE_RECHERCHE = {
  A: "Adresse",
  T: "Téléphone",
  D: "Décès",
  B: "Coordonnées bancaires",
  E: "Coordonnées employeur",
  R: "Revenus"
};

// Codes résultat selon le cahier des charges
const CODES_RESULTAT = [
  { code: 'P', libelle: 'Positif' },
  { code: 'N', libelle: 'Négatif / NPA' },
  { code: 'H', libelle: 'Adresse/téléphone confirmés' },
  { code: 'Z', libelle: 'Annulation agence' },
  { code: 'I', libelle: 'Intraitable (état civil erroné)' },
  { code: 'Y', libelle: 'Annulation EOS' }
];

const FREQUENCES_VERSEMENT = [
  { code: 'Q', libelle: 'Quotidienne' },
  { code: 'H', libelle: 'Hebdomadaire' },
  { code: 'BM', libelle: 'Bimensuelle' },
  { code: 'M', libelle: 'Mensuelle' },
  { code: 'T', libelle: 'Trimestrielle' },
  { code: 'S', libelle: 'Semestrielle' },
  { code: 'A', libelle: 'Annuelle' }
];

// Structure des onglets
const tabs = [
  { id: 'infos', label: 'Informations', icon: Info },
  { id: 'adresse', label: 'Adresse', icon: MapPin },
  { id: 'deces', label: 'Décès', icon: Calendar },
  { id: 'employeur', label: 'Employeur', icon: Briefcase },
  { id: 'banque', label: 'Banque', icon: Building },
  { id: 'revenus', label: 'Revenus', icon: CircleDollarSign },
  { id: 'commentaires', label: 'Commentaires', icon: MessageSquare }
];

const UpdateModal = ({ isOpen, onClose, data }) => {
  const [formData, setFormData] = useState({
    // Résultat enquête
    code_resultat: 'P',
    elements_retrouves: 'A',
    flag_etat_civil_errone: '',
    date_retour: new Date().toISOString().split('T')[0],

    // Adresse
    adresse1: '',
    adresse2: '',
    adresse3: '',
    adresse4: '',
    code_postal: '',
    ville: '',
    pays_residence: 'FRANCE',
    telephone_personnel: '',
    telephone_chez_employeur: '',

    // Décès
    date_deces: '',
    numero_acte_deces: '',
    code_insee_deces: '',
    code_postal_deces: '',
    localite_deces: '',

    // Informations employeur
    nom_employeur: '',
    telephone_employeur: '',
    telecopie_employeur: '',
    adresse1_employeur: '',
    adresse2_employeur: '',
    adresse3_employeur: '',
    adresse4_employeur: '',
    code_postal_employeur: '',
    ville_employeur: '',
    pays_employeur: '',

    // Informations bancaires
    banque_domiciliation: '',
    libelle_guichet: '',
    titulaire_compte: '',
    code_banque: '',
    code_guichet: '',

    // Informations sur les revenus
    commentaires_revenus: '',
    montant_salaire: '',
    periode_versement_salaire: '',
    frequence_versement_salaire: '',

    // Autres revenus 1
    nature_revenu1: '',
    montant_revenu1: '',
    periode_versement_revenu1: '',
    frequence_versement_revenu1: '',

    // Autres revenus 2
    nature_revenu2: '',
    montant_revenu2: '',
    periode_versement_revenu2: '',
    frequence_versement_revenu2: '',

    // Autres revenus 3
    nature_revenu3: '',
    montant_revenu3: '',
    periode_versement_revenu3: '',
    frequence_versement_revenu3: '',

    // Mémos
    memo1: '',
    memo2: '',
    memo3: '',
    memo4: '',
    memo5: ''
  });

  const [suggestions, setSuggestions] = useState({
    adresses: [],
    codesPostaux: [],
    villes: []
  });

  const [isLoading, setIsLoading] = useState({
    submit: false,
    adresse: false
  });

  const [activeTab, setActiveTab] = useState('infos');
  const [showDeathInfo, setShowDeathInfo] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Charger les données de l'enquêteur si disponibles
  useEffect(() => {
    if (data) {
      // Récupérer les données enquêteur si elles existent
      const fetchEnqueteurData = async () => {
        try {
          const response = await axios.get(`${API_URL}/api/donnees-enqueteur/${data.id}`);
          if (response.data.success && response.data.data) {
            updateFormWithData(response.data.data);
          } else {
            // Initialiser avec les données du dossier
            initializeWithDossierData();
          }
        } catch (error) {
          console.error("Erreur lors de la récupération des données enquêteur:", error);
          initializeWithDossierData();
        }
      };

      fetchEnqueteurData();
    }
  }, [data]);

  // Initialiser le formulaire avec les données du dossier
  const initializeWithDossierData = () => {
    if (!data) return;

    setFormData(prev => ({
      ...prev,
      // Adresse
      adresse1: data.adresse1 || '',
      adresse2: data.adresse2 || '',
      adresse3: data.adresse3 || '',
      adresse4: data.adresse4 || '',
      code_postal: data.codePostal || '',
      ville: data.ville || '',
      pays_residence: data.paysResidence || 'FRANCE',
      telephone_personnel: data.telephonePersonnel || '',

      // Employeur
      nom_employeur: data.nomEmployeur || '',
      telephone_employeur: data.telephoneEmployeur || '',
      telecopie_employeur: data.telecopieEmployeur || '',

      // Banque
      banque_domiciliation: data.banqueDomiciliation || '',
      libelle_guichet: data.libelleGuichet || '',
      titulaire_compte: data.titulaireCompte || '',
      code_banque: data.codeBanque || '',
      code_guichet: data.codeGuichet || '',

      // Éléments retrouvés par défaut basés sur les éléments demandés
      elements_retrouves: data.elementDemandes || 'A'
    }));
  };

  // Mettre à jour le formulaire avec les données de l'enquêteur
  const updateFormWithData = (enqueteurData) => {
    setFormData(prev => ({
      ...prev,
      code_resultat: enqueteurData.code_resultat || 'P',
      elements_retrouves: enqueteurData.elements_retrouves || data.elementDemandes || 'A',
      flag_etat_civil_errone: enqueteurData.flag_etat_civil_errone || '',
      date_retour: enqueteurData.date_retour || new Date().toISOString().split('T')[0],

      // Adresse
      adresse1: enqueteurData.adresse1 || data.adresse1 || '',
      adresse2: enqueteurData.adresse2 || data.adresse2 || '',
      adresse3: enqueteurData.adresse3 || data.adresse3 || '',
      adresse4: enqueteurData.adresse4 || data.adresse4 || '',
      code_postal: enqueteurData.code_postal || data.codePostal || '',
      ville: enqueteurData.ville || data.ville || '',
      pays_residence: enqueteurData.pays_residence || data.paysResidence || 'FRANCE',
      telephone_personnel: enqueteurData.telephone_personnel || data.telephonePersonnel || '',
      telephone_chez_employeur: enqueteurData.telephone_chez_employeur || '',

      // Décès
      date_deces: enqueteurData.date_deces || '',
      numero_acte_deces: enqueteurData.numero_acte_deces || '',
      code_insee_deces: enqueteurData.code_insee_deces || '',
      code_postal_deces: enqueteurData.code_postal_deces || '',
      localite_deces: enqueteurData.localite_deces || '',

      // Employeur
      nom_employeur: enqueteurData.nom_employeur || data.nomEmployeur || '',
      telephone_employeur: enqueteurData.telephone_employeur || data.telephoneEmployeur || '',
      telecopie_employeur: enqueteurData.telecopie_employeur || data.telecopieEmployeur || '',
      adresse1_employeur: enqueteurData.adresse1_employeur || '',
      adresse2_employeur: enqueteurData.adresse2_employeur || '',
      adresse3_employeur: enqueteurData.adresse3_employeur || '',
      adresse4_employeur: enqueteurData.adresse4_employeur || '',
      code_postal_employeur: enqueteurData.code_postal_employeur || '',
      ville_employeur: enqueteurData.ville_employeur || '',
      pays_employeur: enqueteurData.pays_employeur || '',

      // Banque
      banque_domiciliation: enqueteurData.banque_domiciliation || data.banqueDomiciliation || '',
      libelle_guichet: enqueteurData.libelle_guichet || data.libelleGuichet || '',
      titulaire_compte: enqueteurData.titulaire_compte || data.titulaireCompte || '',
      code_banque: enqueteurData.code_banque || data.codeBanque || '',
      code_guichet: enqueteurData.code_guichet || data.codeGuichet || '',

      // Revenus
      commentaires_revenus: enqueteurData.commentaires_revenus || '',
      montant_salaire: enqueteurData.montant_salaire || '',
      periode_versement_salaire: enqueteurData.periode_versement_salaire || '',
      frequence_versement_salaire: enqueteurData.frequence_versement_salaire || '',
      
      // Autres revenus
      nature_revenu1: enqueteurData.nature_revenu1 || '',
      montant_revenu1: enqueteurData.montant_revenu1 || '',
      periode_versement_revenu1: enqueteurData.periode_versement_revenu1 || '',
      frequence_versement_revenu1: enqueteurData.frequence_versement_revenu1 || '',
      
      nature_revenu2: enqueteurData.nature_revenu2 || '',
      montant_revenu2: enqueteurData.montant_revenu2 || '',
      periode_versement_revenu2: enqueteurData.periode_versement_revenu2 || '',
      frequence_versement_revenu2: enqueteurData.frequence_versement_revenu2 || '',
      
      nature_revenu3: enqueteurData.nature_revenu3 || '',
      montant_revenu3: enqueteurData.montant_revenu3 || '',
      periode_versement_revenu3: enqueteurData.periode_versement_revenu3 || '',
      frequence_versement_revenu3: enqueteurData.frequence_versement_revenu3 || '',

      // Mémos
      memo1: enqueteurData.memo1 || '',
      memo2: enqueteurData.memo2 || '',
      memo3: enqueteurData.memo3 || '',
      memo4: enqueteurData.memo4 || '',
      memo5: enqueteurData.memo5 || ''
    }));

    // Mettre à jour l'affichage des informations de décès si nécessaires
    if (enqueteurData.date_deces) {
      setShowDeathInfo(true);
    }
  };

  // Recherche d'adresse via API adresse.data.gouv.fr
  const searchAddress = useCallback(async (query) => {
    if (query.length > 2) {
      setIsLoading(prev => ({ ...prev, adresse: true }));
      try {
        const response = await axios.get(
          `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=5&type=housenumber`
        );
        if (response.data.features?.length > 0) {
          const adresses = response.data.features.map(feature => ({
            adresse: `${feature.properties.housenumber} ${feature.properties.street}`,
            codePostal: feature.properties.postcode,
            ville: feature.properties.city,
            adresseComplete: feature.properties.label
          }));
          setSuggestions(prev => ({ ...prev, adresses }));
        }
      } catch (error) {
        console.error('Erreur lors de la recherche d\'adresse:', error);
      } finally {
        setIsLoading(prev => ({ ...prev, adresse: false }));
      }
    } else {
      setSuggestions(prev => ({ ...prev, adresses: [] }));
    }
  }, []);

  // Recherche par code postal
  const searchByPostalCode = useCallback(async (codePostal) => {
    if (codePostal.length >= 3) {
      setIsLoading(prev => ({ ...prev, adresse: true }));
      try {
        const response = await axios.get(
          `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(codePostal)}&type=municipality&limit=5`
        );
        if (response.data.features?.length > 0) {
          const villes = response.data.features.map(feature => ({
            codePostal: feature.properties.postcode,
            ville: feature.properties.city,
            label: `${feature.properties.postcode} ${feature.properties.city}`
          }));
          setSuggestions(prev => ({ ...prev, codesPostaux: villes }));

          // Si code postal complet (5 chiffres) et une seule ville, auto-sélectionner
          if (codePostal.length === 5 && villes.length === 1) {
            setFormData(prev => ({
              ...prev,
              ville: villes[0].ville
            }));
          }
        }
      } catch (error) {
        console.error('Erreur recherche code postal:', error);
      } finally {
        setIsLoading(prev => ({ ...prev, adresse: false }));
      }
    }
  }, []);

  // Gestion des changements de valeurs dans le formulaire
  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // Traitement spécial pour certains champs
    if (name === 'adresse3') {
      searchAddress(value);
    } else if (name === 'code_postal') {
      if (value.length >= 3) searchByPostalCode(value);
    } else if (name === 'code_resultat') {
      // Si le code résultat change à 'D' (décédé), activer l'onglet décès
      if (value === 'D') {
        setShowDeathInfo(true);
        setActiveTab('deces');
        // Mettre à jour les éléments retrouvés pour inclure D
        setFormData(prev => ({
          ...prev,
          [name]: value,
          elements_retrouves: 'D'
        }));
        return;
      }
    }

    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Sélection d'une adresse depuis les suggestions
  const handleAddressSelect = (adresse) => {
    setFormData(prev => ({
      ...prev,
      adresse3: adresse.adresse,
      code_postal: adresse.codePostal,
      ville: adresse.ville,
      pays_residence: 'FRANCE'
    }));
    setSuggestions({ adresses: [], codesPostaux: [], villes: [] });
  };

  // Sélection d'un code postal et ville depuis les suggestions
  const handlePostalCodeSelect = (item) => {
    setFormData(prev => ({
      ...prev,
      code_postal: item.codePostal,
      ville: item.ville,
      pays_residence: 'FRANCE'
    }));
    setSuggestions(prev => ({ ...prev, codesPostaux: [] }));
  };

  // Soumission du formulaire
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(prev => ({ ...prev, submit: true }));
    setError(null);
    setSuccess(null);

    try {
      // Validation des données selon le code résultat
      let errorMsg = validateFormData();
      if (errorMsg) {
        setError(errorMsg);
        setIsLoading(prev => ({ ...prev, submit: false }));
        return;
      }

      // Préparer les données à envoyer
      const dataToSend = {
        donnee_id: data.id,
        code_resultat: formData.code_resultat,
        elements_retrouves: formData.elements_retrouves,
        flag_etat_civil_errone: formData.flag_etat_civil_errone,
        date_retour: formData.date_retour,

        // Adresse
        adresse1: formData.adresse1,
        adresse2: formData.adresse2,
        adresse3: formData.adresse3,
        adresse4: formData.adresse4,
        code_postal: formData.code_postal,
        ville: formData.ville,
        pays_residence: formData.pays_residence,
        telephone_personnel: formData.telephone_personnel,
        telephone_chez_employeur: formData.telephone_chez_employeur,

        // Décès
        date_deces: formData.date_deces || null,
        numero_acte_deces: formData.numero_acte_deces,
        code_insee_deces: formData.code_insee_deces,
        code_postal_deces: formData.code_postal_deces,
        localite_deces: formData.localite_deces,

        // Employeur
        nom_employeur: formData.nom_employeur,
        telephone_employeur: formData.telephone_employeur,
        telecopie_employeur: formData.telecopie_employeur,
        adresse1_employeur: formData.adresse1_employeur,
        adresse2_employeur: formData.adresse2_employeur,
        adresse3_employeur: formData.adresse3_employeur,
        adresse4_employeur: formData.adresse4_employeur,
        code_postal_employeur: formData.code_postal_employeur,
        ville_employeur: formData.ville_employeur,
        pays_employeur: formData.pays_employeur,

        // Banque
        banque_domiciliation: formData.banque_domiciliation,
        libelle_guichet: formData.libelle_guichet,
        titulaire_compte: formData.titulaire_compte,
        code_banque: formData.code_banque,
        code_guichet: formData.code_guichet,

        // Revenus
        commentaires_revenus: formData.commentaires_revenus,
        montant_salaire: formData.montant_salaire || null,
        periode_versement_salaire: formData.periode_versement_salaire || null,
        frequence_versement_salaire: formData.frequence_versement_salaire || null,

        // Autres revenus
        nature_revenu1: formData.nature_revenu1,
        montant_revenu1: formData.montant_revenu1 || null,
        nature_revenu2: formData.nature_revenu2,
        montant_revenu2: formData.montant_revenu2 || null,
        nature_revenu3: formData.nature_revenu3,
        montant_revenu3: formData.montant_revenu3 || null,
        periode_versement_revenu1: formData.periode_versement_revenu1 || null,
        frequence_versement_revenu1: formData.frequence_versement_revenu1 || null,
        periode_versement_revenu2: formData.periode_versement_revenu2 || null,
        frequence_versement_revenu2: formData.frequence_versement_revenu2 || null,
        periode_versement_revenu3: formData.periode_versement_revenu3 || null,
        frequence_versement_revenu3: formData.frequence_versement_revenu3 || null,

        // Mémos
        memo1: formData.memo1,
        memo2: formData.memo2,
        memo3: formData.memo3,
        memo4: formData.memo4,
        memo5: formData.memo5
      };

      // Envoyer les données
      const response = await axios.post(
        `${API_URL}/api/donnees-enqueteur/${data.id}`,
        dataToSend,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        setSuccess("Données enregistrées avec succès");
        // Attendre un peu avant de fermer pour montrer le message de succès
        setTimeout(() => {
          onClose(true); // Fermer le modal avec refresh = true
        }, 1000);
      } else {
        setError("Erreur lors de l'enregistrement des données: " + response.data.error);
      }
    } catch (error) {
      console.error('Erreur détaillée:', error.response?.data || error.message);
      setError("Erreur lors de l'enregistrement: " + (error.response?.data?.error || error.message));
    } finally {
      setIsLoading(prev => ({ ...prev, submit: false }));
    }
  };

  // Validation des données du formulaire
  const validateFormData = () => {
    // Vérifier selon le code résultat
    if (formData.code_resultat === 'P') {
      // Vérifier les éléments retrouvés
      if (!formData.elements_retrouves) {
        return "Vous devez spécifier les éléments retrouvés";
      }

      // Si adresse (A) est dans les éléments retrouvés
      if (formData.elements_retrouves.includes('A')) {
        if (!formData.adresse3 || !formData.code_postal || !formData.ville) {
          return "L'adresse est incomplète (numéro+voie, code postal et ville sont obligatoires)";
        }
      }

      // Si téléphone (T) est dans les éléments retrouvés
      if (formData.elements_retrouves.includes('T') && !formData.telephone_personnel) {
        return "Le téléphone est obligatoire quand il est indiqué comme retrouvé";
      }

      // Si décès (D) est dans les éléments retrouvés
      if (formData.elements_retrouves.includes('D')) {
        if (!formData.date_deces) {
          return "La date de décès est obligatoire";
        }
      }

      // Si coordonnées bancaires (B) est dans les éléments retrouvés
      if (formData.elements_retrouves.includes('B')) {
        if (!formData.banque_domiciliation || !formData.code_banque || !formData.code_guichet) {
          return "Les coordonnées bancaires sont incomplètes";
        }
      }

      // Si coordonnées employeur (E) est dans les éléments retrouvés
      if (formData.elements_retrouves.includes('E')) {
        if (!formData.nom_employeur) {
          return "Le nom de l'employeur est obligatoire";
        }
      }
    } else if (formData.code_resultat === 'D') {
      // Vérifier les informations de décès
      if (!formData.date_deces) {
        return "La date de décès est obligatoire";
      }
    }

    return null; // Pas d'erreur
  };

  // Formatter les données pour l'affichage
  const formatValue = (value) => {
    if (value === null || value === undefined || value === '') return '-';
    return value;
  };

  // Si le modal n'est pas ouvert, ne rien afficher
  if (!isOpen || !data) return null;

  // Récupérer les éléments demandés et obligatoires
  const elementsDemandes = data?.elementDemandes?.split('') || [];
  const elementsObligatoires = data?.elementObligatoires?.split('') || [];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-auto">
      <div className="bg-white rounded-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        {/* En-tête */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-4 sm:p-6 rounded-t-xl sticky top-0 z-10">
          <div className="flex justify-between items-start">
            <div className="text-white space-y-2">
              <h2 className="text-xl sm:text-2xl font-bold">Dossier n° {data?.numeroDossier}</h2>
              <p className="text-sm sm:text-base">{data?.typeDemande === 'ENQ' ? 'Enquête' : 'Contestation'}</p>

              {/* Éléments demandés */}
              <div className="space-y-1">
                <p className="text-sm font-medium">Éléments demandés :</p>
                <div className="flex flex-wrap gap-2">
                  {elementsDemandes.map(code => (
                    <span key={code} className="bg-blue-500/20 px-2 py-1 rounded text-xs sm:text-sm">
                      {TYPE_RECHERCHE[code] || code}
                    </span>
                  ))}
                </div>
              </div>

              {/* Éléments obligatoires */}
              {elementsObligatoires.length > 0 && (
                <div className="space-y-1">
                  <p className="text-sm font-medium">Éléments obligatoires :</p>
                  <div className="flex flex-wrap gap-2">
                    {elementsObligatoires.map(code => (
                      <span key={code} className="bg-red-500/20 px-2 py-1 rounded text-xs sm:text-sm flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 sm:w-4 sm:h-4" />
                        {TYPE_RECHERCHE[code] || code}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <button onClick={() => onClose(false)} className="text-white/70 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Messages d'erreur ou de succès */}
        {error && (
          <div className="m-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="m-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-lg flex items-center gap-2">
            <Check className="w-5 h-5 flex-shrink-0" />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Navigation par onglets */}
          <div className="px-4 border-b overflow-x-auto">
            <div className="flex space-x-2">
              {tabs.map(tab => {
                // Cacher l'onglet décès si pas nécessaire
                if (tab.id === 'deces' && !showDeathInfo && !formData.elements_retrouves.includes('D')) {
                  return null;
                }
                
                // Cacher les onglets qui dépendent des éléments retrouvés
                if (
                  (tab.id === 'employeur' && !formData.elements_retrouves.includes('E')) ||
                  (tab.id === 'banque' && !formData.elements_retrouves.includes('B')) ||
                  (tab.id === 'revenus' && !formData.elements_retrouves.includes('R'))
                ) {
                  // Ne pas cacher ces onglets si on a des données dedans
                  const hasBankData = formData.banque_domiciliation || formData.code_banque;
                  const hasEmployerData = formData.nom_employeur;
                  const hasRevenueData = formData.montant_salaire;
                  
                  if (
                    (tab.id === 'employeur' && !hasEmployerData) ||
                    (tab.id === 'banque' && !hasBankData) ||
                    (tab.id === 'revenus' && !hasRevenueData)
                  ) {
                    return null;
                  }
                }
                
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={`px-4 py-3 text-sm font-medium whitespace-nowrap inline-flex items-center gap-1
                      ${activeTab === tab.id
                        ? 'border-b-2 border-blue-500 text-blue-600'
                        : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                  >
                    {tab.icon && <tab.icon className="w-4 h-4" />}
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="p-4">
            {/* Contenu des onglets */}
            {activeTab === 'infos' && (
              <div className="space-y-4">
                {/* Informations générales en lecture seule */}
                <div className="bg-gray-50 rounded-lg p-4 border">
                  <h3 className="text-lg font-medium mb-4">Informations générales du dossier</h3>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Informations de base */}
                    <div>
                      <p className="text-sm text-gray-500">Numéro de dossier</p>
                      <p className="font-medium">{formatValue(data.numeroDossier)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Référence dossier</p>
                      <p className="font-medium">{formatValue(data.referenceDossier)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Type de demande</p>
                      <p className="font-medium">{formatValue(data.typeDemande)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Numéro demande</p>
                      <p className="font-medium">{formatValue(data.numeroDemande)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Date retour espéré</p>
                      <p className="font-medium">{formatValue(data.dateRetourEspere)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Forfait demande</p>
                      <p className="font-medium">{formatValue(data.forfaitDemande)}</p>
                    </div>

                    {/* Informations personnelles */}
                    <div>
                      <p className="text-sm text-gray-500">Civilité</p>
                      <p className="font-medium">{formatValue(data.qualite)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Nom</p>
                      <p className="font-medium">{formatValue(data.nom)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Prénom</p>
                      <p className="font-medium">{formatValue(data.prenom)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Date de naissance</p>
                      <p className="font-medium">{formatValue(data.dateNaissance)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Lieu de naissance</p>
                      <p className="font-medium">{formatValue(data.lieuNaissance)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Pays de naissance</p>
                      <p className="font-medium">{formatValue(data.paysNaissance)}</p>
                    </div>
                    
                    {/* Adresse connue */}
                    <div className="col-span-1 sm:col-span-2 lg:col-span-3">
                      <p className="text-sm text-gray-500">Adresse connue</p>
                      <p className="font-medium">
                        {[data.adresse1, data.adresse2, data.adresse3, data.adresse4]
                          .filter(Boolean)
                          .join(', ')}
                        {data.codePostal || data.ville ?
                          ` - ${data.codePostal || ''} ${data.ville || ''}` : ''}
                        {data.paysResidence && data.paysResidence !== 'FRANCE' ?
                          ` - ${data.paysResidence}` : ''}
                      </p>
                    </div>
                  </div>

                  {/* Résultat de l'enquête */}
                  <div className="mt-6 border-t pt-4">
                    <h4 className="font-medium mb-3">Résultat de l'enquête</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">Code résultat</label>
                        <select
                          name="code_resultat"
                          value={formData.code_resultat}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          {CODES_RESULTAT.map(({ code, libelle }) => (
                            <option key={code} value={code}>{code} - {libelle}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">Éléments retrouvés</label>
                        <select
                          name="elements_retrouves"
                          value={formData.elements_retrouves}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          disabled={formData.code_resultat === 'D'}
                        >
                          <option value="A">A - Adresse</option>
                          <option value="AT">AT - Adresse et téléphone</option>
                          <option value="D">D - Décès</option>
                          <option value="AB">AB - Adresse et banque</option>
                          <option value="AE">AE - Adresse et employeur</option>
                          <option value="ATB">ATB - Adresse, téléphone et banque</option>
                          <option value="ATE">ATE - Adresse, téléphone et employeur</option>
                          <option value="ATBE">ATBE - Adresse, téléphone, banque et employeur</option>
                          <option value="ATBER">ATBER - Adresse, téléphone, banque, employeur et revenus</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">
                          État civil erroné ?
                        </label>
                        <select
                          name="flag_etat_civil_errone"
                          value={formData.flag_etat_civil_errone}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          <option value="">Non</option>
                          <option value="E">Oui (E)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Adresse */}
            {activeTab === 'adresse' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Coordonnées actuelles</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Ligne 1 (Étage, Appartement)
                    </label>
                    <input
                      type="text"
                      name="adresse1"
                      value={formData.adresse1}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Ligne 2 (Bâtiment, Escalier)
                    </label>
                    <input
                      type="text"
                      name="adresse2"
                      value={formData.adresse2}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div className="relative">
                    <label className="block text-sm text-gray-600 mb-1">
                      Ligne 3 (Numéro et nom de rue) *
                    </label>
                    <input
                      type="text"
                      name="adresse3"
                      value={formData.adresse3}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                    {suggestions.adresses?.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-48 overflow-auto">
                        {suggestions.adresses.map((adresse, index) => (
                          <button
                            key={index}
                            type="button"
                            onClick={() => handleAddressSelect(adresse)}
                            className="w-full p-2 text-left hover:bg-gray-100 border-b"
                          >
                            {adresse.adresseComplete}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Ligne 4 (Lieu-dit, Hameau)
                    </label>
                    <input
                      type="text"
                      name="adresse4"
                      value={formData.adresse4}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="relative">
                      <label className="block text-sm text-gray-600 mb-1">
                        Code postal *
                      </label>
                      <input
                        type="text"
                        name="code_postal"
                        value={formData.code_postal}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={10}
                      />
                      {suggestions.codesPostaux?.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-48 overflow-auto">
                          {suggestions.codesPostaux.map((item, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => handlePostalCodeSelect(item)}
                              className="w-full p-2 text-left hover:bg-gray-100 border-b"
                            >
                              {item.label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Ville *
                      </label>
                      <input
                        type="text"
                        name="ville"
                        value={formData.ville}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={32}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Pays
                      </label>
                      <select
                        name="pays_residence"
                        value={formData.pays_residence}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                      >
                        {COUNTRIES.map(country => (
                          <option key={country} value={country}>{country}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Téléphone personnel
                      </label>
                      <input
                        type="text"
                        name="telephone_personnel"
                        value={formData.telephone_personnel}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={15}
                        placeholder="ex: 0123456789"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Téléphone chez l'employeur
                      </label>
                      <input
                        type="text"
                        name="telephone_chez_employeur"
                        value={formData.telephone_chez_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={15}
                        placeholder="ex: 0123456789"
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Décès */}
            {activeTab === 'deces' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Informations sur le décès</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Date de décès *
                    </label>
                    <input
                      type="date"
                      name="date_deces"
                      value={formData.date_deces}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Numéro de l'acte de décès
                    </label>
                    <input
                      type="text"
                      name="numero_acte_deces"
                      value={formData.numero_acte_deces}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={10}
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Code INSEE
                      </label>
                      <input
                        type="text"
                        name="code_insee_deces"
                        value={formData.code_insee_deces}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={5}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Code postal
                      </label>
                      <input
                        type="text"
                        name="code_postal_deces"
                        value={formData.code_postal_deces}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={10}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Localité
                      </label>
                      <input
                        type="text"
                        name="localite_deces"
                        value={formData.localite_deces}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={32}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Employeur */}
            {activeTab === 'employeur' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Informations sur l'employeur</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="sm:col-span-3">
                      <label className="block text-sm text-gray-600 mb-1">
                        Nom de l'employeur *
                      </label>
                      <input
                        type="text"
                        name="nom_employeur"
                        value={formData.nom_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={32}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Téléphone
                      </label>
                      <input
                        type="text"
                        name="telephone_employeur"
                        value={formData.telephone_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={15}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Télécopie
                      </label>
                      <input
                        type="text"
                        name="telecopie_employeur"
                        value={formData.telecopie_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={15}
                      />
                    </div>
                  </div>
                  <h4 className="font-medium mt-4 mb-2">Adresse de l'employeur</h4>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Adresse 1
                    </label>
                    <input
                      type="text"
                      name="adresse1_employeur"
                      value={formData.adresse1_employeur}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Adresse 2
                    </label>
                    <input
                      type="text"
                      name="adresse2_employeur"
                      value={formData.adresse2_employeur}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Adresse 3
                    </label>
                    <input
                      type="text"
                      name="adresse3_employeur"
                      value={formData.adresse3_employeur}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Adresse 4
                    </label>
                    <input
                      type="text"
                      name="adresse4_employeur"
                      value={formData.adresse4_employeur}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Code postal
                      </label>
                      <input
                        type="text"
                        name="code_postal_employeur"
                        value={formData.code_postal_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={10}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Ville
                      </label>
                      <input
                        type="text"
                        name="ville_employeur"
                        value={formData.ville_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={32}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Pays
                      </label>
                      <select
                        name="pays_employeur"
                        value={formData.pays_employeur || 'FRANCE'}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                      >
                        {COUNTRIES.map(country => (
                          <option key={country} value={country}>{country}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Banque */}
            {activeTab === 'banque' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Informations bancaires</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Banque de domiciliation *
                    </label>
                    <input
                      type="text"
                      name="banque_domiciliation"
                      value={formData.banque_domiciliation}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Libellé du guichet
                    </label>
                    <input
                      type="text"
                      name="libelle_guichet"
                      value={formData.libelle_guichet}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={30}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Titulaire du compte
                    </label>
                    <input
                      type="text"
                      name="titulaire_compte"
                      value={formData.titulaire_compte}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={32}
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Code banque *
                      </label>
                      <input
                        type="text"
                        name="code_banque"
                        value={formData.code_banque}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={5}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Code guichet *
                      </label>
                      <input
                        type="text"
                        name="code_guichet"
                        value={formData.code_guichet}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={5}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Revenus */}
            {activeTab === 'revenus' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Informations sur les revenus</h3>
                <div className="space-y-6">
                  <div>
                    <h4 className="text-sm font-medium mb-3">Salaire</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Montant
                        </label>
                        <input
                          type="text"
                          name="montant_salaire"
                          value={formData.montant_salaire}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Jour de versement (-1 pour dernier jour)
                        </label>
                        <input
                          type="number"
                          name="periode_versement_salaire"
                          value={formData.periode_versement_salaire}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          min="-1"
                          max="31"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">
                          Fréquence
                        </label>
                        <select
                          name="frequence_versement_salaire"
                          value={formData.frequence_versement_salaire}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          <option value="">Sélectionner...</option>
                          {FREQUENCES_VERSEMENT.map(freq => (
                            <option key={freq.code} value={freq.code}>
                              {freq.code} - {freq.libelle}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="mt-2">
                      <label className="block text-xs text-gray-600 mb-1">
                        Commentaires sur les revenus
                      </label>
                      <textarea
                        name="commentaires_revenus"
                        value={formData.commentaires_revenus}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        rows="2"
                        maxLength={128}
                      ></textarea>
                    </div>
                  </div>

                  {/* Autres revenus */}
                  <div>
                    <h4 className="text-sm font-medium mb-3">Autre revenu 1</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Nature</label>
                        <input
                          type="text"
                          name="nature_revenu1"
                          value={formData.nature_revenu1}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          maxLength={30}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Montant</label>
                        <input
                          type="text"
                          name="montant_revenu1"
                          value={formData.montant_revenu1}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Jour de versement</label>
                        <input
                          type="number"
                          name="periode_versement_revenu1"
                          value={formData.periode_versement_revenu1}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          min="-1"
                          max="31"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu1"
                          value={formData.frequence_versement_revenu1}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          <option value="">Sélectionner...</option>
                          {FREQUENCES_VERSEMENT.map(freq => (
                            <option key={freq.code} value={freq.code}>
                              {freq.code} - {freq.libelle}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-3">Autre revenu 2</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Nature</label>
                        <input
                          type="text"
                          name="nature_revenu2"
                          value={formData.nature_revenu2}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          maxLength={30}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Montant</label>
                        <input
                          type="text"
                          name="montant_revenu2"
                          value={formData.montant_revenu2}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Jour de versement</label>
                        <input
                          type="number"
                          name="periode_versement_revenu2"
                          value={formData.periode_versement_revenu2}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          min="-1"
                          max="31"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu2"
                          value={formData.frequence_versement_revenu2}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          <option value="">Sélectionner...</option>
                          {FREQUENCES_VERSEMENT.map(freq => (
                            <option key={freq.code} value={freq.code}>
                              {freq.code} - {freq.libelle}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium mb-3">Autre revenu 3</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Nature</label>
                        <input
                          type="text"
                          name="nature_revenu3"
                          value={formData.nature_revenu3}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          maxLength={30}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Montant</label>
                        <input
                          type="text"
                          name="montant_revenu3"
                          value={formData.montant_revenu3}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Jour de versement</label>
                        <input
                          type="number"
                          name="periode_versement_revenu3"
                          value={formData.periode_versement_revenu3}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          min="-1"
                          max="31"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu3"
                          value={formData.frequence_versement_revenu3}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                        >
                          <option value="">Sélectionner...</option>
                          {FREQUENCES_VERSEMENT.map(freq => (
                            <option key={freq.code} value={freq.code}>
                              {freq.code} - {freq.libelle}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {/* Onglet Commentaires */}
            {activeTab === 'commentaires' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Commentaires</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Mémo 1
                    </label>
                    <input
                      type="text"
                      name="memo1"
                      value={formData.memo1}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={64}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Mémo 2
                    </label>
                    <input
                      type="text"
                      name="memo2"
                      value={formData.memo2}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={64}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Mémo 3
                    </label>
                    <input
                      type="text"
                      name="memo3"
                      value={formData.memo3}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={64}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Mémo 4
                    </label>
                    <input
                      type="text"
                      name="memo4"
                      value={formData.memo4}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={64}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Commentaires détaillés
                    </label>
                    <textarea
                      name="memo5"
                      value={formData.memo5}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      rows="4"
                      maxLength={1000}
                    ></textarea>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Boutons d'action */}
          <div className="p-4 flex justify-end gap-3 border-t sticky bottom-0 bg-white z-10">
            <button
              type="button"
              onClick={() => onClose(false)}
              className="px-4 py-2 text-gray-600 border rounded-lg hover:bg-gray-50 focus:outline-none"
              disabled={isLoading.submit}
            >
              Annuler
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none flex items-center"
              disabled={isLoading.submit}
            >
              {isLoading.submit ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Enregistrement...
                </>
              ) : 'Enregistrer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UpdateModal;