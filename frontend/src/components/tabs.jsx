import { useState, lazy, Suspense } from 'react';
import { BarChart2, Database, Users, ClipboardList, FileUp, FileDown, User, DollarSign, CheckSquare } from 'lucide-react';

// Lazy loading of components
const StatsViewer = lazy(() => import('./StatsViewer'));
const DataViewer = lazy(() => import('./DataViewer'));
const ImprovedEnqueteurViewer = lazy(() => import('./ImprovedEnqueteurViewer'));
const AssignmentViewer = lazy(() => import('./AssignmentViewer'));
const EnqueteurDashboard = lazy(() => import('./EnqueteurDashboard'));
const ImportHandler = lazy(() => import('./ImportHandler'));
//const ExportHandler = lazy(() => import('./ExportHandler'));
const TarificationViewer = lazy(() => import('./TarificationViewer'));
const EnqueteurRestrictedDashboard = lazy(() => import('./EnqueteurRestrictedDashboard'));
const EnqueteExporter = lazy(() => import('./EnqueteExporter'));

// Non-lazy loaded components
import PaiementManager from './PaiementManager';
import FinancialReports from './FinancialReports';

// Loading component
const LoadingComponent = () => (
  <div className="flex justify-center items-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    <span className="ml-2">Chargement en cours...</span>
  </div>
);

const Tabs = () => {
  const [activeTab, setActiveTab] = useState('stats');
  const [enquetes] = useState([]);

  // Function to refresh data after import
  const handleImportComplete = async () => {
    // You can implement logic to refresh data after an import
    console.log('Import complete, refreshing data...');
  };
  
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
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
      id: 'validation',
      label: 'Validation Enquêtes',
      icon: <CheckSquare className="w-4 h-4" />,
      component: <EnqueteurRestrictedDashboard />
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
      component: <EnqueteExporter enquetes={enquetes} />
    },
    {
      id: 'enqueteurs',
      label: 'Enquêteurs',
      icon: <Users className="w-4 h-4" />,
      component: <ImprovedEnqueteurViewer />
    },
    {
      id: 'assignments',
      label: 'Assignations',
      icon: <ClipboardList className="w-4 h-4" />,
      component: <AssignmentViewer />
    },
    {
      id: 'tarification',
      label: 'Tarification',
      icon: <DollarSign className="w-4 h-4" />,
      component: <TarificationViewer onTabChange={handleTabChange} />
    },
    {
      id: 'paiements',
      label: 'Paiements Enquêteurs',
      icon: <DollarSign className="w-4 h-4" />,
      component: <PaiementManager />
    },
    {
      id: 'finance',
      label: 'Rapports Financiers',
      icon: <BarChart2 className="w-4 h-4" />,
      component: <FinancialReports />
    }
  ];

  // Function to render the active component
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

// Add a style to hide the horizontal scrollbar while allowing scrolling
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