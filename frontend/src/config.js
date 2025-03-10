const config = {
    // Utiliser l'adresse IP du frontend pour contacter le backend
    API_URL: `http://${window.location.hostname}:5000`,
    FRONTEND_URL: `http://${window.location.hostname}:5173`
};

export default config;