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
from Model.Chroniques import *
from io import BytesIO
import base64

# -------------- HISTOGRAMME -------------------#

sns.set_theme(style='ticks')

def histo_grouped(data, labels, categories, x_label, y_label, titre):
    x = np.arange(len(labels))  # les positions des groupes
    width = 0.8 / len(data)     # largeur des barres (adaptée selon le nombre de catégories)

    fig, ax = plt.subplots(figsize=(8, 6))

    colors = ['cyan', 'deepskyblue', 'steelblue']
    rects = []

    for i in range(len(data)):
        rect = ax.bar(x + (i - len(data)/2)*width + width/2, data[i], width, label=categories[i], color=colors[i % len(colors)])
        rects.append(rect)

    # Ajout des valeurs au-dessus des barres
    for rect in rects:
        for r in rect:
            height = r.get_height()
            ax.annotate(f'{height}',
                        xy=(r.get_x() + r.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(titre)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    image_stream = BytesIO()
    plt.savefig(image_stream, format='png', bbox_inches='tight')
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

def sns_courbe_double(data1: list, data2: list, x_values: list, titre: str, x_label: str, y_label: str, label1="Courbe 1", label2="Courbe 2"):
    df1 = pd.DataFrame({'x': x_values, 'y': data1, 'serie': label1})
    df2 = pd.DataFrame({'x': x_values, 'y': data2, 'serie': label2})
    df = pd.concat([df1, df2])
    sns.relplot(data=df, kind="line", x="x", y="y", hue="serie")
    plt.title(titre)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_courbe(data: list, x_values: list, titre: str, x_label: str, y_label: str):
    df = pd.DataFrame({'x': x_values, 'y': data})
    sns.relplot(data=df, kind="line", x="x", y="y")
    plt.title(titre)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

def sns_horizontalbarplot(data: list,category, value, x_label, y_label, titre):
    
    df = pd.DataFrame(data)
    
    f, ax = plt.subplots(figsize=(6, 15))
    
    # X et Y sont les différentes colonnes que l'on souhaite
    sns.barplot(x=value, y=category, data=df, ax=ax)

    # * Y a que dieu qui sait ce que les trois lignes en dessous font
    ax.legend(ncol=2, loc="lower right", frameon=True, ) # mettre les légendes
    ax.set(xlim=(0, 2000), ylabel=y_label, xlabel=x_label) 
    sns.despine(left=True, bottom=True) # ! JSP
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# ------------------------------------------------------------- #
# ---------------------- GRAPHIQUES FINAUX ------------------------------ #
# ------------------------------------------------------------- #

chroniques = Chroniques()

def diagramme_circu():
    data_usages = chroniques.usage2()
    return sns_pie(data_usages, chroniques.usage(), "Nombre d'ouvrages par usage")

def evo():
    usage_1 = chroniques.data_evo(chroniques.usage()[0], 10**(-3))
    usage_2 = chroniques.data_evo(chroniques.usage()[1], 1)
    return sns_courbe_double(usage_1, usage_2, chroniques.annee(), "Volume par annee", "Annees", "Volumes")

def histo():
    data_histo = chroniques.compte_dep()
    titre = "Histogramme du nombre d'ouvrage par département"
    x_label = "Nombre d'ouvrages"
    y_label = " "
    return sns_horizontalbarplot(data_histo, 'dep', 'value', x_label, y_label, titre)

def histo_horiz():
    data_histo_2 = []
    for c in chroniques.usage():
        data_histo_2.append(milieu(c))

    labels = ["SOUT", "CONT"]
    categories = ["EAU POTABLE", "INDUSTRIE"]
    titre = "Volumes par usage et par milieu"
    x_label = "Type de milieu"
    y_label = "Volume"
    return histo_grouped(data_histo_2, labels,categories, x_label, y_label, titre)

diagramme_circu() # filtrage pas faisable
evo()
histo()
histo_horiz()

# ---------------------------------------------#
# ----------------- CARTE ---------------------#    
# ---------------------------------------------#

chroniques = Chroniques()

# ! J'ai pas réussi à faire celle qui est timed si quelqu'un a la foi de faire

def heatmap(data: np.array, heat: str, map_obj: map):
    """Fonction qui crée une heatmap selon l'argument que l'on souhaite"""
    
    localisation = [[c['latitude'], c['longitude'], c[heat]] for c in data]
    HeatMap(localisation, radius=15).add_to(map_obj)

m = f.Map(location=(49.017561743666164, 6.022989879006374), zoom_start=6)

heatmap(chroniques.donnees(), 'volume', m)

m.save("map.html")