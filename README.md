# SAE2.01 - README.md

## Informations importantes
- Fonctions utilisées dans graphiques.py non-définies dans chroniques.py -> Mise en commentaire temporaire des fonctions obsolètes
- Fonctions en doubles dans graphiques.py -> Mise en commentaire temporaire des fonctions inutiles
- Fichier de sauvegarde de la carte Folium mis à jour automtiquement à cahque lancement de l'application -> Impossibilité d'ajouter une structure HTML et un style CSS pour formater cette page

# Modifications apportées
- Uniformisation de la documentation (commentaires et docstring) dans chaque fichier 

## Comment on va procéder pour la SAE 2.01 ?
  - On utilise une architecture MVC (Modèle-Vue-Contrôleur)
  - On développera en même temps chacune des couches
  - ATTENTION POUR LE MODELE : FAIRE UNE CLASSE

## Répartition des couches et des tâches : 
  - Massi et Willy -> Modèle : faire les différentes méthodes pour communiquer avec la base de données
  - Théo et Amaury -> Contrôleur : faire la liaison entre le modèle et la vue
  - Clémence et Idriss -> Vue : faire les pages HTML, le style CSS et éventuellement des animations JS

## Tâches principales : 
  - Création de la maquette sur Canva :
      * Quelles seront les différentes fonctionnalités du site Web ?
      * Quelle sera la structure des pages Web ?
      * À quoi ressembleront les pages du site ?
  - Création du site -> Approche MVC
  - Réalisation de tests et validation des codes

## Comment développer chacune des couches en même temps ? -> Grâce à la maquette
  - Tout part de la maquette, on se basera dessus pour faire notre IHM :
    - Vue -> programmer littéralement la maquette sans accès à la base de données
    - Contrôleur -> on aura les différentes routes grace à la maquette
    - Modèle -> comme on saura quelles données on veut avec la maquette, on saura quelles méthodes faire
  - Si vous voulez faire ou donner des suggestions de modifications -> PREVENIR TOUT LE MONDE POUR EN DISCUTER

> EN RÉSUMÉ -> NE PAS SE JETER DANS DÉVELOPPEMENT DU CODE ET BIEN FAIRE LA MAQUETTE EN AMONT