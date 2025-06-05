import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# LES DONNEES SONT DE 2012 A 2022

class Chroniques:
    def __init__(self):
        self.url = "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques"

    def acces_chroniques(self):
        df = pd.read_json(self.url)
        info = df["data"]
        arr = np.array(info)
        return arr
    
    def donnees(self):
        L = []
        for c in self.acces_chroniques():
            if c['code_statut_volume'] == 1 or c['code_statut_volume'] == 2 and c['code_qualification_volume'] == 1 and c['prelevement_ecrasant'] == True:
                L.append(c)
        return L
    def colonnes(self):
        L = []
        for i in self.acces_chroniques()[0]:
            L.append(i)
        return L
    
    def filtre(self, colonne, filtre):
        chroniques = self.donnees()
        L = []
        for c in chroniques:
            if c[colonne] == filtre:
                L.append(c['volume'])
        return pd.DataFrame(L)
    
    def annee(self, colonne, filtre):
        chroniques = self.donnees()
        L = []
        for c in chroniques:
            if c[colonne] == filtre:
                L.append(c['annee'])
        return L
    
    def min_annee(self, colonne, filtre):
        return str(min(self.annee(colonne, filtre)))
    
    def max_annee(self, colonne, filtre):
        return str(max(self.annee(colonne, filtre)))
    
    def nom_ouvrage(self, ouvrage):
        for c in self.donnees():
            if c['code_ouvrage'] == ouvrage:
                return c['nom_ouvrage']
            
#######################################################

def rel_plot(liste, titre):
    sns.relplot(
        data=liste, kind="line"
    )
    plt.title(titre)
    plt.show()

def diagramme_courbe(valeurs: list, titre: str, text: list):
    """
    Cette fonction va créer un diagramme courbe
    On peut utiliser cette fonction directement pour mettre
    le diagramme dans le site web
    """
    plt.plot(valeurs, marker='o', color='cyan')
    plt.title(titre)
    plt.xlabel("Annee")
    plt.ylabel("Volumes")
    if text:
        plt.xticks(ticks=range(len(valeurs)), labels=text)
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    plt.show()
    plt.close()
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{image_base64}'

# print(len(acces_chroniques()))
# print(acces_chroniques()[0]['volume'])

# print(max(liste_volumes))
# for i in chroniques:
#     if i['volume'] == max(liste_volumes):
#         print(i)

chroniques = Chroniques()

print(chroniques.colonnes())

# print(get_volume())


# rel_plot(filtre('annee', 2020), "Volume sur l'annee 2020")
# rel_plot(filtre('libelle_usage', 'EAU POTABLE'), "Volume d'eau potable")
# rel_plot(chroniques.filtre('libelle_departement', 'Meurthe-et-Moselle'), "Volume à Meurthe-et-Moselle")
# print(chroniques.filtre('libelle_departement', 'Meurthe-et-Moselle'))

ouvrage = 'OPR0000000101'
diagramme_courbe(chroniques.filtre('code_ouvrage', ouvrage), "Evolution de " + chroniques.nom_ouvrage(ouvrage) + " entre " + chroniques.min_annee('code_ouvrage', ouvrage) + " et " + chroniques.max_annee('code_ouvrage', ouvrage), chroniques.annee('code_ouvrage', ouvrage))