import React from 'react';
import EnqueteurDashboard from './components/EnqueteurDashboard';

function EnqueteurApp() {
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

      {/* Main Content */}
      <main>
        <EnqueteurDashboard />
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