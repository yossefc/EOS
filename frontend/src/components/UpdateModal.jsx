import { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import {
  User, MapPin, Calendar, Info, MessageSquare, Briefcase,
  CircleDollarSign, Check, AlertCircle, X, Building,
  StickyNote, HelpCircle, Baby, FileText
} from 'lucide-react';
import { COUNTRIES } from './countryData';
import config from '../config';
import EtatCivilPanel from './EtatCivilPanel';
import PartnerDemandesHeader from './PartnerDemandesHeader';
import PropTypes from 'prop-types';

const API_URL = config.API_URL;

// ============================================================
// CONSTANTS
// ============================================================
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

const STATUS_LABELS = {
  'P': 'Positif', 'N': 'Négatif / NPA', 'H': 'Confirmé',
  'Z': 'Annulé (agence)', 'I': 'Intraitable', 'Y': 'Annulé (EOS)', '': 'En attente'
};

const hasTextValue = (value) => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'string') return value.trim() !== '';
  return true;
};

const buildProximiteFromForm = (values) => {
  const confirmeParRaw =
    values?.elements_retrouves === 'AUTRE'
      ? (values?.elements_retrouves_autre || '')
      : (values?.elements_retrouves || '');
  const confirmePar = confirmeParRaw.trim() || 'non renseigne';

  const elements = [];

  const hasAdresse = [
    values?.adresse1, values?.adresse2, values?.adresse3, values?.adresse4,
    values?.code_postal, values?.ville, values?.pays_residence
  ].some(hasTextValue);
  if (hasAdresse) elements.push('adresse');

  const hasTelephone = [
    values?.telephone_personnel, values?.telephone_chez_employeur
  ].some(hasTextValue);
  if (hasTelephone) elements.push('telephone');

  const hasEmployeur = [
    values?.nom_employeur, values?.telephone_employeur, values?.telecopie_employeur,
    values?.adresse1_employeur, values?.adresse2_employeur, values?.adresse3_employeur,
    values?.adresse4_employeur, values?.code_postal_employeur, values?.ville_employeur,
    values?.pays_employeur
  ].some(hasTextValue);
  if (hasEmployeur) elements.push('employeur');

  const hasBanque = [
    values?.banque_domiciliation, values?.libelle_guichet, values?.titulaire_compte,
    values?.code_banque, values?.code_guichet
  ].some(hasTextValue);
  if (hasBanque) elements.push('banque');

  const hasDeces = [
    values?.date_deces, values?.numero_acte_deces, values?.code_insee_deces,
    values?.code_postal_deces, values?.localite_deces
  ].some(hasTextValue);
  if (hasDeces) elements.push('deces');

  const hasRevenus = [
    values?.commentaires_revenus, values?.montant_salaire,
    values?.nature_revenu1, values?.montant_revenu1,
    values?.nature_revenu2, values?.montant_revenu2,
    values?.nature_revenu3, values?.montant_revenu3
  ].some(hasTextValue);
  if (hasRevenus) elements.push('revenus');

  const foundText = elements.length > 0 ? elements.join(', ') : 'aucun element detaille';
  return `Confirme par: ${confirmePar} | Retrouve: ${foundText}`;
};

const ENQUETEUR_EXCLUDED_KEYS = new Set(['id', 'donnee_id', 'client_id', 'created_at', 'updated_at']);

const ENQUETEUR_FIELD_LABELS = {
  code_resultat: 'Code resultat',
  elements_retrouves: 'Elements retrouves',
  proximite: 'Confirme par / Proximite',
  flag_etat_civil_errone: 'Etat civil errone',
  date_retour: 'Date retour',
  adresse1: 'Adresse 1',
  adresse2: 'Adresse 2',
  adresse3: 'Adresse 3',
  adresse4: 'Adresse 4',
  code_postal: 'Code postal',
  ville: 'Ville',
  pays_residence: 'Pays residence',
  telephone_personnel: 'Telephone personnel',
  telephone_chez_employeur: 'Telephone chez employeur',
  date_deces: 'Date deces',
  numero_acte_deces: 'Numero acte deces',
  code_insee_deces: 'Code INSEE deces',
  code_postal_deces: 'Code postal deces',
  localite_deces: 'Localite deces',
  nom_employeur: 'Nom employeur',
  telephone_employeur: 'Telephone employeur',
  telecopie_employeur: 'Telecopie employeur',
  adresse1_employeur: 'Adresse 1 employeur',
  adresse2_employeur: 'Adresse 2 employeur',
  adresse3_employeur: 'Adresse 3 employeur',
  adresse4_employeur: 'Adresse 4 employeur',
  code_postal_employeur: 'Code postal employeur',
  ville_employeur: 'Ville employeur',
  pays_employeur: 'Pays employeur',
  banque_domiciliation: 'Banque domiciliation',
  libelle_guichet: 'Libelle guichet',
  titulaire_compte: 'Titulaire compte',
  code_banque: 'Code banque',
  code_guichet: 'Code guichet',
  commentaires_revenus: 'Commentaires revenus',
  montant_salaire: 'Montant salaire',
  periode_versement_salaire: 'Periode versement salaire',
  frequence_versement_salaire: 'Frequence versement salaire',
  nature_revenu1: 'Nature revenu 1',
  montant_revenu1: 'Montant revenu 1',
  periode_versement_revenu1: 'Periode versement revenu 1',
  frequence_versement_revenu1: 'Frequence versement revenu 1',
  nature_revenu2: 'Nature revenu 2',
  montant_revenu2: 'Montant revenu 2',
  periode_versement_revenu2: 'Periode versement revenu 2',
  frequence_versement_revenu2: 'Frequence versement revenu 2',
  nature_revenu3: 'Nature revenu 3',
  montant_revenu3: 'Montant revenu 3',
  periode_versement_revenu3: 'Periode versement revenu 3',
  frequence_versement_revenu3: 'Frequence versement revenu 3',
  memo1: 'Memo 1',
  memo2: 'Memo 2',
  memo3: 'Memo 3',
  memo4: 'Memo 4',
  memo5: 'Memo 5',
  notes_personnelles: 'Memo personnel',
  dateNaissance_maj: 'Date naissance MAJ',
  lieuNaissance_maj: 'Lieu naissance MAJ'
};

const buildHistoricalEnqueteurRows = (source) => {
  if (!source || typeof source !== 'object') return [];

  return Object.entries(source)
    .filter(([key, value]) => !ENQUETEUR_EXCLUDED_KEYS.has(key) && hasTextValue(value))
    .map(([key, value]) => ({
      key,
      label: ENQUETEUR_FIELD_LABELS[key] || key.replace(/_/g, ' '),
      value: typeof value === 'string' ? value.trim() : String(value)
    }));
};

const formatHistoryDate = (value) => {
  if (!value) return '-';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString('fr-FR');
};

// ============================================================
// REUSABLE COMPONENTS
// ============================================================

// Input field component
const Field = ({ label, name, value, onChange, type = 'text', disabled, placeholder, maxLength, className = '' }) => (
  <div className={className}>
    <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
    <input
      type={type}
      name={name}
      value={value || ''}
      onChange={onChange}
      disabled={disabled}
      placeholder={placeholder}
      maxLength={maxLength}
      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white 
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                 disabled:bg-slate-50 disabled:text-slate-400 transition-colors"
    />
  </div>
);

Field.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  type: PropTypes.string,
  disabled: PropTypes.bool,
  placeholder: PropTypes.string,
  maxLength: PropTypes.number,
  className: PropTypes.string
};

// Select field component
const SelectField = ({ label, name, value, onChange, options, disabled, className = '' }) => (
  <div className={className}>
    <label className="block text-xs font-medium text-slate-600 mb-1">{label}</label>
    <select
      name={name}
      value={value || ''}
      onChange={onChange}
      disabled={disabled}
      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white 
                 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                 disabled:bg-slate-50 disabled:text-slate-400 transition-colors"
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

SelectField.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  options: PropTypes.arrayOf(PropTypes.shape({
    value: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired
  })).isRequired,
  disabled: PropTypes.bool,
  className: PropTypes.string
};

