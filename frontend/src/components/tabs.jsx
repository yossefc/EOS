import { useState, lazy, Suspense } from 'react';
import { BarChart2, Database, Users, ClipboardList, FileUp, FileDown, DollarSign, Archive } from 'lucide-react';

// Lazy loading of components
const StatsViewer = lazy(() => import('./StatsViewer'));
const DataViewer = lazy(() => import('./DataViewer'));
const ImprovedEnqueteurViewer = lazy(() => import('./ImprovedEnqueteurViewer'));
const AssignmentViewer = lazy(() => import('./AssignmentViewer'));
const ImportHandler = lazy(() => import('./ImportHandler'));
const PartnerKeywordsAdmin = lazy(() => import('./PartnerKeywordsAdmin'));
const EnqueteExporter = lazy(() => import('./EnqueteExporter'));
const ArchivesViewer = lazy(() => import('./ArchivesViewer'));

// Non-lazy loaded components
import FinanceManager from './FinanceManager';

// Loading component
const LoadingComponent = () => (
  <div className="flex justify-center items-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    <span className="ml-2">Chargement en cours...</span>
  </div>
);

const Tabs = () => {
  const [activeTab, setActiveTab] = useState('stats');

  // Function to refresh data after import
  const handleImportComplete = async () => {
    // You can implement logic to refresh data after an import
    console.log('Import complete, refreshing data...');
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
      id: 'data',
      label: 'Donnees',
      icon: <Database className="w-4 h-4" />,
      component: <DataViewer />
    },
    {
      id: 'export',
      label: 'Export des resultats',
      icon: <FileDown className="w-4 h-4" />,
      component: <EnqueteExporter />
    },
    {
      id: 'archives',
      label: 'Archives',
      icon: <Archive className="w-4 h-4" />,
      component: <ArchivesViewer />
    },
    {
      id: 'enqueteurs',
      label: 'Enqueteurs',
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
      id: 'finance',
      label: 'Finance & Paiements',
      icon: <DollarSign className="w-4 h-4" />,
      component: <FinanceManager />
    },
    {
      id: 'partner-keywords',
      label: 'PARTNER - Mots-cles',
      icon: <ClipboardList className="w-4 h-4" />,
      component: <PartnerKeywordsAdmin />
    }
  ];

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
    <div className="w-full max-w-[1600px] mx-auto px-3 sm:px-6 lg:px-8 py-3 sm:py-4">
      <div className="sticky top-2 sm:top-4 z-40 mb-6 sm:mb-10">
        <nav
          className="flex flex-nowrap items-center gap-1.5 sm:gap-2 p-1.5 bg-white/80 backdrop-blur-xl rounded-2xl sm:rounded-[24px] border border-white/40 shadow-xl shadow-slate-200/40 overflow-x-auto"
          aria-label="Tabs"
        >
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-3 sm:px-4 lg:px-5 py-2 text-xs sm:text-sm font-semibold whitespace-nowrap
                  rounded-xl transition-all duration-300
                  ${isActive
                    ? 'bg-slate-800 text-white shadow-md shadow-slate-200 translate-y-[-1px]'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-white hover:border-slate-200/50 hover:shadow-sm'}
                `}
              >
                <span className={isActive ? 'text-blue-400' : 'text-slate-400'}>
                  {tab.icon}
                </span>
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
        {renderActiveComponent()}
      </div>
    </div>
  );
};

export default Tabs;
