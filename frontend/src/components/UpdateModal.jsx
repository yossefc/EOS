import React, { useState, useRef, useEffect } from 'react';
import { X, Save, ChevronDown, Search } from 'lucide-react';
import { searchAddress, searchByPostalCode } from './addressService';
import { COUNTRIES, isValidFrenchPostalCode, formatAddress } from './countryData';

export default function UpdateModal({ isOpen, onClose, data }) {
    const [formData, setFormData] = useState(data || {});
    const [addressSuggestions, setAddressSuggestions] = useState([]);
    const [showAddressSuggestions, setShowAddressSuggestions] = useState(false);
    const [errors, setErrors] = useState({});
    const [countrySearch, setCountrySearch] = useState('');
    const [showCountryList, setShowCountryList] = useState(false);
    const countryListRef = useRef(null);


    const filteredCountries = COUNTRIES.filter(country =>
        country.toLowerCase().includes(countrySearch.toLowerCase())
    );
    const handlePostalCodeChange = async (e) => {
        const value = e.target.value;
        setFormData(prev => ({ ...prev, codePostal: value }));

        if (value.length === 5) {
            const suggestions = await searchByPostalCode(value);
            if (suggestions.length > 0) {
                const city = suggestions[0].properties;
                setFormData(prev => ({
                    ...prev,
                    ville: city.city,
                    codePostal: city.postcode,
                    paysResidence: 'FRANCE'  // Ajout automatique du pays
                }));
                // Met à jour aussi la recherche de pays
                setCountrySearch('FRANCE');
            }
        }
    };

    const handleAddressSearch = async (e) => {
        const value = e.target.value;
        setFormData(prev => ({ ...prev, adresse3: value }));

        if (value.length > 3) {
            const query = formData.codePostal ?
                `${value} ${formData.codePostal}` :
                value;
            const suggestions = await searchAddress(query);
            setAddressSuggestions(suggestions);
            setShowAddressSuggestions(true);
        } else {
            setAddressSuggestions([]);
            setShowAddressSuggestions(false);
        }
    };
    const handleAddressSelect = (address) => {
        const props = address.properties;
        setFormData(prev => ({
            ...prev,
            adresse3: props.name,
            codePostal: props.postcode,
            ville: props.city,
            paysResidence: 'FRANCE'  // Ajout automatique du pays
        }));
        setCountrySearch('FRANCE');  // Met à jour la recherche de pays
        setShowAddressSuggestions(false);
    };
    const validateForm = () => {
        const newErrors = {};

        // Validation du code postal pour la France
        if (formData.paysResidence === 'FRANCE' && !isValidFrenchPostalCode(formData.codePostal)) {
            newErrors.codePostal = 'Code postal invalide';
        }

        // Validation de l'adresse
        if (formData.adresse3 && formData.adresse3.length > 32) {
            newErrors.adresse3 = 'Adresse trop longue (max 32 caractères)';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validateForm()) return;

        try {
            const response = await fetch(`http://localhost:5000/api/donnees/${data.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                onClose(true);
            }
        } catch (error) {
            console.error('Erreur:', error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        let formattedValue = value;

        if (name === 'adresse3' || name === 'ville') {
            formattedValue = formatAddress(value);
        } else if (name === 'codePostal' && formData.paysResidence === 'FRANCE') {
            formattedValue = value.replace(/[^\d]/g, '').slice(0, 5);
        }

        setFormData(prev => ({
            ...prev,
            [name]: formattedValue
        }));

        // Validation en temps réel
        if (name === 'codePostal' && formData.paysResidence === 'FRANCE') {
            if (!isValidFrenchPostalCode(formattedValue)) {
                setErrors(prev => ({ ...prev, codePostal: 'Code postal invalide' }));
            } else {
                setErrors(prev => ({ ...prev, codePostal: undefined }));
            }
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg w-[600px] max-h-[80vh] overflow-y-auto">
                <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
                    <h2 className="text-lg font-semibold">Dossier n° {data?.numeroDossier}</h2>
                    <button
                        onClick={() => onClose(false)}
                        className="text-gray-500 hover:text-gray-700"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    {/* Informations de base */}
                    <div className="bg-gray-50 p-3 rounded text-sm">
                        <div className="grid grid-cols-2 gap-2">
                            <div>Type: {data?.typeDemande || '-'}</div>
                            <div>Ref: {data?.referenceDossier || '-'}</div>
                            <div>Nom: {data?.nom || '-'}</div>
                            <div>Prénom: {data?.prenom || '-'}</div>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                        {/* Adresse */}
                        <div className="space-y-2">
                            <label className="text-sm">Adresse</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    name="adresse3"
                                    placeholder="Numéro et rue"
                                    value={formData.adresse3 || ''}
                                    onChange={handleAddressSearch}
                                    className="w-full p-1.5 text-sm border rounded"
                                />
                                {showAddressSuggestions && addressSuggestions.length > 0 && (
                                    <div className="absolute z-20 w-full mt-1 bg-white border rounded-md shadow-lg max-h-48 overflow-y-auto">
                                        {addressSuggestions.map((suggestion, index) => (
                                            <div
                                                key={index}
                                                className="px-3 py-1.5 hover:bg-gray-100 cursor-pointer text-sm"
                                                onClick={() => handleAddressSelect(suggestion)}
                                            >
                                                {suggestion.properties.label}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <input
                                        type="text"
                                        name="codePostal"
                                        placeholder="Code postal"
                                        value={formData.codePostal || ''}
                                        onChange={handlePostalCodeChange}
                                        className="w-full p-1.5 text-sm border rounded"
                                    />
                                </div>
                                <div>
                                    <input
                                        type="text"
                                        name="ville"
                                        placeholder="Ville"
                                        value={formData.ville || ''}
                                        className="w-full p-1.5 text-sm border rounded"
                                        readOnly
                                    />
                                </div>
                            </div>
                        </div>
                        {/* Section pays avec autocomplétion */}
                        <div className="relative">
                            <label className="text-sm">Pays</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    value={countrySearch}
                                    onChange={(e) => setCountrySearch(e.target.value)}
                                    onFocus={() => setShowCountryList(true)}
                                    className="w-full p-1.5 text-sm border rounded pr-8"
                                    placeholder="Rechercher un pays..."
                                />
                                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                            </div>

                            {showCountryList && (
                                <div
                                    ref={countryListRef}
                                    className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-48 overflow-y-auto"
                                >
                                    {filteredCountries.map((country) => (
                                        <div
                                            key={country}
                                            className="px-3 py-1.5 hover:bg-gray-100 cursor-pointer text-sm"
                                            onClick={() => {
                                                setFormData(prev => ({ ...prev, paysResidence: country }));
                                                setCountrySearch(country);
                                                setShowCountryList(false);
                                            }}
                                        >
                                            {country}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        {/* Affichage des erreurs */}
                        {Object.keys(errors).length > 0 && (
                            <div className="mt-2 text-red-500 text-sm">
                                {Object.values(errors).map((error, index) => (
                                    <div key={index}>{error}</div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Contacts */}
                    <div className="grid grid-cols-2 gap-3">
                        <div>
                            <label className="text-sm">Téléphone personnel</label>
                            <input
                                type="text"
                                name="telephonePersonnel"
                                value={formData.telephonePersonnel || ''}
                                onChange={handleInputChange}
                                className="w-full p-1.5 text-sm border rounded"
                            />
                        </div>
                        <div>
                            <label className="text-sm">Téléphone employeur</label>
                            <input
                                type="text"
                                name="telephoneEmployeur"
                                value={formData.telephoneEmployeur || ''}
                                onChange={handleInputChange}
                                className="w-full p-1.5 text-sm border rounded"
                            />
                        </div>
                    </div>

                    {/* Banque */}
                    <div className="grid grid-cols-3 gap-2">
                        <div>
                            <label className="text-sm">Code banque</label>
                            <input
                                type="text"
                                name="codeBanque"
                                value={formData.codeBanque || ''}
                                onChange={handleInputChange}
                                maxLength={5}
                                className="w-full p-1.5 text-sm border rounded"
                            />
                        </div>
                        <div>
                            <label className="text-sm">Code guichet</label>
                            <input
                                type="text"
                                name="codeGuichet"
                                value={formData.codeGuichet || ''}
                                onChange={handleInputChange}
                                maxLength={5}
                                className="w-full p-1.5 text-sm border rounded"
                            />
                        </div>
                        <div>
                            <label className="text-sm">Banque</label>
                            <input
                                type="text"
                                name="banqueDomiciliation"
                                value={formData.banqueDomiciliation || ''}
                                onChange={handleInputChange}
                                className="w-full p-1.5 text-sm border rounded"
                            />
                        </div>
                    </div>

                    {/* Commentaire */}
                    <div>
                        <label className="text-sm">Commentaire</label>
                        <textarea
                            name="memo5"
                            value={formData.memo5 || ''}
                            onChange={handleInputChange}
                            rows={2}
                            className="w-full p-1.5 text-sm border rounded"
                        />
                    </div>

                    <div className="flex justify-end gap-2 pt-3">
                        <button
                            type="button"
                            onClick={() => onClose(false)}
                            className="px-3 py-1.5 text-sm border rounded hover:bg-gray-50"
                        >
                            Annuler
                        </button>
                        <button
                            type="submit"
                            className="px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center gap-1"
                        >
                            <Save className="w-4 h-4" />
                            Enregistrer
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}