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
from model.chroniques import *
from io import BytesIO
import base64
from model.model import obtenir_info_prelevement, obtenir_info_ouvrage as db

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
    f, ax = plt.subplots(figsize=(6, 15))
    sns.barplot(x=value, y=category, data=data, ax=ax)
    ax.set(xlim=(0, data[value].max() * 1.1), ylabel=y_label, xlabel=x_label) 
    sns.despine(left=True, bottom=True)
    plt.title(titre)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return image_base64

# --------------------------------------------------------------- #
# ---------------------- GRAPHIQUES FINAUX ---------------------- #
# --------------------------------------------------------------- #

chroniques = Chroniques()

def diagramme_circu(data):
    data_usages = data['libelle_usage'].value_counts()
    return sns_pie(data_usages.values, data_usages.index, "Nombre d'ouvrages par usage")

def evo(data):
    if len(data['libelle_usage'].unique()) >= 2:
        usage_1 = data[data['libelle_usage'] == data['libelle_usage'].unique()[0]].groupby('annee')['volume'].sum()
        usage_2 = data[data['libelle_usage'] == data['libelle_usage'].unique()[1]].groupby('annee')['volume'].sum()
        return sns_courbe_double(usage_1.values, usage_2.values, usage_1.index, 
                               "Volume par année", "Années", "Volumes",
                               data['libelle_usage'].unique()[0], data['libelle_usage'].unique()[1])
    return None

def histo(data):
    data_histo = data['libelle_departement'].value_counts().reset_index()
    data_histo.columns = ['dep', 'value']
    return sns_horizontalbarplot(data_histo, 'dep', 'value', 
                                "Nombre d'ouvrages", "Départements", 
                                "Nombre d'ouvrages par département")

def histo_horiz(data):
    if 'milieu' in data.columns:
        grouped = data.groupby(['libelle_usage', 'milieu'])['volume'].sum().unstack()
        data_histo_2 = [grouped[col].values for col in grouped.columns]
        return histo_grouped(data_histo_2, grouped.index, grouped.columns, 
                           "Type de milieu", "Volume", 
                           "Volumes par usage et par milieu")
    return None
# diagramme_circu() # filtrage pas faisable
# evo()
# histo()
# histo_horiz()