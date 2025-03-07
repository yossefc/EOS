// Service pour l'API adresse.data.gouv.fr
const API_URL = import.meta.env.VITE_API_URL || 'http://192.168.150.107:5000';

export const getApiUrl = () => API_URL;

export const endpoints = {
    enqueteurs: `${API_URL}/enqueteurs`,
    vpnConfig: `${API_URL}/vpn-config`,
    downloadVpn: `${API_URL}/download-vpn`,
    uploadTemplate: `${API_URL}/upload-template`,
    getTemplate: `${API_URL}/get-template`,
};

export const searchAddress = async (query) => {
    try {
        const response = await fetch(
            `${API_URL}/search/?q=${encodeURIComponent(query)}&type=housenumber&limit=5`
        );
        const data = await response.json();
        return data.features;
    } catch (error) {
        console.error('Erreur lors de la recherche d\'adresse:', error);
        return [];
    }
};

export const searchByPostalCode = async (postalCode) => {
    try {
        const response = await fetch(
            `${API_URL}/search/?q=${postalCode}&type=municipality&postcode=${postalCode}`
        );
        const data = await response.json();
        return data.features;
    } catch (error) {
        console.error('Erreur lors de la recherche par code postal:', error);
        return [];
    }
};