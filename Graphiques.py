# -------------- IMPORTATIONS -------------------#

import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from random import *
import folium as f
from folium.plugins import HeatMap, HeatMapWithTime
import numpy as np
from Model.Chroniques import Chroniques
from math import exp
from io import BytesIO
import base64

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

def diagramme_courbe(valeurs: list, titre: str):
    """
    Cette fonction va créer un diagramme courbe
    On peut utiliser cette fonction directement pour mettre
    le diagramme dans le site web
    """
    plt.plot(valeurs, marker='o', color='cyan')
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# -------------- TESTS --------------------#

# Liste = [2, 3, 4, 6, 1]
# fake_histogramme(Liste)

# Liste2 = [7,2,4,5]
# labels = ["1er", "2eme", "3eme", "4eme"]
# diagramme_circle(Liste2, "Test", labels)

# valeurs = [7,4,2,5,9]
# titre = "Test"
# diagramme_courbe(valeurs, titre)

# --------- TEST SEABORN ----------------#


sns.set_theme(style='ticks')

def sns_displot(liste: list):
    """
    Utilisation de base64 et io pour pouvoir mettre l'image
    dans une page web
    """
    data = pd.Series(liste)
    sns.displot(data)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_pie(data: list, labels: list):
    plt.figure(figsize=(6,6)) 
    plt.pie(data, labels=labels)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_courbe(data:list):
    sns.relplot(
    data, kind="line")
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_horizontalbarplot(data: list,category, value ):
    
    df = pd.DataFrame(data)
    
    f, ax = plt.subplots(figsize=(6, 15))
    
    # X et Y sont les différentes colonnes que l'on souhaite
    sns.barplot(x=value, y=category, data=df, ax=ax)

    # * Y a que dieu qui sait ce que les trois lignes en dessous font
    ax.legend(ncol=2, loc="lower right", frameon=True, ) # mettre les légendes
    ax.set(xlim=(0, 24), ylabel="Contribution", xlabel="test") 
    sns.despine(left=True, bottom=True) # ! JSP
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# don = [
#     {"cook": "chatgpt", "value": 10},
#     {"cook": "amaurrrr", "value": 15},
#     {"cook": "idriss", "value": 5}
# ]

# Liste = [uniform(0,1.5) for _ in range(0,10000)]
# data = [30, 20, 50] # Données juste pour try
# labels = ['A', 'B', 'C'] # Nom pour chaque part.
# sns_horizontalbarplot(don, 'cook' , 'value' )
# sns_displot(Liste) 
# sns_pie(data, labels)
# sns_courbe(data)
# ----------------- CARTE ---------------------#

chroniques = Chroniques()

# ! J'ai pas réussi à faire celle qui est timed si quelqu'un a la foi de faire

def heatmap(data: np.array, heat: str, map_obj: map):
    """Fonction qui crée une heatmap selon l'argument que l'on souhaite"""
    
    localisation = [[c['latitude'], c['longitude'], c[heat]] for c in data]
    HeatMap(localisation, radius=15).add_to(map_obj)

m = f.Map(location=(49.017561743666164, 6.022989879006374), zoom_start=6)

# heatmap(chroniques.donnees(), 'volume', m)

def map_prelevement(data: np.array, map_obj: map,):
    """Fonction qui permet d'obtenir une carte"""
    
m.save("map.html")