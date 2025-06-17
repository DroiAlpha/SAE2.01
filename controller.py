"""
Contrôleur de l'application Flask pour le site web sur les prélèvements d'eau
"""

#####################################################################
# IMPORTATION DES MODULES
#####################################################################

# ! Installer Flask-Caching depuis le terminal avec la commande : pip install flask-caching redis

from flask import Flask, render_template, request
import matplotlib
from flask_caching import Cache
import time
from graphiques import sns_horizontalbarplot, sns_pie, sns_courbe, histo_horiz
import Model.model as db
from Model.chroniques import *
import folium
from flask import jsonify

#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration de l'application Flask
app = Flask(__name__)

# Importation du serveur Redis hébergé sur la VM pour le cache

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = '10.10.41.217'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Utilisation du cache simple pour le développement local
app.config['CACHE_TYPE'] = 'SimpleCache'

cache = Cache(app)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

# Route pour tester si Redis fonctionne si ça fonctionne la page va montrer le même temps pendant 10 secondes puis changer
@app.route("/test_cache")
@cache.cached(timeout=10) 
def test_cache():
    return f"Time: {time.time()}"

#####################################################################
# ROUTES
#####################################################################

################################
# ACCUEIL
################################

# Route pour la page d'accueil "index.html"
@app.route("/")
def accueil():
    """
    Fonction de définition de l'adresse de la page d'accueil "index.html"
    """
    # Affichage du template
    return render_template(
        'index.html', 
        page_title="Accueil"
    )

################################
# TABLEAU DE BORD
################################

# Route pour la page de la carte des prélèvements en eau "tab_carte.html"

@app.route('/tableau-bord/carte-prelevements')
def tab_carte():
    """Renvoie la map avec les deux layers : les prélèvements et la heatmap"""
    return render_template(
        'carte.html',
        page_title="Tableau de bord",
        page_sub_title="Carte des prélèvements",
        sub_header_template="dashboard.html"
    )

@app.route('/api/map-data')
@cache.cached(timeout=500)
def get_map_data():
    """Api pour récupérer les données de la carte des prélèvements"""
    ouvrages = db.obtenir_info_ouvrage()
    heatmap_data = chroniques.donnees()
    
    prelevements = []
    for _, row in ouvrages.iterrows():
        try:
            lat = float(row['latitude'])
            lng = float(row['longitude'])
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                prelevements.append({
                    'lat': lat,
                    'lng': lng,
                    'name': str(row['nom_ouvrage'])[:50],
                    'code': str(row['code_ouvrage'])
                })
        except (ValueError, TypeError):
            continue
    
    heatmap_points = []
    for d in heatmap_data:
        try:
            lat = float(d['latitude'])
            lng = float(d['longitude'])
            vol = float(d.get('volume', 1))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                heatmap_points.append([lat, lng, vol])
        except (ValueError, TypeError):
            continue
    
    return jsonify({
        'prelevements': prelevements,
        'heatmap': heatmap_points
    })
    
