from flask import Flask, request, session, render_template_string, send_file
from math import pi, sqrt
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)

app = Flask(__name__)
app.secret_key = "bati-ia-cle-locale-a-changer"


# =========================================================
# OUTILS DE CALCUL
# =========================================================

def number(value, default=0):
    try:
        result = float(value)
        if result < 0:
            return default
        return result
    except (TypeError, ValueError):
        return default


def fmt(value):
    return f"{value:,.3f}".replace(",", " ").replace(".", ",")


def calculate_shape(shape, a, b, c):
    """Retourne volume, surface, formule et dimensions."""

    volume = 0.0
    area = 0.0
    formula = ""

    if shape == "cube":
        volume = a ** 3
        area = 6 * a ** 2
        formula = "V = a³ ; S = 6 × a²"

    elif shape == "pave":
        volume = a * b * c
        area = 2 * (a*b + a*c + b*c)
        formula = "V = L × l × h ; S = 2(Ll + Lh + lh)"

    elif shape == "cylinder":
        volume = pi * a**2 * b
        area = 2 * pi * a * (a + b)
        formula = "V = π × r² × h ; S = 2πr(r + h)"

    elif shape == "cone":
        volume = pi * a**2 * b / 3
        slant = sqrt(a**2 + b**2)
        area = pi * a * (a + slant)
        formula = "V = π × r² × h / 3"

    elif shape == "tri_prism":
        # a = base du triangle, b = hauteur du triangle,
        # c = longueur du prisme.
        volume = (a * b / 2) * c
        side = sqrt((a / 2)**2 + b**2)
        area = a*b + c*(a + 2*side)
        formula = "V = (base × hauteur du triangle / 2) × longueur"

    elif shape == "square_pyramid":
        # a = côté de base ; b = hauteur verticale.
        volume = a**2 * b / 3
        slant = sqrt((a/2)**2 + b**2)
        area = a**2 + 2*a*slant
        formula = "V = côté² × hauteur / 3"

    elif shape == "rect_pyramid":
        # a = longueur de base, b = largeur de base,
        # c = hauteur verticale.
        volume = a * b * c / 3
        slant_a = sqrt(c**2 + (b/2)**2)
        slant_b = sqrt(c**2 + (a/2)**2)
        area = a*b + a*slant_a + b*slant_b
        formula = "V = longueur × largeur × hauteur / 3"

    elif shape == "sphere":
        volume = 4 * pi * a**3 / 3
        area = 4 * pi * a**2
        formula = "V = 4πr³ / 3 ; S = 4πr²"

    elif shape == "hemisphere":
        volume = 2 * pi * a**3 / 3
        area = 3 * pi * a**2
        formula = "V = 2πr³ / 3 ; S totale = 3πr²"

    elif shape == "cone_frustum":
        # a = rayon inférieur ; b = rayon supérieur ; c = hauteur.
        volume = pi*c*(a**2 + a*b + b**2)/3
        slant = sqrt(c**2 + (a-b)**2)
        area = pi*(a+b)*slant + pi*a**2 + pi*b**2
        formula = "V = πh(R² + Rr + r²) / 3"

    elif shape == "rectangle_area":
        area = a * b
        formula = "S = longueur × largeur"

    elif shape == "square_area":
        area = a**2
        formula = "S = côté²"

    elif shape == "triangle_area":
        area = a * b / 2
        formula = "S = base × hauteur / 2"

    elif shape == "trapezoid_area":
        # a et b = côtés parallèles ; c = hauteur.
        area = (a+b)*c/2
        formula = "S = (grande base + petite base) × hauteur / 2"

    elif shape == "circle_area":
        area = pi * a**2
        formula = "S = πr²"

    return {
        "volume_one": volume,
        "area_one": area,
        "formula": formula
    }


SHAPES = {
    "cube": "Cube",
    "pave": "Pavé droit",
    "cylinder": "Cylindre",
    "cone": "Cône",
    "tri_prism": "Prisme à base triangulaire",
    "square_pyramid": "Pyramide à base carrée",
    "rect_pyramid": "Pyramide à base rectangulaire",
    "sphere": "Sphère",
    "hemisphere": "Demi-sphère",
    "cone_frustum": "Tronc de cône",
    "rectangle_area": "Rectangle — surface",
    "square_area": "Carré — surface",
    "triangle_area": "Triangle — surface",
    "trapezoid_area": "Trapèze — surface",
    "circle_area": "Disque — surface",
}


# =========================================================
# LECTURE DU FORMULAIRE ET CALCULS
# =========================================================

