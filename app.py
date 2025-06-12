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