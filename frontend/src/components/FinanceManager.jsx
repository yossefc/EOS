import { useState, lazy, Suspense } from 'react';
import { DollarSign, TrendingUp, Users, Settings } from 'lucide-react';

// Composants existants
const TarificationViewer = lazy(() => import('./TarificationViewer'));
import FinancialReports from './FinancialReports';
import PaiementManager from './PaiementManager';

const LoadingComponent = () => (
  <div className="flex justify-center items-center p-8">
    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
    <span className="ml-2">Chargement...</span>
  </div>
);

/**
 * Composant principal pour gérer toute la partie financière
 * Organisé en 3 sections claires :
 * 1. Tarifs (configuration)
 * 2. Gains Administrateur (revenus EOS vs PARTNER)
 * 3. Paiements Enquêteurs (ce qu'on doit payer)
 */
const FinanceManager = () => {
  const [activeSection, setActiveSection] = useState('gains');

  const sections = [
    {
      id: 'gains',
      label: 'Gains Administrateur',
      icon: <TrendingUp className="w-5 h-5" />,
      description: 'Combien EOS a gagné (client) vs versé aux enquêteurs',
      color: 'blue'
    },
    {
      id: 'paiements',
      label: 'Paiements Enquêteurs',
      icon: <Users className="w-5 h-5" />,
      description: 'Combien chaque enquêteur a gagné et ce qu\'il reste à payer',
      color: 'green'
    },
    {
      id: 'tarifs',
      label: 'Gérer les Tarifs',
      icon: <Settings className="w-5 h-5" />,
      description: 'Configurer les tarifs EOS, Enquêteur et PARTNER',
      color: 'purple'
    }
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'gains':
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                💰 Rapports Financiers - Vue Administrateur
              </h3>
              <p className="text-blue-700 text-sm mb-4">
                Visualisez les revenus totaux (prix facturés aux clients) et les coûts (montants versés aux enquêteurs).
                Filtrez par client (EOS / PARTNER) pour voir la rentabilité de chaque activité.
              </p>
              <ul className="text-sm text-blue-700 space-y-1 ml-4 list-disc">
                <li><strong>Total Facturé</strong> : Montant total facturé aux clients (EOS ou PARTNER)</li>
                <li><strong>Total Enquêteurs</strong> : Montant total versé aux enquêteurs</li>
                <li><strong>Marge</strong> : Différence entre facturé et versé = profit</li>
              </ul>
            </div>
            
            <Suspense fallback={<LoadingComponent />}>
              <FinancialReports />
            </Suspense>
          </div>
        );

      case 'paiements':
        return (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                👥 Gestion des Paiements Enquêteurs
              </h3>
              <p className="text-green-700 text-sm mb-4">
                Consultez les gains de chaque enquêteur et effectuez les paiements.
                Vous pouvez filtrer par client pour voir les gains EOS ou PARTNER séparément.
              </p>
              <ul className="text-sm text-green-700 space-y-1 ml-4 list-disc">
                <li><strong>Total Gagné</strong> : Montant total des enquêtes confirmées</li>
                <li><strong>Déjà Payé</strong> : Montants déjà versés à l'enquêteur</li>
                <li><strong>Reste à Payer</strong> : Ce qu'il faut encore verser</li>
              </ul>
            </div>
            
            <Suspense fallback={<LoadingComponent />}>
              <PaiementManager />
            </Suspense>
          </div>
        );

      case 'tarifs':
        return (
          <div className="space-y-4">
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-purple-900 mb-2">
                ⚙️ Configuration des Tarifs
              </h3>
              <p className="text-purple-700 text-sm mb-4">
                Gérez les grilles tarifaires pour EOS, les enquêteurs et les clients PARTNER.
              </p>
              <ul className="text-sm text-purple-700 space-y-1 ml-4 list-disc">
                <li><strong>Tarifs EOS</strong> : Prix facturés aux clients EOS (A, AT, ATB, etc.)</li>
                <li><strong>Tarifs Enquêteur</strong> : Montants versés aux enquêteurs</li>
                <li><strong>Tarifs PARTNER</strong> : Mapping lettres → prix pour clients PARTNER</li>
              </ul>
            </div>

            {/* Composant de tarification complet */}
            <div className="-mt-2">
              <Suspense fallback={<LoadingComponent />}>
                <TarificationViewer />
              </Suspense>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* En-tête avec titre */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <DollarSign className="w-7 h-7 text-blue-600" />
          Gestion Financière
        </h1>
        <p className="text-gray-600 mt-1">
          Gérez les tarifs, consultez les gains et effectuez les paiements
        </p>
      </div>

      {/* Cartes de sélection des sections */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {sections.map((section) => (
          <button
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            className={`
              p-6 rounded-lg border-2 transition-all text-left
              ${activeSection === section.id
                ? `border-${section.color}-500 bg-${section.color}-50 shadow-md`
                : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
              }
            `}
          >
            <div className={`
              flex items-center gap-3 mb-2
              ${activeSection === section.id ? `text-${section.color}-600` : 'text-gray-700'}
            `}>
              {section.icon}
              <h3 className="font-semibold text-lg">{section.label}</h3>
            </div>
            <p className="text-sm text-gray-600">{section.description}</p>
          </button>
        ))}
      </div>

      {/* Contenu de la section active */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default FinanceManager;

