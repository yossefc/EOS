import React, { useState, useEffect, lazy, Suspense } from 'react';
import { BarChart2, FileText, Database, Users, ClipboardList, FileUp, FileDown, User } from 'lucide-react';

// Lazy loading des composants
const StatsViewer = lazy(() => import('./StatsViewer'));
const DataViewer = lazy(() => import('./DataViewer'));
const EnqueteurViewer = lazy(() => import('./EnqueteurViewer'));
const AssignmentViewer = lazy(() => import('./AssignmentViewer'));
const EnqueteurDashboard = lazy(() => import('./EnqueteurDashboard'));
const ImportHandler = lazy(() => import('./ImportHandler'));
const ExportHandler = lazy(() => import('./ExportHandler'));

// Composant de chargement
const LoadingComponent = () => (
  <div className="flex justify-center items-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    <span className="ml-2">Chargement en cours...</span>
  </div>
);

const Tabs = () => {
  const [activeTab, setActiveTab] = useState('stats');
  const [enquetes, setEnquetes] = useState([]);

  // Fonction pour rafraîchir les données après import
  const handleImportComplete = async () => {
    // Vous pouvez implémenter la logique pour rafraîchir les données après un import
    // Cette fonction sera passée aux composants qui en ont besoin
    console.log('Import terminé, rafraîchissement des données...');
  };

  const tabs = [
    {
      id: 'stats',
      label: 'Statistiques',
      icon: <BarChart2 className="w-4 h-4" />,
      component: <StatsViewer />
    },
    {
      id: 'import',
      label: 'Import de fichiers',
      icon: <FileUp className="w-4 h-4" />,
      component: <ImportHandler onImportComplete={handleImportComplete} />
    },
    {
      id: 'enqueteur-interface',
      label: 'Interface Enquêteur',
      icon: <User className="w-4 h-4" />,
      component: <EnqueteurDashboard />
    },
    {
      id: 'data',
      label: 'Données',
      icon: <Database className="w-4 h-4" />,
      component: <DataViewer />
    },
    {
      id: 'export',
      label: 'Export des résultats',
      icon: <FileDown className="w-4 h-4" />,
      component: <ExportHandler enquetes={enquetes} />
    },
    {
      id: 'enqueteurs',
      label: 'Enquêteurs',
      icon: <Users className="w-4 h-4" />,
      component: <EnqueteurViewer />
    },
    {
      id: 'assignments',
      label: 'Assignations',
      icon: <ClipboardList className="w-4 h-4" />,
      component: <AssignmentViewer />
    }
  ];

  // Fonction pour rendre le composant actif
  const renderActiveComponent = () => {
    const activeTabObj = tabs.find(tab => tab.id === activeTab);
    if (!activeTabObj) return null;

    return (
      <Suspense fallback={<LoadingComponent />}>
        {activeTabObj.component}
      </Suspense>
    );
  };

  return (
    <div className="w-full">
      <div className="border-b border-gray-200">
        <nav className="flex overflow-x-auto hide-scrollbar" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                flex items-center gap-2 px-4 py-2 text-sm font-medium whitespace-nowrap
                border-b-2 transition-colors duration-200
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
              `}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-4">
        {renderActiveComponent()}
      </div>
    </div>
  );
};

// Ajout d'un style pour masquer la barre de défilement horizontale tout en permettant le défilement
const style = document.createElement('style');
style.textContent = `
  .hide-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .hide-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
`;
document.head.appendChild(style);

export default Tabs;