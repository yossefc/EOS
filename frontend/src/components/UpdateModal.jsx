import  { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  User, MapPin, Calendar, Info,
  MessageSquare, Briefcase, CircleDollarSign,
  Check, AlertCircle, X, Building, StickyNote, HelpCircle
} from 'lucide-react';
import { COUNTRIES } from './countryData';
import config from '../config';
import EtatCivilPanel from './EtatCivilPanel';
import PropTypes from 'prop-types';

// Définition des PropTypes en dehors du composant
const UpdateModalPropTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  data: PropTypes.shape({
    id: PropTypes.number.isRequired,
    numeroDossier: PropTypes.string,
    referenceDossier: PropTypes.string,
    typeDemande: PropTypes.string,
    motifDeContestation: PropTypes.string,
    elementDemandes: PropTypes.string,
    elementObligatoires: PropTypes.string,
    qualite: PropTypes.string,
    nom: PropTypes.string,
    prenom: PropTypes.string,
    dateNaissance: PropTypes.string,
    lieuNaissance: PropTypes.string,
    codePostalNaissance: PropTypes.string,
    paysNaissance: PropTypes.string,
    nomPatronymique: PropTypes.string,
    enqueteOriginale: PropTypes.shape({
      numeroDossier: PropTypes.string,
      enqueteurNom: PropTypes.string,
    }),
  }).isRequired
};

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

