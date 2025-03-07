// Ajoutez ces états au début du composant DataViewer
const [selectedData, setSelectedData] = useState(null);
const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);

// Ajoutez cette fonction pour gérer le clic sur MAJ
const handleUpdate = (donnee) => {
    setSelectedData(donnee);
    setIsUpdateModalOpen(true);
};

// Ajoutez cette fonction pour gérer la fermeture du modal
const handleModalClose = (shouldRefresh) => {
    setIsUpdateModalOpen(false);
    setSelectedData(null);
    if (shouldRefresh) {
        fetchData();
    }
};

// Dans le bouton MAJ de votre table, modifiez l'événement onClick:
<button
    onClick={() => handleUpdate(donnee)}
    className="px-2 py-1 bg-green-500 text-white rounded hover:bg-blue-600 text-xs"
>
    MAJ
</button>

// À la fin du composant, juste avant le dernier return, ajoutez:
{
    isUpdateModalOpen && (
        <UpdateModal
            isOpen={isUpdateModalOpen}
            onClose={handleModalClose}
            data={selectedData}
        />
    )
}