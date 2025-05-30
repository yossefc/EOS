import { useState, useEffect } from 'react';
import EnqueteurLogin from './EnqueteurLogin';
import EnqueteurDashboard from './EnqueteurDashboard';

function EnqueteurApp() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [enqueteur, setEnqueteur] = useState(null);
  const [loading, setLoading] = useState(true);

  // Vérifier l'authentification au chargement
  // EnqueteurApp.jsx - Améliorer la vérification d'authentification
useEffect(() => {
  const enqueteurId = localStorage.getItem('enqueteurId');
  console.log("Vérification d'authentification - enqueteurId:", enqueteurId);
  
  if (enqueteurId) {
    const enqueteurData = {
      id: enqueteurId,
      nom: localStorage.getItem('enqueteurNom') || '',
      prenom: localStorage.getItem('enqueteurPrenom') || '',
      email: localStorage.getItem('enqueteurEmail') || ''
    };
    
    console.log("Informations d'enquêteur trouvées:", enqueteurData);
    setEnqueteur(enqueteurData);
    setIsAuthenticated(true);
  } else {
    console.log("Aucune information d'authentification trouvée");
    setIsAuthenticated(false);
    setEnqueteur(null);
  }
  
  setLoading(false);
}, []);

  // Gérer la connexion réussie
  const handleLoginSuccess = (enqueteurData) => {
    setEnqueteur(enqueteurData);
    setIsAuthenticated(true);
  };

  // Gérer la déconnexion
  const handleLogout = () => {
    localStorage.removeItem('enqueteurId');
    localStorage.removeItem('enqueteurNom');
    localStorage.removeItem('enqueteurPrenom');
    localStorage.removeItem('enqueteurEmail');
    setEnqueteur(null);
    setIsAuthenticated(false);
  };

  // Afficher un indicateur de chargement
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <img src="/logo-eos.png" alt="EOS France" className="h-8 w-auto mr-3" onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://placehold.co/100x40/e6e6e6/808080?text=EOS+FRANCE';
              }} />
              <h1 className="text-2xl font-bold text-gray-900">
                Interface Enquêteur
              </h1>
            </div>
            <div className="text-sm text-gray-500">
              Version 1.0
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Affiche la page de login ou le dashboard en fonction de l'authentification */}
      <main>
        {isAuthenticated ? (
          <EnqueteurDashboard 
            enqueteur={enqueteur} 
            onLogout={handleLogout} 
          />
        ) : (
          <EnqueteurLogin onLoginSuccess={handleLoginSuccess} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center text-sm text-gray-500">
            <div>
              © {new Date().getFullYear()} EOS France - Système de gestion des enquêtes
            </div>
            <div className="text-gray-400">
              Développé conformément au cahier des charges
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default EnqueteurApp;