def read_project(form):
    project_name = form.get("project_name", "").strip() or "Projet sans nom"
    client = form.get("client", "").strip() or "Non renseigné"
    unit_currency = form.get("currency", "DH").strip() or "DH"

    names = form.getlist("g_name[]")
    shapes = form.getlist("g_shape[]")
    counts = form.getlist("g_count[]")
    values_a = form.getlist("g_a[]")
    values_b = form.getlist("g_b[]")
    values_c = form.getlist("g_c[]")

    geometries = []

    for i in range(len(shapes)):
        shape = shapes[i] if shapes[i] in SHAPES else "pave"
        name = names[i].strip() if i < len(names) else ""
        a = number(values_a[i] if i < len(values_a) else 0)
        b = number(values_b[i] if i < len(values_b) else 0)
        c = number(values_c[i] if i < len(values_c) else 0)
        count = max(1, int(number(counts[i] if i < len(counts) else 1, 1)))

        result = calculate_shape(shape, a, b, c)
        geometries.append({
            "name": name or SHAPES[shape],
            "shape": shape,
            "shape_label": SHAPES[shape],
            "a": a, "b": b, "c": c,
            "count": count,
            "volume_one": result["volume_one"],
            "area_one": result["area_one"],
            "volume_total": result["volume_one"] * count,
            "area_total": result["area_one"] * count,
            "formula": result["formula"]
        })

    total_volume = sum(g["volume_total"] for g in geometries)
    total_area = sum(g["area_total"] for g in geometries)
    total_parts = sum(g["count"] for g in geometries)

    material_names = form.getlist("m_name[]")
    material_units = form.getlist("m_unit[]")
    material_bases = form.getlist("m_basis[]")
    dosages = form.getlist("m_dosage[]")
    wastes = form.getlist("m_waste[]")
    material_prices = form.getlist("m_price[]")

    materials = []

    for i in range(len(material_names)):
        name = material_names[i].strip()
        if not name:
            continue

        unit = material_units[i] if i < len(material_units) else "unité"
        basis = material_bases[i] if i < len(material_bases) else "m3"
        dosage = number(dosages[i] if i < len(dosages) else 0)
        waste = number(wastes[i] if i < len(wastes) else 0)
        price = number(material_prices[i] if i < len(material_prices) else 0)

        details = []
        installed = 0.0

        for g in geometries:
            if basis == "m3":
                base_quantity = g["volume_total"]
            elif basis == "m2":
                base_quantity = g["area_total"]
            else:
                base_quantity = g["count"]

            quantity = base_quantity * dosage
            installed += quantity

            details.append({
                "geometry": g["name"],
                "base_quantity": base_quantity,
                "quantity": quantity
            })

        purchase = installed * (1 + waste/100)
        cost = purchase * price

        materials.append({
            "name": name,
            "unit": unit,
            "basis": basis,
            "dosage": dosage,
            "waste": waste,
            "price": price,
            "details": details,
            "installed": installed,
            "purchase": purchase,
            "cost": cost
        })

    cost_names = form.getlist("c_name[]")
    cost_quantities = form.getlist("c_qty[]")
    cost_units = form.getlist("c_unit[]")
    cost_prices = form.getlist("c_price[]")

    other_costs = []

    for i in range(len(cost_names)):
        name = cost_names[i].strip()
        if not name:
            continue

        qty = number(cost_quantities[i] if i < len(cost_quantities) else 0)
        unit = cost_units[i] if i < len(cost_units) else "forfait"
        price = number(cost_prices[i] if i < len(cost_prices) else 0)

        other_costs.append({
            "name": name,
            "quantity": qty,
            "unit": unit,
            "price": price,
            "total": qty * price
        })

    material_total = sum(m["cost"] for m in materials)
    other_total = sum(c["total"] for c in other_costs)
    grand_total = material_total + other_total

    return {
        "project_name": project_name,
        "client": client,
        "currency": unit_currency,
        "date": datetime.now().strftime("%d/%m/%Y"),
        "geometries": geometries,
        "materials": materials,
        "other_costs": other_costs,
        "total_volume": total_volume,
        "total_area": total_area,
        "total_parts": total_parts,
        "material_total": material_total,
        "other_total": other_total,
        "grand_total": grand_total
    }


# =========================================================
# INTERFACE WEB
# =========================================================

