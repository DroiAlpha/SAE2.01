import pandas as pd
import psycopg2

# Chemin relatif vers la base de données PostgreSQL
DBPARAMS = {
    "database": "eaufrance",
    "user": "yuri",
    "password": "yuri",
    "host": "10.10.47.80",
    "port": 5432
}

def connect_db():
    return psycopg2.connect(**DBPARAMS)

def fct_condition(filtres: dict) -> str:
    conditions = []
    params = []
    for cle, valeur in filtres.items():
        if valeur:
            conditions.append(f"{cle} = %s")
            params.append(valeur)
# Cette ligne join les conditions de filtrage (comme des 'colonne = valeur') avec "AND" pour former une clause WHERE complète.
# Exemple : "colonne1 = noob" AND "colonne2 = clemence" on voit les données de "noob" et de "clémence"
    return " AND ".join(conditions), params


def obtenir_valeurs_distinctes(table, colonne):
    conn = connect_db()
    requete = f"""
    SELECT DISTINCT
        {colonne}
    FROM
        {table}
    """
    resultat = pd.read_sql_query(requete, conn)
    conn.close()
    return resultat.to_dict(orient='records')

# Fonction générique pour obtenir des données filtrées
def obtenir_donnees_filtrees(table, colonnes, jointures, filtres) -> pd.DataFrame:
    """
    Méthode permettant d'obtenir des données qui seront filtrées
    """
    conn = connect_db()
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
    info = pd.read_sql_query(requete, conn, params=params)
    conn.close()
    return info

# Exemple d'utilisation pour la table Ouvrage
def obtenir_info_ouvrage(filtres):
    table = "Ouvrage"
    colonnes = [
        'code_ouvrage', #varchar300 PK
        'nom_ouvrage', #varchar200
        'date_exploitation_debut', #DATE
        'date_exploitation_fin', #DATE
        'code_type_milieu', #varchar100
        'libelle_departement', #VARCHAR(150)
        'longitude', #DECIMAL(9,6)
        'latitude', #DECIMAL(9,6)
        'code_departement'# FK
    ]
    jointures = """
    INNER JOIN Departement ON Departement.code_departement = Ouvrage.code_departement
    """
    return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)

# Exemple d'utilisation pour la table Point Prelevement
def obtenir_info_prelevement(filtres):
    table = "Point_Prelevement"
    colonnes = [
        'code_point_prelevement', #varchar300 PK
        'code_ouvrage', #Varchar200
        'nom_point_prelevement', #varchar200
        'date_exploitation_debut', #DATE
        'code_type_milieu', #varchar100
        'libelle_nature', #varchar150
        'code_departement'#FK
    ]
    jointures = """
    INNER JOIN Departement ON Departement.code_departement = Point_Prelevement.code_departement
    """
    return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)

# Exemple d'utilisation pour la table Commune
def obtenir_info_commune(filtres):
    table = "Commune"
    colonnes = [
        'nom_commune', #varchar500
        'code_commune_insee', #PK
        'code_departement'#FK
    ]
    jointures = """
    INNER JOIN Departement ON Departement.code_departement = Commune.code_departement
    """
    return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)

# Exemple d'utilisation pour la table Departement
def obtenir_info_departement(filtres):
    table = "Departement"
    colonnes = [
        "code_departement", #PK
        "libelle_departement", #varchar500
    ]
    jointures = """"""  # Pas de jointure pour cette table
    return obtenir_donnees_filtrees(table, colonnes, jointures, filtres)