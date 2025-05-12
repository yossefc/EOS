import { useRef, useState } from 'react';
import { Printer, FileText,  CheckCircle, AlertCircle, X } from 'lucide-react';
import PropTypes from 'prop-types';

EnqueteBatchExporter.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  onClose: PropTypes.func.isRequired,
};

/**
 * Composant pour exporter plusieurs enquêtes en un seul document
 * @param {Object} props - Les propriétés du composant
 * @param {Array} props.data - Liste des enquêtes à exporter
 * @param {Function} props.onClose - Fonction appelée à la fermeture
 */
const EnqueteBatchExporter = ({ data, onClose }) => {
  const printRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6">
        <div className="bg-white rounded-xl p-6 w-full max-w-md">
          <div className="flex items-center gap-2 text-amber-600 mb-4">
            <AlertCircle className="w-6 h-6" />
            <h2 className="text-lg font-medium">Aucune donnée à exporter</h2>
          </div>
          <p className="text-gray-600 mb-4">Veuillez sélectionner au moins une enquête à exporter.</p>
          <div className="flex justify-end">
            <button 
              onClick={onClose}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Fermer
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Fonction pour imprimer le document
  const handlePrint = () => {
    try {
      setLoading(true);
      const printContent = printRef.current;
      const originalContents = document.body.innerHTML;
      
      document.body.innerHTML = printContent.innerHTML;
      window.print();
      document.body.innerHTML = originalContents;
      
      // Recharger les scripts perdus lors du remplacement du contenu
      const scripts = document.getElementsByTagName('script');
      for (let i = 0; i < scripts.length; i++) {
        const oldScript = scripts[i];
        const newScript = document.createElement('script');
        newScript.src = oldScript.src;
        document.body.appendChild(newScript);
      }
      
      setSuccess(true);
      setTimeout(() => {
        window.location.reload(); // Recharger la page pour restaurer entièrement l'application
      }, 1500);
    } catch (err) {
      setError(`Erreur lors de l'impression : ${err.message}`);
      setLoading(false);
    }
  };

  // Fonction pour exporter en Word
  const handleExportWord = () => {
    try {
      setLoading(true);
      const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' " +
        "xmlns:w='urn:schemas-microsoft-com:office:word' " +
        "xmlns='http://www.w3.org/TR/REC-html40'>" +
        "<head><meta charset='utf-8'><title>Export Enquêtes</title>" +
        "<!--[if gte mso 9]>" +
        "<xml>" +
        "<w:WordDocument>" +
        "<w:View>Print</w:View>" +
        "<w:Zoom>90</w:Zoom>" +
        "<w:DoNotOptimizeForBrowser/>" +
        "</w:WordDocument>" +
        "</xml>" +
        "<![endif]-->" +
        "<style>" +
        "/* Styles pour Word */" +
        "body { font-family: 'Calibri', sans-serif; }" +
        "table { border-collapse: collapse; width: 100%; }" +
        "th, td { border: 1px solid #ccc; padding: 8px; }" +
        "th { background-color: #f0f0f0; }" +
        "h1, h2, h3 { color: #2563eb; }" +
        ".section { margin-bottom: 20px; }" +
        ".header-logo { text-align: center; margin-bottom: 20px; }" +
        ".enquete-info { margin-bottom: 30px; }" +
        ".enquete-details { margin-top: 20px; }" +
        ".page-break { page-break-before: always; }" +
        "</style></head><body>";
      
      const footer = "</body></html>";
      
      // Récupérer le contenu formaté
      const content = printRef.current.innerHTML;
      
      // Créer le document complet
      const source = header + content + footer;
      
      // Créer un blob et un lien de téléchargement
      const blob = new Blob([source], { type: 'application/msword' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      
      // Configurer le lien de téléchargement
      link.href = url;
      link.download = `Export_Enquetes_${new Date().toISOString().slice(0, 10)}.doc`;
      link.click();
      
      // Nettoyer
      URL.revokeObjectURL(url);
      setSuccess(true);
      setLoading(false);
    } catch (err) {
      setError(`Erreur lors de l'export : ${err.message}`);
      setLoading(false);
    }
  };

  // Formatage des dates pour l'affichage
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    
    // Si la date est déjà au format français (DD/MM/YYYY)
    if (dateString.includes('/')) return dateString;
    
    // Sinon, convertir depuis le format ISO
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  // Rendu des éléments demandés
  const renderElements = (elements) => {
    if (!elements) return '-';
    
    const elementMap = {
      'A': 'Adresse',
      'T': 'Téléphone',
      'D': 'Décès',
      'B': 'Coordonnées bancaires',
      'E': 'Coordonnées employeur',
      'R': 'Revenus'
    };
    
    return elements.split('').map(code => elementMap[code] || code).join(', ');
  };

  // Rendu du statut
  const renderStatut = (code) => {
    const statuts = {
      'P': 'Positif',
      'N': 'Négatif / NPA',
      'H': 'Confirmé',
      'Z': 'Annulé (agence)',
      'I': 'Intraitable',
      'Y': 'Annulé (EOS)',
      '': 'En attente'
    };
    
    return statuts[code] || 'Inconnu';
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-auto">
      <div className="bg-white rounded-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto">
        {/* Barre d'outils */}
        <div className="bg-blue-600 px-6 py-4 text-white flex justify-between items-center sticky top-0 z-10">
          <h2 className="text-xl font-bold">
            Export de {data.length} enquête{data.length > 1 ? 's' : ''}
          </h2>
          <div className="flex gap-3">
            {loading ? (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-white text-blue-600 rounded-md">
                <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <span>Traitement...</span>
              </div>
            ) : (
              <>
                <button 
                  onClick={handlePrint}
                  className="flex items-center gap-1 px-3 py-1.5 bg-white text-blue-600 rounded-md hover:bg-blue-50"
                  disabled={loading || success}
                >
                  <Printer className="w-4 h-4" />
                  <span>Imprimer</span>
                </button>
                <button 
                  onClick={handleExportWord}
                  className="flex items-center gap-1 px-3 py-1.5 bg-white text-blue-600 rounded-md hover:bg-blue-50"
                  disabled={loading || success}
                >
                  <FileText className="w-4 h-4" />
                  <span>Export Word</span>
                </button>
              </>
            )}
            <button 
              onClick={onClose}
              className="flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white rounded-md hover:bg-red-600"
              disabled={loading}
            >
              <X className="w-4 h-4" />
              <span>Fermer</span>
            </button>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 m-4 p-4 rounded-md flex items-center gap-2 text-red-700 border border-red-200">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {success && (
          <div className="bg-green-50 m-4 p-4 rounded-md flex items-center gap-2 text-green-700 border border-green-200">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <p>Opération réussie !</p>
          </div>
        )}

        {/* Contenu à imprimer */}
        <div className="p-8" ref={printRef}>
          {/* Page de garde */}
          <div className="header-logo mb-8 text-center">
            <h1 className="text-2xl font-bold text-blue-600 mb-1">EOS FRANCE</h1>
            <p className="text-gray-500">Rapport d&apos;enquêtes</p>
            <p className="mt-6 text-lg font-medium">Export de {data.length} enquête{data.length > 1 ? 's' : ''}</p>
            <p className="mt-2 text-gray-500">Généré le {new Date().toLocaleDateString('fr-FR')}</p>
          </div>

          {/* Table des matières */}
          <div className="mb-12">
            <h2 className="text-xl font-bold text-blue-700 mb-4">Table des matières</h2>
            <ol className="list-decimal pl-8">
              {data.map((item, index) => (
                <li key={index} className="mb-2">
                  Enquête {item.numeroDossier} - {item.nom} {item.prenom} 
                  {item.code_resultat && ` (${renderStatut(item.code_resultat)})`}
                </li>
              ))}
            </ol>
          </div>

          {/* Une page par enquête */}
          {data.map((enqueteData, index) => (
            <div key={index} className={index > 0 ? 'page-break' : ''}>
              <h2 className="text-2xl font-bold text-blue-700 mb-6 text-center">
                Enquête {enqueteData.numeroDossier}
              </h2>

              {/* Informations générales */}
              <div className="enquete-info border-b pb-6 mb-6">
                <h3 className="text-xl font-bold text-blue-700 mb-4">Informations générales</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p><strong>Numéro de dossier:</strong> {enqueteData.numeroDossier || '-'}</p>
                    <p><strong>Référence:</strong> {enqueteData.referenceDossier || '-'}</p>
                    <p><strong>Type de demande:</strong> {enqueteData.typeDemande === 'ENQ' ? 'Enquête' : 
                      enqueteData.typeDemande === 'CON' ? 'Contestation' : enqueteData.typeDemande || '-'}</p>
                    <p><strong>Éléments demandés:</strong> {renderElements(enqueteData.elementDemandes)}</p>
                    <p><strong>Date de retour espérée:</strong> {formatDate(enqueteData.dateRetourEspere)}</p>
                  </div>
                  <div>
                    <p><strong>Statut:</strong> {renderStatut(enqueteData.code_resultat)}</p>
                    <p><strong>Éléments retrouvés:</strong> {renderElements(enqueteData.elements_retrouves)}</p>
                    <p><strong>Date de création:</strong> {formatDate(enqueteData.created_at)}</p>
                    <p><strong>Date de mise à jour:</strong> {formatDate(enqueteData.updated_at)}</p>
                  </div>
                </div>
              </div>

              {/* État civil */}
              <div className="section mb-6">
                <h3 className="text-xl font-bold text-blue-700 mb-4">État civil</h3>
                <table className="w-full border-collapse">
                  <tbody>
                    <tr>
                      <th className="text-left p-2 bg-gray-100 border">Nom</th>
                      <td className="p-2 border">{enqueteData.nom || '-'}</td>
                      <th className="text-left p-2 bg-gray-100 border">Prénom</th>
                      <td className="p-2 border">{enqueteData.prenom || '-'}</td>
                    </tr>
                    <tr>
                      <th className="text-left p-2 bg-gray-100 border">Date de naissance</th>
                      <td className="p-2 border">{formatDate(enqueteData.dateNaissance)}</td>
                      <th className="text-left p-2 bg-gray-100 border">Lieu de naissance</th>
                      <td className="p-2 border">{enqueteData.lieuNaissance || '-'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Adresse actuelle */}
              {enqueteData.elements_retrouves?.includes('A') && (
                <div className="section mb-6">
                  <h3 className="text-xl font-bold text-blue-700 mb-4">Adresse actuelle</h3>
                  <table className="w-full border-collapse">
                    <tbody>
                      <tr>
                        <th className="text-left p-2 bg-gray-100 border">Adresse</th>
                        <td className="p-2 border">
                          {enqueteData.adresse1 && <div>{enqueteData.adresse1}</div>}
                          {enqueteData.adresse2 && <div>{enqueteData.adresse2}</div>}
                          {enqueteData.adresse3 && <div>{enqueteData.adresse3}</div>}
                          {enqueteData.adresse4 && <div>{enqueteData.adresse4}</div>}
                          {!enqueteData.adresse1 && !enqueteData.adresse2 && 
                           !enqueteData.adresse3 && !enqueteData.adresse4 && '-'}
                        </td>
                      </tr>
                      <tr>
                        <th className="text-left p-2 bg-gray-100 border">Code postal / Ville</th>
                        <td className="p-2 border">
                          {enqueteData.code_postal || '-'} {enqueteData.ville || '-'}
                        </td>
                      </tr>
                      <tr>
                        <th className="text-left p-2 bg-gray-100 border">Téléphone</th>
                        <td className="p-2 border">{enqueteData.telephone_personnel || '-'}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

              {/* Autres sections si éléments retrouvés */}
              {/* ... Inclure selon besoin ... */}

              {/* Commentaires */}
              {(enqueteData.memo1 || enqueteData.memo2 || enqueteData.memo3 || 
                enqueteData.memo4 || enqueteData.memo5) && (
                <div className="section mb-6">
                  <h3 className="text-xl font-bold text-blue-700 mb-4">Commentaires</h3>
                  <p>{enqueteData.memo1}</p>
                  <p>{enqueteData.memo2}</p>
                  <p>{enqueteData.memo3}</p>
                  <p>{enqueteData.memo4}</p>
                  <p>{enqueteData.memo5}</p>
                </div>
              )}

              {/* Pied de page */}
              <div className="mt-6 text-center text-gray-500 text-sm">
                <p>Page {index + 1} sur {data.length}</p>
                <p>EOS FRANCE - Document confidentiel</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EnqueteBatchExporter;