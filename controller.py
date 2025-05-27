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

app.route('/donnees', methods=['GET', 'POST'])

# Route pour la page d'à propos "apropos.html"
@app.route('/apropos')
def apropos():
    """
    Fonction de définition de l'adresse de la page d'à propos "apropos.html"
    """
    # Affichage du template
    return render_template('apropos.html')

app.route('/connexion')

app.route('/forum')