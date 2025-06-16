#####################################################################
# IMPORTATION DES MODULES
#####################################################################
# ! Il vous faut installer : pip install flask-caching redis
from flask import Flask, render_template, request
import matplotlib
from flask_caching import Cache
import time
from graphiques import *
import model.model as db
from model.chroniques import *

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
@app.route('/a-propos/manuel-utilisation')
def a_propos_manuel_utilisation():
    """
    Fonction de définition de l'adresse de la page d'à propos "apropos.html"
    """
    # Affichage du template
    return render_template('a-propos-manuel-utilisation.html')

# Table : “Tableau de bord”
@app.route('/tableau-bord')
def tableau_de_bord():
    """
    Affiche le template tableau-bord.html
    """
    return render_template('tableau-bord.html')

# Page “Jeux de données”
@app.route('/jeux-de-donnees')
def jeux_de_donnees():
    """
    Affiche le template jeux-de-donnees.html
    """
    return render_template('jeux-de-donnees.html')

# Route pour la page d'affichage des tableaux intermédiaires "data_tab.html"
@app.route('/data_tab')
# Fonction générique de transmission des valeurs filtrées d'un tableau
def render_filtered_template(template, filter_fct, form_keys):
    """
    Fonction générique de transmission des valeurs filtrées d'un tableau
    Je dois mettre les données des 3 tableaux (chroniques, pt_prelevement, ouvrage)
    DANS la fonction
    """
    if request.method == 'POST':
        filters = {key: request.form.get(key) for key in form_keys}
        filtered_values = filter_fct(filters)
        return render_template(template, filtered_values=filtered_values, **filters)
    
    chroniques = Chroniques()

    tab_chroniques = chroniques.filtre()
    tab_pt_prelev = db.obtenir_info_prelevement()
    tab_ouvrages = db.obtenir_info_ouvrage()

    return render_template(template,
                           tab_chroniques = tab_chroniques,
                           tab_ouvrages = tab_ouvrages,
                           tab_pt_prelev = tab_pt_prelev
                           )

@app.route('/Carte',  methods=['GET', 'POST'])
def map():
    """
    Route permettant d'aller a la carte
    """
    return render_template('map.html')

@app.route('/Graphiques', methods=['GET', 'POST'])
def graphiques():
    """
    Route pour afficher histogramme + diagramme circulaire,
    avec ou sans filtres.
    """
    chroniques = Chroniques()
    
    # Données par défaut (non filtrées)
    donnees = chroniques.donnees()  
    
    if request.method == 'POST':
        # Récupération des filtres depuis le formulaire
        filters = {
            "annee": request.form.get("annee"),
            "libelle_usage": request.form.get("libelle_usage"),
            "nom_commune": request.form.get("nom_commune"),
            "libelle_departement": request.form.get("libelle_departement"),
            "nom_ouvrage": request.form.get("nom_ouvrage")
        }

        # Filtrage des données manuellement
        filtered_data = []
        
        for c in donnees:
            if (not filters["annee"] or str(c["annee"]) == filters["annee"]) and \
               (not filters["libelle_usage"] or c["libelle_usage"] == filters["libelle_usage"]) and \
               (not filters["nom_commune"] or c["nom_commune"] == filters["nom_commune"]) and \
               (not filters["libelle_departement"] or c["libelle_departement"] == filters["libelle_departement"]) and \
               (not filters["nom_ouvrage"] or c["nom_ouvrage"] == filters["nom_ouvrage"]):
                filtered_data.append(c)

        # Génération des graphiques à partir des données filtrées
        diagramme_circulaire = sns_pie(filtered_data)
        histogramme = sns_horizontalbarplot(filtered_data)

        return render_template(
            'Graphiques.html',
            diagramme_circulaire=diagramme_circulaire,
            histogramme=histogramme,
            filters=filters  
        )

    # Si GET ou aucun filtre
    diagramme_circulaire = sns_pie(donnees)
    histogramme = sns_horizontalbarplot(donnees)
    
    return render_template(
        'Graphiques.html',
        diagramme_circulaire=diagramme_circulaire,
        histogramme=histogramme,
        filters=None
    )


@app.route('/Evolution', methods=['GET', 'POST'])
def evolution():
    """
    Route pour afficher une courbe d'évolution pour un ouvrage.
    L'utilisateur choisit un ouvrage, et la courbe montre les volumes selon les années.
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
        'Evolution.html',
        graphique=graphique,
        nom_ouvrage=nom_ouvrage
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

""" Contrôler de l'application Flask pour le site web sur les prélèvements d'eau """

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/accueil')
def accueil():
    return render_template('accueil.html', page_title="Accueil")

@app.route('/tableau-de-bord/carte-des-prelevements')
def tableau_de_bord():
    return render_template('carte-des-prelevements.html', page_title="Tableau de bord")

@app.route('/tableau-de-bord/usages-de-l-eau')
def tableau_de_bord():
    return render_template('usages-de-l-eau.html', page_title="Tableau de bord")

@app.route('/tableau-de-bord/evolution-temporelle')
def tableau_de_bord():
    return render_template('evolution-temporelle.html', page_title="Tableau de bord")

@app.route('/jeux-de-donnees/chroniques')
def tableau_de_bord():
    return render_template('jeu-chroniques.html', page_title="Jeux de données")

@app.route('/jeux-de-donnees/ouvrages')
def tableau_de_bord():
    return render_template('jeu-ouvrages.html', page_title="Jeux de données")

@app.route('/jeux-de-donnees/points-de-prelevement')
def tableau_de_bord():
    return render_template('jeu-points-de-prelevement.html', page_title="Jeux de données")

@app.route('/a-propos/manuel-d-utilisation')
def tableau_de_bord():
    return render_template('manuel-d-utilisation.html', page_title="À propos")

@app.route('/a-propos/notre-equipe-projet')
def tableau_de_bord():
    return render_template('notre-equipe-projet.html', page_title="À propos")