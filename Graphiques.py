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
from bordel_Amaury import *
from math import exp
from io import BytesIO
import base64
from bordel_Amaury import *

sns.set_theme(style='ticks')

def sns_displot(liste: list, titre: str, x_label: str, y_label: str):
    """
    C'est l'histogramme
    Utilisation de base64 et io pour pouvoir mettre l'image
    dans une page web
    """
    data = pd.Series(liste)
    sns.displot(data)
    plt.title(titre)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_pie(data: list, labels: list, titre: str):
    """
    C'est le diagramme circulaire
    """
    plt.figure(figsize=(6,6)) 
    plt.pie(data, labels=labels)
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_courbe(data:list, titre: str, x_label: str, y_label: str):
    sns.relplot(
    data, kind="line")
    plt.title(titre)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
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

# ------------------------------------------------------------- #
# ---------------------- TESTS -------------------------------- #
# ------------------------------------------------------------- #

don = [
    {"cook": "chatgpt", "value": 10},
    {"cook": "amaurrrr", "value": 15},
    {"cook": "idriss", "value": 5}
]

Liste = [uniform(0,1.5) for _ in range(0,10000)]
data = [30, 20, 50] # Données juste pour try
labels = ['A', 'B', 'C'] # Nom pour chaque part.
sns_horizontalbarplot(don, 'cook' , 'value' )
sns_displot(Liste, "Titre", "Abscisse", "Ordonnées") 
sns_pie(data, labels, "Titre")
sns_courbe(data, "Titre", "Abscisse", "Ordonnées")

chroniques = Chroniques()

# ---- DIAGRAMME CIRCULAIRE ---- #
data_usages = chroniques.usage2()
sns_pie(data_usages, chroniques.usage(), "Nombre d'ouvrages par usage")

# ---- HISTOGRAMME ---- #
data_evo = chroniques.data_evo("EAU POTABLE")
sns_courbe(data_evo, "Evolution du volume pour eau potable", "Années", "Volume en m^3")

# ----------------- CARTE ---------------------#

chroniques = Chroniques()

# ! J'ai pas réussi à faire celle qui est timed si quelqu'un a la foi de faire

def heatmap(data: np.array, heat: str, map_obj: map):
    """Fonction qui crée une heatmap selon l'argument que l'on souhaite"""
    
    localisation = [[c['latitude'], c['longitude'], c[heat]] for c in data]
    HeatMap(localisation, radius=15).add_to(map_obj)

m = f.Map(location=(49.017561743666164, 6.022989879006374), zoom_start=6)

heatmap(chroniques.donnees(), 'volume', m)

m.save("map.html")