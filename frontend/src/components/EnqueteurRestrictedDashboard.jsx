import { useState, useEffect } from 'react';
import { User, ClipboardList, BarChart2, LogOut } from 'lucide-react';
import PropTypes from 'prop-types';
import EnqueteurEnquetes from './EnqueteurEnquetes';
import EnhancedEarningsViewer from './EarningsViewer';

const EnqueteurRestrictedDashboard = ({ enqueteur, onLogout }) => {
  const [activeTab, setActiveTab] = useState('enquetes');
  const [userFullName, setUserFullName] = useState('');

  useEffect(() => {
    if (enqueteur) {
      setUserFullName(`${enqueteur.prenom} ${enqueteur.nom}`);
    }
  }, [enqueteur]);

  return (
    <div className="container mx-auto px-4 py-6">
      {/* En-tête avec les informations de l'enquêteur */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold">{userFullName}</h2>
              <p className="text-gray-500">{enqueteur?.email}</p>
            </div>
          </div>
          <button
            onClick={onLogout}
            className="flex items-center gap-1 px-4 py-2 bg-red-50 text-red-600 rounded-md hover:bg-red-100"
          >
            <LogOut className="w-4 h-4" />
            <span>Déconnexion</span>
          </button>
        </div>
      </div>

      {/* Navigation par onglets */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('enquetes')}
              className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center gap-2 ${
                activeTab === 'enquetes'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <ClipboardList className="w-5 h-5" />
              <span>Mes enquêtes</span>
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`py-4 px-6 border-b-2 font-medium text-sm flex items-center gap-2 ${
                activeTab === 'stats'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <BarChart2 className="w-5 h-5" />
              <span>Mes statistiques</span>
            </button>
          </nav>
        </div>

        {/* Contenu des onglets */}
        <div className="p-6">
          {activeTab === 'enquetes' && enqueteur && (
            <EnqueteurEnquetes enqueteurId={enqueteur.id} />
          )}
          {activeTab === 'stats' && enqueteur && (
            <EnhancedEarningsViewer enqueteurId={enqueteur.id} />
          )}
        </div>
      </div>
    </div>
  );
};

EnqueteurRestrictedDashboard.propTypes = {
  enqueteur: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    nom: PropTypes.string,
    prenom: PropTypes.string,
    email: PropTypes.string
  }),
  onLogout: PropTypes.func.isRequired
};

export default EnqueteurRestrictedDashboard;