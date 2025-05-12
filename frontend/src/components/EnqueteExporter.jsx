import  { useRef, useState } from 'react';
import { Printer, FileText, X } from 'lucide-react';
import PropTypes from 'prop-types';

EnqueteExporter.propTypes = {
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  onClose: PropTypes.func.isRequired,
};

/**
 * Composant pour exporter et imprimer les données complètes d'une enquête
 */
const EnqueteExporter = ({ data, onClose }) => {
  const printRef = useRef(null);
  // Utiliser directement les données passées sans faire d'appel API
  const [loading] = useState(false);

  // Fonction pour imprimer le document
  const handlePrint = () => {
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
    
    window.location.reload(); // Recharger la page pour restaurer entièrement l'application
  };

  // Fonction pour exporter en Word
  const handleExportWord = () => {
    const header = "<html xmlns:o='urn:schemas-microsoft-com:office:office' " +
      "xmlns:w='urn:schemas-microsoft-com:office:word' " +
      "xmlns='http://www.w3.org/TR/REC-html40'>" +
      "<head><meta charset='utf-8'><title>Enquête " + (data?.numeroDossier || '') + "</title>" +
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
      "@page { size: landscape; }" +
      "body { font-family: 'Calibri', sans-serif; margin: 0; padding: 0; }" +
      "table { border-collapse: collapse; width: 100%; margin-bottom: 10px; font-size: 9pt; }" +
      "th, td { border: 1px solid #ccc; padding: 3px 5px; }" +
      "th { background-color: #f0f0f0; text-align: left; font-weight: bold; }" +
      ".header { text-align: center; margin-bottom: 10px; }" +
      ".main-title { font-size: 16pt; color: #2563eb; margin: 0; }" +
      ".section-title { font-size: 11pt; font-weight: bold; color: #2563eb; margin: 8px 0 5px 0; }" +
      ".footer { font-size: 8pt; text-align: center; margin-top: 5px; color: #666; }" +
      ".compact-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px; }" +
      ".grid-item { margin-bottom: 3px; }" +
      ".container { padding: 10px; }" +
      ".bold { font-weight: bold; }" +
      ".note { font-size: 8pt; color: #666; }" +
      ".data-label { font-weight: bold; width: 30%; }" +
      ".data-value { width: 70%; }" +
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
    link.setAttribute('download', `Enquete_${data?.numeroDossier || 'export'}.doc`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Nettoyer
    URL.revokeObjectURL(url);
  };

  // Formatage des dates pour l'affichage
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    
    // Si la date est déjà au format français (DD/MM/YYYY)
    if (dateString.includes('/')) return dateString;
    
    // Sinon, convertir depuis le format ISO
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch (e) {
      console.log(e)
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-8 max-w-md">
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
          <p className="text-center mt-4">Chargement des données...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-6 overflow-auto">
      <div className="bg-white rounded-xl w-full max-w-5xl h-[90vh] overflow-hidden flex flex-col">
        {/* Barre d'outils */}
        <div className="bg-blue-600 px-6 py-4 text-white flex justify-between items-center">
          <h2 className="text-xl font-bold">
            Enquête {data?.numeroDossier || ''}
          </h2>
          <div className="flex gap-3">
            <button 
              onClick={handlePrint}
              className="flex items-center gap-1 px-3 py-1.5 bg-white text-blue-600 rounded-md hover:bg-blue-50"
            >
              <Printer className="w-4 h-4" />
              <span>Imprimer</span>
            </button>
            <button 
              onClick={handleExportWord}
              className="flex items-center gap-1 px-3 py-1.5 bg-white text-blue-600 rounded-md hover:bg-blue-50"
            >
              <FileText className="w-4 h-4" />
              <span>Export Word</span>
            </button>
            <button 
              onClick={onClose}
              className="flex items-center gap-1 px-3 py-1.5 bg-red-500 text-white rounded-md hover:bg-red-600"
            >
              <X className="w-4 h-4" />
              <span>Fermer</span>
            </button>
          </div>
        </div>

        {/* Contenu à imprimer (avec défilement) */}
        <div className="overflow-y-auto flex-grow p-6">
          <div ref={printRef} className="container">
            {/* En-tête */}
            <div className="header">
              <h1 className="main-title">FICHE D&apos;ENQUÊTE EOS FRANCE</h1>
              <p className="note">Document confidentiel - {new Date().toLocaleDateString('fr-FR')}</p>
            </div>

            {/* Informations générales */}
            <h2 className="section-title">INFORMATIONS GÉNÉRALES</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">ID</th>
                  <td width="18%">{data?.id || '-'}</td>
                  <th width="15%">N° Dossier</th>
                  <td width="18%">{data?.numeroDossier || '-'}</td>
                  <th width="15%">Référence</th>
                  <td width="19%">{data?.referenceDossier || '-'}</td>
                </tr>
                <tr>
                  <th>Type demande</th>
                  <td>{data?.typeDemande === 'ENQ' ? 'Enquête' : 
                    data?.typeDemande === 'CON' ? 'Contestation' : 
                    data?.typeDemande || '-'}</td>
                  <th>Éléments demandés</th>
                  <td>{data?.elementDemandes || '-'}</td>
                  <th>Éléments obligatoires</th>
                  <td>{data?.elementObligatoires || '-'}</td>
                </tr>
                <tr>
                  <th>Date de retour</th>
                  <td>{formatDate(data?.dateRetourEspere)}</td>
                  <th>Date de création</th>
                  <td>{formatDate(data?.created_at)}</td>
                  <th>Date modification</th>
                  <td>{formatDate(data?.updated_at)}</td>
                </tr>
              </tbody>
            </table>

            {/* État civil */}
            <h2 className="section-title">ÉTAT CIVIL</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">Qualité</th>
                  <td width="18%">{data?.qualite || '-'}</td>
                  <th width="15%">Nom</th>
                  <td width="18%">{data?.nom || '-'}</td>
                  <th width="15%">Prénom</th>
                  <td width="19%">{data?.prenom || '-'}</td>
                </tr>
                <tr>
                  <th>Nom patronymique</th>
                  <td>{data?.nomPatronymique || '-'}</td>
                  <th>Date naissance</th>
                  <td>{formatDate(data?.dateNaissance)}</td>
                  <th>Lieu naissance</th>
                  <td>{data?.lieuNaissance || '-'}</td>
                </tr>
                <tr>
                  <th>Code postal naiss.</th>
                  <td>{data?.codePostalNaissance || '-'}</td>
                  <th>Pays naissance</th>
                  <td>{data?.paysNaissance || '-'}</td>
                  <th>Fichier ID</th>
                  <td>{data?.fichier_id || '-'}</td>
                </tr>
              </tbody>
            </table>

            {/* Adresse actuelle */}
            <h2 className="section-title">ADRESSE</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">Adresse 1</th>
                  <td width="35%">{data?.adresse1 || '-'}</td>
                  <th width="15%">Adresse 2</th>
                  <td width="35%">{data?.adresse2 || '-'}</td>
                </tr>
                <tr>
                  <th>Adresse 3</th>
                  <td>{data?.adresse3 || '-'}</td>
                  <th>Adresse 4</th>
                  <td>{data?.adresse4 || '-'}</td>
                </tr>
                <tr>
                  <th>Code postal</th>
                  <td>{data?.codePostal || '-'}</td>
                  <th>Ville</th>
                  <td>{data?.ville || '-'}</td>
                </tr>
                <tr>
                  <th>Pays</th>
                  <td>{data?.paysResidence || '-'}</td>
                  <th>Téléphone</th>
                  <td>{data?.telephonePersonnel || '-'}</td>
                </tr>
              </tbody>
            </table>

            {/* Informations bancaires */}
            <h2 className="section-title">INFORMATIONS BANCAIRES</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">Banque</th>
                  <td width="35%">{data?.banqueDomiciliation || '-'}</td>
                  <th width="15%">Guichet</th>
                  <td width="35%">{data?.libelleGuichet || '-'}</td>
                </tr>
                <tr>
                  <th>Titulaire</th>
                  <td>{data?.titulaireCompte || '-'}</td>
                  <th>Code banque</th>
                  <td>{data?.codeBanque || '-'}</td>
                </tr>
                <tr>
                  <th>Code guichet</th>
                  <td>{data?.codeGuichet || '-'}</td>
                  <th>Numéro compte</th>
                  <td>{data?.numeroCompte || '-'}</td>
                </tr>
                <tr>
                  <th>RIB</th>
                  <td colSpan="3">{data?.ribCompte || '-'}</td>
                </tr>
              </tbody>
            </table>

            {/* Employeur */}
            <h2 className="section-title">INFORMATIONS EMPLOYEUR</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">Nom employeur</th>
                  <td width="35%">{data?.nomEmployeur || '-'}</td>
                  <th width="15%">Téléphone</th>
                  <td width="35%">{data?.telephoneEmployeur || '-'}</td>
                </tr>
                <tr>
                  <th>Télécopie</th>
                  <td colSpan="3">{data?.telecopieEmployeur || '-'}</td>
                </tr>
              </tbody>
            </table>

            {/* Autres informations */}
            <h2 className="section-title">AUTRES INFORMATIONS</h2>
            <table>
              <tbody>
                <tr>
                  <th width="15%">Numéro demande</th>
                  <td width="35%">{data?.numeroDemande || '-'}</td>
                  <th width="15%">Numéro demande contestée</th>
                  <td width="35%">{data?.numeroDemandeContestee || '-'}</td>
                </tr>
                <tr>
                  <th>Numéro interlocuteur</th>
                  <td>{data?.numeroInterlocuteur || '-'}</td>
                  <th>GUID interlocuteur</th>
                  <td>{data?.guidInterlocuteur || '-'}</td>
                </tr>
                <tr>
                  <th>Numéro demande initiale</th>
                  <td>{data?.numeroDemandeInitiale || '-'}</td>
                  <th>Forfait demande</th>
                  <td>{data?.forfaitDemande || '-'}</td>
                </tr>
                <tr>
                  <th>Code motif</th>
                  <td>{data?.codeMotif || '-'}</td>
                  <th>Motif contestation</th>
                  <td>{data?.motifDeContestation || '-'}</td>
                </tr>
                <tr>
                  <th>Éléments contestés</th>
                  <td>{data?.elementContestes || '-'}</td>
                  <th>Code société</th>
                  <td>{data?.codesociete || '-'}</td>
                </tr>
                <tr>
                  <th>Urgence</th>
                  <td>{data?.urgence || '-'}</td>
                  <th>Enquêteur ID</th>
                  <td>{data?.enqueteurId || '-'}</td>
                </tr>
                <tr>
                  <th>Commentaire</th>
                  <td colSpan="3">{data?.commentaire || '-'}</td>
                </tr>
              </tbody>
            </table>

            {/* TOUS LES AUTRES CHAMPS qui n'ont pas été affichés explicitement */}
            <h2 className="section-title">CHAMPS SUPPLÉMENTAIRES</h2>
            <table>
              <tbody>
                {Object.entries(data || {}).map(([key, value]) => {
                  // Liste des clés déjà affichées dans les sections précédentes
                  const displayedKeys = [
                    'id', 'numeroDossier', 'referenceDossier', 'typeDemande', 'elementDemandes', 
                    'elementObligatoires', 'dateRetourEspere', 'created_at', 'updated_at',
                    'qualite', 'nom', 'prenom', 'nomPatronymique', 'dateNaissance', 'lieuNaissance',
                    'codePostalNaissance', 'paysNaissance', 'fichier_id', 'adresse1', 'adresse2',
                    'adresse3', 'adresse4', 'codePostal', 'ville', 'paysResidence', 'telephonePersonnel',
                    'banqueDomiciliation', 'libelleGuichet', 'titulaireCompte', 'codeBanque', 'codeGuichet',
                    'numeroCompte', 'ribCompte', 'nomEmployeur', 'telephoneEmployeur', 'telecopieEmployeur',
                    'numeroDemande', 'numeroDemandeContestee', 'numeroInterlocuteur', 'guidInterlocuteur',
                    'numeroDemandeInitiale', 'forfaitDemande', 'codeMotif', 'motifDeContestation',
                    'elementContestes', 'codesociete', 'urgence', 'enqueteurId', 'commentaire'
                  ];
                  
                  // Ignorer les champs qui sont déjà affichés ou qui viennent de donnee_enqueteur
                  // ou qui sont null/undefined
                  if (displayedKeys.includes(key) || 
                      ['donnee_enqueteur', 'code_resultat', 'elements_retrouves', 'flag_etat_civil_errone'].includes(key) ||
                      value === null || value === undefined) {
                    return null;
                  }
                  
                  return (
                    <tr key={key}>
                      <th width="15%">{key}</th>
                      <td colSpan="3">
                        {typeof value === 'object' ? JSON.stringify(value) : 
                         key.toLowerCase().includes('date') ? formatDate(value) : 
                         String(value)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>

            {/* Pied de page */}
            <div className="footer">
              <p>Document généré le {new Date().toLocaleDateString('fr-FR')} à {new Date().toLocaleTimeString('fr-FR')}</p>
              <p>EOS FRANCE - Document confidentiel - Ne pas diffuser</p>
              <p>Uniquement les données de la table  sont incluses dans ce document</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnqueteExporter;