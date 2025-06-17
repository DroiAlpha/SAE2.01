"""
Contrôleur de l'application Flask pour le site web sur les prélèvements d'eau
"""

#####################################################################
# IMPORTATION DES MODULES
#####################################################################

# ! Installer Flask-Caching depuis le terminal avec la commande : pip install flask-caching redis

from flask import Flask, render_template, request
import matplotlib
from graphiques import sns_horizontalbarplot, sns_pie, histo_horiz, evo
import model.model as db
from model.chroniques import *
from flask import jsonify
from model.cache import cache
from model.chroniques import cache_chroniques
from dotenv import load_dotenv # N'oublie pas d'ajouter cette ligne si tu utilises .env
from Flexible_ChatBot.chatbot import ask_bot
#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration de l'application Flask
app = Flask(__name__)
load_dotenv() # Appelle cette fonction au début de ton fichier si tu utilises .env
# Importation du serveur Redis hébergé sur la VM pour le cache

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = '192.168.1.24'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

cache.init_app(app)
# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')
# Configuration de l'application Flask
# Route pour tester si Redis fonctionne si ça fonctionne la page va montrer le même temps pendant 10 secondes puis changer

#####################################################################
# ROUTES
#####################################################################

with app.app_context():
    cache_chroniques()  # Charge les données des chroniques au démarrage de l'application  
################################
# ACCUEIL
################################

# Route pour la page d'accueil "index.html"
@app.route("/")
@cache.cached(timeout=3600)
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
    chroniques, data = cache_chroniques()
    heatmap_data = data
    
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
    for _, row in heatmap_data.iterrows():
        try:
            lat = float(row['latitude'])
            lng = float(row['longitude'])
            vol = float(row.get('volume', 1))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                heatmap_points.append([lat, lng, vol])
        except (ValueError, TypeError):
            continue

    return jsonify({
        'prelevements': prelevements,
        'heatmap': heatmap_points
    })
    
# Route pour la page des graphiques sur les usages de l'eau "tab_usages.html"
@app.route('/tableau-bord/usages-eau', methods=['GET', 'POST'],)
def tab_usages():
    chroniques, data = cache_chroniques()
    data = pd.DataFrame(data)
    filters = {
        "annee": request.form.get("annee"),
        "libelle_usage": request.form.get("libelle_usage"),
        "nom_commune": request.form.get("nom_commune"),
        "libelle_departement": request.form.get("libelle_departement"),
        "nom_ouvrage": request.form.get("nom_ouvrage")
    } if request.method == 'POST' else {}

    filtered_data = data.copy()
    if filters:
        if filters.get("annee"):
            filtered_data = filtered_data[filtered_data['annee'] == int(filters["annee"])]
        if filters.get("libelle_usage"):
            filtered_data = filtered_data[filtered_data['libelle_usage'] == filters["libelle_usage"]]
        if filters.get("nom_commune"):
            filtered_data = filtered_data[filtered_data['nom_commune'] == filters["nom_commune"]]
        if filters.get("libelle_departement"):
            filtered_data = filtered_data[filtered_data['libelle_departement'] == filters["libelle_departement"]]
        if filters.get("nom_ouvrage"):
            filtered_data = filtered_data[filtered_data['nom_ouvrage'] == filters["nom_ouvrage"]]

    if not filtered_data.empty:
        usage_counts = filtered_data['libelle_usage'].value_counts()
        diagramme_circulaire = f'data:image/png;base64,{sns_pie(usage_counts.values, usage_counts.index, "Répartition des usages")}'

        hist_data = filtered_data['libelle_departement'].value_counts().reset_index()
        hist_data.columns = ['dep', 'value']
        histogrammehorizon = f'data:image/png;base64,{sns_horizontalbarplot(hist_data, "dep", "value", "Nombre d ouvrages", "Départements", "Nombre d ouvrages par département")}'

        filter_cols = [k for k, v in filters.items() if v]
        filter_vals = [int(v) if k == 'annee' else v for k, v in filters.items() if v]

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
@app.route('/tableau-bord/evolution-temporelle', methods=['GET', 'POST'])
def tab_evolution():
    """
    Route pour la page du graphique sur évolution temporelle du volume d'eau prélevé "tab_evolution.html"
    Affiche un graphique linéaire multiple filtrable par année, usage, et nom d'ouvrage
    """

    chroniques, data = cache_chroniques()
    data = pd.DataFrame(data)
    available_ouvrages=data['nom_ouvrage'].unique()
    graphique = evo()
    nom_ouvrage = 'AUDELONCOURT'
    years = chroniques.annee()
    usages = chroniques.usage()

    # Valeurs par défaut
    nom_ouvrage = 'AUDELONCOURT'
    annee = None
    colonne_filtre = []
    valeur_filtre = []

    if request.method == 'POST':
        # Récupérer les filtres s'ils sont soumis
        nom_ouvrage = request.form.get('available_ouvrages')
        annee = request.form.get('annee')

        # Ajouter aux filtres si sélectionné
        if nom_ouvrage:
            colonne_filtre.append('nom_ouvrage')
            valeur_filtre.append(nom_ouvrage)
        if annee:
            colonne_filtre.append('annee')
            valeur_filtre.append(annee)

    # Génération du graphique avec ou sans filtres
    if colonne_filtre and valeur_filtre:
        graphique = evo(colonne_filtre, valeur_filtre)
    else:
        graphique = evo()

    return render_template(
        'tab_evolution.html',
        graphique=graphique,
        years=years,
        usages=usages,
        available_ouvrages=available_ouvrages,
        nom_ouvrage=nom_ouvrage,
        page_title="Tableau de bord",
        page_sub_title="Évolution temporelle",
        sub_header_template="dashboard.html"
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
    chroniques, data = cache_chroniques()
    return render_filtered_template(
        'jeu_chroniques.html',
        chroniques().filtre,
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
    chroniques, data = cache_chroniques()
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
        page_sub_title="Manuel d'utilisation",
        sub_header_template="about.html"
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
        page_sub_title="Notre équipe projet",
        sub_header_template="about.html"
    )

@app.route('/contact')
def contact():
    return render_template('contact.html', page_title="Contact")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")
    if not user_input:
        return jsonify({"error": "No input"}), 400
    try:
        bot_response = ask_bot(user_input)
        print(f"User: {user_input} -> Bot: {bot_response}")
        return jsonify({"response": bot_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
################################
# LANCEMENT DE L'APPLICATION
################################

if __name__ == '__main__':
    app.run(debug=True, port=777) # Port chanceux la team