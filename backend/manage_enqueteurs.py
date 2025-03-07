import tkinter as tk
from tkinter import ttk, messagebox
from models.enqueteur import Enqueteur
from extensions import db
import os

class EnqueteurManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion des Enquêteurs")
        self.root.geometry("800x600")

        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(root, text="Nouvel Enquêteur", padding="10")
        form_frame.pack(fill="x", padx=10, pady=5)

        # Champs du formulaire
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky="w", pady=2)
        self.nom_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.nom_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text="Prénom:").grid(row=1, column=0, sticky="w", pady=2)
        self.prenom_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.prenom_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text="Téléphone:").grid(row=3, column=0, sticky="w", pady=2)
        self.telephone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.telephone_var).grid(row=3, column=1, sticky="ew", pady=2)

        # Bouton pour créer
        ttk.Button(form_frame, text="Créer Enquêteur", command=self.create_enqueteur).grid(row=4, column=0, columnspan=2, pady=10)

        # Liste des enquêteurs
        list_frame = ttk.LabelFrame(root, text="Liste des Enquêteurs", padding="10")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview pour afficher les enquêteurs
        columns = ("ID", "Nom", "Prénom", "Email", "Téléphone", "Config VPN")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Définir les en-têtes
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Placement de la liste et scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Charger la liste initiale
        self.load_enqueteurs()

    def create_enqueteur(self):
        try:
            # Créer l'enquêteur avec sa config VPN
            enqueteur, config_path = Enqueteur.create_with_vpn(
                nom=self.nom_var.get(),
                prenom=self.prenom_var.get(),
                email=self.email_var.get(),
                telephone=self.telephone_var.get()
            )

            # Afficher le message de succès
            messagebox.showinfo(
                "Succès",
                f"Enquêteur créé avec succès!\n\n"
                f"ID: {enqueteur.id}\n"
                f"Nom: {enqueteur.nom} {enqueteur.prenom}\n"
                f"Configuration VPN: {config_path}"
            )

            # Vider les champs
            self.nom_var.set("")
            self.prenom_var.set("")
            self.email_var.set("")
            self.telephone_var.set("")

            # Recharger la liste
            self.load_enqueteurs()

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def load_enqueteurs(self):
        # Effacer la liste actuelle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Charger tous les enquêteurs
        enqueteurs = Enqueteur.query.all()
        
        for enqueteur in enqueteurs:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'vpn_configs',
                f'client{enqueteur.id}.ovpn'
            )
            config_status = "Généré ✓" if os.path.exists(config_path) else "Non généré ✗"
            
            self.tree.insert("", "end", values=(
                enqueteur.id,
                enqueteur.nom,
                enqueteur.prenom,
                enqueteur.email,
                enqueteur.telephone or "N/A",
                config_status
            ))

if __name__ == "__main__":
    # Créer la fenêtre principale
    root = tk.Tk()
    app = EnqueteurManager(root)
    root.mainloop()
