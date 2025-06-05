#####################################################################
# IMPORTATION DES MODULES
#####################################################################

from flask import Flask, render_template, request
import matplotlib

#####################################################################
# CONFIGURATION
#####################################################################

# Déclaration de l'application Flask
app = Flask(__name__)

# Assure la compatibilité de Matplotlib avec Flask
matplotlib.use('Agg')

# Route pour la page d'accueil "index.html"
@app.route("/")
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

@app.route('/Carte')
def map():
    """
    Route permettant d'aller a la carte
    """
    return render_template('map.html')

@app.route('/Graphiques', methods=['GET', 'POST']) # a modifier
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

    filtered_values = None

    diagramme_circulaire = None # a modifier
    histogramme = None # a modifier

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
    donnees = None # a modifier
    graphique = None # a modifier

    return render_template(
        'Evolution.html',
        graphique = graphique
    )

@app.route('/Donnees', methods=['GET', 'POST']) # a modifier
def donnees():
    """
    Route pour les données
    IL FAUT MODIFIER DES TRUCS AVEC LE MODELE
    """
    filters = {
        "annee" : request.form.get("annee"),
        "libelle_usage" : request.form.get("libelle_usage"),
        "nom_commune" : request.form.get("nom_commune"),
        "libelle_departement" : request.form.get("libelle_departement"),
        "nom_ouvrage" : request.form.get("nom_ouvrage")
    }

    filtered_values = None # a modifier avec le modele

    annee = None # a modifier avec le modele
    usage = None # a modifier avec le modele
    commune = None # a modifier avec le modele
    departement = None # a modifier avec le modele
    ouvrage = None # a modifier avec le modele

    is_empty = filtered_values.empty

    return render_template(
        'donnees.html',
        annee = annee,
        usage = usage,
        commune = commune,
        departement = departement,
        ouvrage = ouvrage,
        is_empty = is_empty
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