PAGE = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BATI-IA | Calculs et devis BTP</title>
<style>
:root {
 --navy:#132b46; --blue:#1769aa; --orange:#f5a623;
 --bg:#f3f6fa; --white:#fff; --text:#263548; --muted:#66758a;
 --line:#dce4ee; --green:#16845b;
}
* {box-sizing:border-box}
body {margin:0;background:var(--bg);color:var(--text);
 font-family:Arial,Helvetica,sans-serif;line-height:1.5}
header {background:var(--navy);color:white;padding:16px 5%;
 display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
.logo {font-size:25px;font-weight:900;letter-spacing:1px}
.logo span {color:var(--orange)}
nav {display:flex;gap:16px;flex-wrap:wrap}
nav a {color:white;text-decoration:none;font-weight:bold;font-size:14px}
.hero {padding:48px 6%;color:white;
 background:linear-gradient(90deg,rgba(9,29,49,.92),rgba(9,29,49,.45)),
 url('https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=1600&q=80')
 center/cover}
.hero h1 {font-size:clamp(30px,5vw,48px);margin:0 0 12px}
.hero p {max-width:700px;font-size:17px}
.container {max-width:1200px;margin:25px auto;padding:0 15px}
.card {background:white;border:1px solid var(--line);border-radius:14px;
 padding:22px;margin-bottom:22px;box-shadow:0 5px 18px #10243b0b}
h2 {margin-top:0;color:var(--navy)}
h3 {color:var(--navy);margin-bottom:10px}
label {display:block;font-size:13px;font-weight:bold;margin-bottom:5px}
input,select {width:100%;padding:11px;border:1px solid #cbd5e1;
 border-radius:8px;background:white;color:var(--text);font-size:14px}
input:focus,select:focus {outline:2px solid #b6d7f5;border-color:var(--blue)}
.grid {display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:13px}
.entry {border:1px solid var(--line);border-radius:10px;padding:14px;margin:12px 0;
 background:#fbfdff}
.entry-title {display:flex;justify-content:space-between;align-items:center;gap:10px}
.btn {display:inline-block;border:0;border-radius:8px;padding:12px 17px;
 font-weight:bold;cursor:pointer;text-decoration:none;font-size:14px}
.primary {background:var(--blue);color:white}
.orange {background:var(--orange);color:#1d2939}
.dark {background:var(--navy);color:white}
.light {background:#e9f1f9;color:var(--navy)}
.remove {background:#fee2e2;color:#991b1b;padding:7px 10px}
.actions {display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
table {width:100%;border-collapse:collapse;font-size:13px;margin:12px 0}
th,td {padding:10px;border:1px solid var(--line);text-align:left}
th {background:#eaf1f8;color:var(--navy)}
.table-wrap {overflow-x:auto}
.metrics {display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.metric {padding:18px;border-radius:10px;background:#eef5fc}
.metric small {color:var(--muted)}
.metric strong {display:block;font-size:22px;color:var(--navy);margin-top:5px}
.notice {padding:13px;border-radius:8px;background:#fff7e5;color:#75500b}
.success {padding:13px;border-radius:8px;background:#e6f7ee;color:#176a49}
footer {background:var(--navy);color:white;text-align:center;padding:24px;margin-top:35px}
.muted {color:var(--muted);font-size:13px}
@media(max-width:600px) {
 .card {padding:15px}.hero {padding:34px 6%}
 nav {gap:10px}.actions .btn {width:100%;text-align:center}
}
</style>
</head>
<body>
<header>
 <div class="logo">BATI<span>-IA</span></div>
 <nav>
  <a href="#geometrie">Géométrie</a>
  <a href="#materiaux">Matériaux</a>
  <a href="#couts">Coûts</a>
  <a href="#resultats">Résultats</a>
 </nav>
</header>
<section class="hero">
 <h1>Le calcul BTP, plus simple.</h1>
 <p>Calcule les volumes et les surfaces, estime tes matériaux selon tes propres dosages
 et prépare des documents professionnels pour tes projets.</p>
 <a class="btn orange" href="#projet">Commencer un calcul</a>
</section>

<div class="container">
<form method="post" action="/">
<section class="card" id="projet">
 <h2>01 — Informations du projet</h2>
 <div class="grid">
  <div><label>Nom du projet</label><input name="project_name" placeholder="Ex. Construction d'une maison" required></div>
  <div><label>Client / maître d'ouvrage</label><input name="client" placeholder="Nom du client"></div>
  <div><label>Devise</label>
   <select name="currency"><option>DH</option><option>FCFA</option><option>EUR</option></select>
  </div>
 </div>
</section>

<section class="card" id="geometrie">
 <h2>02 — Géométrie et quantités</h2>
 <p class="muted">Entre les dimensions en mètres. Pour une surface, le volume restera nul.
 Le nombre de parties multiplie le résultat d'un seul solide.</p>
 <div id="geometryRows">
  <div class="entry geometry-row">
   <div class="entry-title"><h3>Élément géométrique</h3><button type="button" class="btn remove" onclick="removeRow(this)">Supprimer</button></div>
   <div class="grid">
    <div><label>Désignation</label><input name="g_name[]" placeholder="Ex. Semelle S1"></div>
    <div><label>Forme</label><select name="g_shape[]" onchange="updateDimensions(this)">
     <option value="pave">Pavé droit</option><option value="cube">Cube</option>
     <option value="cylinder">Cylindre</option><option value="cone">Cône</option>
     <option value="tri_prism">Prisme triangulaire</option>
     <option value="square_pyramid">Pyramide base carrée</option>
     <option value="rect_pyramid">Pyramide base rectangulaire</option>
     <option value="sphere">Sphère</option><option value="hemisphere">Demi-sphère</option>
     <option value="cone_frustum">Tronc de cône</option>
     <option value="rectangle_area">Rectangle — surface</option>
     <option value="square_area">Carré — surface</option>
     <option value="triangle_area">Triangle — surface</option>
     <option value="trapezoid_area">Trapèze — surface</option>
     <option value="circle_area">Disque — surface</option>
    </select></div>
    <div><label>Nombre de parties (n)</label><input name="g_count[]" type="number" min="1" step="1" value="1" required></div>
   </div>
   <div class="grid dimensions">
    <div><label class="la">Longueur / rayon / côté a (m)</label><input name="g_a[]" type="number" min="0" step="any" value="1" required></div>
    <div><label class="lb">Largeur / hauteur b (m)</label><input name="g_b[]" type="number" min="0" step="any" value="1"></div>
    <div><label class="lc">Hauteur c (m)</label><input name="g_c[]" type="number" min="0" step="any" value="1"></div>
   </div>
   <p class="muted dim-help">a, b et c sont interprétés selon la forme sélectionnée.</p>
  </div>
 </div>
 <button type="button" class="btn light" onclick="addGeometry()">+ Ajouter un solide ou une surface</button>
</section>

<section class="card" id="materiaux">
 <h2>03 — Matériaux et dosages</h2>
 <div class="notice">Tu définis toi-même le dosage. BATI-IA ne choisit pas automatiquement le dosage du béton,
 du mortier ou d'un autre matériau. Vérifie les unités et les spécifications de ton projet.</div>
 <div id="materialRows">
  <div class="entry material-row">
   <div class="entry-title"><h3>Matériau</h3><button type="button" class="btn remove" onclick="removeRow(this)">Supprimer</button></div>
   <div class="grid">
    <div><label>Nom du matériau</label><input name="m_name[]" placeholder="Ex. Ciment"></div>
    <div><label>Unité d'achat</label><input name="m_unit[]" value="sac"></div>
    <div><label>Base de calcul</label><select name="m_basis[]">
     <option value="m3">Par m³ de volume</option><option value="m2">Par m² de surface</option>
     <option value="part">Par partie / élément</option></select></div>
    <div><label>Dosage par unité de base</label><input name="m_dosage[]" type="number" min="0" step="any" value="0"></div>
    <div><label>Pertes prévues (%)</label><input name="m_waste[]" type="number" min="0" step="any" value="0"></div>
    <div><label>Prix par unité (devise choisie)</label><input name="m_price[]" type="number" min="0" step="any" value="0"></div>
   </div>
  </div>
 </div>
 <button type="button" class="btn light" onclick="addMaterial()">+ Ajouter un matériau</button>
</section>

<section class="card" id="couts">
 <h2>04 — Main-d'œuvre et autres coûts</h2>
 <p class="muted">Ajoute la main-d'œuvre, le transport, la location ou tout autre poste.
 Le montant est calculé par quantité × prix unitaire.</p>
 <div id="costRows">
  <div class="entry cost-row">
   <div class="entry-title"><h3>Poste de dépense</h3><button type="button" class="btn remove" onclick="removeRow(this)">Supprimer</button></div>
   <div class="grid">
    <div><label>Désignation</label><input name="c_name[]" placeholder="Ex. Main-d'œuvre"></div>
    <div><label>Quantité</label><input name="c_qty[]" type="number" min="0" step="any" value="0"></div>
    <div><label>Unité</label><input name="c_unit[]" value="forfait"></div>
    <div><label>Prix unitaire</label><input name="c_price[]" type="number" min="0" step="any" value="0"></div>
   </div>
  </div>
 </div>
 <button type="button" class="btn light" onclick="addCost()">+ Ajouter un poste de dépense</button>
</section>

<div class="card">
 <h2>05 — Calculer et enregistrer</h2>
 <p class="muted">Enregistre les données de cette session pour afficher les résultats et générer les PDF.</p>
 <button type="submit" class="btn primary">Calculer tous les résultats</button>
</div>
</form>

{% if data %}
<section class="card" id="resultats">
 <h2>Résultats du projet : {{ data.project_name }}</h2>
 <div class="success">Calcul terminé. Tu peux télécharger le rapport de calcul ou le devis PDF ci-dessous.</div>
 <div class="metrics" style="margin-top:15px">
  <div class="metric"><small>Volume total</small><strong>{{ fmt(data.total_volume) }} m³</strong></div>
  <div class="metric"><small>Surface totale</small><strong>{{ fmt(data.total_area) }} m²</strong></div>
  <div class="metric"><small>Nombre de parties</small><strong>{{ data.total_parts }}</strong></div>
  <div class="metric"><small>Coût estimatif total</small><strong>{{ fmt(data.grand_total) }} {{ data.currency }}</strong></div>
 </div>

 <h3>Détail géométrique</h3>
 <div class="table-wrap"><table>
 <tr><th>Désignation</th><th>Forme</th><th>n</th><th>Volume total (m³)</th><th>Surface totale (m²)</th></tr>
 {% for g in data.geometries %}
 <tr><td>{{ g.name }}</td><td>{{ g.shape_label }}</td><td>{{ g.count }}</td>
 <td>{{ fmt(g.volume_total) }}</td><td>{{ fmt(g.area_total) }}</td></tr>
 {% endfor %}
 </table></div>

 <h3>Matériaux</h3>
 <div class="table-wrap"><table>
 <tr><th>Matériau</th><th>Dosage</th><th>Quantité installée</th><th>Quantité à acheter</th><th>Prix unitaire</th><th>Coût</th></tr>
 {% for m in data.materials %}
 <tr><td>{{ m.name }}</td><td>{{ fmt(m.dosage) }} / {{ m.basis }}</td>
 <td>{{ fmt(m.installed) }} {{ m.unit }}</td><td>{{ fmt(m.purchase) }} {{ m.unit }}</td>
 <td>{{ fmt(m.price) }}</td><td>{{ fmt(m.cost) }} {{ data.currency }}</td></tr>
 {% endfor %}
 </table></div>

 <h3>Autres dépenses</h3>
 <div class="table-wrap"><table>
 <tr><th>Désignation</th><th>Quantité</th><th>Unité</th><th>Prix unitaire</th><th>Total</th></tr>
 {% for c in data.other_costs %}
 <tr><td>{{ c.name }}</td><td>{{ fmt(c.quantity) }}</td><td>{{ c.unit }}</td>
 <td>{{ fmt(c.price) }}</td><td>{{ fmt(c.total) }} {{ data.currency }}</td></tr>
 {% endfor %}
 </table></div>

 <div class="metrics">
  <div class="metric"><small>Total matériaux</small><strong>{{ fmt(data.material_total) }} {{ data.currency }}</strong></div>
  <div class="metric"><small>Total autres coûts</small><strong>{{ fmt(data.other_total) }} {{ data.currency }}</strong></div>
  <div class="metric"><small>Total général estimatif</small><strong>{{ fmt(data.grand_total) }} {{ data.currency }}</strong></div>
 </div>

 <div class="actions">
  <a class="btn primary" href="/pdf/rapport">Télécharger le rapport de calcul PDF</a>
  <a class="btn orange" href="/pdf/devis">Télécharger le devis PDF</a>
 </div>
 <p class="muted">Les résultats sont conservés dans la session du navigateur. Télécharge tes PDF avant de fermer la session.</p>
</section>
{% endif %}
</div>

<footer>
 <div class="logo">BATI<span>-IA</span></div>
 <p>Outil de calcul et d'estimation pour le BTP</p>
 <p>Réalisé par Moïse © 2026</p>
</footer>

<script>
function removeRow(button) {
 const row = button.closest('.entry');
 const parent = row.parentElement;
 if (parent.children.length > 1) row.remove();
 else alert("Garde au moins une ligne dans cette section.");
}

function addGeometry() {
 const container = document.getElementById('geometryRows');
 const row = container.querySelector('.geometry-row').cloneNode(true);
 row.querySelectorAll('input').forEach(input => {
   if (input.name === 'g_count[]') input.value = 1;
   else input.value = '';
 });
 row.querySelector('select[name="g_shape[]"]').value = 'pave';
 container.appendChild(row);
 updateDimensions(row.querySelector('select[name="g_shape[]"]'));
}

function addMaterial() {
 const container = document.getElementById('materialRows');
 const row = container.querySelector('.material-row').cloneNode(true);
 row.querySelectorAll('input').forEach(input => {
   if (input.name === 'm_unit[]') input.value = 'unité';
   else if (input.name === 'm_waste[]' || input.name === 'm_price[]' ||
            input.name === 'm_dosage[]') input.value = 0;
   else input.value = '';
 });
 container.appendChild(row);
}

function addCost() {
 const container = document.getElementById('costRows');
 const row = container.querySelector('.cost-row').cloneNode(true);
 row.querySelectorAll('input').forEach(input => {
   if (input.name === 'c_unit[]') input.value = 'forfait';
   else if (input.name === 'c_qty[]' || input.name === 'c_price[]') input.value = 0;
   else input.value = '';
 });
 container.appendChild(row);
}

function updateDimensions(select) {
 const row = select.closest('.geometry-row');
 const shape = select.value;
 const labels = row.querySelectorAll('.dimensions label');
 const inputs = row.querySelectorAll('.dimensions input');
 labels[0].textContent = 'Longueur / rayon / côté a (m)';
 labels[1].textContent = 'Largeur / hauteur b (m)';
 labels[2].textContent = 'Hauteur c (m)';

 if (['cube','square_area','circle_area','sphere','hemisphere'].includes(shape)) {
   labels[0].textContent = shape.includes('circle') || shape === 'sphere' ||
     shape === 'hemisphere' ? 'Rayon a (m)' : 'Côté a (m)';
   labels[1].textContent = 'Non utilisé';
   labels[2].textContent = 'Non utilisé';
 } else if (shape === 'cylinder' || shape === 'cone') {
   labels[0].textContent = 'Rayon a (m)';
   labels[1].textContent = 'Hauteur b (m)';
   labels[2].textContent = 'Non utilisé';
 } else if (shape === 'cone_frustum') {
   labels[0].textContent = 'Rayon inférieur a (m)';
   labels[1].textContent = 'Rayon supérieur b (m)';
   labels[2].textContent = 'Hauteur c (m)';
 } else if (shape === 'triangle_area') {
   labels[0].textContent = 'Base a (m)';
   labels[1].textContent = 'Hauteur b (m)';
   labels[2].textContent = 'Non utilisé';
 } else if (shape === 'trapezoid_area') {
   labels[0].textContent = 'Grande base a (m)';
   labels[1].textContent = 'Petite base b (m)';
   labels[2].textContent = 'Hauteur c (m)';
 } else if (shape === 'rectangle_area') {
   labels[0].textContent = 'Longueur a (m)';
   labels[1].textContent = 'Largeur b (m)';
   labels[2].textContent = 'Non utilisé';
 } else if (shape === 'square_pyramid') {
   labels[0].textContent = 'Côté de base a (m)';
   labels[1].textContent = 'Hauteur verticale b (m)';
   labels[2].textContent = 'Non utilisé';
 } else if (shape === 'rect_pyramid') {
   labels[0].textContent = 'Longueur de base a (m)';
   labels[1].textContent = 'Largeur de base b (m)';
   labels[2].textContent = 'Hauteur verticale c (m)';
 } else if (shape === 'tri_prism') {
   labels[0].textContent = 'Base du triangle a (m)';
   labels[1].textContent = 'Hauteur du triangle b (m)';
   labels[2].textContent = 'Longueur du prisme c (m)';
 }
}
document.querySelectorAll('.geometry-row select[name="g_shape[]"]').forEach(updateDimensions);
</script>
</body>
</html>
"""


# =========================================================
# CRÉATION DES PDF
# =========================================================

def make_pdf(data, document_type):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.6*cm, leftMargin=1.6*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle", parent=styles["Title"],
        fontName="Helvetica-Bold", fontSize=27, leading=33,
        textColor=colors.HexColor("#132b46"), alignment=TA_CENTER,
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", parent=styles["Heading2"],
        textColor=colors.HexColor("#1769aa"),
        spaceBefore=13, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name="SmallText", parent=styles["BodyText"],
        fontSize=8, leading=10
    ))

    story = []
    currency = data["currency"]
    is_report = document_type == "rapport"
    title = "RAPPORT DE CALCUL BTP" if is_report else "DEVIS ESTIMATIF BTP"

    story += [
        Spacer(1, 3.0*cm),
        Paragraph("BATI-IA", styles["CoverTitle"]),
        Paragraph(title, styles["Heading1"]),
        Spacer(1, 1.0*cm)
    ]

    cover_data = [
        ["Projet", data["project_name"]],
        ["Client / maître d'ouvrage", data["client"]],
        ["Date d'édition", data["date"]],
        ["Document préparé par", "Moïse"]
    ]
    cover = Table(cover_data, colWidths=[6*cm, 9*cm])
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eaf1f8")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#132b46")),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 10)
    ]))
    story += [
        cover, Spacer(1, 1.2*cm),
        Paragraph("Document généré par BATI-IA.", styles["BodyText"]),
        Paragraph("Les dimensions, dosages, prix et hypothèses doivent être vérifiés par l'utilisateur.",
                  styles["SmallText"]),
        PageBreak()
    ]

    def add_table(title_text, headers, rows, widths=None):
        story.append(Paragraph(title_text, styles["SectionTitle"]))
        if not rows:
            story.append(Paragraph("Aucune donnée renseignée.", styles["BodyText"]))
            return

        table_data = [headers] + rows
        table = Table(table_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#132b46")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.white, colors.HexColor("#f3f6fa")]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6)
        ]))
        story.append(table)
        story.append(Spacer(1, 8))

    if is_report:
        story.append(Paragraph("1. Synthèse géométrique", styles["SectionTitle"]))
        summary = [
            ["Volume total", fmt(data["total_volume"]) + " m³"],
            ["Surface totale", fmt(data["total_area"]) + " m²"],
            ["Nombre total de parties", str(data["total_parts"])]
        ]
        table = Table(summary, colWidths=[7*cm, 7*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#eaf1f8")),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#cbd5e1")),
            ("PADDING", (0,0), (-1,-1), 8)
        ]))
        story.append(table)

        geom_rows = []
        for g in data["geometries"]:
            geom_rows.append([
                g["name"], g["shape_label"], str(g["count"]),
                fmt(g["a"]), fmt(g["b"]), fmt(g["c"]),
                fmt(g["volume_one"]), fmt(g["volume_total"]),
                fmt(g["area_total"])
            ])
        add_table(
            "2. Détail des éléments géométriques",
            ["Désignation", "Forme", "n", "a", "b", "c",
             "V d'une partie", "V total", "S totale"],
            geom_rows,
            [2.5*cm, 2.2*cm, 0.7*cm, 1.0*cm, 1.0*cm,
             1.0*cm, 1.7*cm, 1.5*cm, 1.5*cm]
        )

        story.append(Paragraph("3. Formules et calculs détaillés", styles["SectionTitle"]))
        for g in data["geometries"]:
            dimensions = f"a = {fmt(g['a'])} m ; b = {fmt(g['b'])} m ; c = {fmt(g['c'])} m"
            text = (
                f"<b>{g['name']}</b> — {g['shape_label']}<br/>"
                f"Nombre de parties : n = {g['count']}<br/>"
                f"Dimensions : {dimensions}<br/>"
                f"Formule : {g['formula']}<br/>"
                f"Volume d'une partie : {fmt(g['volume_one'])} m³<br/>"
                f"Volume total : {fmt(g['volume_one'])} × {g['count']} = "
                f"{fmt(g['volume_total'])} m³<br/>"
                f"Surface totale : {fmt(g['area_one'])} × {g['count']} = "
                f"{fmt(g['area_total'])} m²"
            )
            story.append(KeepTogether([
                Paragraph(text, styles["BodyText"]), Spacer(1, 10)
            ]))

        material_rows = []
        for m in data["materials"]:
            material_rows.append([
                m["name"], m["basis"], fmt(m["dosage"]), fmt(m["installed"]),
                fmt(m["waste"]) + "%", fmt(m["purchase"]) + " " + m["unit"],
                fmt(m["price"]), fmt(m["cost"]) + " " + currency
            ])
        add_table(
            "4. Quantités de matériaux",
            ["Matériau", "Base", "Dosage", "Installé", "Pertes",
             "À acheter", "Prix unit.", "Coût"],
            material_rows,
            [2.5*cm, 1.2*cm, 1.3*cm, 1.5*cm, 1.2*cm,
             1.8*cm, 1.4*cm, 2.0*cm]
        )

        story.append(Paragraph("5. Détail des quantités par élément", styles["SectionTitle"]))
        for m in data["materials"]:
            story.append(Paragraph(
                f"<b>{m['name']}</b> — dosage {fmt(m['dosage'])} par {m['basis']}",
                styles["BodyText"]
            ))
            detail_rows = []
            for d in m["details"]:
                detail_rows.append([
                    d["geometry"], fmt(d["base_quantity"]), fmt(d["quantity"]) + " " + m["unit"]
                ])
            add_table(
                "Calcul par élément",
                ["Élément géométrique", "Base utilisée", "Quantité de matériau"],
                detail_rows,
                [7*cm, 4*cm, 5*cm]
            )

        other_rows = [[
            c["name"], fmt(c["quantity"]), c["unit"],
            fmt(c["price"]), fmt(c["total"]) + " " + currency
        ] for c in data["other_costs"]]
        add_table(
            "6. Main-d'œuvre et autres dépenses",
            ["Désignation", "Quantité", "Unité", "Prix unit.", "Montant"],
            other_rows, [5*cm, 2*cm, 2*cm, 3*cm, 4*cm]
        )

        totals = [
            ["Coût des matériaux", fmt(data["material_total"]) + " " + currency],
            ["Autres dépenses", fmt(data["other_total"]) + " " + currency],
            ["COÛT TOTAL ESTIMATIF", fmt(data["grand_total"]) + " " + currency]
        ]
        add_table("7. Récapitulatif financier", ["Désignation", "Montant"], totals,
                  [9*cm, 6*cm])

    else:
        story.append(Paragraph("Objet du devis", styles["SectionTitle"]))
        story.append(Paragraph(
            f"Estimation des quantités et des coûts pour le projet : {data['project_name']}.",
            styles["BodyText"]
        ))

        rows = []
        for m in data["materials"]:
            rows.append([
                "Matériau", m["name"], fmt(m["purchase"]), m["unit"],
                fmt(m["price"]), fmt(m["cost"])
            ])
        for c in data["other_costs"]:
            rows.append([
                "Prestation / dépense", c["name"], fmt(c["quantity"]), c["unit"],
                fmt(c["price"]), fmt(c["total"])
            ])

        add_table(
            "Détail estimatif",
            ["Type", "Désignation", "Quantité", "Unité", "Prix unitaire", "Montant"],
            rows,
            [2.5*cm, 4.0*cm, 2.0*cm, 1.5*cm, 2.5*cm, 3.0*cm]
        )

        totals = [
            ["Sous-total matériaux", fmt(data["material_total"]) + " " + currency],
            ["Sous-total prestations et autres coûts", fmt(data["other_total"]) + " " + currency],
            ["TOTAL ESTIMATIF", fmt(data["grand_total"]) + " " + currency]
        ]
        add_table("Récapitulatif du devis", ["Désignation", "Montant"], totals,
                  [9*cm, 6*cm])

        story.append(Spacer(1, 20))
        story.append(Paragraph(
            "Devis estimatif à valider avant engagement. Les prix, quantités, pertes et conditions "
            "d'exécution doivent être vérifiés. Ce document ne constitue pas une facture.",
            styles["SmallText"]
        ))

    def page_footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#dce4ee"))
        canvas.line(1.6*cm, 1.35*cm, A4[0]-1.6*cm, 1.35*cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#66758a"))
        canvas.drawString(1.6*cm, 0.9*cm, "BATI-IA — Réalisé par Moïse")
        canvas.drawRightString(A4[0]-1.6*cm, 0.9*cm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    buffer.seek(0)
    return buffer


# =========================================================
# ROUTES FLASK
# =========================================================

@app.route("/", methods=["GET", "POST"])
def home():
    data = None

    if request.method == "POST":
        data = read_project(request.form)
        session["bati_ia_data"] = data

    else:
        data = session.get("bati_ia_data")

    return render_template_string(PAGE, data=data, fmt=fmt)


@app.route("/pdf/<document_type>")
def download_pdf(document_type):
    if document_type not in ("rapport", "devis"):
        return "Type de document inconnu.", 404

    data = session.get("bati_ia_data")
    if not data:
        return (
            "Aucun calcul enregistré. Retourne sur la page BATI-IA, "
            "renseigne le projet puis clique sur « Calculer tous les résultats ».",
            400
        )

    pdf = make_pdf(data, document_type)
    project = "".join(
        ch if ch.isalnum() or ch in "-_" else "_"
        for ch in data["project_name"]
    )[:60]

    if document_type == "rapport":
        filename = f"BATI-IA_Rapport_{project}.pdf"
    else:
        filename = f"BATI-IA_Devis_{project}.pdf"

    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    print("BATI-IA démarre...")
    print("Ouvre ensuite : http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)