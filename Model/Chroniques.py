import pandas as pd
import numpy as np

class Chroniques:
    def __init__(self):
        self.url = "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques"

    def acces_chroniques(self):
        df = pd.read_json(self.url)
        info = df["data"]
        arr = np.array(info)
        return arr
    
    def donnees(self):
        """
        (GROS) Probleme : Ya pas une donnée avec true comme prelevement_ecrasant
        """
        L = []
        #c['code_qualification_volume'] == "1" and (c['code_statut_volume'] in ["1", "2"]) and c['prelevement_ecrasant']
        for c in self.acces_chroniques():
            if c['code_qualification_volume'] == "1" and (c['code_statut_volume'] in ["1", "2"]):
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
    
    def filtre_ouv(self, nom_ouvrage):
        """
        Retourne une liste de dictionnaires contenant les volumes et années
        pour un nom d'ouvrage donné.
        """
        result = []
        for c in self.donnees():
            if c['nom_ouvrage'] == nom_ouvrage:
                result.append({
                    "annee": c['annee'],
                    "volume": c['volume']
                })
        return result

    
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

    def ouvrage(self, nom_ouvrage):
        L = []
        for c in self.donnees():
            if c['nom_ouvrage'] == nom_ouvrage:
                L.append(c['volume'])
        return L

    def usage(self):
        e = set()
        for c in self.acces_chroniques():
            e.add(c['libelle_usage'])
        return list(e)