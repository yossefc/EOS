import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { User, Phone, MapPin, Building2, Calendar, Info, CreditCard } from 'lucide-react';

const ModernUpdateForm = ({ donnee, onClose }) => {
    const [formData, setFormData] = useState({
        code_resultat: '',
        code_resultat_adresse: '',
        telephone: '',
        adresse1: '', // Étage, Appartement, Porte, Chez
        adresse2: '', // Bâtiment, Escalier, Résidence
        adresse3: '', // Numéro, voie et/ou boîte postale
        adresse4: '', // Lieu-dit, Hameau
        code_postal: '',
        ville: '',
        pays: 'FRANCE',
        montant_facture: '',
        montant_cumule: '',
        tarif_applicable: ''
    });

    const [suggestions, setSuggestions] = useState({
        adresses: [],
        codesPostaux: [],
        villes: []
    });
    const [isLoading, setIsLoading] = useState({
        ville: false,
        rue: false
    });
        // Recherche par code postal
    const searchByPostalCode = useCallback(async (codePostal) => {
        if (codePostal.length >= 2) {
            try {
                const response = await axios.get(
                    `https://api-adresse.data.gouv.fr/search/?q=${codePostal}&type=municipality&limit=15`
                );
                if (response.data.features.length > 0) {
                    const results = response.data.features.map(feature => ({
                        codePostal: feature.properties.postcode,
                        ville: feature.properties.city,
                        label: `${feature.properties.postcode} ${feature.properties.city}`
                    }));
                    setSuggestions(prev => ({ ...prev, codesPostaux: results }));
                }
            } catch (error) {
                console.error('Erreur recherche code postal:', error);
            }
        }
    }, []);

    // Recherche par ville
    const searchByCity = useCallback(async (ville) => {
        if (ville.length >= 2) {
            try {
                const encodedVille = encodeURIComponent(ville);
                const response = await axios.get(
                    `https://api-adresse.data.gouv.fr/search/?q=${encodedVille}&type=municipality&limit=15`
                );
                if (response.data.features.length > 0) {
                    const results = response.data.features.map(feature => ({
                        codePostal: feature.properties.postcode,
                        ville: feature.properties.city,
                        label: `${feature.properties.city} (${feature.properties.postcode})`
                    }));
                    setSuggestions(prev => ({ ...prev, villes: results }));
                }
            } catch (error) {
                console.error('Erreur recherche ville:', error);
            }
        }
    }, []);
    // Recherche des villes par code postal
    const searchAddress = useCallback(async (codePostal) => {
        if (codePostal?.length === 5) {
            setIsLoading(prev => ({ ...prev, ville: true }));
            try {
                const response = await axios.get(
                    `https://api-adresse.data.gouv.fr/search/?q=${codePostal}&type=municipality&postcode=${codePostal}`
                );
                if (response.data.features.length > 0) {
                    const villes = response.data.features.map(feature => ({
                        nom: feature.properties.city,
                        code: feature.properties.citycode
                    }));
                    setSuggestions(prev => ({ ...prev, villes }));
                    
                    // Auto-sélection si une seule ville
                    if (villes.length === 1) {
                        setFormData(prev => ({
                            ...prev,
                            ville: villes[0].nom,
                            pays: 'FRANCE'
                        }));
                    }
                }
            } catch (error) {
                console.error('Erreur de recherche de ville:', error);
            }
            setIsLoading(prev => ({ ...prev, ville: false }));
        }
    }, []);

    // Recherche des rues
    const searchStreets = useCallback(async (ville, codePostal) => {
        if (ville && codePostal) {
            setIsLoading(prev => ({ ...prev, rue: true }));
            try {
                const response = await axios.get(
                    `https://api-adresse.data.gouv.fr/search/?q=${ville}&type=street&postcode=${codePostal}&limit=50`
                );
                if (response.data.features.length > 0) {
                    const rues = response.data.features.map(feature => ({
                        nom: feature.properties.name,
                        id: feature.properties.id
                    }));
                    setSuggestions(prev => ({ ...prev, rues }));
                }
            } catch (error) {
                console.error('Erreur de recherche de rue:', error);
            }
            setIsLoading(prev => ({ ...prev, rue: false }));
        }
    }, []);
    // Recherche d'adresse complète
    const searchFullAddress = useCallback(async (query) => {
        if (query.length > 2) {
            setIsLoading(prev => ({ ...prev, rue: true }));
            try {
                const response = await axios.get(
                    `https://api-adresse.data.gouv.fr/search/?q=${query}&limit=10&type=housenumber`
                );
                if (response.data.features.length > 0) {
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
            }
            setIsLoading(prev => ({ ...prev, rue: false }));
        } else {
            setSuggestions(prev => ({ ...prev, adresses: [] }));
        }
    }, []);
    // Gestionnaires d'événements
    const handlePostalCodeChange = (e) => {
        const value = e.target.value;
        setFormData(prev => ({ ...prev, code_postal: value }));
        if (value.length === 5) {
            searchAddress(value);
        } else {
            setSuggestions(prev => ({ ...prev, villes: [] }));
        }
    };

    const handleVilleSelect = (ville) => {
        setFormData(prev => ({
            ...prev,
            ville: ville,
            pays: 'FRANCE'
        }));
        searchStreets(ville, formData.code_postal);
        setSuggestions(prev => ({ ...prev, villes: [] }));
    };

    const handleRueSelect = (rue) => {
        setFormData(prev => ({
            ...prev,
            adresse3: rue
        }));
        setSuggestions(prev => ({ ...prev, rues: [] }));
    };
    const CODES_STATUT = [
        { code: 'T', libelle: 'À traiter' },
        { code: 'P', libelle: 'Positif' },
        { code: 'H', libelle: 'Aucun élément nouveau trouvé' },
        { code: 'N', libelle: 'NPA/négatif' },
        { code: 'I', libelle: 'Intraitable' },
        { code: 'Y', libelle: 'Annulation CREDIREC' }
    ];

    useEffect(() => {
        if (donnee?.donnee_enqueteur) {
            setFormData(prev => ({
                ...prev,
                code_resultat: donnee.donnee_enqueteur.code_resultat || 'T',
                code_resultat_adresse: donnee.donnee_enqueteur.code_resultat_adresse || 'T',
                telephone: donnee.donnee_enqueteur.telephone_personnel || '',
                adresse1: donnee.donnee_enqueteur.adresse1 || '',  // Corrigé
                adresse2: donnee.donnee_enqueteur.adresse2 || '',  // Corrigé
                adresse3: donnee.donnee_enqueteur.adresse3 || '',  // Corrigé
                adresse4: donnee.donnee_enqueteur.adresse4 || '',  // Corrigé
                code_postal: donnee.donnee_enqueteur.code_postal || '',
                ville: donnee.donnee_enqueteur.ville || '',
                pays: donnee.donnee_enqueteur.pays_residence || 'FRANCE',
                montant_facture: donnee.donnee_enqueteur.montant_facture || '',
                montant_cumule: donnee.donnee_enqueteur.cumul_montants_precedents || '',
                tarif_applicable: donnee.donnee_enqueteur.tarif_applique || ''
            }));
        }
    }, [donnee]);
    const handleAddressSelect = (adresse) => {
        setFormData(prev => ({
            ...prev,
            adresse3: adresse.adresse, // On utilise directement l'adresse formatée
            code_postal: adresse.codePostal,
            ville: adresse.ville,
            pays: 'FRANCE'
        }));
        setSuggestions({ adresses: [], codesPostaux: [], villes: [] });
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const dataToSend = {
                donnee_id: donnee.id,
                code_resultat: formData.code_resultat,
                code_resultat_adresse: formData.code_resultat_adresse,
                telephone_personnel: formData.telephone,
                adresse1: formData.adresse1,
                adresse2: formData.adresse2,
                adresse3: formData.adresse3,
                adresse4: formData.adresse4,
                code_postal: formData.code_postal,
                ville: formData.ville,
                pays_residence: formData.pays,
                montant_facture: formData.montant_facture || null,
                cumul_montants_precedents: formData.montant_cumule || null,
                tarif_applique: formData.tarif_applicable || null
            };
    
            const response = await axios.post(
                'http://localhost:5000/api/donnees-enqueteur/' + donnee.id,
                dataToSend,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
    
            if (response.data.success) {
                console.log('Enregistrement réussi');
                onClose(true);
            }
        } catch (error) {
            console.error('Erreur détaillée:', error.response?.data || error.message);
        }
    };

    return (
<div className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center">
    {/* Réduire la largeur de 1200px à 1000px et la hauteur de 800px à 700px */}
    <div className="bg-gray-50 rounded-xl shadow-xl w-[1000px] h-[700px] flex flex-col">

               {/* En-tête */}
    <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-2 rounded-t-xl">
        <div className="flex justify-between items-start">
        {/* Partie gauche */}
        <div>
            <div className="flex items-center gap-2">
                <Building2 className="w-6 h-6 text-white" />
                <h2 className="text-xl font-bold text-white">
                    Dossier n°{donnee?.numeroDossier}
                </h2>
            </div>
            <div className="mt-2 text-sm text-white space-y-1">
                <p>Référence : {donnee?.referenceDossier}</p>
                <p>Nom : {donnee?.nom}</p>
                <p>Date de naissance : {donnee?.dateNaissance}</p>
            </div>
        </div>

        {/* Partie droite */}
        <div className="flex flex-col items-end">
            <button onClick={() => onClose(false)} 
                    className="text-white/70 hover:text-white p-1">
                ✕
            </button>
            <div className="mt-2 space-y-2">
                {/* Éléments demandés */}
                <div>
                    <p className="text-orange-300 font-medium text-sm">
                        Éléments demandés
                    </p>
                    <div className="flex gap-2 mt-1">
                        {donnee?.elementDemandes?.split('').map((element, index) => (
                            <span key={index} 
                                  className="px-3 py-1 bg-orange-500/20 rounded-full text-white text-sm">
                                {element}
                            </span>
                        ))}
                    </div>
                </div>
                {/* Éléments obligatoires */}
                <div>
                    <p className="text-red-300 font-medium text-sm">
                        Éléments obligatoires
                    </p>
                    <div className="flex gap-2 mt-1">
                        {donnee?.elementObligatoires?.split('').map((element, index) => (
                            <span key={index} 
                                  className="px-3 py-1 bg-red-500/20 rounded-full text-white text-sm">
                                {element}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
    
                {/* Contenu principal */}
                <div className="flex flex-1 p-3 gap-3">
                    {/* Colonne gauche */}
                    <div className="w-1/2 space-y-3">
                        {/* Données originales */}
                        <div className="bg-white p-3 rounded-lg border shadow-sm">
                            <div className="flex items-center gap-2 text-gray-700 text-sm mb-2">
                                <Info className="w-4 h-4" />
                                <span className="font-medium">Données originales</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                                <div>
                                    <p><span className="text-gray-500">Téléphone:</span> {donnee?.telephonePersonnel || '-'}</p>
                                    <p><span className="text-gray-500">Adresse:</span> {[donnee?.adresse1, donnee?.adresse2, donnee?.adresse3].filter(Boolean).join(' ') || '-'}</p>
                                </div>
                                <div>
                                    <p><span className="text-gray-500">Code postal:</span> {donnee?.codePostal || '-'}</p>
                                    <p><span className="text-gray-500">Ville:</span> {donnee?.ville || '-'}</p>
                                </div>
                            </div>
                        </div>
    
                        {/* Facturation */}
                        <div className="bg-white p-3 rounded-lg border shadow-sm">
                            <div className="flex items-center gap-2 text-gray-700 mb-2 text-sm">
                                <CreditCard className="w-4 h-4" />
                                <span className="font-medium">Facturation</span>
                            </div>
                            <div className="grid grid-cols-3 gap-3">
                                <div>
                                    <label className="block text-xs text-gray-600">Montant facturé</label>
                                    <input
                                        type="text"
                                        value={formData.montant_facture}
                                        onChange={(e) => setFormData(prev => ({...prev, montant_facture: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-600">Montant cumulé</label>
                                    <input
                                        type="text"
                                        value={formData.montant_cumule}
                                        onChange={(e) => setFormData(prev => ({...prev, montant_cumule: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-600">Tarif applicable</label>
                                    <input
                                        type="text"
                                        value={formData.tarif_applicable}
                                        onChange={(e) => setFormData(prev => ({...prev, tarif_applicable: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                </div>
                            </div>
                        </div>
    
                        {/* Téléphone */}
                        <div className="bg-white p-3 rounded-lg border shadow-sm">
                            <div className="flex items-center gap-2 text-gray-700 mb-2 text-sm">
                                <Phone className="w-4 h-4" />
                                <span className="font-medium">Téléphone</span>
                            </div>
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="block text-xs text-gray-600">Code résultat</label>
                                    <select
                                        value={formData.code_resultat}
                                        onChange={(e) => setFormData(prev => ({...prev, code_resultat: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    >
                                        <option value="">Sélectionner un code</option>
                                        {CODES_STATUT.map(({ code, libelle }) => (
                                            <option key={code} value={code}>{code} - {libelle}</option>
                                        ))}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-600">Téléphone</label>
                                    <input
                                        type="text"
                                        value={formData.telephone}
                                        onChange={(e) => setFormData(prev => ({...prev, telephone: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
    
                    {/* Colonne droite - Adresse */}
                    <div className="w-1/2 bg-white p-3 rounded-lg border shadow-sm">
                        <div className="flex items-center gap-2 text-gray-700 mb-2 text-sm">
                            <MapPin className="w-4 h-4" />
                            <span className="font-medium">Adresse</span>
                        </div>
                        <div className="space-y-3">
                            <div>
                                <label className="block text-xs text-gray-600">Code résultat adresse</label>
                                <select
                                    value={formData.code_resultat_adresse}
                                    onChange={(e) => setFormData(prev => ({...prev, code_resultat_adresse: e.target.value}))}
                                    className="w-full px-2 py-1 text-sm rounded border"
                                >
                                    <option value="">Sélectionner un code</option>
                                    {CODES_STATUT.map(({ code, libelle }) => (
                                        <option key={code} value={code}>{code} - {libelle}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-600">Étage, Apt, Porte</label>
                                <input
                                    type="text"
                                    value={formData.adresse1}
                                    onChange={(e) => setFormData(prev => ({...prev, adresse1: e.target.value}))}
                                    className="w-full px-2 py-1 text-sm rounded border"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-600">Bâtiment, Escalier, Résidence</label>
                                <input
                                    type="text"
                                    value={formData.adresse2}
                                    onChange={(e) => setFormData(prev => ({...prev, adresse2: e.target.value}))}
                                    className="w-full px-2 py-1 text-sm rounded border"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-600">Lieu-dit, Hameau</label>
                                <input
                                    type="text"
                                    value={formData.adresse4}
                                    onChange={(e) => setFormData(prev => ({...prev, adresse4: e.target.value}))}
                                    className="w-full px-2 py-1 text-sm rounded border"
                                />
                            </div>
                            {/* N°, voie / BP */}
                            <div className="relative">
                                <label className="block text-xs text-gray-600">N°, voie / BP</label>
                                <input
                                    type="text"
                                    value={formData.adresse3}
                                    onChange={(e) => {
                                        const value = e.target.value;
                                        setFormData(prev => ({ ...prev, adresse3: value }));
                                        searchFullAddress(value);
                                    }}
                                    className="w-full px-2 py-1 text-sm rounded border"
                                />
                                {suggestions.adresses?.length > 0 && (
                                    <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-32 overflow-auto">
                                        {suggestions.adresses.map((adresse, index) => (
                                            <button
                                                key={index}
                                                type="button"
                                                onClick={() => handleAddressSelect(adresse)}
                                                className="w-full px-2 py-1 text-sm text-left hover:bg-gray-100"
                                            >
                                                {adresse.adresseComplete}
                                            </button>
                                        ))}
                                    </div>
                                )}
</div>
                            <div className="grid grid-cols-3 gap-3">
                                <div>
                                    <label className="block text-xs text-gray-600">Code postal</label>
                                    <input
                                        type="text"
                                        value={formData.code_postal}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            setFormData(prev => ({...prev, code_postal: value}));
                                            if(value.length >= 2) searchByPostalCode(value);
                                        }}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                    {suggestions.codesPostaux?.length > 0 && (
                                        <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-32 overflow-auto">
                                            {suggestions.codesPostaux.map((item, index) => (
                                                <button
                                                    key={index}
                                                    type="button"
                                                    onClick={() => {
                                                        setFormData(prev => ({
                                                            ...prev,
                                                            code_postal: item.codePostal,
                                                            ville: item.ville,
                                                            pays: 'FRANCE'
                                                        }));
                                                        setSuggestions(prev => ({ ...prev, codesPostaux: [] }));
                                                    }}
                                                    className="w-full px-2 py-1 text-sm text-left hover:bg-gray-100"
                                                >
                                                    {item.label}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                </div>
                                <div>
                                    <label className="block text-xs text-gray-600">Ville</label>
                                    <input
                                        type="text"
                                        value={formData.ville}
                                        onChange={(e) => {
                                            const value = e.target.value;
                                            setFormData(prev => ({...prev, ville: value}));
                                            if(value.length >= 2) searchByCity(value);
                                        }}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                    {suggestions.villes?.length > 0 && (
                                        <div className="absolute z-10 w-full mt-1 bg-white border rounded shadow-lg max-h-32 overflow-auto">
                                            {suggestions.villes.map((item, index) => (
                                                <button
                                                    key={index}
                                                    type="button"
                                                    onClick={() => {
                                                        setFormData(prev => ({
                                                            ...prev,
                                                            code_postal: item.codePostal,
                                                            ville: item.ville,
                                                            pays: 'FRANCE'
                                                        }));
                                                        setSuggestions(prev => ({ ...prev, villes: [] }));
                                                    }}
                                                    className="w-full px-2 py-1 text-sm text-left hover:bg-gray-100"
                                                >
                                                    {item.label}
                                                </button>
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <div>
                                    <label className="block text-xs text-gray-600">Pays</label>
                                    <input
                                        type="text"
                                        value={formData.pays}
                                        onChange={(e) => setFormData(prev => ({...prev, pays: e.target.value}))}
                                        className="w-full px-2 py-1 text-sm rounded border"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
                {/* Boutons d'action */}
                <div className="p-3 flex justify-end gap-3 border-t">
                    <button
                        type="button"
                        onClick={() => onClose(false)}
                        className="px-3 py-1.5 text-sm text-gray-700 bg-white border rounded hover:bg-gray-50"
                    >
                        Annuler
                    </button>
                    <button
                        type="submit"
                        onClick={handleSubmit}
                        className="px-3 py-1.5 text-sm text-white bg-blue-600 rounded hover:bg-blue-700"
                    >
                        Enregistrer
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ModernUpdateForm;