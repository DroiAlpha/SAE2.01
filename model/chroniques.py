"""
Modèle de l'application Flask pour interagir avec les données Chroniques de l'API Hub'eau Prélèvements en eau
"""

#####################################################################
# IMPORTATION DES MODULES
#####################################################################

import pandas as pd
import numpy as np

#####################################################################
# CLASSE Chroniques
#####################################################################

class Chroniques:
    def __init__(self):
        """
        Initialise la classe Chroniques avec l'URL de l'API Hub'eau Prélèvements en eau
        """
        self.url = "https://hubeau.eaufrance.fr/api/v1/prelevements/chroniques"

    def acces_chroniques(self):
        """
        Accède aux données chroniques de l'API Hub'eau Prélèvements en eau
        :return: Un tableau numpy contenant les données chroniques
        """
        df = pd.read_json(self.url)
        info = df["data"]
        arr = np.array(info)
        return arr
    
    def donnees(self):
        """
        Renvoie les données de chronique sous forme de liste de dictionnaires
        :return: Une liste de dictionnaires contenant les données de chronique        
        """
        L = []
        #? Sélection des données à partir des prelevement_ecrasant impossible : prelevement_ecrasant != true
        # c['code_qualification_volume'] == "1" and (c['code_statut_volume'] in ["1", "2"]) and c['prelevement_ecrasant']
        for c in self.acces_chroniques():
            if c['code_qualification_volume'] == "1" and (c['code_statut_volume'] in ["1", "2"]):
                L.append(c)
        return L


    def colonnes(self):
        """
        Renvoie les noms des colonnes de données chroniques
        :return: Une liste de noms de colonnes
        """
        L = []
        for i in self.acces_chroniques()[0]:
            L.append(i)
        return L
    
    def filtre(self, colonne = None, filtre = None):
        """
        Renvoie un dataframe pandas contenant les données chroniques, filtrées selon la colonne et le filtre spécifiés
        Si aucun filtre n'est spécifié, renvoie toutes les données
        :param colonne: Nom de la colonne à filtrer (optionnel)
        :param filtre: Valeur à filtrer dans la colonne spécifiée (optionnel)
        :return: Un dataframe pandas contenant les données filtrées
        """
        chroniques = self.donnees()
        L = []
        for c in chroniques:
            if colonne and filtre:
                if c[colonne] == filtre:
                    L.append(c)
            else:
                L.append(c)
        return pd.DataFrame(L)
    
    def filtre_ouv(self, nom_ouvrage):
        """
        Retourne une liste de dictionnaires contenant les données chroniques sur les volumes d'eau et années, pour un ouvrage spécifique
        :param nom_ouvrage: Nom de l'ouvrage à filtrer
        :return: Une liste de dictionnaires contenant les données chroniques pour l'ouvrage spécifié
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
        """
        Renvoie une liste des années pour lesquelles les données chroniques correspondent à un filtre spécifique sur une colonne donnée
        :param colonne: Nom de la colonne à filtrer
        :param filtre: Valeur à filtrer dans la colonne spécifiée
        :return: Une liste d'années correspondant au filtre appliqué
        """
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
        """
        Renvoie une liste des volumes d'eau pour un ouvrage spécifique
        :param nom_ouvrage: Nom de l'ouvrage à filtrer
        :return: Une liste de volumes d'eau pour l'ouvrage spécifié
        """
        L = []
        for c in self.donnees():
            if c['nom_ouvrage'] == nom_ouvrage:
                L.append(c['volume'])
        return L

    def usage(self):
        """
        Renvoie une liste des usages uniques présents dans les données chroniques
        :return: Une liste d'usages uniques
        """
        e = set()
        for c in self.acces_chroniques():
            e.add(c['libelle_usage'])
        return list(e)
    
#####################################################################
# TESTS
#####################################################################

chroniques = Chroniques()
print(chroniques.filtre())