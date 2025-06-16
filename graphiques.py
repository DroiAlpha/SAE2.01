# -------------- IMPORTATIONS -------------------#
#! Installer le framework Seaborn depuis le terminal avec la commande : pip install seaborn

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import folium as f
from folium.plugins import HeatMap, HeatMapWithTime
from io import BytesIO
import base64
from random import *
from model.chroniques import Chroniques
import model.model as db

# -------------- HISTOGRAMME -------------------#

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
# sns_horizontalbarplot(don, 'cook' , 'value' )
# sns_displot(Liste, "Titre", "Abscisse", "Ordonnées") 
# sns_pie(data, labels, "Titre")
# sns_courbe(data, "Titre", "Abscisse", "Ordonnées")

chroniques = Chroniques()

# ---- DIAGRAMME CIRCULAIRE ---- #
data_usages = chroniques.usage2()
# sns_pie(data_usages, chroniques.usage(), "Nombre d'ouvrages par usage")

# ---- HISTOGRAMME ---- #

usage_1 = chroniques.data_evo(chroniques.usage()[0], 10**(-3))
usage_2 = chroniques.data_evo(chroniques.usage()[1], 1)

sns_courbe_double(usage_1, usage_2, chroniques.annee(), "Volume par annee", "Annees", "Volumes")

# sns_courbe(usage_1, chroniques.annee(), "Evolution du volume EAU POTABLE", "Annees", "Volumes")
# sns_courbe(usage_2, chroniques.annee(), "Evolution du volume INDUSTRIE", "Annees", "Volumes")

# for c in chroniques.usage():
#     data_evo = chroniques.data_evo(c)
#     sns_courbe(data_evo, chroniques.annee(), "Evolution du volume pour "+c, "Années", "Volume en m^3")

# ----------------- CARTE ---------------------#

chroniques = Chroniques()

def heatmap(data: np.array, heat: str, map_obj: map):
    """Fonction qui crée une heatmap selon l'argument que l'on souhaite"""
    
    localisation = [[c['latitude'], c['longitude'], c[heat]] for c in data]
    HeatMap(localisation, radius=15).add_to(map_obj)

m = f.Map(location=(49.017561743666164, 6.022989879006374), zoom_start=6)

heatmap(chroniques.donnees(), 'volume', m)

def map_prelevement(map_obj):
    """
    Ajoute les ouvrages sur la carte Folium avec les noms des points de prélèvement associés.
    """
    ouvrages = db.obtenir_info_ouvrage()
    prelevements = db.obtenir_info_prelevement()
    
    for _, row in ouvrages.iterrows():
        lat = row['latitude']
        lon = row['longitude']

        if pd.notna(lat) and pd.notna(lon):
            popup_html = f'''
                <b>{row['nom_ouvrage']}</b><br>
                Code ouvrage : {row['code_ouvrage']}<br>
                Département : {row['libelle_departement']}
            '''
            popup = f.Popup(popup_html, max_width=150, min_width=50)

            # Taille réduite pour l'icône
            icon = f.Icon(color='blue', icon='tint', prefix='fa')

            f.Marker(
                location=(lat, lon),
                popup=popup,
                icon=icon
            ).add_to(map_obj)

m = f.Map(location=(49.017561743666164, 6.022989879006374), zoom_start=6)
m.save("tab_carte.html")