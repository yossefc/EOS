import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re

class DataViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualisateur de Données EOS")
        self.root.state('zoomed')
        
        # Définition des colonnes avec leurs largeurs
        self.column_specs = [
            ("N° DOSSIER", 10),
            ("REFERENCE DOSSIER", 15),
            ("NUMERO INTERLOCUTEUR", 12),
            ("GUID INTERLOCUTEUR", 36),
            ("TYPE DE DEMANDE D'ENQUÊTE", 3),
            ("NUMERO DEMANDE ENQUETE", 11),
            ("NUMERO DEMANDE ENQUETE CONTESTEE", 11),
            ("NUMERO DEMANDE ENQUETE INITIALE", 11),
            ("FORFAIT DEMANDE", 16),
            ("DATE DE RETOUR ESPERE", 10),
            ("QUALITE", 10),
            ("NOM", 30),
            ("PRENOM", 20),
            ("DATE DE NAISSANCE", 10),
            ("LIEU DE NAISSANCE", 50),
            ("CODE POSTAL NAISSANCE", 10),
            ("PAYS DE NAISSANCE", 32),
            ("NOM PATRONYMIQUE", 30),
            ("DATE DE RETOUR", 10),
            ("CODE RESULTAT DE L'ENQUETE", 1),
            ("ELEMENTS RETROUVES", 10),
            ("FLAG état civil erroné", 1),
            ("NUMERO DE FACTURE", 9),
            ("DATE DE FACTURE", 10),
            ("MONTANT FACTURE", 8),
            ("TARIF APPLIQUE", 8),
            ("CUMUL DES MONTANTS PRECEDEMMENT FACTURES", 8),
            ("REPRISE DE FACTURATION", 8),
            ("REMISE EVENTUELLE", 8),
            ("DATE DE DECES", 10),
            ("N° ACTE DE DECES", 10),
            ("CODE INSEE DECES", 5),
            ("CODE POSTAL DECES", 10),
            ("LOCALITE DECES", 32),
            ("ADRESSE 1", 32),
            ("ADRESSE 2", 32),
            ("ADRESSE 3", 32),
            ("ADRESSE 4", 32),
            ("CODE POSTAL", 10),
            ("VILLE", 32),
            ("PAYS RESIDENCE", 32),
            ("TELEPHONE PERSONNEL", 15),
            ("TELEPHONE CHEZ L'EMPLOYEUR", 15),
            ("NOM DE L'EMPLOYEUR", 32),
            ("TELEPHONE DE L'EMPLOYEUR", 15),
            ("TELECOPIE EMPLOYEUR", 15),
            ("ADRESSE 1 DE L'EMPLOYEUR", 32),
            ("ADRESSE 2 DE L'EMPLOYEUR", 32),
            ("ADRESSE 3 DE L'EMPLOYEUR", 32),
            ("ADRESSE 4 DE L'EMPLOYEUR", 32),
            ("CODE POSTAL DE L'EMPLOYEUR", 10),
            ("VILLE DE L'EMPLOYEUR", 32),
            ("PAYS DE L'EMPLOYEUR", 32),
            ("BANQUE DE DOMICILIATION", 32),
            ("LIBELLE GUICHET", 30),
            ("TITULAIRE DU COMPTE", 32),
            ("CODE BANQUE", 5),
            ("CODE GUICHET", 5),
            ("NUMERO DE COMPTE", 11),
            ("RIB DU COMPTE", 2)
        ]
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(
            "Treeview.Heading",
            background="#2C3E50",
            foreground="white",
            font=('Arial', 9, 'bold'),
            relief="raised",
            borderwidth=1
        )
        
        style.configure(
            "Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            font=('Courier New', 9),
            fieldbackground="white"
        )
        
        style.map("Treeview",
            background=[('selected', '#3498DB')],
            foreground=[('selected', 'white')]
        )

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Bouton et frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        self.load_button = ttk.Button(
            controls_frame,
            text="Charger un fichier",
            command=self.load_file,
            padding=5
        )
        self.load_button.pack(side='left')
        
        # Frame pour le tableau avec bordure visible
        table_frame = ttk.Frame(main_frame, relief='solid', borderwidth=1)
        table_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame)
        y_scrollbar.pack(side='right', fill='y')
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal')
        x_scrollbar.pack(side='bottom', fill='x')
        
        # Création du Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=[name for name, _ in self.column_specs],
            show='headings',
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )
        
        # Configuration des scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)
        
        # Configuration des colonnes
        for (name, width) in self.column_specs:
            self.tree.heading(name, text=name)
            display_width = max(width * 8, len(name) * 8)
            self.tree.column(name, width=display_width, minwidth=display_width)
        
        self.tree.pack(fill='both', expand=True)

    def parse_line(self, line):
        """Parse une ligne selon les spécifications exactes"""
        if len(line.strip()) == 0:
            return []
            
        try:
            values = [
                line[0:10].strip(),                    # N° DOSSIER
                line[10:25].strip(),                   # REFERENCE DOSSIER
                line[25:37].strip(),                   # NUMERO INTERLOCUTEUR
                line[37:73].strip(),                   # GUID INTERLOCUTEUR
                line[73:76].strip(),                   # TYPE DE DEMANDE
                line[76:87].strip(),                   # NUMERO DEMANDE ENQUETE
                line[87:98].strip(),                   # NUMERO DEMANDE ENQUETE CONTESTEE
                line[98:109].strip(),                  # NUMERO DEMANDE ENQUETE INITIALE
                line[109:125].strip(),                 # FORFAIT DEMANDE
                line[125:135].strip(),                 # DATE DE RETOUR ESPERE
                line[135:145].strip(),                 # QUALITE
                line[145:175].strip(),                 # NOM
                line[175:195].strip(),                 # PRENOM
                line[195:205].strip(),                 # DATE DE NAISSANCE
                line[205:255].strip(),                 # LIEU DE NAISSANCE
                line[255:265].strip(),                 # CODE POSTAL NAISSANCE
                line[265:297].strip(),                 # PAYS DE NAISSANCE
                line[297:327].strip(),                 # NOM PATRONYMIQUE
                line[327:337].strip(),                 # DATE DE RETOUR
                line[337:338].strip(),                 # CODE RESULTAT
                line[338:348].strip(),                 # ELEMENTS RETROUVES
                line[348:349].strip(),                 # FLAG ETAT CIVIL ERRONE
                line[349:358].strip(),                 # NUMERO FACTURE
                line[358:368].strip(),                 # DATE FACTURE
                line[368:376].strip(),                 # MONTANT FACTURE
                line[376:384].strip(),                 # TARIF APPLIQUE
                line[384:392].strip(),                 # CUMUL MONTANTS PRECEDENTS
                line[392:400].strip(),                 # REPRISE FACTURATION
                line[400:408].strip(),                 # REMISE EVENTUELLE
                line[408:418].strip(),                 # DATE DE DECES
                line[418:428].strip(),                 # NUMERO ACTE DECES
                line[428:433].strip(),                 # CODE INSEE DECES
                line[433:443].strip(),                 # CODE POSTAL DECES
                line[443:475].strip(),                 # LOCALITE DECES
                line[475:507].strip(),                 # ADRESSE 1
                line[507:539].strip(),                 # ADRESSE 2
                line[539:571].strip(),                 # ADRESSE 3
                line[571:603].strip(),                 # ADRESSE 4
                line[603:613].strip(),                 # CODE POSTAL
                line[613:645].strip(),                 # VILLE
                line[645:677].strip(),                 # PAYS RESIDENCE
                line[677:692].strip(),                 # TELEPHONE PERSONNEL
                line[692:707].strip(),                 # TELEPHONE EMPLOYEUR
                line[707:739].strip(),                 # NOM EMPLOYEUR
                line[739:754].strip(),                 # TELEPHONE DE L'EMPLOYEUR
                line[754:769].strip(),                 # TELECOPIE EMPLOYEUR
                line[769:801].strip(),                 # ADRESSE 1 EMPLOYEUR
                line[801:833].strip(),                 # ADRESSE 2 EMPLOYEUR
                line[833:865].strip(),                 # ADRESSE 3 EMPLOYEUR
                line[865:897].strip(),                 # ADRESSE 4 EMPLOYEUR
                line[897:907].strip(),                 # CODE POSTAL EMPLOYEUR
                line[907:939].strip(),                 # VILLE EMPLOYEUR
                line[939:971].strip(),                 # PAYS EMPLOYEUR
                line[971:1003].strip(),                # BANQUE DOMICILIATION
                line[1003:1033].strip(),               # LIBELLE GUICHET
                line[1033:1065].strip(),               # TITULAIRE COMPTE
                line[1065:1070].strip(),               # CODE BANQUE
                line[1070:1075].strip(),               # CODE GUICHET
                line[1075:1086].strip(),               # NUMERO COMPTE
                line[1086:1088].strip()                # RIB COMPTE
            ]
            return values
        except Exception as e:
            print(f"Erreur lors du parsing de la ligne: {str(e)}")
            return []

    def parse_file(self, file_path):
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    
                        values = self.parse_line(line)
                        if len(values) > 0:  # Ignorer les lignes sans données
                            data.append(values)
            
            columns = [name for name, _ in self.column_specs]
            df = pd.DataFrame(data, columns=columns)
            return df
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du parsing du fichier: {str(e)}")
            return None

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner le fichier de données",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            df = self.parse_file(file_path)
            if df is not None:
                # Effacer les données existantes
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Insérer les nouvelles données avec alternance de couleurs
                for idx, row in df.iterrows():
                    tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                    self.tree.insert('', 'end', values=list(row), tags=(tag,))

def main():
    root = tk.Tk()
    app = DataViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()