// Status labels pour l'affichage
const STATUS_LABELS = {
  'P': 'Positif',
  'N': 'Négatif / NPA',
  'H': 'Confirmé',
  'Z': 'Annulé (agence)',
  'I': 'Intraitable',
  'Y': 'Annulé (EOS)',
  '': 'En attente'
};

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
  { id: 'etat-civil', label: 'État civil', icon: User },
  { id: 'adresse', label: 'Adresse', icon: MapPin },
  { id: 'deces', label: 'Décès', icon: Calendar },
  { id: 'employeur', label: 'Employeur', icon: Briefcase },
  { id: 'banque', label: 'Banque', icon: Building },
  { id: 'revenus', label: 'Revenus', icon: CircleDollarSign },
  { id: 'commentaires', label: 'Commentaires', icon: MessageSquare },
  { id: 'notes', label: 'Notes perso', icon: StickyNote }
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

    // Banque
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
    memo5: '',
    
    // Notes personnelles
    notes_personnelles: ''
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
  const [donneesSauvegardees, setDonneesSauvegardees] = useState(null);
  const [showEtatCivilHelp, setShowEtatCivilHelp] = useState(false);
  

  // Initialiser le formulaire avec les données du dossier
  const initializeWithDossierData = useCallback(() => {
    if (!data) return;
  
    setFormData(prev => ({
      ...prev,
      code_resultat: 'P',
      elements_retrouves: data.elementDemandes || 'A',
      flag_etat_civil_errone: '',
      date_retour: new Date().toISOString().split('T')[0],

      // Tous les autres champs sont vides pour s'assurer qu'on n'utilise pas de données de la table donnees
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

      // Employeur
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

      // Banque
      banque_domiciliation: '',
      libelle_guichet: '',
      titulaire_compte: '',
      code_banque: '',
      code_guichet: '',
    }));
  }, [data]);

  // Charger les données de l'enquêteur si disponibles
  useEffect(() => {
    if (data) {
      const fetchEnqueteurData = async () => {
        try {
          const response = await axios.get(`${API_URL}/api/donnees-enqueteur/${data.id}`);
          
          if (response.data.success && response.data.data) {
            const enqueteurData = response.data.data;
            
            // Stocker les données sauvegardées
            setDonneesSauvegardees(enqueteurData);
            
            // Mise à jour du formulaire avec les données
            setFormData({
              // Valeurs par défaut
              code_resultat: enqueteurData.code_resultat || 'P',
              elements_retrouves: enqueteurData.elements_retrouves || data.elementDemandes || 'A',
              flag_etat_civil_errone: enqueteurData.flag_etat_civil_errone || '',
              date_retour: enqueteurData.date_retour || new Date().toISOString().split('T')[0],

              // Adresse
              adresse1: enqueteurData.adresse1 || '',
              adresse2: enqueteurData.adresse2 || '',
              adresse3: enqueteurData.adresse3 || '',
              adresse4: enqueteurData.adresse4 || '',
              code_postal: enqueteurData.code_postal || '',
              ville: enqueteurData.ville || '',
              pays_residence: enqueteurData.pays_residence || 'FRANCE',
              telephone_personnel: enqueteurData.telephone_personnel || '',
              telephone_chez_employeur: enqueteurData.telephone_chez_employeur || '',

              // Décès
              date_deces: enqueteurData.date_deces || '',
              numero_acte_deces: enqueteurData.numero_acte_deces || '',
              code_insee_deces: enqueteurData.code_insee_deces || '',
              code_postal_deces: enqueteurData.code_postal_deces || '',
              localite_deces: enqueteurData.localite_deces || '',

              // Employeur
              nom_employeur: enqueteurData.nom_employeur || '',
              telephone_employeur: enqueteurData.telephone_employeur || '',
              telecopie_employeur: enqueteurData.telecopie_employeur || '',
              adresse1_employeur: enqueteurData.adresse1_employeur || '',
              adresse2_employeur: enqueteurData.adresse2_employeur || '',
              adresse3_employeur: enqueteurData.adresse3_employeur || '',
              adresse4_employeur: enqueteurData.adresse4_employeur || '',
              code_postal_employeur: enqueteurData.code_postal_employeur || '',
              ville_employeur: enqueteurData.ville_employeur || '',
              pays_employeur: enqueteurData.pays_employeur || '',

              // Banque
              banque_domiciliation: enqueteurData.banque_domiciliation || '',
              libelle_guichet: enqueteurData.libelle_guichet || '',
              titulaire_compte: enqueteurData.titulaire_compte || '',
              code_banque: enqueteurData.code_banque || '',
              code_guichet: enqueteurData.code_guichet || '',

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
              memo5: enqueteurData.memo5 || '',
              
              // Notes personnelles
              notes_personnelles: enqueteurData.notes_personnelles || ''
            });
            
            // Mettre à jour l'onglet de décès si nécessaire
            if (enqueteurData.date_deces || enqueteurData.elements_retrouves?.includes('D')) {
              setShowDeathInfo(true);
            }
            
            // Si le code résultat est déjà 'I' (intraitable), s'assurer que les zones d'état civil
            // contiennent les valeurs d'origine ou sont vides
            if (enqueteurData.code_resultat === 'I') {
              setFormData(prev => ({
                ...prev,
                // Utiliser l'état civil d'origine
                qualite: data.qualite || '',
                nom: data.nom || '',
                prenom: data.prenom || '',
                dateNaissance: data.dateNaissance || '',
                lieuNaissance: data.lieuNaissance || '',
                codePostalNaissance: data.codePostalNaissance || '',
                paysNaissance: data.paysNaissance || '',
                nomPatronymique: data.nomPatronymique || '',
                elements_retrouves: ''
              }));
            }
          } else {
            initializeWithDossierData();
          }
        } catch (error) {
          console.log(error);
          initializeWithDossierData();
        }
      };
  
      fetchEnqueteurData();
    }
  }, [data, initializeWithDossierData]);

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
      
      // Si le code résultat change à 'I' (intraitable), rétablir les zones d'état civil d'origine
      // conformément au cahier des charges
      if (value === 'I') {
        setFormData(prev => ({
          ...prev,
          [name]: value,
          // Rétablir les données d'état civil d'origine
          qualite: data?.qualite || '',
          nom: data?.nom || '',
          prenom: data?.prenom || '',
          dateNaissance: data?.dateNaissance || '',
          lieuNaissance: data?.lieuNaissance || '',
          codePostalNaissance: data?.codePostalNaissance || '',
          paysNaissance: data?.paysNaissance || '',
          nomPatronymique: data?.nomPatronymique || '',
          elements_retrouves: '',  // Vider car aucun élément n'est retrouvé
          flag_etat_civil_errone: '' // Réinitialiser le flag
        }));
        return;
      }
    } else if (name === 'flag_etat_civil_errone') {
      // Si on met le flag état civil erroné, il faut s'assurer que le code résultat est 'P'
      // puisque selon le cahier des charges, on peut envoyer un résultat positif avec état civil légèrement différent
      if (value === 'E') {
        setFormData(prev => ({
          ...prev,
          [name]: value,
          code_resultat: 'P'
        }));
        
        // Afficher l'aide sur les états civils erronés
        setShowEtatCivilHelp(true);
        
        // Afficher un message d'information
        setError("N'oubliez pas de documenter dans les mémos (onglet Commentaires) les différences d'état civil. Vous ne devez utiliser le flag 'E' que pour les cas prévus par le cahier des charges.");
        return;
      } else {
        setShowEtatCivilHelp(false);
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
      let dataToSend = {
        donnee_id: data.id,
        code_resultat: formData.code_resultat,
        elements_retrouves: formData.code_resultat === 'I' ? '' : formData.elements_retrouves,
        flag_etat_civil_errone: formData.flag_etat_civil_errone,
        date_retour: formData.date_retour,
      };
  
      // Gérer les données d'état civil corrigées
      if (formData.flag_etat_civil_errone === 'E') {
        dataToSend = {
          ...dataToSend,
          qualite_corrigee: formData.qualite_corrigee || null,
          nom_corrige: formData.nom_corrige || null,
          prenom_corrige: formData.prenom_corrige || null,
          nom_patronymique_corrige: formData.nom_patronymique_corrige || null,
          date_naissance_corrigee: formData.date_naissance_corrigee || null,
          lieu_naissance_corrige: formData.lieu_naissance_corrige || null,
          code_postal_naissance_corrige: formData.code_postal_naissance_corrige || null,
          pays_naissance_corrige: formData.pays_naissance_corrige || null,
          type_divergence: formData.type_divergence || null,
        };
        
        // Log des données d'état civil pour débogage
        console.log("Données d'état civil envoyées au backend:", {
          flag_etat_civil_errone: formData.flag_etat_civil_errone,
          qualite_corrigee: formData.qualite_corrigee,
          nom_corrige: formData.nom_corrige,
          prenom_corrige: formData.prenom_corrige,
          nom_patronymique_corrige: formData.nom_patronymique_corrige,
          date_naissance_corrigee: formData.date_naissance_corrigee,
          lieu_naissance_corrige: formData.lieu_naissance_corrige,
          code_postal_naissance_corrige: formData.code_postal_naissance_corrige,
          pays_naissance_corrige: formData.pays_naissance_corrige,
          type_divergence: formData.type_divergence
        });
      }
      // Si le code résultat est 'I' (intraitable), on ne transmet pas les modifications
      // des données d'état civil selon le cahier des charges
      if (formData.code_resultat === 'I') {
        // Utiliser l'état civil d'origine
        dataToSend = {
          ...dataToSend,
          qualite: data?.qualite || '',
          nom: data?.nom || '',
          prenom: data?.prenom || '',
          dateNaissance: data?.dateNaissance || '',
          lieuNaissance: data?.lieuNaissance || '',
          codePostalNaissance: data?.codePostalNaissance || '',
          paysNaissance: data?.paysNaissance || '',
          nomPatronymique: data?.nomPatronymique || '',
          // Pour les cas intraitables, on n'envoie pas d'éléments retrouvés
          elements_retrouves: ''
        };
        
        // On vide également tous les autres champs d'information
        dataToSend = {
          ...dataToSend,
          // Adresse
          adresse1: '',
          adresse2: '',
          adresse3: '',
          adresse4: '',
          code_postal: '',
          ville: '',
          pays_residence: '',
          telephone_personnel: '',
          telephone_chez_employeur: '',

          // Décès
          date_deces: null,
          numero_acte_deces: '',
          code_insee_deces: '',
          code_postal_deces: '',
          localite_deces: '',

          // Employeur
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

          // Banque
          banque_domiciliation: '',
          libelle_guichet: '',
          titulaire_compte: '',
          code_banque: '',
          code_guichet: '',

          // Revenus
          commentaires_revenus: '',
          montant_salaire: null,
          periode_versement_salaire: null,
          frequence_versement_salaire: '',

          // Autres revenus
          nature_revenu1: '',
          montant_revenu1: null,
          periode_versement_revenu1: null,
          frequence_versement_revenu1: '',
          
          nature_revenu2: '',
          montant_revenu2: null,
          periode_versement_revenu2: null,
          frequence_versement_revenu2: '',
          
          nature_revenu3: '',
          montant_revenu3: null,
          periode_versement_revenu3: null,
          frequence_versement_revenu3: ''
        };
        
        // Préserver les mémos et notes personnelles car ils peuvent contenir des informations utiles
        dataToSend = {
          ...dataToSend,
          memo1: formData.memo1,
          memo2: formData.memo2,
          memo3: formData.memo3,
          memo4: formData.memo4,
          memo5: formData.memo5,
          notes_personnelles: formData.notes_personnelles
        };
      } else {
        // Pour les autres codes résultat, on envoie les données normalement
        dataToSend = {
          ...dataToSend,
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
          memo5: formData.memo5,
          
          // Notes personnelles
          notes_personnelles: formData.notes_personnelles
        };
      }

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
        // Après avoir enregistré les données enquêteur, mettre le statut à "confirmee"
        // Cela indique que l'enquêteur a terminé et confirmé son travail
        try {
          await axios.put(
            `${API_URL}/api/donnees/${data.id}/statut`,
            { statut_validation: 'confirmee' },
            {
              headers: {
                'Content-Type': 'application/json'
              }
            }
          );
        } catch (statutError) {
          console.warn('Erreur lors de la mise à jour du statut:', statutError);
          // Ne pas bloquer le processus si la mise à jour du statut échoue
        }
        
        setSuccess("Données enregistrées avec succès - Enquête confirmée et prête pour validation par l'administrateur");
        setDonneesSauvegardees(response.data.data);
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
      
      // Si le flag état civil erroné est 'E', vérifier que les mémos contiennent des explications
      if (formData.flag_etat_civil_errone === 'E') {
        if (!formData.memo1 && !formData.memo2 && !formData.memo3 && !formData.memo4 && !formData.memo5) {
          return "Quand l'état civil est erroné (flag E), vous devez documenter les différences dans les mémos";
        }
      }
    } else if (formData.code_resultat === 'D') {
      // Vérifier les informations de décès
      if (!formData.date_deces) {
        return "La date de décès est obligatoire";
      }
    } else if (formData.code_resultat === 'I') {
      // Cas intraitable : aucune validation spéciale requise
    }

    return null; // Pas d'erreur
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
                {/* Résultat de l'enquête */}
                <div className="bg-gray-50 rounded-lg p-4 border">
                  <h3 className="text-lg font-medium mb-4">Informations générales et résultat</h3>
                  
                  {data.typeDemande === 'CON' && (
  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
    <h3 className="font-medium mb-2">Informations sur la contestation</h3>
    {console.log("Données contestation:", data)}
    {data.enqueteOriginale ? (
      <div>
        <p><span className="font-medium">Dossier contesté :</span> {data.enqueteOriginale.numeroDossier}</p>
        <p><span className="font-medium">Enquêteur initial :</span> {data.enqueteOriginale.enqueteurNom}</p>
        <p><span className="font-medium">Motif de contestation :</span> {data.motifDeContestation || 'Non précisé'}</p>
      </div>
    ) : (
      <p className="text-yellow-600">Information sur l&apos;enquête originale non disponible</p>
    )}
  </div>
)}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <p className="text-sm text-gray-500">Numéro de dossier</p>
                      <p className="font-medium">{data.numeroDossier}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Référence</p>
                      <p className="font-medium">{data.referenceDossier || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Nom</p>
                      <p className="font-medium">{data.nom}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Prénom</p>
                      <p className="font-medium">{data.prenom || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Date de naissance</p>
                      <p className="font-medium">{data.dateNaissance || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Lieu de naissance</p>
                      <p className="font-medium">{data.lieuNaissance || '-'}</p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-3">Résultat de l&apos;enquête</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                          disabled={formData.code_resultat === 'D' || formData.code_resultat === 'I'}
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
                        <label className="flex items-center gap-1 text-sm text-gray-600 mb-1">
                          État civil erroné ?
                          <button 
                            type="button" 
                            onClick={() => setShowEtatCivilHelp(!showEtatCivilHelp)}
                            className="text-blue-500 hover:text-blue-700"
                          >
                            <HelpCircle className="w-4 h-4" />
                          </button>
                        </label>
                        <select
                          name="flag_etat_civil_errone"
                          value={formData.flag_etat_civil_errone}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          disabled={formData.code_resultat === 'I'}
                        >
                          <option value="">Non</option>
                          <option value="E">Oui (E)</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Afficher les données sauvegardées précédemment */}
                  {donneesSauvegardees && (
                    <div className="mt-4 border-t pt-4">
                      <h4 className="font-medium mb-3">Dernières modifications enregistrées</h4>
                      <div className="text-sm text-gray-700">
                        <p><span className="font-medium">Statut:</span> {STATUS_LABELS[donneesSauvegardees.code_resultat] || '-'}</p>
                        <p><span className="font-medium">Éléments retrouvés:</span> {donneesSauvegardees.elements_retrouves || '-'}</p>
                        <p><span className="font-medium">Date de modification:</span> {new Date(donneesSauvegardees.updated_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
            {/* Onglet État civil */}
            {activeTab === 'etat-civil' && (
            <EtatCivilPanel
                originalData={{
                qualite: data?.qualite,
                nom: data?.nom,
                prenom: data?.prenom,
                dateNaissance: data?.dateNaissance,
                lieuNaissance: data?.lieuNaissance,
                codePostalNaissance: data?.codePostalNaissance,
                paysNaissance: data?.paysNaissance,
                nomPatronymique: data?.nomPatronymique
                }}
                formData={formData}
                setFormData={setFormData}
                onValidate={(correctedData, divergenceType) => {
                // Mise à jour des mémos et du flag
                setFormData(prev => ({
                    ...prev,
                    flag_etat_civil_errone: 'E',
                    // Stocker les informations corrigées
                    qualite_corrigee: correctedData.qualite,
                    nom_corrige: correctedData.nom,
                    prenom_corrige: correctedData.prenom,
                    nom_patronymique_corrige: correctedData.nomPatronymique,
                    date_naissance_corrigee: correctedData.dateNaissance,
                    lieu_naissance_corrige: correctedData.lieuNaissance,
                    code_postal_naissance_corrige: correctedData.codePostalNaissance,
                    pays_naissance_corrige: correctedData.paysNaissance,
                    type_divergence: divergenceType,
                    // Ajouter une explication dans le mémo
                    memo5: `${prev.memo5 ? prev.memo5 + '\n\n' : ''}État civil corrigé (${divergenceType}):\n` +
                        `Nom: ${correctedData.nom || '-'}\n` +
                        `Prénom: ${correctedData.prenom || '-'}\n` +
                        `Date de naissance: ${correctedData.dateNaissance || '-'}\n` +
                        `Lieu de naissance: ${correctedData.lieuNaissance || '-'}`
                }));
                }}
            />
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
                    />
                    {suggestions.adresses?.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-48 overflow-auto">
                        {suggestions.adresses.map((adresse, index) => (
                          <button
                            key={index}
                            type="button"
                            onClick={() => handleAddressSelect(adresse)}
                            className="w-full p-2 text-left hover:bg-gray-100 border-b"
                            disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
                      />
                      {suggestions.codesPostaux?.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-48 overflow-auto">
                          {suggestions.codesPostaux.map((item, index) => (
                            <button
                              key={index}
                              type="button"
                              onClick={() => handlePostalCodeSelect(item)}
                              className="w-full p-2 text-left hover:bg-gray-100 border-b"
                              disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-600 mb-1">
                        Téléphone chez l&apos;employeur
                      </label>
                      <input
                        type="text"
                        name="telephone_chez_employeur"
                        value={formData.telephone_chez_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={15}
                        placeholder="ex: 0123456789"
                        disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">
                      Numéro de l&apos;acte de décès
                    </label>
                    <input
                      type="text"
                      name="numero_acte_deces"
                      value={formData.numero_acte_deces}
                      onChange={handleInputChange}
                      className="w-full p-2 border rounded"
                      maxLength={10}
                      disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Onglet Employeur */}
            {activeTab === 'employeur' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4">Informations sur l&apos;employeur</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="sm:col-span-3">
                      <label className="block text-sm text-gray-600 mb-1">
                        Nom de l&apos;employeur *
                      </label>
                      <input
                        type="text"
                        name="nom_employeur"
                        value={formData.nom_employeur}
                        onChange={handleInputChange}
                        className="w-full p-2 border rounded"
                        maxLength={32}
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
                      />
                    </div>
                  </div>
                  <h4 className="font-medium mt-4 mb-2">Adresse de l&apos;employeur</h4>
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                      disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                        disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu1"
                          value={formData.frequence_versement_revenu1}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu2"
                          value={formData.frequence_versement_revenu2}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
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
                          disabled={formData.code_resultat === 'I'}
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-600 mb-1">Fréquence</label>
                        <select
                          name="frequence_versement_revenu3"
                          value={formData.frequence_versement_revenu3}
                          onChange={handleInputChange}
                          className="w-full p-2 border rounded"
                          disabled={formData.code_resultat === 'I'}
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
                {formData.flag_etat_civil_errone === 'E' && (
                  <div className="p-3 mb-4 bg-blue-50 border border-blue-200 text-blue-700 rounded">
                    <div className="flex items-center gap-2 font-medium mb-1">
                      <HelpCircle className="w-4 h-4" />
                      <span>État civil erroné</span>
                    </div>
                    <p className="text-sm">Documentez ici précisément les différences entre l&apos;état civil fourni et celui détecté (ex: date de naissance avec un chiffre différent, prénom correspondant au 2ème prénom, etc.)</p>
                  </div>
                )}
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
            
            {/* Onglet Notes personnelles */}
            {activeTab === 'notes' && (
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-medium mb-4 flex items-center gap-2">
                  <StickyNote className="w-5 h-5 text-yellow-500" />
                  Notes personnelles
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Ces notes sont personnelles et vous aideront à vous rappeler des détails importants pour cette enquête.
                  Elles ne sont visibles que par vous et ne seront pas exportées dans les fichiers EOS.
                </p>
                <div>
                  <textarea
                    name="notes_personnelles"
                    value={formData.notes_personnelles}
                    onChange={handleInputChange}
                    className="w-full p-4 border rounded bg-yellow-50 min-h-[200px]"
                    placeholder="Ajoutez ici vos notes personnelles, rappels, ou informations confidentielles concernant cette enquête..."
                    rows="8"
                  ></textarea>
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

// Assigner les PropTypes après la définition du composant
UpdateModal.propTypes = UpdateModalPropTypes;

export default UpdateModal;
