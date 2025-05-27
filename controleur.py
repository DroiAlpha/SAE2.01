#####################################################################
# IMPORTATION DES MODULES
#####################################################################
from flask import Flask, render_template, request, redirect, url_for
import matplotlib

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

app.route("/graphiques", methods=['POST', 'GET'])

app.route("/tableau", methods=['POST', 'GET'])

app.route("/carte", methods=['GET'])

################################ ? Mayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyybe ###########################################################################
app.route("/dashboard")
app.route("/forum")
app.route("/connexion")

# Route pour la page d'à propos "apropos.html"
@app.route('/apropos')
def apropos():
    """
    Fonction de définition de la page d'à propos "apropos.html"
    """
    # Affichage du template
    return render_template('apropos.html')



if __name__ == '__main__':
    app.run(debug=True)
    
    