# Route pour la page des graphiques sur les usages de l'eau "tab_usages.html"
@app.route('/tableau-bord/usages-eau', methods=['GET', 'POST'])
@cache.cached(timeout=10)
def tab_usages():
    chroniques = Chroniques()
    data = pd.DataFrame(chroniques.donnees())

    filters = {
        "annee": request.form.get("annee"),
        "libelle_usage": request.form.get("libelle_usage"),
        "nom_commune": request.form.get("nom_commune"),
        "libelle_departement": request.form.get("libelle_departement"),
        "nom_ouvrage": request.form.get("nom_ouvrage")
    } if request.method == 'POST' else None

    # Prepare filter lists for histo_horiz
    filter_cols = []
    filter_vals = []
    if filters:
        if filters["annee"]:
            filter_cols.append('annee')
            filter_vals.append(int(filters["annee"]))
        if filters["libelle_usage"]:
            filter_cols.append('libelle_usage')
            filter_vals.append(filters["libelle_usage"])
        if filters["nom_commune"]:
            filter_cols.append('nom_commune')
            filter_vals.append(filters["nom_commune"])
        if filters["libelle_departement"]:
            filter_cols.append('libelle_departement')
            filter_vals.append(filters["libelle_departement"])
        if filters["nom_ouvrage"]:
            filter_cols.append('nom_ouvrage')
            filter_vals.append(filters["nom_ouvrage"])

    if not data.empty:
        usage_counts = data['libelle_usage'].value_counts()
        diagramme_circulaire = f'data:image/png;base64,{sns_pie(usage_counts.values, usage_counts.index, "Répartition des usages")}'
        
        hist_data = data['libelle_departement'].value_counts().reset_index()
        hist_data.columns = ['dep', 'value']
        histogrammehorizon = f'data:image/png;base64,{sns_horizontalbarplot(hist_data, "dep", "value", "Nombre d ouvrages", "Départements", "Nombre d ouvrages par département")}'
        
        # Corrected histo_horiz call
        histo_img = histo_horiz(filter_cols if filter_cols else None, 
                               filter_vals if filter_vals else None)
        volumes_usage_milieu = f'data:image/png;base64,{histo_img}' if histo_img else None
        
    else:
        diagramme_circulaire = None
        histogrammehorizon = None
        volumes_usage_milieu = None
    
    return render_template(
        'tab_usages.html',
        diagramme_circulaire=diagramme_circulaire,
        histogrammehorizon=histogrammehorizon,
        volumes_usage_milieu=volumes_usage_milieu,
        filters=filters,
        available_years=sorted(data['annee'].unique()),
        available_usages=data['libelle_usage'].unique(),
        available_communes=data['nom_commune'].unique(),
        available_departements=data['libelle_departement'].unique(),
        available_ouvrages=data['nom_ouvrage'].unique(),
        page_title="Tableau de bord", 
        page_sub_title="Usages de l'eau",
        sub_header_template="dashboard.html"
    )


# Route pour la page du graphique sur évolution temporelle du volume d'eau prélevé "tab_evolution.html"
@cache.cached(timeout=300)
@app.route('/tableau-bord/evolution-temporelle', methods=['GET', 'POST'])
def tab_evolution():
    """
    Route pour la page du graphique sur évolution temporelle du volume d'eau prélevé "tab_evolution.html"
    Affiche un graphique linéaire multiple sur l'évolution des volumes d'eau prélevés pour un ouvrage spécifique
    Chaque ouvrage est représenté par une courbe, et l'utilisateur peut choisir l'ouvrage à afficher
    """

    chroniques = Chroniques()
    graphique = None
    nom_ouvrage = None

    if request.method == 'GET':
        nom_ouvrage = 'AUDELONCOURT'

    elif request.method == 'POST':
        nom_ouvrage = request.form.get("nom_ouvrage")

    if nom_ouvrage:
        donnees = chroniques.filtre_ouv(nom_ouvrage)
        if donnees:
            df = pd.DataFrame(donnees).sort_values(by='annee')
            graphique = sns_courbe(df)

    return render_template(
        'tab_evolution.html',
        graphique=graphique,
        nom_ouvrage=nom_ouvrage, 
        page_title="Tableau de bord", 
        page_sub_title="Évolution temporelle"
    )

################################
# JEUX DE DONNÉES
################################

# Route pour la page du jeu de données pour les chroniques "jeu_chroniques.html"
@app.route('/jeux-donnees/chroniques')
def jeu_chroniques():
    """
    Route pour la page du jeu de données pour les chroniques "jeu_chroniques.html"
    Affiche les données chroniques d'eau prélevée dans un tableau, avec des filtres pour affiner la recherche
    """
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_filtered_template(
        'jeu_chroniques.html',
        Chroniques().filtre,
        form_keys=["annee", "libelle_usage", "nom_commune", "libelle_departement", "nom_ouvrage"],
        data_type="chroniques",
        page_title="Jeux de données", 
        page_sub_title="Chroniques"
    )

