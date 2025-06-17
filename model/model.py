"""
Modèle de l'application Flask pour interagir avec la base de données locale PostgreSQL
"""

#####################################################################
# IMPORTATION DES MODULES
#####################################################################

# ! Installer SQLAlchemy depuis le terminal avec la commande : pip install sqlalchemy

import pandas as pd
from sqlalchemy import create_engine

#####################################################################
# CONFIGURATION
#####################################################################

# Crée un engine SQLAlchemy UNE SEULE FOIS (en global)
engine = create_engine("postgresql+psycopg2://yuri:yuri@10.10.11.253:5432/eaufrance")

#####################################################################
# FONCTIONS
#####################################################################

def fct_condition(filtres: dict):
    """
    Fonction pour générer les conditions WHERE et les paramètres pour une requête SQL
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'colonne1': valeur1, 'colonne2': valeur2}
    :return: Tuple contenant la condition WHERE sous forme de chaîne et les paramètres à utiliser dans la requête
    """
    conditions = []
    params = []
    for cle, valeur in filtres.items():
        if valeur:
            conditions.append(f"{cle} = %s")
            params.append(valeur)
    return " AND ".join(conditions), tuple(params)

def obtenir_valeurs_distinctes(table, colonne):
    """
    Fonction pour obtenir les valeurs distinctes d'une colonne dans une table
    :param table: Nom de la table dans la base de données
    :param colonne: Nom de la colonne pour laquelle on veut les valeurs distinctes
    :return: Liste de dictionnaires contenant les valeurs distinctes
    """
    requete = f"""
    SELECT DISTINCT
        {colonne}
    FROM
        {table}
    """
    resultat = pd.read_sql_query(requete, engine)
    return resultat.to_dict(orient='records')

# Fonction générique pour obtenir des données filtrées
def obtenir_donnees_filtrees(table, colonnes, jointures, filtres) -> pd.DataFrame:
    """
    Fonction pour obtenir des données d'une table avec des filtres appliqués
    :param table: Nom de la table dans la base de données
    :param colonnes: Liste des colonnes à sélectionner
    :param jointures: Chaîne de jointures SQL à appliquer
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'colonne1': valeur1, 'colonne2': valeur2}
    :return: DataFrame contenant les données filtrées
    """
    condi_where, params = fct_condition(filtres)
    requete = f"""
    SELECT
        {', '.join(colonnes)}
    FROM
        {table}
    {jointures}
    WHERE
        {condi_where};
    """
    # Correction ici : transformer params en tuple
    info = pd.read_sql_query(requete, engine, params=tuple(params))
    return info

# Fonction générique pour obtenir des données
def obtenir_donnees(table, colonnes, jointures) -> pd.DataFrame:
    """
    Fonction pour obtenir des données d'une table sans filtres
    :param table: Nom de la table dans la base de données
    :param colonnes: Liste des colonnes à sélectionner
    :param jointures: Chaîne de jointures SQL à appliquer
    :return: DataFrame contenant les données de la table
    """
    requete = f"""
    SELECT
        {', '.join(colonnes)}
    FROM
        {table}
    {jointures}
    """
    # Correction ici : transformer params en tuple
    info = pd.read_sql_query(requete, engine)
    return info

#####################################################################
# EXEMPLE D'UTILISATION POUR LES TABLES
#####################################################################

# Exemple d'utilisation pour la table Ouvrage
def obtenir_info_ouvrage(filtres=None):
    """
    Fonction pour obtenir des informations sur les ouvrages
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'nom_ouvrage': 'AUDELONCOURT'}
    :return: DataFrame contenant les informations sur les ouvrages
    """
    table = "ouvrages"
    colonnes = [
        'ouvrages.code_ouvrage', #varchar300 PK
        'ouvrages.nom_ouvrage', #varchar200
        'ouvrages.date_exploitation_debut', #DATE
        'ouvrages.date_exploitation_fin', #DATE
        'ouvrages.code_type_milieu', #varchar100
        'departement.libelle_departement', #VARCHAR(150)
        'ouvrages.longitude', #DECIMAL(9,6)
        'ouvrages.latitude', #DECIMAL(9,6)
        'ouvrages.code_departement'# FK
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = ouvrages.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Point Prelevement
def obtenir_info_prelevement(filtres=None):
    """
    Fonction pour obtenir des informations sur les points de prélèvement
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'nom_point_prelevement': 'ELECTRICITE DE FRANCE'}
    :return: DataFrame contenant les informations sur les points de prélèvement
    """
    table = "pt_prelevement"
    colonnes = [
        'pt_prelevement.code_point_prelevement', #varchar300 PK
        'pt_prelevement.code_ouvrage', #Varchar200
        'pt_prelevement.nom_point_prelevement', #varchar200
        'pt_prelevement.date_exploitation_debut', #DATE
        'pt_prelevement.code_type_milieu', #varchar100
        'pt_prelevement.libelle_nature', #varchar150
        'pt_prelevement.code_departement', #FK
        'departement.libelle_departement' # pour avoir le nom du département
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = pt_prelevement.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Commune
def obtenir_info_commune(filtres=None):
    """
    Fonction pour obtenir des informations sur les communes
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'nom_commune': 'Craincourt'}
    :return: DataFrame contenant les informations sur les communes
    """
    table = "commune"
    colonnes = [
        'commune.nom_commune', #varchar500
        'commune.code_commune_insee', #PK
        'commune.code_departement'#FK
    ]
    jointures = """
    INNER JOIN departement ON departement.code_departement = commune.code_departement
    """
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

# Exemple d'utilisation pour la table Departement
def obtenir_info_departement(filtres=None):
    """
    Fonction pour obtenir des informations sur les départements
    :param filtres: Dictionnaire contenant les filtres à appliquer, par exemple {'code_departement': '12'}
    :return: DataFrame contenant les informations sur les départements
    """
    table = "departement"
    colonnes = [
        "departement.code_departement", #PK
        "departement.libelle_departement", #varchar500
    ]
    jointures = """"""  # Pas de jointure pour cette table
    if filtres:
        return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)
    else:
        return obtenir_donnees(table, colonnes, jointures)

#####################################################################
# TESTS
#####################################################################
# Décommenter pour exécuter les tests

# print(obtenir_info_ouvrage())
# print(obtenir_info_ouvrage({"nom_ouvrage": "AUDELONCOURT"}))
# print(obtenir_info_prelevement())
# print(obtenir_info_prelevement({"nom_point_prelevement": "ELECTRICITE DE FRANCE"}))
# print(obtenir_info_commune())
# print(obtenir_info_commune({"nom_commune": "Craincourt"}))
# print(obtenir_info_departement())
# print(obtenir_info_departement({"code_departement": "12"}))