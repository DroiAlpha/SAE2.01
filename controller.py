#####################################################################
# IMPORTATION DES MODULES
#####################################################################
# ! Il vous faut installer : pip install flask-caching redis
from flask import Flask, render_template, request
import matplotlib
from flask_caching import Cache
import time
from Graphiques import *
import Model.model as db  
#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration de l'application Flask
app = Flask(__name__)

# Import le server Redis de la vm 
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = '10.10.41.217'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

# Route pour tester si Redis fonctionne si ça fonctionne la page va montrer le même temps pendant 10 secondes puis changer
@app.route("/test_cache")
@cache.cached(timeout=10) 
def test_cache():
    return f"Time: {time.time()}"

# Route pour la page d'accueil "index.html"
@app.route("/")
@cache.cached(timeout=300)
def accueil():
    """
    Fonction de définition de l'adresse de la page d'accueil "index.html"
    """
    # Affichage du template
    return render_template('index.html')

# Route pour la page d'à propos "apropos.html"
@app.route('/apropos')
def apropos():
    """
    Fonction de définition de l'adresse de la page d'à propos "apropos.html"
    """
    # Affichage du template
    return render_template('apropos.html')

# Route pour la page d'affichage des tableaux intermédiaires "data_tab.html"
@app.route('/data_tab')
# Fonction générique de transmission des valeurs filtrées d'un tableau
def render_filtered_template(template, filter_fct, form_keys):
    """
    Fonction générique de transmission des valeurs filtrées d'un tableau
    """
    if request.method == 'POST':
        filters = {key: request.form.get(key) for key in form_keys}
        filtered_values = filter_fct(filters)
        return render_template(template, filtered_values=filtered_values, **filters)
    return render_template(template)

@app.route('/Carte',  methods=['GET', 'POST'])
def map():
    """
    Route permettant d'aller a la carte
    """
    return render_template('map.html')

@app.route('/Graphiques', methods=['GET', 'POST']) # a modifier en priorite
def graphiques():
    """
    Route pour afficher histogramme + diagramme circulaire
    """
    filters = {
        "annee" : request.form.get("annee"),
        "libelle_usage" : request.form.get("libelle_usage"),
        "nom_commune" : request.form.get("nom_commune"),
        "libelle_departement" : request.form.get("libelle_departement"),
        "nom_ouvrage" : request.form.get("nom_ouvrage")
    }

    filtered_values = 

    diagramme_circulaire = sns_pie(filtered_values) # a modifier

    histogramme = sns_horizontalbarplot(filtered_values) # a modifier

    return render_template(
        'Graphiques.html',
        diagramme_circulaire = diagramme_circulaire,
        histogramme = histogramme
    )


@app.route('/Evolution', methods=['GET', 'POST']) # a modifier
def evolution():
    """
    Route pour afficher une courbe d'évolution pour un ouvrage
    
    Il faudrait une methode pour n'avoir que les volumes pour 1 ouvrage (avec TOUTES les annees)
    """

    nom_ouvrage = request.form.get("nom_ouvrage")
    donnees = db.obtenir_info_ouvrage(nom_ouvrage)
    graphique = sns_courbe(donnees) # a modifier

    return render_template(
        'Evolution.html',
        graphique = graphique
    )


# ------- OPTIONNELS ----------#

@app.route('/connexion')
def connexion():
    pass

@app.route('/forum')
def forum():
    pass

if __name__ == '__main__':
    app.run(debug=True)