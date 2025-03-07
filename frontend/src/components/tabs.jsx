import React, { useState } from 'react';
import { BarChart2, FileText, Database, Users, ClipboardList, FileUp, FileDown,User  } from 'lucide-react';
import StatsViewer from './StatsViewer';
import ImportHandler from './ImportHandler'; // Nouveau composant d'import
import DataViewer from './DataViewer';
import EnqueteurViewer from './EnqueteurViewer';
import AssignmentViewer from './AssignmentViewer';
import EnqueteurDashboard from './EnqueteurDashboard';
import ExportHandler from './ExportHandler'; // Nouveau composant d'export

const Tabs = () => {
    const [activeTab, setActiveTab] = useState('stats');
    const [enquetes, setEnquetes] = useState([]);

    // Fonction pour rafraîchir les données après import
    const handleImportComplete = async () => {
        // Vous pouvez implémenter la logique pour rafraîchir les données après un import
        // Par exemple, mettre à jour la liste des enquêtes
        // Cette fonction sera passée aux composants qui en ont besoin
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

    return (
        <div className="w-full">
            <div className="border-b border-gray-200">
                <nav className="flex gap-4" aria-label="Tabs">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`
                                flex items-center gap-2 px-4 py-2 text-sm font-medium
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
                {tabs.map((tab) => (
                    <div
                        key={tab.id}
                        className={`${activeTab === tab.id ? 'block' : 'hidden'}`}
                        role="tabpanel"
                    >
                        {tab.component}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Tabs;