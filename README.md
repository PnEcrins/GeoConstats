# GeoConstats

1. Préparation de l'environnement de travail

Créer un dossier dans lequel placer les fichiers télechargés.
Dans le terminal, se placer dans le dossier créé à l'étape précédente et lancer la ligne de commande suivante : python3 -m env venv

2. Préparation de la base de données

Dans PgAdmin, créer une base de données.
Dans le schéma postgres, entrer l'instruction SQL suivante : create extension postgis;
Ensuite, dans la base de données, aller dans l'éditeur SQL et ouvrir le fichier scriptSQL_Constats.sql. Attention, ce fichier contient deux lignes qui sont insérées directement dans la table créée.

3. Mise en relation de la base de données avec l'application

Dans le sous-dossier app, éditer le fichier routes.py. En dessous de la liste des librairies importées et de l'instanciation de l'application se trouve les paramètres de connexion à la base de données. Remplir ces paramètres en fonction de vos valeurs.
Enregistrer les modifications.

4. Lancement

De retour dans la console dans le dossier où la ligne python3 -m env venv a été lancée, exécuter la ligne de commande env\Scripts\activate
A ce moment, on rentre dans l'environnement de travail.
On commence par charger les librairies nécessaires au fonctionnementde l'application avec la ligne de commande pip install -r requirements.txt . Il n'est utile de lancer cette commande qu'une seule fois tant qu'il n'y a pas de changements ou d'ajouts dans la liste des librairies.
Ensuite, on lance l'application avec la ligne de commande python run.py .
Dans un navigateur web, rentrer l'url http://localhost:5000/ pour accéder à la carte ou http://localhost:5000/form pour accéder au formulaire de saisie.

**Auteur** : Raphaël Bres / Juin 2020

Inspiré de l'application réalisé à l'url https://github.com/PnEcrins/Flask-leaflet-example
