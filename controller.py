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
from graphiques import *
import model.model as db
from model.chroniques import *

#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration de l'application Flask
app = Flask(__name__)

# Importation du serveur Redis hébergé sur la VM pour le cache

# Décommenter les lignes suivantes pour utiliser RedisCache
# app.config['CACHE_TYPE'] = 'RedisCache'
# app.config['CACHE_REDIS_HOST'] = '10.10.41.217'
# app.config['CACHE_REDIS_PORT'] = 6379
# app.config['CACHE_DEFAULT_TIMEOUT'] = 300

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
@cache.cached(timeout=300)
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
@app.route('/tableau-bord/carte-prelevements',  methods=['GET', 'POST'])
def tab_carte():
    """
    Fonction de définition de l'adresse de la page de la carte des prélèvements en eau "tab_carte.html"
    Affiche la carte des prélèvements d'eau avec les ouvrages
    """
    return render_template(
        'tab_carte.html', 
        page_title="Tableau de bord"
    )

# Route pour la page des graphiques sur les usages de l'eau "tab_usages.html"
@app.route('/tableau-bord/usages-eau', methods=['GET', 'POST'])
def tab_usages():
    """
    Fonction de définition de l'adresse de la page des graphiques sur les usages de l'eau "tab_usages.html"
    Affiche les graphiques (histogrammes groupés, diagramme en barres empilées et diagramme circulaire) sur les usages de l'eau, avec ou sans filtres
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
            'tab_usages.html',
            diagramme_circulaire=diagramme_circulaire,
            histogramme=histogramme,
            filters=filters, 
            page_title="Tableau de bord"
        )

    # Si GET ou aucun filtre
    diagramme_circulaire = sns_pie(donnees)
    histogramme = sns_horizontalbarplot(donnees)
    
    return render_template(
        'tab_usages.html',
        diagramme_circulaire=diagramme_circulaire,
        histogramme=histogramme,
        filters=None, 
        page_title="Tableau de bord"
    )

# Route pour la page du graphique sur évolution temporelle du volume d'eau prélevé "tab_evolution.html"
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
        page_title="Tableau de bord"
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
    render_filtered_template(
        'jeu_chroniques.html',
        Chroniques().filtre,
        form_keys=["annee", "libelle_usage", "nom_commune", "libelle_departement", "nom_ouvrage"]
    )
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_template('jeu_chroniques.html', page_title="Jeux de données")

# Route pour la page du jeu de données pour les points de prélèvement "jeu_points_prelevement.html"
@app.route('/jeux-donnees/points-prelevement')
def jeu_points_prelevement():
    """
    Route pour la page du jeu de données pour les points de prélèvement "jeu_points_prelevement.html"
    Affiche les points de prélèvement d'eau dans un tableau, avec des filtres pour affiner la recherche
    """
    render_filtered_template(
        'jeu_points_prelevement.html',
        Chroniques().filtre,
        form_keys=["annee", "libelle_usage", "nom_commune", "libelle_departement", "nom_ouvrage"]
    )
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_template('jeu_points_prelevement.html', page_title="Jeux de données")

# Route pour la page du jeu de données pour les ouvrages "jeu_ouvrages.html"
@app.route('/jeux-donnees/ouvrages')
def jeu_ouvrages():
    """
    Route pour la page du jeu de données pour les ouvrages "jeu_ouvrages.html
    Affiche les ouvrages d'eau dans un tableau, avec des filtres pour affiner la recherche
    """
    render_filtered_template(
        'jeu_ouvrages.html',
        Chroniques().filtre,
        form_keys=["annee", "libelle_usage", "nom_commune", "libelle_departement", "nom_ouvrage"]
    )
    # Fonction générique de transmission des valeurs filtrées d'un tableau
    return render_template('jeu_ouvrages.html', page_title="Jeux de données")

def render_filtered_template(template, filter_fct, form_keys):
    """
    Fonction générique de transmission des valeurs filtrées d'un tableau
    """
    #! Il faut encore mettre les données des 3 tableaux (chroniques, pt_prelevement, ouvrages) DANS la fonction
    if request.method == 'POST':
        filters = {key: request.form.get(key) for key in form_keys}
        filtered_values = filter_fct(filters)
        return render_template(template, filtered_values=filtered_values, **filters)
    
    chroniques = Chroniques()

    tab_chroniques = chroniques.filtre()
    tab_pt_prelev = db.obtenir_info_prelevement()
    tab_ouvrages = db.obtenir_info_ouvrage()

    return render_template(
        template,
        tab_chroniques = tab_chroniques,
        tab_ouvrages = tab_ouvrages,
        tab_pt_prelev = tab_pt_prelev
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
    return render_template('a_propos_manuel.html', page_title="À propos")

# Route pour la page d'à propos sur l'équipe projet "a_propos_equipe.html"
@app.route('/a-propos/notre-equipe-projet')
def a_propos_equipe():
    """
    Fonction de définition de l'adresse de la page d'à propos sur l'équipe projet "a_propos_equipe.html"
    Cette page présente l'équipe projet, ses membres et leurs rôles dans le développement de l'application
    """
    # Affichage du template
    return render_template('a_propos_equipe.html', page_title="À propos")

################################
# LANCEMENT DE L'APPLICATION
################################

if __name__ == '__main__':
    app.run(debug=True)