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
from Model.chroniques import *
from io import BytesIO
import base64
from Model.model import obtenir_info_prelevement, obtenir_info_ouvrage as db
# -------------- HISTOGRAMME -------------------#

sns.set_theme(style='ticks')

def evo_graph(data):
    """Génère le graphique des volumes par usage et milieu"""
    grouped = data.groupby(['libelle_usage', 'milieu'])['volume'].sum().unstack()
    
    # Préparer les données pour histo_grouped
    data_histo = [grouped[col].values for col in grouped.columns]
    labels = grouped.index.tolist()
    categories = grouped.columns.tolist()
    
    # Créer le graphique
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, (col, values) in enumerate(zip(categories, data_histo)):
        ax.bar(x + i*width, values, width, label=col)
    
    ax.set_xlabel("Usage")
    ax.set_ylabel("Volume (m³)")
    ax.set_title("Volume d'eau par usage et milieu")
    ax.set_xticks(x + width/2)
    ax.set_xticklabels(labels)
    ax.legend(title='Milieu')
    
    # Sauvegarder en image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def sns_pie(data: list, labels: list, titre: str):
    """
    C'est le diagramme circulaire
    """
    plt.figure(figsize=(6,6)) 
    plt.pie(data, labels=labels, autopct='%1.1f%%')
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return image_base64

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

def sns_horizontalbarplot(data: list, category: str, value: str, x_label: str, y_label: str, titre: str):
    f, ax = plt.subplots(figsize=(14, 10))
    sns.barplot(x=value, y=category, data=data, ax=ax)
    ax.set(xlim=(0, data[value].max() * 1.1), ylabel=y_label, xlabel=x_label) 
    sns.despine(left=True, bottom=True)
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return image_base64
# ------------------------------------------------------------- #
# ---------------------- GRAPHIQUES FINAUX ------------------------------ #
# ------------------------------------------------------------- #

chroniques = Chroniques()

def diagramme_circu(colonne: list = None, filtre: list = None):
    if colonne and filtre:
        data_usages = chroniques.usage2(colonne, filtre)
    else:
        data_usages = chroniques.usage2()
    return sns_pie(data_usages, chroniques.usage(), "Nombre d'ouvrages par usage")

def evo(colonne: list = None, filtre: list = None):
    if colonne and filtre:
        usage_1 = chroniques.data_evo(chroniques.usage()[0], 1, colonne, filtre)
        usage_2 = chroniques.data_evo(chroniques.usage()[1], 1, colonne, filtre)
    else:
        usage_1 = chroniques.data_evo(chroniques.usage()[0], 1)
        usage_2 = chroniques.data_evo(chroniques.usage()[1], 1)
    return sns_courbe_double(usage_1, usage_2, chroniques.annee(), "Volume par annee", "Annees", "Volumes")

def histo(colonne: list = None, filtre: list = None):
    if colonne and filtre:
        data_histo = chroniques.compte_dep(colonne, filtre)
        titre = "Histogramme du nombre d'ouvrage par département"
        x_label = "Nombre d'ouvrages"
        y_label = " "
    else:
        data_histo = chroniques.compte_dep()
        titre = "Histogramme du nombre d'ouvrage par département"
        x_label = "Nombre d'ouvrages"
        y_label = " "
    return sns_horizontalbarplot(data_histo, 'dep', 'value', x_label, y_label, titre)

def histo_horiz(colonne: list = None, filtre: list = None):
    data_histo_2 = []
    for c in chroniques.usage():
        if colonne and filtre:
            data_histo_2.append(milieu(c, colonne, filtre))
        else:
            data_histo_2.append(milieu(c))

    labels = ["SOUT", "CONT"]
    categories = ["EAU POTABLE", "INDUSTRIE"]
    titre = "Volumes par usage et par milieu"
    x_label = "Type de milieu"
    y_label = "Volume"
    return evo_graph(data_histo_2, labels,categories, x_label, y_label, titre)

# diagramme_circu() # filtrage pas faisable
# evo()
# histo()
# histo_horiz()

