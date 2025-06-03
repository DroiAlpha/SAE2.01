# -------------- IMPORTATIONS -------------------#

import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from random import *
import folium as f

# -------------- HISTOGRAMME -------------------#

def fake_histogramme(liste):
    """
    Cette fonction crée un histogramme.
    On peut utiliser cette fonction directement pour mettre un histogramme
    dans une page web
    Il y aura écrit sur les barres les valeurs des barres, ainsi que les noms des abscisses et ordonnées
    """
    plt.figure(figsize=(8, 6))
    bars = plt.bar(range(len(liste)), liste, color='skyblue')

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

    # Ajout des labels et du titre
    plt.xlabel('Abscisses')
    plt.ylabel('Ordonnées')
    plt.title('Histogramme Test')

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    #plt.show() # à retirer si utilisé dans page web
    plt.close()

    # Convertion de l'image en format base64 pour l'inclure dans le template
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# ---------------- DIAGRAMME CIRCULAIRE ----------------------#

def diagramme_circle(liste: list, nom: str, labels: list):
    """
    Cette fonction crée un diagramme circulaire
    ATTENTION : il faut que le nombre d'éléments de la liste soit égale à au nombre de labels
    On peut utiliser cette fonction directement pour mettre un diagramme circulaire
    dans une page web
    """
    fig, axes = plt.subplots(1, 1, figsize=(5, 5))

    axes.pie(liste, labels=labels, autopct='%.1f%%')

    axes.set_title(nom)

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    #plt.show() # à retirer si utilisé dans page web
    plt.close()

    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# ------------- DIAGRAMME COURBE -----------------#

def diagramme_courbe(valeurs: list, labels: list, titre: str, nom_serie: str):
    """
    Cette fonction va créer un diagramme courbe
    On peut utiliser cette fonction directement pour mettre
    le diagramme dans le site web
    """
    plt.plot(labels, valeurs, marker='o', color='cyan', label=nom_serie)
    plt.title(titre)
    plt.legend()
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    #plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# -------------- TESTS --------------------#

Liste = [2, 3, 4, 6, 1]
fake_histogramme(Liste)

Liste2 = [7,2,4,5]
labels = ["1er", "2eme", "3eme", "4eme"]
diagramme_circle(Liste2, "Test", labels)

valeurs = [7,4,2,5,9]
labels = ['Élément 1', 'Élément 2', 'Élément 3', 'Élément 4', 'Élément 5']
titre = "Test"
serie = "Serie 1"
diagramme_courbe(valeurs, labels, titre, serie)

# --------- TEST SEABORN ----------------#


sns.set_theme(style='ticks')

def sns_barplot(liste: list):
    data = pd.Series(liste)
    sns.countplot(x=data)
    #plt.show()

Liste = [1, 2, 1, 1, 1, 4, 5, 6, 6]
sns_barplot(Liste)

def sns_displot(liste: list):
    data = pd.Series(liste)
    sns.displot(x=data)
    #plt.show()

Liste = [uniform(0,1.5) for _ in range(0,10000)]
sns_displot(Liste)

# ----------------- CARTE ---------------------#

m = f.Map(location=(48.525, 2.385  ))

m.save("templates/map.html")