// Info card for displaying original data
const InfoCard = ({ icon: Icon, title, children, color = 'slate' }) => {
  const colors = {
    slate: 'bg-slate-50 border-slate-200',
    blue: 'bg-blue-50 border-blue-200',
    amber: 'bg-amber-50 border-amber-200'
  };

  return (
    <div className={`rounded-lg border p-3 ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4 text-slate-500" />
        <span className="text-xs font-semibold text-slate-700 uppercase tracking-wide">{title}</span>
      </div>
      <div className="text-sm text-slate-700">{children}</div>
    </div>
  );
};

InfoCard.propTypes = {
  icon: PropTypes.elementType.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  color: PropTypes.oneOf(['slate', 'blue', 'amber'])
};

// Tab button component
const TabButton = ({ active, onClick, icon: Icon, label }) => (
  <button
    type="button"
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all
      ${active
        ? 'bg-white text-blue-600 border-t-2 border-x border-t-blue-500 border-x-slate-200 border-b-white -mb-px shadow-sm'
        : 'text-slate-500 hover:text-blue-600 hover:bg-white/50'}`}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
);

TabButton.propTypes = {
  active: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired,
  icon: PropTypes.elementType.isRequired,
  label: PropTypes.string.isRequired
};

// ============================================================
// TABS CONFIGURATION
// ============================================================
const getTabsForClient = (isPartner, showDeathTab, formData) => {
  const tabs = [
    { id: 'dossier', label: 'Dossier', icon: FileText },
  ];

  // Onglet Résultat uniquement pour EOS (pas PARTNER car dans l'en-tête)
  if (!isPartner) {
    tabs.push({ id: 'resultat', label: 'Résultat', icon: Check });
  }

  tabs.push({ id: 'etat-civil', label: 'État civil', icon: User });
  tabs.push({ id: 'adresse', label: 'Adresse', icon: MapPin });

  if (isPartner) {
    tabs.push({ id: 'naissance', label: 'Naissance', icon: Baby });
  }

  if (showDeathTab || formData.elements_retrouves?.includes('D')) {
    tabs.push({ id: 'deces', label: 'Décès', icon: Calendar });
  }

  if (isPartner || formData.elements_retrouves?.includes('E')) {
    tabs.push({ id: 'employeur', label: 'Employeur', icon: Briefcase });
  }

  if (!isPartner && formData.elements_retrouves?.includes('B')) {
    tabs.push({ id: 'banque', label: 'Banque', icon: Building });
  }

  if (!isPartner && formData.elements_retrouves?.includes('R')) {
    tabs.push({ id: 'revenus', label: 'Revenus', icon: CircleDollarSign });
  }

  tabs.push({ id: 'commentaires', label: 'Commentaires', icon: MessageSquare });
  tabs.push({ id: 'notes', label: 'Notes', icon: StickyNote });

  return tabs;
};

// ============================================================
// MAIN COMPONENT
// ============================================================
const UpdateModal = ({ isOpen, onClose, data }) => {
  // State
  const [clientCode, setClientCode] = useState('EOS');
  const [clientId, setClientId] = useState(null);
  const [confirmationOptions, setConfirmationOptions] = useState([]);
  const [activeTab, setActiveTab] = useState('dossier');
  const [showDeathInfo, setShowDeathInfo] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [donneesSauvegardees, setDonneesSauvegardees] = useState(null);
  const [enqueteurs, setEnqueteurs] = useState([]);
  const [isLoading, setIsLoading] = useState({ submit: false, adresse: false });
  const [suggestions, setSuggestions] = useState({ adresses: [], codesPostaux: [] });
  const [enqueteOriginaleData, setEnqueteOriginaleData] = useState(
    data?.enqueteOriginale || data?.enquete_originale || null
  );
  const [historiqueArchivesRows, setHistoriqueArchivesRows] = useState([]);

  const demandesHeaderRef = useRef(null);
  const confirmationOptionsRef = useRef([]);
  const isPartner = clientCode === 'PARTNER';

  // Form state
  const [formData, setFormData] = useState({
    enqueteurId: null,
    code_resultat: 'P',
    elements_retrouves: 'A',
    elements_retrouves_autre: '',
    flag_etat_civil_errone: '',
    date_retour: new Date().toISOString().split('T')[0],
    // Adresse
    adresse1: '', adresse2: '', adresse3: '', adresse4: '',
    code_postal: '', ville: '', pays_residence: 'FRANCE',
    telephone_personnel: '', telephone_chez_employeur: '',
    // Décès
    date_deces: '', numero_acte_deces: '', code_insee_deces: '',
    code_postal_deces: '', localite_deces: '',
    // Employeur
    nom_employeur: '', telephone_employeur: '', telecopie_employeur: '',
    adresse1_employeur: '', adresse2_employeur: '', adresse3_employeur: '', adresse4_employeur: '',
    code_postal_employeur: '', ville_employeur: '', pays_employeur: '',
    // Banque
    banque_domiciliation: '', libelle_guichet: '', titulaire_compte: '',
    code_banque: '', code_guichet: '',
    // Revenus
    commentaires_revenus: '', montant_salaire: '', periode_versement_salaire: '', frequence_versement_salaire: '',
    nature_revenu1: '', montant_revenu1: '', periode_versement_revenu1: '', frequence_versement_revenu1: '',
    nature_revenu2: '', montant_revenu2: '', periode_versement_revenu2: '', frequence_versement_revenu2: '',
    nature_revenu3: '', montant_revenu3: '', periode_versement_revenu3: '', frequence_versement_revenu3: '',
    // Mémos
    memo1: '', memo2: '', memo3: '', memo4: '', memo5: '',
    notes_personnelles: '',
    // PARTNER
    dateNaissance_maj: '', lieuNaissance_maj: ''
  });

  // ============================================================
  // EFFECTS & CALLBACKS
  // ============================================================

  // Load enquêteurs
  useEffect(() => {
    if (!isOpen) return;
    axios.get(`${API_URL}/api/enqueteurs`)
      .then(res => res.data.success && setEnqueteurs(res.data.data || []))
      .catch(err => console.error("Erreur enquêteurs:", err));
  }, [isOpen]);

  // Initialize form
  const initializeWithDossierData = useCallback(() => {
    if (!data) return;
    setFormData(prev => ({
      ...prev,
      enqueteurId: data.enqueteurId || null,
      code_resultat: 'P',
      elements_retrouves: data.elementDemandes || 'A',
      flag_etat_civil_errone: '',
      date_retour: new Date().toISOString().split('T')[0],
    }));
  }, [data]);

  useEffect(() => {
    setEnqueteOriginaleData(data?.enqueteOriginale || data?.enquete_originale || null);
  }, [data]);

  useEffect(() => {
    confirmationOptionsRef.current = confirmationOptions;
  }, [confirmationOptions]);

  // Load client and enqueteur data. For contestations, preserve original survey data.
  useEffect(() => {
    if (!data) return;
    let cancelled = false;
    const isContestation = data?.typeDemande === 'CON' || data?.est_contestation === true;

    const fetchClientData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/donnees/${data.id}`);
        if (!(response.data.success && response.data.data)) {
          setHistoriqueArchivesRows([]);
          return { originalData: null, resolvedClientCode: 'EOS' };
        }

        const payload = response.data.data;
        const clientData = payload.client || null;
        let fetchedOriginal = payload.enqueteOriginale || payload.enquete_originale || null;

        if (isContestation && data?.numeroDossier) {
          try {
            const historiqueResponse = await axios.get(
              `${API_URL}/api/historique-enquete/${encodeURIComponent(data.numeroDossier)}?donnee_id=${data.id}`
            );
            if (historiqueResponse.data?.success && historiqueResponse.data?.data?.enquete_originale) {
              fetchedOriginal = historiqueResponse.data.data.enquete_originale;
            }
          } catch (historiqueError) {
            console.warn('Impossible de charger historique-enquete pour pré-remplissage:', historiqueError);
          }
        }

        if (isContestation) {
          try {
            const samePersonHistoryResponse = await axios.get(`${API_URL}/api/donnees/${data.id}/historique`);
            if (samePersonHistoryResponse.data?.success) {
              setHistoriqueArchivesRows(samePersonHistoryResponse.data?.data?.enquetes_meme_nom || []);
            } else {
              setHistoriqueArchivesRows([]);
            }
          } catch (historyRowsError) {
            console.warn('Impossible de charger les enquetes archivees du meme nom/prenom:', historyRowsError);
            setHistoriqueArchivesRows([]);
          }
        } else {
          setHistoriqueArchivesRows([]);
        }

        const resolvedClientCode = clientData?.code || 'EOS';
        if (clientData) {
          setClientCode(clientData.code || 'EOS');
          setClientId(clientData.id);
        } else {
          setClientCode('EOS');
          setClientId(null);
        }

        setEnqueteOriginaleData(fetchedOriginal);

        if (clientData && clientData.code !== 'EOS') {
          const optionsRes = await axios.get(`${API_URL}/api/confirmation-options/${clientData.id}`);
          if (optionsRes.data.success) {
            setConfirmationOptions(optionsRes.data.all_options || []);
          }
        }

        return { originalData: fetchedOriginal, resolvedClientCode };
      } catch (error) {
        console.error('Erreur client:', error);
        setClientCode('EOS');
        setClientId(null);
        setHistoriqueArchivesRows([]);
        return { originalData: null, resolvedClientCode: 'EOS' };
      }
    };

    const fetchEnqueteurData = async (resolvedClientCode = 'EOS') => {
      try {
        const response = await axios.get(`${API_URL}/api/donnees-enqueteur/${data.id}`);
        if (response.data.success && response.data.data) {
          const d = response.data.data;
          const isPartnerClient = resolvedClientCode === 'PARTNER';

          setDonneesSauvegardees(d);

          const optionsPredefinies = isPartnerClient
            ? [...confirmationOptionsRef.current]
            : ['A', 'AT', 'D', 'AB', 'AE', 'ATB', 'ATE', 'ATBE', 'ATBER'];
          const elemVal = isPartnerClient
            ? (d.proximite || '')
            : (d.elements_retrouves || '');
          const hasElemVal = typeof elemVal === 'string' ? elemVal.trim() !== '' : Boolean(elemVal);
          const isPredefinie = hasElemVal && optionsPredefinies.includes(elemVal);

          // IMPORTANT: on ne pré-remplit que les données déjà saisies sur cette enquête.
          // Aucune reprise auto depuis l'historique enquêteur dans les autres onglets.
          setFormData({
            code_resultat: d.code_resultat || 'P',
            elements_retrouves: hasElemVal ? (isPredefinie ? elemVal : 'AUTRE') : '',
            elements_retrouves_autre: hasElemVal ? (isPredefinie ? '' : elemVal) : '',
            flag_etat_civil_errone: d.flag_etat_civil_errone || '',
            date_retour: d.date_retour || new Date().toISOString().split('T')[0],
            adresse1: d.adresse1 || '',
            adresse2: d.adresse2 || '',
            adresse3: d.adresse3 || '',
            adresse4: d.adresse4 || '',
            code_postal: d.code_postal || '',
            ville: d.ville || '',
            pays_residence: d.pays_residence || 'FRANCE',
            telephone_personnel: d.telephone_personnel || '',
            telephone_chez_employeur: d.telephone_chez_employeur || '',
            date_deces: d.date_deces || '',
            numero_acte_deces: d.numero_acte_deces || '',
            code_insee_deces: d.code_insee_deces || '',
            code_postal_deces: d.code_postal_deces || '',
            localite_deces: d.localite_deces || '',
            nom_employeur: d.nom_employeur || '',
            telephone_employeur: d.telephone_employeur || '',
            telecopie_employeur: d.telecopie_employeur || '',
            adresse1_employeur: d.adresse1_employeur || '',
            adresse2_employeur: d.adresse2_employeur || '',
            adresse3_employeur: d.adresse3_employeur || '',
            adresse4_employeur: d.adresse4_employeur || '',
            code_postal_employeur: d.code_postal_employeur || '',
            ville_employeur: d.ville_employeur || '',
            pays_employeur: d.pays_employeur || '',
            banque_domiciliation: d.banque_domiciliation || '',
            libelle_guichet: d.libelle_guichet || '',
            titulaire_compte: d.titulaire_compte || '',
            code_banque: d.code_banque || '',
            code_guichet: d.code_guichet || '',
            commentaires_revenus: d.commentaires_revenus || '',
            montant_salaire: d.montant_salaire || '',
            periode_versement_salaire: d.periode_versement_salaire || '',
            frequence_versement_salaire: d.frequence_versement_salaire || '',
            nature_revenu1: d.nature_revenu1 || '',
            montant_revenu1: d.montant_revenu1 || '',
            periode_versement_revenu1: d.periode_versement_revenu1 || '',
            frequence_versement_revenu1: d.frequence_versement_revenu1 || '',
            nature_revenu2: d.nature_revenu2 || '',
            montant_revenu2: d.montant_revenu2 || '',
            periode_versement_revenu2: d.periode_versement_revenu2 || '',
            frequence_versement_revenu2: d.frequence_versement_revenu2 || '',
            nature_revenu3: d.nature_revenu3 || '',
            montant_revenu3: d.montant_revenu3 || '',
            periode_versement_revenu3: d.periode_versement_revenu3 || '',
            frequence_versement_revenu3: d.frequence_versement_revenu3 || '',
            memo1: d.memo1 || '',
            memo2: d.memo2 || '',
            memo3: d.memo3 || '',
            memo4: d.memo4 || '',
            memo5: d.memo5 || '',
            notes_personnelles: d.notes_personnelles || '',
            dateNaissance_maj: data.dateNaissance_maj || '',
            lieuNaissance_maj: data.lieuNaissance_maj || ''
          });

          if (d.date_deces || String(elemVal).includes('D')) {
            setShowDeathInfo(true);
          }
        } else {
          initializeWithDossierData();
        }
      } catch (error) {
        console.log(error);
        initializeWithDossierData();
      }
    };

    const loadData = async () => {
      const clientLoad = await fetchClientData();
      if (cancelled) return;
      await fetchEnqueteurData(clientLoad?.resolvedClientCode || 'EOS');
    };

    loadData();
    return () => {
      cancelled = true;
    };
  }, [data, initializeWithDossierData]);

  // Address search
  const searchAddress = useCallback(async (query) => {
    if (query.length <= 2) {
      setSuggestions(prev => ({ ...prev, adresses: [] }));
      return;
    }
    setIsLoading(prev => ({ ...prev, adresse: true }));
    try {
      const res = await axios.get(
        `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=5&type=housenumber`
      );
      if (res.data.features?.length > 0) {
        setSuggestions(prev => ({
          ...prev,
          adresses: res.data.features.map(f => ({
            adresse: `${f.properties.housenumber} ${f.properties.street}`,
            codePostal: f.properties.postcode,
            ville: f.properties.city,
            adresseComplete: f.properties.label
          }))
        }));
      }
    } catch (err) {
      console.error('Erreur adresse:', err);
    } finally {
      setIsLoading(prev => ({ ...prev, adresse: false }));
    }
  }, []);

  // Postal code search
  const searchByPostalCode = useCallback(async (code) => {
    if (code.length < 3) return;
    setIsLoading(prev => ({ ...prev, adresse: true }));
    try {
      const res = await axios.get(
        `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(code)}&type=municipality&limit=5`
      );
      if (res.data.features?.length > 0) {
        const villes = res.data.features.map(f => ({
          codePostal: f.properties.postcode,
          ville: f.properties.city,
          label: `${f.properties.postcode} ${f.properties.city}`
        }));
        setSuggestions(prev => ({ ...prev, codesPostaux: villes }));
        if (code.length === 5 && villes.length === 1) {
          setFormData(prev => ({ ...prev, ville: villes[0].ville }));
        }
      }
    } catch (err) {
      console.error('Erreur CP:', err);
    } finally {
      setIsLoading(prev => ({ ...prev, adresse: false }));
    }
  }, []);

  // ============================================================
  // HANDLERS
  // ============================================================

  const handleEnqueteurChange = async (newEnqueteurId) => {
    try {
      await axios.put(`${API_URL}/api/donnees/${data.id}`, { enqueteurId: newEnqueteurId || null });
      setFormData(prev => ({ ...prev, enqueteurId: newEnqueteurId }));
      setSuccess("Enquêteur assigné");
      setTimeout(() => setSuccess(null), 2000);
    } catch (error) {
      console.error('Erreur assignation:', error);
      setError("Erreur lors de l'assignation");
      setTimeout(() => setError(null), 3000);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === 'adresse3') searchAddress(value);
    else if (name === 'code_postal' && value.length >= 3) searchByPostalCode(value);
    else if (name === 'code_resultat') {
      if (value === 'D') {
        setShowDeathInfo(true);
        setActiveTab('deces');
        setFormData(prev => ({ ...prev, [name]: value, elements_retrouves: 'D' }));
        return;
      }
      if (value === 'I') {
        setFormData(prev => ({
          ...prev, [name]: value,
          qualite: data?.qualite || '', nom: data?.nom || '', prenom: data?.prenom || '',
          dateNaissance: data?.dateNaissance || '', lieuNaissance: data?.lieuNaissance || '',
          codePostalNaissance: data?.codePostalNaissance || '', paysNaissance: data?.paysNaissance || '',
          nomPatronymique: data?.nomPatronymique || '', elements_retrouves: '', flag_etat_civil_errone: ''
        }));
        return;
      }
    } else if (name === 'flag_etat_civil_errone' && value === 'E') {
      setFormData(prev => ({ ...prev, [name]: value, code_resultat: 'P' }));
      setError("Documentez les différences d'état civil dans les commentaires.");
      return;
    }

    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddressSelect = (adresse) => {
    setFormData(prev => ({
      ...prev,
      adresse3: adresse.adresse,
      code_postal: adresse.codePostal,
      ville: adresse.ville,
      pays_residence: 'FRANCE'
    }));
    setSuggestions({ adresses: [], codesPostaux: [] });
  };

  const handlePostalCodeSelect = (item) => {
    setFormData(prev => ({
      ...prev,
      code_postal: item.codePostal,
      ville: item.ville,
      pays_residence: 'FRANCE'
    }));
    setSuggestions(prev => ({ ...prev, codesPostaux: [] }));
  };

  // Validation
  const validateFormData = () => {
    if (clientCode !== 'EOS') return null;

    if (formData.code_resultat === 'P') {
      if (!formData.elements_retrouves) return "Spécifiez les éléments retrouvés";
      if (formData.elements_retrouves.includes('A') && (!formData.adresse3 || !formData.code_postal || !formData.ville))
        return "L'adresse est incomplète";
      if (formData.elements_retrouves.includes('T') && !formData.telephone_personnel)
        return "Le téléphone est obligatoire";
      if (formData.elements_retrouves.includes('D') && !formData.date_deces)
        return "La date de décès est obligatoire";
      if (formData.elements_retrouves.includes('B') && (!formData.banque_domiciliation || !formData.code_banque || !formData.code_guichet))
        return "Les coordonnées bancaires sont incomplètes";
      if (formData.elements_retrouves.includes('E') && !formData.nom_employeur)
        return "Le nom de l'employeur est obligatoire";
      if (formData.flag_etat_civil_errone === 'E' && !formData.memo1 && !formData.memo2 && !formData.memo3 && !formData.memo4 && !formData.memo5)
        return "Documentez les différences d'état civil dans les mémos";
    } else if (formData.code_resultat === 'D' && !formData.date_deces) {
      return "La date de décès est obligatoire";
    }
    return null;
  };

  // Submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(prev => ({ ...prev, submit: true }));
    setError(null);
    setSuccess(null);

    const errorMsg = validateFormData();
    if (errorMsg) {
      setError(errorMsg);
      setIsLoading(prev => ({ ...prev, submit: false }));
      return;
    }

    try {
      let elementsRetrouvesValue = formData.elements_retrouves;
      if (isPartner && formData.elements_retrouves === 'AUTRE' && formData.elements_retrouves_autre) {
        elementsRetrouvesValue = formData.elements_retrouves_autre;
      }

      let dataToSend = {
        donnee_id: data.id,
        code_resultat: formData.code_resultat,
        elements_retrouves: formData.code_resultat === 'I' ? '' : (isPartner ? '' : elementsRetrouvesValue),
        flag_etat_civil_errone: formData.flag_etat_civil_errone,
        date_retour: formData.date_retour,
      };

      if (isPartner) {
        dataToSend.proximite = formData.code_resultat === 'I' ? '' : elementsRetrouvesValue;
      }

      if (formData.flag_etat_civil_errone === 'E') {
        dataToSend = {
          ...dataToSend,
          qualite_corrigee: formData.qualite_corrigee || null,
          nom_corrige: formData.nom_corrige || null,
          prenom_corrige: formData.prenom_corrige || null,
          nom_patronymique_corrige: formData.nom_patronymique_corrige || null,
          code_postal_naissance_corrige: formData.code_postal_naissance_corrige || null,
          pays_naissance_corrige: formData.pays_naissance_corrige || null,
          type_divergence: formData.type_divergence || null,
        };
      }

      if (formData.code_resultat === 'I') {
        dataToSend = {
          ...dataToSend,
          qualite: data?.qualite || '', nom: data?.nom || '', prenom: data?.prenom || '',
          dateNaissance: data?.dateNaissance || '', lieuNaissance: data?.lieuNaissance || '',
          codePostalNaissance: data?.codePostalNaissance || '', paysNaissance: data?.paysNaissance || '',
          nomPatronymique: data?.nomPatronymique || '', elements_retrouves: '',
          adresse1: '', adresse2: '', adresse3: '', adresse4: '',
          code_postal: '', ville: '', pays_residence: '',
          telephone_personnel: '', telephone_chez_employeur: '',
          date_deces: null, numero_acte_deces: '', code_insee_deces: '',
          code_postal_deces: '', localite_deces: '',
          nom_employeur: '', telephone_employeur: '', telecopie_employeur: '',
          adresse1_employeur: '', adresse2_employeur: '', adresse3_employeur: '', adresse4_employeur: '',
          code_postal_employeur: '', ville_employeur: '', pays_employeur: '',
          banque_domiciliation: '', libelle_guichet: '', titulaire_compte: '',
          code_banque: '', code_guichet: '',
          commentaires_revenus: '', montant_salaire: null, periode_versement_salaire: null,
          frequence_versement_salaire: '',
          nature_revenu1: '', montant_revenu1: null, periode_versement_revenu1: null, frequence_versement_revenu1: '',
          nature_revenu2: '', montant_revenu2: null, periode_versement_revenu2: null, frequence_versement_revenu2: '',
          nature_revenu3: '', montant_revenu3: null, periode_versement_revenu3: null, frequence_versement_revenu3: '',
          memo1: formData.memo1, memo2: formData.memo2, memo3: formData.memo3,
          memo4: formData.memo4, memo5: formData.memo5, notes_personnelles: formData.notes_personnelles
        };
        if (isPartner) {
          dataToSend.proximite = '';
        }
      } else {
        dataToSend = {
          ...dataToSend,
          adresse1: formData.adresse1, adresse2: formData.adresse2,
          adresse3: formData.adresse3, adresse4: formData.adresse4,
          code_postal: formData.code_postal, ville: formData.ville,
          pays_residence: formData.pays_residence,
          telephone_personnel: formData.telephone_personnel,
          telephone_chez_employeur: formData.telephone_chez_employeur,
          date_deces: formData.date_deces || null,
          numero_acte_deces: formData.numero_acte_deces,
          code_insee_deces: formData.code_insee_deces,
          code_postal_deces: formData.code_postal_deces,
          localite_deces: formData.localite_deces,
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
          banque_domiciliation: formData.banque_domiciliation,
          libelle_guichet: formData.libelle_guichet,
          titulaire_compte: formData.titulaire_compte,
          code_banque: formData.code_banque,
          code_guichet: formData.code_guichet,
          commentaires_revenus: formData.commentaires_revenus,
          montant_salaire: formData.montant_salaire || null,
          periode_versement_salaire: formData.periode_versement_salaire || null,
          frequence_versement_salaire: formData.frequence_versement_salaire || null,
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
          memo1: formData.memo1, memo2: formData.memo2, memo3: formData.memo3,
          memo4: formData.memo4, memo5: formData.memo5,
          notes_personnelles: formData.notes_personnelles
        };

        if (isPartner) {
          dataToSend.dateNaissance_maj = formData.dateNaissance_maj || null;
          dataToSend.lieuNaissance_maj = formData.lieuNaissance_maj || null;

          if (formData.elements_retrouves === 'AUTRE' && formData.elements_retrouves_autre && clientId) {
            try {
              await axios.post(`${API_URL}/api/confirmation-options`, {
                client_id: clientId,
                option_text: formData.elements_retrouves_autre
              });
            } catch (err) {
              console.error("Erreur sauvegarde option:", err);
            }
          }
        }
      }

      const response = await axios.post(`${API_URL}/api/donnees-enqueteur/${data.id}`, dataToSend);

      if (response.data.success) {
        try {
          await axios.put(`${API_URL}/api/donnees/${data.id}/statut`, { statut_validation: 'confirmee' });
        } catch (err) {
          console.warn('Erreur statut:', err);
        }

        setSuccess("Données enregistrées avec succès");
        setDonneesSauvegardees(response.data.data);

        if (isPartner && demandesHeaderRef.current) {
          setTimeout(() => demandesHeaderRef.current.refresh(), 300);
        }

        setTimeout(() => onClose(true), 1000);
      } else {
        setError("Erreur: " + response.data.error);
      }
    } catch (error) {
      console.error('Erreur:', error.response?.data || error.message);
      setError("Erreur: " + (error.response?.data?.error || error.message));
    } finally {
      setIsLoading(prev => ({ ...prev, submit: false }));
    }
  };

  // ============================================================
  // RENDER
  // ============================================================
  if (!isOpen || !data) return null;

  const isContestationRecord = data?.typeDemande === 'CON' || data?.est_contestation === true;
  const contestationOriginal = enqueteOriginaleData || data.enqueteOriginale || data.enquete_originale || null;
  const originalEnqueteur = contestationOriginal?.donnee_enqueteur || contestationOriginal?.donneeEnqueteur || {};
  const partnerInstructionText =
    data?.instructions ||
    data?.motif ||
    data?.motifDeContestation ||
    data?.motif_contestation_detail ||
    '';
  const historicalEnqueteurRows = buildHistoricalEnqueteurRows(originalEnqueteur);
  const historiqueArchives = (historiqueArchivesRows || []).filter((row) => row && row.id !== data.id);
  const proximitePreview = isPartner ? buildProximiteFromForm(formData) : '';
  const tabs = getTabsForClient(isPartner, showDeathInfo, formData);
  const isDisabled = formData.code_resultat === 'I';

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl w-full max-w-6xl h-[90vh] flex flex-col shadow-2xl overflow-hidden border border-slate-200">

        {/* ==================== HEADER ==================== */}
        <div className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-6">
            {/* Dossier info */}
            <div>
              <div className="text-[10px] text-blue-600 font-semibold uppercase tracking-wider">Dossier</div>
              <div className="text-xl font-bold text-slate-800">{data?.numeroDossier}</div>
            </div>

            <div className="h-10 w-px bg-slate-200" />

            {/* Cible */}
            <div>
              <div className="text-[10px] text-blue-600 font-semibold uppercase tracking-wider">Cible</div>
              <div className="font-semibold text-slate-800">{data?.nom} {data?.prenom}</div>
            </div>

            <div className="h-10 w-px bg-slate-200" />

            {/* Type */}
            <span className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase
              ${isContestationRecord
                ? 'bg-amber-100 text-amber-700 border border-amber-200'
                : 'bg-blue-100 text-blue-700 border border-blue-200'}`}>
              {isContestationRecord ? 'Contestation' : 'Enquête'}
            </span>

            {/* Enquêteur */}
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5">
              <User className="w-4 h-4 text-slate-500" />
              <select
                value={formData.enqueteurId || ''}
                onChange={(e) => handleEnqueteurChange(e.target.value)}
                className="bg-transparent text-sm font-medium text-slate-700 border-none focus:ring-0 cursor-pointer"
              >
                <option value="">Non assigné</option>
                {enqueteurs.map((enq) => (
                  <option key={enq.id} value={enq.id}>
                    {enq.nom} {enq.prenom}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => onClose(false)}
              disabled={isLoading.submit}
              className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-300 
                         rounded-lg hover:bg-slate-50 transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              form="enquete-form"
              disabled={isLoading.submit}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg 
                         hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {isLoading.submit ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Enregistrement...
                </>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  Enregistrer
                </>
              )}
            </button>

            {/* Close button */}
            <button
              type="button"
              onClick={() => onClose(false)}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* PARTNER Section - Demandes + Instructions à gauche, Résultat à droite */}
        {isPartner && (
          <div className="bg-gradient-to-r from-slate-50 to-blue-50 border-b border-slate-200 px-6 py-3">
            <div className="flex items-start gap-8">
              {/* Colonne gauche : Demandes + Instructions */}
              <div className="flex-1 space-y-2">
                {/* Demandes */}
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-500 uppercase w-24">Demandes:</span>
                  <PartnerDemandesHeader ref={demandesHeaderRef} donneeId={data.id} compact={true} />
                </div>

                {/* Instructions */}
                {partnerInstructionText && (
                  <div className="flex items-start gap-2">
                    <span className="text-xs font-bold text-amber-600 uppercase w-24 flex-shrink-0">Instructions:</span>
                    <span className="text-sm text-slate-700">{partnerInstructionText}</span>
                  </div>
                )}
              </div>

              {/* Colonne droite : Champs résultat */}
              <div className="flex items-center gap-4 bg-white rounded-lg border border-slate-200 px-4 py-2 shadow-sm">
                {/* Code résultat */}
                <div className="flex items-center gap-2">
                  <label className="text-xs font-medium text-slate-500">Résultat:</label>
                  <select
                    name="code_resultat"
                    value={formData.code_resultat}
                    onChange={handleInputChange}
                    className="px-2 py-1 text-sm font-semibold border border-slate-200 rounded bg-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="P">P - Positif</option>
                    <option value="N">N - Négatif</option>
                  </select>
                </div>

                {/* Séparateur */}
                <div className="h-8 w-px bg-slate-200" />

                {/* Confirmé par qui */}
                <div className="flex items-center gap-2">
                  <label className="text-xs font-medium text-slate-500">Confirmé par:</label>
                  <select
                    name="elements_retrouves"
                    value={formData.elements_retrouves}
                    onChange={handleInputChange}
                    className="px-2 py-1 text-sm border border-slate-200 rounded bg-white focus:ring-2 focus:ring-blue-500 min-w-[160px]"
                  >
                    <option value="">Sélectionner...</option>
                    {confirmationOptions.map((opt, i) => (
                      <option key={i} value={opt}>{opt}</option>
                    ))}
                    <option value="AUTRE">Autre...</option>
                  </select>
                </div>

                {/* Saisie libre si "Autre" */}
                {formData.elements_retrouves === 'AUTRE' && (
                  <>
                    <div className="h-8 w-px bg-slate-200" />
                    <input
                      type="text"
                      name="elements_retrouves_autre"
                      value={formData.elements_retrouves_autre}
                      onChange={handleInputChange}
                      placeholder="Précisez..."
                      className="px-2 py-1 text-sm border border-blue-300 rounded bg-blue-50 focus:ring-2 focus:ring-blue-500 w-32"
                    />
                  </>
                )}

                {/* Séparateur */}
                <div className="h-8 w-px bg-slate-200" />

                {/* État civil erroné */}
                <div className="flex items-center gap-2">
                  <label className="text-xs font-medium text-slate-500">État civil erroné:</label>
                  <select
                    name="flag_etat_civil_errone"
                    value={formData.flag_etat_civil_errone}
                    onChange={handleInputChange}
                    className="px-2 py-1 text-sm border border-slate-200 rounded bg-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Non</option>
                    <option value="E">Oui</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        {(error || success) && (
          <div className={`mx-6 mt-4 p-3 rounded-lg flex items-center gap-2 text-sm font-medium
            ${error ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200'}`}>
            {error ? <AlertCircle className="w-4 h-4" /> : <Check className="w-4 h-4" />}
            {error || success}
          </div>
        )}

        {/* ==================== TABS ==================== */}
        <div className="px-6 pt-4 bg-slate-50 flex-shrink-0">
          <div className="flex gap-1 border-b border-slate-200">
            {tabs.map(tab => (
              <TabButton
                key={tab.id}
                active={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
                icon={tab.icon}
                label={tab.label}
              />
            ))}
          </div>
        </div>

        {/* ==================== CONTENT ==================== */}
        <form id="enquete-form" onSubmit={handleSubmit} className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-6 py-4 bg-slate-50/50">

            {/* TAB: Dossier (infos originales) */}
            {activeTab === 'dossier' && (
              <div className="grid grid-cols-3 gap-4">
                {/* Identité */}
                <InfoCard icon={User} title="Identité">
                  <div className="space-y-1">
                    <div><span className="text-slate-500">Nom:</span> <strong>{data.nom}</strong></div>
                    <div><span className="text-slate-500">Prénom:</span> <strong>{data.prenom}</strong></div>
                    {data.nomPatronymique && <div><span className="text-slate-500">Patronyme:</span> {data.nomPatronymique}</div>}
                    {data.qualite && <div><span className="text-slate-500">Qualité:</span> {data.qualite}</div>}
                  </div>
                </InfoCard>

                {/* Naissance */}
                <InfoCard icon={Baby} title="Naissance">
                  <div className="space-y-1">
                    <div><span className="text-slate-500">Date:</span> <strong>{data.dateNaissance || '-'}</strong></div>
                    <div><span className="text-slate-500">Lieu:</span> {data.lieuNaissance || '-'}</div>
                    {data.codePostalNaissance && <div><span className="text-slate-500">CP:</span> {data.codePostalNaissance}</div>}
                    {data.paysNaissance && <div><span className="text-slate-500">Pays:</span> {data.paysNaissance}</div>}
                  </div>
                </InfoCard>

                {/* Adresse origine */}
                <InfoCard icon={MapPin} title="Adresse (fichier)">
                  <div className="space-y-1">
                    {data.adresse1_origine && <div>{data.adresse1_origine}</div>}
                    {data.adresse2_origine && <div>{data.adresse2_origine}</div>}
                    {data.adresse3_origine && <div>{data.adresse3_origine}</div>}
                    {data.adresse4_origine && <div>{data.adresse4_origine}</div>}
                    <div>{data.codePostal_origine} {data.ville_origine}</div>
                    {data.paysResidence_origine && <div>{data.paysResidence_origine}</div>}
                  </div>
                </InfoCard>

                {/* Téléphones */}
                {(data.telephonePersonnel_origine || data.telephoneEmployeur_origine) && (
                  <InfoCard icon={Info} title="Téléphones">
                    <div className="space-y-1">
                      {data.telephonePersonnel_origine && <div><span className="text-slate-500">Personnel:</span> {data.telephonePersonnel_origine}</div>}
                      {data.telephoneEmployeur_origine && <div><span className="text-slate-500">Employeur:</span> {data.telephoneEmployeur_origine}</div>}
                    </div>
                  </InfoCard>
                )}

                {/* Banque origine */}
                {data.banqueDomiciliation_origine && (
                  <InfoCard icon={Building} title="Banque (fichier)">
                    <div className="space-y-1">
                      <div><strong>{data.banqueDomiciliation_origine}</strong></div>
                      {data.titulaireCompte_origine && <div><span className="text-slate-500">Titulaire:</span> {data.titulaireCompte_origine}</div>}
                      <div className="text-xs text-slate-500">
                        {data.codeBanque_origine && <>Banque: {data.codeBanque_origine} </>}
                        {data.codeGuichet_origine && <>Guichet: {data.codeGuichet_origine}</>}
                      </div>
                    </div>
                  </InfoCard>
                )}

                {isContestationRecord && historiqueArchives.length > 0 && (
                  <InfoCard
                    icon={FileText}
                    title={`Toutes Les Donnees Trouvees Par L Enqueteur (Archives: ${historiqueArchives.length})`}
                    color="amber"
                  >
                    <div className="space-y-3">
                      {historiqueArchives.map((archiveRow) => {
                        const archiveFields = buildHistoricalEnqueteurRows(archiveRow.donnee_enqueteur_saisie || {});
                        return (
                          <div key={archiveRow.id} className="rounded-lg border border-amber-200 bg-white p-3">
                            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-700">
                              <span className="font-semibold">#{archiveRow.id}</span>
                              {archiveRow.numeroDossier ? <span>Dossier: {archiveRow.numeroDossier}</span> : null}
                              <span>Date: {formatHistoryDate(archiveRow.date)}</span>
                              {archiveRow.element_demandes ? <span>Element demande: {archiveRow.element_demandes}</span> : null}
                              {archiveRow.code_resultat ? <span>Resultat: {archiveRow.code_resultat}</span> : null}
                              {archiveRow.elements_retrouves ? <span>Element retrouve: {archiveRow.elements_retrouves}</span> : null}
                            </div>

                            {archiveRow.memo_personnel ? (
                              <div className="mt-2 text-sm text-slate-700">
                                <span className="text-slate-500">Memo personnel:</span>{' '}
                                <span className="whitespace-pre-wrap">{archiveRow.memo_personnel}</span>
                              </div>
                            ) : null}

                            {archiveFields.length > 0 ? (
                              <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                                {archiveFields.map((row) => (
                                  <div key={`${archiveRow.id}-${row.key}`} className="text-sm">
                                    <span className="text-slate-500">{row.label}:</span>{' '}
                                    <span className="text-slate-800 break-words">{row.value}</span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="mt-2 text-xs text-slate-500">Aucune donnee enqueteur saisie.</div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </InfoCard>
                )}

                {isContestationRecord && historiqueArchives.length === 0 && historicalEnqueteurRows.length > 0 && (
                  <InfoCard icon={FileText} title="Donnees Enqueteur Historique (Lecture Seule)" color="amber">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {historicalEnqueteurRows.map((row) => (
                        <div key={row.key} className="text-sm">
                          <span className="text-slate-500">{row.label}:</span>{' '}
                          <span className="text-slate-800 break-words">{row.value}</span>
                        </div>
                      ))}
                    </div>
                  </InfoCard>
                )}

                {/* Commentaire import */}
                {data.commentaire && (
                  <InfoCard icon={MessageSquare} title="Commentaire import" color="blue">
                    <div className="italic">{data.commentaire}</div>
                  </InfoCard>
                )}

                {/* Dernière sauvegarde */}
                {donneesSauvegardees && (
                  <InfoCard icon={Check} title="Dernière sauvegarde" color="blue">
                    <div className="space-y-1">
                      <div><span className="text-slate-500">Statut:</span> <strong>{STATUS_LABELS[donneesSauvegardees.code_resultat]}</strong></div>
                      <div><span className="text-slate-500">Éléments:</span> {donneesSauvegardees.elements_retrouves || '-'}</div>
                      {donneesSauvegardees.proximite && (
                        <div><span className="text-slate-500">Proximite:</span> {donneesSauvegardees.proximite}</div>
                      )}
                      <div className="text-xs text-slate-500">
                        {new Date(donneesSauvegardees.updated_at).toLocaleString()}
                      </div>
                    </div>
                  </InfoCard>
                )}
              </div>
            )}

            {/* TAB: Résultat */}
            {activeTab === 'resultat' && (
              <div className="grid grid-cols-3 gap-6">
                <SelectField
                  label="Code résultat"
                  name="code_resultat"
                  value={formData.code_resultat}
                  onChange={handleInputChange}
                  options={CODES_RESULTAT.map(c => ({ value: c.code, label: `${c.code} - ${c.libelle}` }))}
                />

                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">
                    {isPartner ? 'Confirmation par qui' : 'Éléments retrouvés'}
                  </label>
                  {isPartner ? (
                    <div className="space-y-2">
                      <select
                        name="elements_retrouves"
                        value={formData.elements_retrouves}
                        onChange={handleInputChange}
                        disabled={isDisabled}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white 
                                   focus:ring-2 focus:ring-blue-500 disabled:bg-slate-50"
                      >
                        <option value="">Sélectionner...</option>
                        {confirmationOptions.map((opt, i) => (
                          <option key={i} value={opt}>{opt}</option>
                        ))}
                        <option value="AUTRE">Autre...</option>
                      </select>
                      {formData.elements_retrouves === 'AUTRE' && (
                        <input
                          type="text"
                          name="elements_retrouves_autre"
                          value={formData.elements_retrouves_autre}
                          onChange={handleInputChange}
                          placeholder="Précisez..."
                          className="w-full px-3 py-2 text-sm border border-blue-300 rounded-lg bg-blue-50"
                        />
                      )}
                    </div>
                  ) : (
                    <select
                      name="elements_retrouves"
                      value={formData.elements_retrouves}
                      onChange={handleInputChange}
                      disabled={isDisabled}
                      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white 
                                 focus:ring-2 focus:ring-blue-500 disabled:bg-slate-50"
                    >
                      <option value="A">A - Adresse</option>
                      <option value="AT">AT - Adresse et téléphone</option>
                      <option value="D">D - Décès</option>
                      <option value="AB">AB - Adresse et banque</option>
                      <option value="AE">AE - Adresse et employeur</option>
                      <option value="ATB">ATB - Adresse, téléphone et banque</option>
                      <option value="ATE">ATE - Adresse, téléphone et employeur</option>
                      <option value="ATBE">ATBE - Adresse, tél, banque et employeur</option>
                      <option value="ATBER">ATBER - Tous éléments</option>
                    </select>
                  )}
                </div>

                <SelectField
                  label="État civil erroné ?"
                  name="flag_etat_civil_errone"
                  value={formData.flag_etat_civil_errone}
                  onChange={handleInputChange}
                  options={[
                    { value: '', label: 'Non' },
                    { value: 'E', label: 'Oui (E)' }
                  ]}
                  disabled={isDisabled}
                />
              </div>
            )}

            {/* TAB: État civil */}
            {activeTab === 'etat-civil' && (
              <EtatCivilPanel
                originalData={{
                  qualite: data?.qualite, nom: data?.nom, prenom: data?.prenom,
                  dateNaissance: data?.dateNaissance, lieuNaissance: data?.lieuNaissance,
                  codePostalNaissance: data?.codePostalNaissance, paysNaissance: data?.paysNaissance,
                  nomPatronymique: data?.nomPatronymique
                }}
                formData={formData}
                setFormData={setFormData}
                onValidate={(correctedData, divergenceType) => {
                  setFormData(prev => ({
                    ...prev,
                    flag_etat_civil_errone: 'E',
                    qualite_corrigee: correctedData.qualite,
                    nom_corrige: correctedData.nom,
                    prenom_corrige: correctedData.prenom,
                    nom_patronymique_corrige: correctedData.nomPatronymique,
                    code_postal_naissance_corrige: correctedData.codePostalNaissance,
                    pays_naissance_corrige: correctedData.paysNaissance,
                    type_divergence: divergenceType,
                    memo5: `${prev.memo5 ? prev.memo5 + '\n\n' : ''}État civil corrigé (${divergenceType}):\nNom: ${correctedData.nom || '-'}\nPrénom: ${correctedData.prenom || '-'}`
                  }));
                }}
              />
            )}

            {/* TAB: Adresse */}
            {activeTab === 'adresse' && (
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                <Field label="Ligne 1 (Étage, Appartement)" name="adresse1" value={formData.adresse1} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <Field label="Ligne 2 (Bâtiment, Escalier)" name="adresse2" value={formData.adresse2} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />

                <div className="relative">
                  <Field label="Ligne 3 (N° et rue) *" name="adresse3" value={formData.adresse3} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                  {suggestions.adresses.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-40 overflow-auto">
                      {suggestions.adresses.map((a, i) => (
                        <button key={i} type="button" onClick={() => handleAddressSelect(a)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-slate-50 border-b last:border-b-0">
                          {a.adresseComplete}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <Field label="Ligne 4 (Lieu-dit)" name="adresse4" value={formData.adresse4} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />

                <div className="relative">
                  <Field label="Code postal *" name="code_postal" value={formData.code_postal} onChange={handleInputChange} disabled={isDisabled} maxLength={10} />
                  {suggestions.codesPostaux.length > 0 && (
                    <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-40 overflow-auto">
                      {suggestions.codesPostaux.map((item, i) => (
                        <button key={i} type="button" onClick={() => handlePostalCodeSelect(item)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-slate-50 border-b last:border-b-0">
                          {item.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                <Field label="Ville *" name="ville" value={formData.ville} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />

                <SelectField label="Pays" name="pays_residence" value={formData.pays_residence} onChange={handleInputChange} disabled={isDisabled}
                  options={COUNTRIES.map(c => ({ value: c, label: c }))} />

                <Field label="Téléphone personnel" name="telephone_personnel" value={formData.telephone_personnel} onChange={handleInputChange} disabled={isDisabled} maxLength={15} placeholder="0123456789" />
                <Field label="Tél. chez employeur" name="telephone_chez_employeur" value={formData.telephone_chez_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={15} />
              </div>
            )}

            {/* TAB: Naissance (PARTNER) */}
            {activeTab === 'naissance' && isPartner && (
              <div className="grid grid-cols-2 gap-6">
                {/* Colonne gauche : Informations d'origine */}
                <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
                  <h3 className="text-sm font-semibold text-slate-700 mb-4 flex items-center gap-2">
                    <Baby className="w-4 h-4 text-slate-500" />
                    Naissance (fichier importé)
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <span className="text-xs text-slate-500 block mb-1">Date de naissance</span>
                      <span className="text-lg font-bold text-slate-800">{data?.dateNaissance || '-'}</span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 block mb-1">Lieu de naissance</span>
                      <span className="text-lg font-bold text-slate-800">{data?.lieuNaissance || '-'}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs text-slate-500 block mb-1">Code postal</span>
                        <span className="text-sm font-semibold text-slate-700">{data?.codePostalNaissance || '-'}</span>
                      </div>
                      <div>
                        <span className="text-xs text-slate-500 block mb-1">Pays</span>
                        <span className="text-sm font-semibold text-slate-700">{data?.paysNaissance || '-'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Colonne droite : Informations retrouvées */}
                <div className="bg-blue-50 rounded-lg border border-blue-200 p-4">
                  <h3 className="text-sm font-semibold text-blue-700 mb-4 flex items-center gap-2">
                    <Check className="w-4 h-4" />
                    Naissance retrouvée
                  </h3>
                  <p className="text-xs text-blue-600 mb-4">
                    Remplissez uniquement si différent du fichier importé
                  </p>
                  <div className="space-y-4">
                    <Field
                      label="Date de naissance retrouvée"
                      name="dateNaissance_maj"
                      type="date"
                      value={formData.dateNaissance_maj}
                      onChange={handleInputChange}
                    />
                    <Field
                      label="Lieu de naissance retrouvé"
                      name="lieuNaissance_maj"
                      value={formData.lieuNaissance_maj}
                      onChange={handleInputChange}
                      placeholder="Ex: Paris 12ème"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Décès */}
            {activeTab === 'deces' && (
              <div className="grid grid-cols-3 gap-4">
                <Field label="Date de décès *" name="date_deces" type="date" value={formData.date_deces} onChange={handleInputChange} disabled={isDisabled} />
                <Field label="N° acte de décès" name="numero_acte_deces" value={formData.numero_acte_deces} onChange={handleInputChange} disabled={isDisabled} maxLength={10} />
                <Field label="Code INSEE" name="code_insee_deces" value={formData.code_insee_deces} onChange={handleInputChange} disabled={isDisabled} maxLength={5} />
                <Field label="Code postal" name="code_postal_deces" value={formData.code_postal_deces} onChange={handleInputChange} disabled={isDisabled} maxLength={10} />
                <Field label="Localité" name="localite_deces" value={formData.localite_deces} onChange={handleInputChange} disabled={isDisabled} maxLength={32} className="col-span-2" />
              </div>
            )}

            {/* TAB: Employeur */}
            {activeTab === 'employeur' && (
              <div className="grid grid-cols-3 gap-4">
                <Field label="Nom employeur *" name="nom_employeur" value={formData.nom_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={32} className="col-span-2" />
                <Field label="Téléphone" name="telephone_employeur" value={formData.telephone_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={15} />
                <Field label="Adresse 1" name="adresse1_employeur" value={formData.adresse1_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <Field label="Adresse 2" name="adresse2_employeur" value={formData.adresse2_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <Field label="Adresse 3" name="adresse3_employeur" value={formData.adresse3_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <Field label="Code postal" name="code_postal_employeur" value={formData.code_postal_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={10} />
                <Field label="Ville" name="ville_employeur" value={formData.ville_employeur} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <SelectField label="Pays" name="pays_employeur" value={formData.pays_employeur || 'FRANCE'} onChange={handleInputChange} disabled={isDisabled}
                  options={COUNTRIES.map(c => ({ value: c, label: c }))} />
              </div>
            )}

            {/* TAB: Banque */}
            {activeTab === 'banque' && (
              <div className="grid grid-cols-3 gap-4">
                <Field label="Banque de domiciliation *" name="banque_domiciliation" value={formData.banque_domiciliation} onChange={handleInputChange} disabled={isDisabled} maxLength={32} className="col-span-2" />
                <Field label="Libellé guichet" name="libelle_guichet" value={formData.libelle_guichet} onChange={handleInputChange} disabled={isDisabled} maxLength={30} />
                <Field label="Titulaire compte" name="titulaire_compte" value={formData.titulaire_compte} onChange={handleInputChange} disabled={isDisabled} maxLength={32} />
                <Field label="Code banque *" name="code_banque" value={formData.code_banque} onChange={handleInputChange} disabled={isDisabled} maxLength={5} />
                <Field label="Code guichet *" name="code_guichet" value={formData.code_guichet} onChange={handleInputChange} disabled={isDisabled} maxLength={5} />
              </div>
            )}

            {/* TAB: Revenus */}
            {activeTab === 'revenus' && (
              <div className="space-y-6">
                {/* Salaire */}
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-3">Salaire</h4>
                  <div className="grid grid-cols-4 gap-4">
                    <Field label="Montant" name="montant_salaire" value={formData.montant_salaire} onChange={handleInputChange} disabled={isDisabled} />
                    <Field label="Jour versement" name="periode_versement_salaire" type="number" value={formData.periode_versement_salaire} onChange={handleInputChange} disabled={isDisabled} />
                    <SelectField label="Fréquence" name="frequence_versement_salaire" value={formData.frequence_versement_salaire} onChange={handleInputChange} disabled={isDisabled}
                      options={[{ value: '', label: 'Sélectionner...' }, ...FREQUENCES_VERSEMENT.map(f => ({ value: f.code, label: `${f.code} - ${f.libelle}` }))]} />
                  </div>
                </div>

                {/* Autres revenus */}
                {[1, 2, 3].map(n => (
                  <div key={n}>
                    <h4 className="text-sm font-semibold text-slate-700 mb-3">Autre revenu {n}</h4>
                    <div className="grid grid-cols-4 gap-4">
                      <Field label="Nature" name={`nature_revenu${n}`} value={formData[`nature_revenu${n}`]} onChange={handleInputChange} disabled={isDisabled} maxLength={30} />
                      <Field label="Montant" name={`montant_revenu${n}`} value={formData[`montant_revenu${n}`]} onChange={handleInputChange} disabled={isDisabled} />
                      <Field label="Jour" name={`periode_versement_revenu${n}`} type="number" value={formData[`periode_versement_revenu${n}`]} onChange={handleInputChange} disabled={isDisabled} />
                      <SelectField label="Fréquence" name={`frequence_versement_revenu${n}`} value={formData[`frequence_versement_revenu${n}`]} onChange={handleInputChange} disabled={isDisabled}
                        options={[{ value: '', label: '...' }, ...FREQUENCES_VERSEMENT.map(f => ({ value: f.code, label: f.code }))]} />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* TAB: Commentaires */}
            {activeTab === 'commentaires' && (
              <div className="space-y-4">
                {formData.flag_etat_civil_errone === 'E' && (
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
                    <HelpCircle className="w-4 h-4 text-blue-500 mt-0.5" />
                    <p className="text-sm text-blue-700">Documentez les différences d&apos;état civil constatées.</p>
                  </div>
                )}

                {isPartner ? (
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Memo adresse / téléphone" name="memo1" value={formData.memo1} onChange={handleInputChange} maxLength={64} />
                    <Field label="Memo employeur" name="memo3" value={formData.memo3} onChange={handleInputChange} maxLength={64} />
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-slate-600 mb-1">Proximite (auto)</label>
                      <textarea
                        value={proximitePreview}
                        readOnly
                        rows="2"
                        className="w-full px-3 py-2 text-sm border border-blue-200 rounded-lg bg-blue-50 text-slate-700"
                      />
                    </div>
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-slate-600 mb-1">Proximité (détails)</label>
                      <textarea name="memo5" value={formData.memo5} onChange={handleInputChange} rows="3" maxLength={1000}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500" />
                    </div>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-4">
                    <Field label="Mémo 1" name="memo1" value={formData.memo1} onChange={handleInputChange} maxLength={64} />
                    <Field label="Mémo 2" name="memo2" value={formData.memo2} onChange={handleInputChange} maxLength={64} />
                    <Field label="Mémo 3" name="memo3" value={formData.memo3} onChange={handleInputChange} maxLength={64} />
                    <Field label="Mémo 4" name="memo4" value={formData.memo4} onChange={handleInputChange} maxLength={64} />
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-slate-600 mb-1">Commentaires détaillés</label>
                      <textarea name="memo5" value={formData.memo5} onChange={handleInputChange} rows="3" maxLength={1000}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500" />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB: Notes */}
            {activeTab === 'notes' && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <StickyNote className="w-5 h-5 text-amber-500" />
                  <span className="text-sm font-semibold text-slate-700">Notes personnelles</span>
                </div>
                <p className="text-xs text-slate-500 mb-3">Ces notes sont privées et ne seront pas exportées.</p>
                <textarea
                  name="notes_personnelles"
                  value={formData.notes_personnelles}
                  onChange={handleInputChange}
                  rows="8"
                  placeholder="Vos notes personnelles..."
                  className="w-full px-4 py-3 text-sm border border-amber-200 rounded-lg bg-amber-50 
                             focus:ring-2 focus:ring-amber-400 focus:border-amber-400"
                />
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

UpdateModal.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  data: PropTypes.shape({
    id: PropTypes.number.isRequired,
    numeroDossier: PropTypes.string,
    typeDemande: PropTypes.string,
    est_contestation: PropTypes.bool,
    motif: PropTypes.string,
    motifDeContestation: PropTypes.string,
    motif_contestation_detail: PropTypes.string,
    motif_contestation_code: PropTypes.string,
    elementDemandes: PropTypes.string,
    qualite: PropTypes.string,
    nom: PropTypes.string,
    prenom: PropTypes.string,
    dateNaissance: PropTypes.string,
    lieuNaissance: PropTypes.string,
    codePostalNaissance: PropTypes.string,
    paysNaissance: PropTypes.string,
    nomPatronymique: PropTypes.string,
    enqueteOriginale: PropTypes.object,
    enquete_originale: PropTypes.object,
    instructions: PropTypes.string,
    enqueteurId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    adresse1_origine: PropTypes.string,
    adresse2_origine: PropTypes.string,
    adresse3_origine: PropTypes.string,
    adresse4_origine: PropTypes.string,
    codePostal_origine: PropTypes.string,
    ville_origine: PropTypes.string,
    paysResidence_origine: PropTypes.string,
    telephonePersonnel_origine: PropTypes.string,
    telephoneEmployeur_origine: PropTypes.string,
    banqueDomiciliation_origine: PropTypes.string,
    titulaireCompte_origine: PropTypes.string,
    codeBanque_origine: PropTypes.string,
    codeGuichet_origine: PropTypes.string,
    commentaire: PropTypes.string,
    dateNaissance_maj: PropTypes.string,
    lieuNaissance_maj: PropTypes.string,
  }).isRequired
};

export default UpdateModal;

