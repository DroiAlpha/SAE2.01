import pandas as pd
import numpy as np
# from Test import *
import seaborn as sns
import matplotlib.pyplot as plt

def acces_chroniques():
    url = "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques"
    df = pd.read_json(url)
    info = df["data"]
    arr = np.array(info)
    return arr

def filtre(colonne, filtre):
    chroniques = acces_chroniques()
    L = []
    for c in chroniques:
        if c[colonne] == filtre:
            L.append(c['volume'])
    return pd.DataFrame(L)

def rel_plot(liste, titre):
    sns.relplot(
        data=liste, kind="line"
    )
    plt.title(titre)
    plt.show()

# print(len(acces_chroniques()))
# print(acces_chroniques()[0]['volume'])

chroniques = acces_chroniques()

liste_volumes = [c['volume'] for c in chroniques]

print(max(liste_volumes))
for i in chroniques:
    if i['volume'] == max(liste_volumes):
        print(i)

# titre = "Volumes"
# diagramme_courbe(liste_volumes,  titre)

liste_volumes = pd.DataFrame(liste_volumes)

# rel_plot(filtre('annee', 2020), "Volume sur l'annee 2020")
# rel_plot(filtre('libelle_usage', 'EAU POTABLE'), "Volume d'eau potable")
rel_plot(filtre('libelle_departement', 'Meurthe-et-Moselle'), "Volume à Meurthe-et-Moselle")