# Route pour la page du jeu de données pour les points de prélèvement "jeu_points_prelevement.html"
@app.route('/jeux-donnees/points-prelevement')
def jeu_points_prelevement():
    """
    Route pour la page du jeu de données pour les points de prélèvement "jeu_points_prelevement.html"
    Affiche les points de prélèvement d'eau dans un tableau, avec des filtres pour affiner la recherche
    """
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_filtered_template(
        'jeu_points_prelevement.html',
        None,
        form_keys=["code_point", "nom_point", "nom_commune", "libelle_departement"],
        data_type="points_prelevement", 
        page_title="Jeux de données", 
        page_sub_title="Points de prélèvement"
    )

# Route pour la page du jeu de données pour les ouvrages "jeu_ouvrages.html"
@app.route('/jeux-donnees/ouvrages')
def jeu_ouvrages():
    """
    Route pour la page du jeu de données pour les ouvrages "jeu_ouvrages.html
    Affiche les ouvrages d'eau dans un tableau, avec des filtres pour affiner la recherche
    """
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_filtered_template(
        'jeu_ouvrages.html',
        None,
        form_keys=["code_ouvrage", "nom_ouvrage", "nom_commune", "libelle_departement"],
        data_type="ouvrages", 
        page_title="Jeux de données", 
        page_sub_title="Ouvrages"
    )

def render_filtered_template(template, filter_fct, form_keys, data_type="chroniques"):
    """
    Fonction générique de transmission des valeurs filtrées d'un tableau
    """
    chroniques = Chroniques()
    # Récupération des données selon le type
    if data_type == "chroniques":
        data = chroniques.donnees()
    elif data_type == "points_prelevement":
        data = db.obtenir_info_prelevement()
    elif data_type == "ouvrages":
        data = db.obtenir_info_ouvrage().to_dict(orient="records")
    else:
        data = []

    # Préparation des options pour les filtres (valeurs uniques)
    filter_options = {
        key: sorted({str(row.get(key, "")) for row in data if row.get(key, "")})
        for key in form_keys
    }

    # Application des filtres si POST
    filtered_values = data
    if request.method == 'POST':
        filters = {key: request.form.get(key) for key in form_keys}
        for key, value in filters.items():
            if value:
                filtered_values = [row for row in filtered_values if str(row.get(key, "")) == value]
    else:
        filters = {}

    return render_template(
        template,
        filter_fields=form_keys,
        filter_labels={  # à adapter selon vos besoins
            'annee': 'Année',
            'libelle_usage': 'Usage',
            'nom_commune': 'Commune',
            'libelle_departement': 'Département',
            'nom_ouvrage': 'Ouvrage'
        },
        filter_options=filter_options,
        filtered_values=filtered_values,
        **filters
    )

################################
# À PROPOS
################################

# Route pour la page s'à propos sur le manuel d'utilisation de l'application "a_propos_manuel.html"
@app.route('/a-propos/manuel-utilisation')
def a_propos_manuel():
    """
    Fonction de définition de l'adresse de la page d'à propos sur le manuel d'utilisation de l'application "a_propos_manuel.html"
    Cette page fournit des informations sur l'utilisation de l'application, les fonctionnalités disponibles et comment naviguer dans le site
    """
    # Affichage du template
    return render_template(
        'a_propos_manuel.html', 
        page_title="À propos",
        page_sub_title="Manuel d'utilisation"
    )

# Route pour la page d'à propos sur l'équipe projet "a_propos_equipe.html"
@app.route('/a-propos/notre-equipe-projet')
def a_propos_equipe():
    """
    Fonction de définition de l'adresse de la page d'à propos sur l'équipe projet "a_propos_equipe.html"
    Cette page présente l'équipe projet, ses membres et leurs rôles dans le développement de l'application
    """
    # Affichage du template
    return render_template(
        'a_propos_equipe.html', 
        page_title="À propos", 
        page_sub_title="Notre équipe projet"
    )

################################
# LANCEMENT DE L'APPLICATION
################################

if __name__ == '__main__':
    app.run(debug=True)