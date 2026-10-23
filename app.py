import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import csv


class BatiIA:
    def __init__(self, root):
        self.root = root
        self.root.title("BATI-IA - Assistant BTP")
        self.root.geometry("1050x720")
        self.root.minsize(850, 600)

        self.volume_unitaire = 0.0
        self.nombre_parts = 1
        self.dimensions = {}
        self.materiaux = []
        self.devis = []

        self.devise = tk.StringVar(value="DH")

        ttk.Label(
            root,
            text="BATI-IA | Assistant de calcul BTP",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        self.onglets = ttk.Notebook(root)
        self.onglets.pack(fill="both", expand=True, padx=10, pady=8)

        self.page_geo = ttk.Frame(self.onglets, padding=10)
        self.page_mat = ttk.Frame(self.onglets, padding=10)
        self.page_devis = ttk.Frame(self.onglets, padding=10)

        self.onglets.add(self.page_geo, text="Géométrie")
        self.onglets.add(self.page_mat, text="Matériaux")
        self.onglets.add(self.page_devis, text="Devis")

        self.creer_geometrie()
        self.creer_materiaux()
        self.creer_devis()

    # ---------------- GÉOMÉTRIE ----------------

    def creer_geometrie(self):
        ttk.Label(
            self.page_geo,
            text="Calcul des surfaces et volumes",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=5)

        ligne = ttk.Frame(self.page_geo)
        ligne.pack(fill="x", pady=5)

        ttk.Label(ligne, text="Figure ou solide :").pack(side="left")

        self.figure = tk.StringVar(value="Pavé droit")

        self.figures = [
            "Carré",
            "Rectangle",
            "Triangle",
            "Trapèze",
            "Parallélogramme",
            "Disque",
            "Cube",
            "Pavé droit",
            "Prisme triangulaire",
            "Prisme pentagonal",
            "Prisme hexagonal",
            "Cylindre",
            "Cône",
            "Tronc de cône",
            "Pyramide à base carrée",
            "Pyramide à base rectangulaire",
            "Pyramide à base triangulaire",
            "Pyramide à base pentagonale",
            "Pyramide à base hexagonale",
            "Tronc de pyramide à base carrée",
            "Tas de cailloux (tronc de pyramide rectangulaire)",
            "Sphère",
            "Demi-sphère",
            "Ellipsoïde"
        ]

        self.liste_figures = ttk.Combobox(
            ligne,
            textvariable=self.figure,
            values=self.figures,
            state="readonly",
            width=49
        )
        self.liste_figures.pack(side="left", padx=8)
        self.liste_figures.bind(
            "<<ComboboxSelected>>",
            lambda event: self.afficher_champs()
        )

        self.zone_champs = ttk.LabelFrame(
            self.page_geo,
            text="Dimensions",
            padding=8
        )
        self.zone_champs.pack(fill="x", pady=8)

        ligne_n = ttk.Frame(self.page_geo)
        ligne_n.pack(fill="x", pady=5)

        ttk.Label(
            ligne_n,
            text="Nombre de parties identiques n :"
        ).pack(side="left")

        self.var_n = tk.StringVar(value="1")
        ttk.Entry(
            ligne_n,
            textvariable=self.var_n,
            width=12
        ).pack(side="left", padx=8)

        ttk.Button(
            self.page_geo,
            text="Calculer",
            command=self.calculer
        ).pack(anchor="w", pady=6)

        # IMPORTANT : créer cette zone avant afficher_champs()
        self.resultat_geo = tk.Text(
            self.page_geo,
            height=12,
            wrap="word",
            font=("Arial", 10)
        )
        self.resultat_geo.pack(fill="both", expand=True, pady=8)
        self.resultat_geo.configure(state="disabled")

        self.afficher_champs()

    def afficher_champs(self):
        for widget in self.zone_champs.winfo_children():
            widget.destroy()

        figure = self.figure.get()

        liste_champs = {
            "Carré": ["Côté"],
            "Rectangle": ["Longueur", "Largeur"],
            "Triangle": ["Base", "Hauteur"],
            "Trapèze": ["Grande base", "Petite base", "Hauteur"],
            "Parallélogramme": ["Base", "Hauteur"],
            "Disque": ["Rayon"],

            "Cube": ["Côté"],
            "Pavé droit": ["Longueur", "Largeur", "Hauteur"],

            "Prisme triangulaire": [
                "Base du triangle",
                "Hauteur du triangle",
                "Longueur du prisme"
            ],
            "Prisme pentagonal": [
                "Côté du pentagone",
                "Hauteur du prisme"
            ],
            "Prisme hexagonal": [
                "Côté de l'hexagone",
                "Hauteur du prisme"
            ],

            "Cylindre": ["Rayon", "Hauteur"],
            "Cône": ["Rayon", "Hauteur"],
            "Tronc de cône": [
                "Grand rayon",
                "Petit rayon",
                "Hauteur"
            ],

            "Pyramide à base carrée": [
                "Côté de la base",
                "Hauteur"
            ],
            "Pyramide à base rectangulaire": [
                "Longueur de base",
                "Largeur de base",
                "Hauteur"
            ],
            "Pyramide à base triangulaire": [
                "Base du triangle",
                "Hauteur du triangle",
                "Hauteur de pyramide"
            ],
            "Pyramide à base pentagonale": [
                "Côté du pentagone",
                "Hauteur"
            ],
            "Pyramide à base hexagonale": [
                "Côté de l'hexagone",
                "Hauteur"
            ],

            "Tronc de pyramide à base carrée": [
                "Grand côté",
                "Petit côté",
                "Hauteur"
            ],
            "Tas de cailloux (tronc de pyramide rectangulaire)": [
                "Grande longueur",
                "Grande largeur",
                "Petite longueur",
                "Petite largeur",
                "Hauteur"
            ],

            "Sphère": ["Rayon"],
            "Demi-sphère": ["Rayon"],
            "Ellipsoïde": [
                "Demi-axe a",
                "Demi-axe b",
                "Demi-axe c"
            ]
        }

        self.dimensions = {}

        for i, nom in enumerate(liste_champs.get(figure, [])):
            ligne = i // 3
            colonne = (i % 3) * 2

            ttk.Label(
                self.zone_champs,
                text=nom + " :"
            ).grid(
                row=ligne,
                column=colonne,
                sticky="w",
                padx=5,
                pady=5
            )

            variable = tk.StringVar()
            ttk.Entry(
                self.zone_champs,
                textvariable=variable,
                width=15
            ).grid(
                row=ligne,
                column=colonne + 1,
                sticky="w",
                padx=5,
                pady=5
            )

            self.dimensions[nom] = variable

        self.ecrire_resultat(
            "Saisis toutes les dimensions, le nombre n, "
            "puis clique sur Calculer."
        )

    def ecrire_resultat(self, texte):
        self.resultat_geo.configure(state="normal")
        self.resultat_geo.delete("1.0", "end")
        self.resultat_geo.insert("end", texte)
        self.resultat_geo.configure(state="disabled")

    def lire_dimensions(self):
        valeurs = {}

        for nom, variable in self.dimensions.items():
            valeur = float(variable.get().replace(",", "."))

            if valeur <= 0:
                raise ValueError(
                    "Toutes les dimensions doivent être positives."
                )

            valeurs[nom] = valeur

        return valeurs

    def calculer(self):
        try:
            d = self.lire_dimensions()
            n = int(self.var_n.get())

            if n < 1:
                raise ValueError(
                    "Le nombre n doit être un entier supérieur ou égal à 1."
                )

            f = self.figure.get()
            pi = math.pi
            surface = 0.0
            volume = 0.0
            formules = []

            # FIGURES PLANES

            if f == "Carré":
                a = d["Côté"]
                surface = a ** 2
                formules.append("Aire = côté²")

            elif f == "Rectangle":
                L, l = d["Longueur"], d["Largeur"]
                surface = L * l
                formules.append("Aire = longueur × largeur")

            elif f == "Triangle":
                b, h = d["Base"], d["Hauteur"]
                surface = b * h / 2
                formules.append("Aire = base × hauteur / 2")

            elif f == "Trapèze":
                B = d["Grande base"]
                b = d["Petite base"]
                h = d["Hauteur"]
                surface = (B + b) * h / 2
                formules.append(
                    "Aire = (grande base + petite base) × hauteur / 2"
                )

            elif f == "Parallélogramme":
                surface = d["Base"] * d["Hauteur"]
                formules.append("Aire = base × hauteur")

            elif f == "Disque":
                r = d["Rayon"]
                surface = pi * r ** 2
                formules.append("Aire = π × rayon²")

            # SOLIDES SIMPLES

            elif f == "Cube":
                a = d["Côté"]
                volume = a ** 3
                surface = 6 * a ** 2
                formules.append("Volume = côté³")
                formules.append("Surface totale = 6 × côté²")

            elif f == "Pavé droit":
                L = d["Longueur"]
                l = d["Largeur"]
                h = d["Hauteur"]
                volume = L * l * h
                surface = 2 * (L*l + L*h + l*h)
                formules.append(
                    "Volume = longueur × largeur × hauteur"
                )

            elif f == "Prisme triangulaire":
                b = d["Base du triangle"]
                ht = d["Hauteur du triangle"]
                longueur = d["Longueur du prisme"]
                aire_base = b * ht / 2
                volume = aire_base * longueur
                surface = aire_base
                formules.append(
                    "Volume = aire triangulaire de base × longueur du prisme"
                )
                formules.append(
                    "Surface affichée = aire d'une base seulement"
                )

            elif f in ("Prisme pentagonal", "Prisme hexagonal"):
                if f == "Prisme pentagonal":
                    cote = d["Côté du pentagone"]
                    nb = 5
                else:
                    cote = d["Côté de l'hexagone"]
                    nb = 6

                h = d["Hauteur du prisme"]
                aire_base = nb * cote**2 / (4 * math.tan(pi / nb))
                volume = aire_base * h
                surface = aire_base
                formules.append(
                    "Aire du polygone régulier = n × côté² / (4 tan(π/n))"
                )
                formules.append(
                    "Surface affichée = aire d'une base seulement"
                )

            elif f == "Cylindre":
                r, h = d["Rayon"], d["Hauteur"]
                volume = pi * r**2 * h
                surface = 2 * pi * r * (r + h)
                formules.append("Volume = πr²h")

            elif f == "Cône":
                r, h = d["Rayon"], d["Hauteur"]
                g = math.sqrt(r**2 + h**2)
                volume = pi * r**2 * h / 3
                surface = pi * r * (r + g)
                formules.append("Volume = πr²h / 3")

            elif f == "Tronc de cône":
                R = d["Grand rayon"]
                r = d["Petit rayon"]
                h = d["Hauteur"]

                if r >= R:
                    raise ValueError(
                        "Le petit rayon doit être inférieur au grand rayon."
                    )

                g = math.sqrt(h**2 + (R-r)**2)
                volume = pi * h * (R**2 + R*r + r**2) / 3
                surface = pi*(R**2 + r**2) + pi*(R+r)*g
                formules.append("Volume = πh(R² + Rr + r²) / 3")

            # PYRAMIDES SIMPLES

            elif f.startswith("Pyramide à base"):
                if f == "Pyramide à base carrée":
                    a = d["Côté de la base"]
                    h = d["Hauteur"]
                    aire_base = a**2

                elif f == "Pyramide à base rectangulaire":
                    L = d["Longueur de base"]
                    l = d["Largeur de base"]
                    h = d["Hauteur"]
                    aire_base = L * l

                elif f == "Pyramide à base triangulaire":
                    b = d["Base du triangle"]
                    ht = d["Hauteur du triangle"]
                    h = d["Hauteur de pyramide"]
                    aire_base = b * ht / 2

                elif f == "Pyramide à base pentagonale":
                    a = d["Côté du pentagone"]
                    h = d["Hauteur"]
                    aire_base = 5 * a**2 / (4 * math.tan(pi/5))

                else:
                    a = d["Côté de l'hexagone"]
                    h = d["Hauteur"]
                    aire_base = 6 * a**2 / (4 * math.tan(pi/6))

                volume = aire_base * h / 3
                surface = aire_base
                formules.append("Volume = aire de base × hauteur / 3")
                formules.append(
                    "Surface affichée = aire de base seulement"
                )

            # TRONC DE PYRAMIDE À BASE CARRÉE

            elif f == "Tronc de pyramide à base carrée":
                B = d["Grand côté"]
                b = d["Petit côté"]
                h = d["Hauteur"]

                if b >= B:
                    raise ValueError(
                        "Le petit côté doit être inférieur au grand côté."
                    )

                A1 = B**2
                A2 = b**2

                # Volume exact du tronc droit à bases parallèles
                volume = h * (A1 + A2 + math.sqrt(A1*A2)) / 3

                # Surface latérale : 4 trapèzes isocèles
                hauteur_face = math.sqrt(h**2 + ((B-b)/2)**2)
                surface_laterale = 2 * (B+b) * hauteur_face
                surface = A1 + A2 + surface_laterale

                formules.append(
                    "V = h × (A1 + A2 + √(A1 × A2)) / 3"
                )
                formules.append(
                    "Surface totale = A1 + A2 + surface latérale"
                )

            # TAS DE CAILLOUX : TRONC DE PYRAMIDE RECTANGULAIRE

            elif f == "Tas de cailloux (tronc de pyramide rectangulaire)":
                L = d["Grande longueur"]
                W = d["Grande largeur"]
                l = d["Petite longueur"]
                w = d["Petite largeur"]
                h = d["Hauteur"]

                if l >= L or w >= W:
                    raise ValueError(
                        "La petite base doit avoir une longueur et une "
                        "largeur inférieures à celles de la grande base."
                    )

                A1 = L * W
                A2 = l * w

                # Volume d'un tas assimilé à un tronc de pyramide
                volume = h * (
                    A1 + A2 + math.sqrt(A1*A2)
                ) / 3

                # Hypothèse : tronc droit centré, bases parallèles
                pente_longueur = math.sqrt(
                    h**2 + ((W-w)/2)**2
                )
                pente_largeur = math.sqrt(
                    h**2 + ((L-l)/2)**2
                )

                surface_laterale = (
                    (L+l) * pente_longueur
                    + (W+w) * pente_largeur
                )

                surface = A1 + A2 + surface_laterale

                formules.append(
                    "V = h × (A1 + A2 + √(A1 × A2)) / 3"
                )
                formules.append(
                    "A1 = grande longueur × grande largeur"
                )
                formules.append(
                    "A2 = petite longueur × petite largeur"
                )
                formules.append(
                    "Modèle : tas assimilé à un tronc droit centré "
                    "à bases rectangulaires parallèles."
                )

            # SPHÈRE, DEMI-SPHÈRE, ELLIPSOÏDE

            elif f == "Sphère":
                r = d["Rayon"]
                volume = 4 * pi * r**3 / 3
                surface = 4 * pi * r**2
                formules.append("Volume = 4πr³ / 3")

            elif f == "Demi-sphère":
                r = d["Rayon"]
                volume = 2 * pi * r**3 / 3
                surface = 3 * pi * r**2
                formules.append(
                    "Volume = 2πr³ / 3 ; surface avec base plane = 3πr²"
                )

            elif f == "Ellipsoïde":
                a = d["Demi-axe a"]
                b = d["Demi-axe b"]
                c = d["Demi-axe c"]

                volume = 4 * pi * a * b * c / 3
                surface = 4 * pi * (
                    ((a*b)**1.6 + (a*c)**1.6 + (b*c)**1.6) / 3
                )**(1/1.6)
                formules.append("Volume = 4πabc / 3")
                formules.append(
                    "Surface = approximation de Knud Thomsen"
                )

            self.volume_unitaire = volume
            self.nombre_parts = n

            texte = f"Figure : {f}\n\n"
            texte += "\n".join(formules) + "\n\n"

            if surface > 0:
                texte += f"Surface calculée : {surface:.4f} unité²\n"

            if volume > 0:
                texte += f"Volume d'une partie : {volume:.4f} unité³\n"
                texte += f"Nombre de parties n : {n}\n"
                texte += f"Volume total = n × V : {n*volume:.4f} unité³\n"

            texte += "\nToutes les dimensions doivent utiliser la même unité."

            if "Tas de cailloux" in f:
                texte += (
                    "\n\nAttention : un tas réel est souvent irrégulier. "
                    "Le résultat est une estimation basée sur le modèle "
                    "géométrique choisi."
                )

            self.ecrire_resultat(texte)
            self.actualiser_materiaux()

        except (ValueError, ZeroDivisionError) as erreur:
            messagebox.showerror("Erreur de saisie", str(erreur))

    # ---------------- MATÉRIAUX ----------------

    def creer_materiaux(self):
        ttk.Label(
            self.page_mat,
            text="Quantités de matériaux selon tes dosages",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=5)

        form = ttk.Frame(self.page_mat)
        form.pack(fill="x", pady=8)

        self.nom_materiau = tk.StringVar()
        self.unite_materiau = tk.StringVar(value="kg")
        self.dosage_materiau = tk.StringVar()
        self.volume_reference = tk.StringVar(value="1")

        champs = [
            ("Nom du matériau", self.nom_materiau),
            ("Unité", self.unite_materiau),
            ("Dosage que tu définis", self.dosage_materiau),
            ("Volume de référence", self.volume_reference)
        ]

        for i, (label, variable) in enumerate(champs):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="w", padx=5, pady=4
            )
            ttk.Entry(
                form, textvariable=variable, width=28
            ).grid(row=i, column=1, sticky="w", padx=5, pady=4)

        ttk.Button(
            form,
            text="Ajouter le matériau",
            command=self.ajouter_materiau
        ).grid(row=4, column=0, columnspan=2, pady=8)

        self.table_materiaux = ttk.Treeview(
            self.page_mat,
            columns=("nom", "unite", "dosage", "reference", "quantite"),
            show="headings"
        )

        colonnes = [
            ("nom", "Matériau"),
            ("unite", "Unité"),
            ("dosage", "Dosage saisi"),
            ("reference", "Volume de référence"),
            ("quantite", "Quantité calculée")
        ]

        for col, titre in colonnes:
            self.table_materiaux.heading(col, text=titre)
            self.table_materiaux.column(col, width=150)

        self.table_materiaux.pack(fill="both", expand=True, pady=8)

        ttk.Button(
            self.page_mat,
            text="Actualiser les quantités",
            command=self.actualiser_materiaux
        ).pack(anchor="w")

    def ajouter_materiau(self):
        try:
            nom = self.nom_materiau.get().strip()
            unite = self.unite_materiau.get().strip()
            dosage = float(
                self.dosage_materiau.get().replace(",", ".")
            )
            reference = float(
                self.volume_reference.get().replace(",", ".")
            )

            if not nom or not unite:
                raise ValueError("Saisis le nom et l'unité du matériau.")

            if dosage < 0 or reference <= 0:
                raise ValueError(
                    "Le dosage doit être positif ou nul et le volume "
                    "de référence strictement positif."
                )

            self.materiaux.append({
                "nom": nom,
                "unite": unite,
                "dosage": dosage,
                "reference": reference
            })

            self.actualiser_materiaux()
            self.nom_materiau.set("")
            self.dosage_materiau.set("")

        except ValueError as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def actualiser_materiaux(self):
        if not hasattr(self, "table_materiaux"):
            return

        for item in self.table_materiaux.get_children():
            self.table_materiaux.delete(item)

        volume_total = self.volume_unitaire * self.nombre_parts

        for materiau in self.materiaux:
            quantite = (
                materiau["dosage"] * volume_total
                / materiau["reference"]
            )

            self.table_materiaux.insert(
                "", "end",
                values=(
                    materiau["nom"],
                    materiau["unite"],
                    materiau["dosage"],
                    materiau["reference"],
                    round(quantite, 4)
                )
            )

    # ---------------- DEVIS ----------------

    def creer_devis(self):
        ttk.Label(
            self.page_devis,
            text="Devis estimatif",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=5)

        form = ttk.Frame(self.page_devis)
        form.pack(fill="x", pady=8)

        self.nom_devis = tk.StringVar()
        self.unite_devis = tk.StringVar(value="kg")
        self.quantite_devis = tk.StringVar()
        self.prix_unitaire = tk.StringVar()

        champs = [
            ("Nom du matériau", self.nom_devis),
            ("Unité", self.unite_devis),
            ("Quantité", self.quantite_devis),
            ("Prix unitaire", self.prix_unitaire),
            ("Devise (DH, FCFA, etc.)", self.devise)
        ]

        for i, (label, variable) in enumerate(champs):
            ttk.Label(form, text=label).grid(
                row=i, column=0, sticky="w", padx=5, pady=4
            )
            ttk.Entry(
                form, textvariable=variable, width=28
            ).grid(row=i, column=1, sticky="w", padx=5, pady=4)

        ttk.Button(
            form,
            text="Ajouter au devis",
            command=self.ajouter_devis
        ).grid(row=5, column=0, columnspan=2, pady=8)

        self.table_devis = ttk.Treeview(
            self.page_devis,
            columns=("nom", "unite", "quantite", "prix", "montant"),
            show="headings"
        )

        for col, titre in [
            ("nom", "Matériau"),
            ("unite", "Unité"),
            ("quantite", "Quantité"),
            ("prix", "Prix unitaire"),
            ("montant", "Montant")
        ]:
            self.table_devis.heading(col, text=titre)
            self.table_devis.column(col, width=145)

        self.table_devis.pack(fill="both", expand=True, pady=8)

        self.label_total = ttk.Label(
            self.page_devis,
            text="Total : 0",
            font=("Arial", 13, "bold")
        )
        self.label_total.pack(anchor="e", pady=6)

        boutons = ttk.Frame(self.page_devis)
        boutons.pack(fill="x")

        ttk.Button(
            boutons,
            text="Actualiser le total",
            command=self.actualiser_total
        ).pack(side="left", padx=5)

        ttk.Button(
            boutons,
            text="Exporter en CSV",
            command=self.exporter_csv
        ).pack(side="left", padx=5)

    def ajouter_devis(self):
        try:
            nom = self.nom_devis.get().strip()
            unite = self.unite_devis.get().strip()
            quantite = float(
                self.quantite_devis.get().replace(",", ".")
            )
            prix = float(
                self.prix_unitaire.get().replace(",", ".")
            )

            if not nom or not unite:
                raise ValueError("Saisis le nom et l'unité.")

            if quantite < 0 or prix < 0:
                raise ValueError(
                    "La quantité et le prix doivent être positifs ou nuls."
                )

            article = {
                "nom": nom,
                "unite": unite,
                "quantite": quantite,
                "prix": prix
            }

            self.devis.append(article)

            self.table_devis.insert(
                "", "end",
                values=(
                    nom,
                    unite,
                    quantite,
                    prix,
                    round(quantite * prix, 2)
                )
            )

            self.actualiser_total()
            self.nom_devis.set("")
            self.quantite_devis.set("")
            self.prix_unitaire.set("")

        except ValueError as erreur:
            messagebox.showerror("Erreur", str(erreur))

    def actualiser_total(self):
        total = sum(
            article["quantite"] * article["prix"]
            for article in self.devis
        )

        self.label_total.configure(
            text=f"Total : {total:.2f} {self.devise.get()}"
        )

    def exporter_csv(self):
        chemin = filedialog.asksaveasfilename(
            title="Enregistrer le devis",
            defaultextension=".csv",
            filetypes=[("Fichier CSV", "*.csv")]
        )

        if not chemin:
            return

        try:
            with open(
                chemin, "w", newline="", encoding="utf-8-sig"
            ) as fichier:
                writer = csv.writer(fichier, delimiter=";")

                writer.writerow([
                    "Matériau", "Unité", "Quantité",
                    "Prix unitaire", "Montant"
                ])

                for article in self.devis:
                    writer.writerow([
                        article["nom"],
                        article["unite"],
                        article["quantite"],
                        article["prix"],
                        article["quantite"] * article["prix"]
                    ])

                total = sum(
                    article["quantite"] * article["prix"]
                    for article in self.devis
                )

                writer.writerow([])
                writer.writerow(["Devise", self.devise.get()])
                writer.writerow(["TOTAL", total])

            messagebox.showinfo(
                "Export terminé",
                "Le devis a été exporté en CSV."
            )

        except OSError as erreur:
            messagebox.showerror("Erreur d'export", str(erreur))


def main():
    root = tk.Tk()
    BatiIA(root)
    root.mainloop()


if __name__ == "__main__":
    main()