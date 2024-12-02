// Service pour l'API adresse.data.gouv.fr
export const searchAddress = async (query) => {
    try {
        const response = await fetch(
            `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&type=housenumber&limit=5`
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
            `https://api-adresse.data.gouv.fr/search/?q=${postalCode}&type=municipality&postcode=${postalCode}`
        );
        const data = await response.json();
        return data.features;
    } catch (error) {
        console.error('Erreur lors de la recherche par code postal:', error);
        return [];
    }
};