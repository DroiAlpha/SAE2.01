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
def rel_plot(liste):
    sns.relplot(
        data=liste, kind="line"
    )
    plt.show()
rel_plot(liste_volumes)