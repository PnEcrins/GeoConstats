# GeoConstats

## 1. Windows

### 1.1. Préparation de l'environnement de travail

- Créer un dossier dans lequel placer les fichiers télechargés.
- Dans le terminal, se placer dans le dossier créé à l'étape précédente et lancer la ligne de commande suivante : ``python3 -m env venv``

### 1.2. Préparation de la base de données

- Dans PgAdmin, créer une base de données.
- Dans la BDD, entrer l'instruction SQL suivante : ``create extension postgis;``
- Ensuite, dans la base de données, aller dans l'éditeur SQL et ouvrir le fichier ``scriptSQL_Constats.sql``. Attention, ce fichier contient deux lignes qui sont insérées directement dans la table créée.

### 1.3. Mise en relation de la base de données avec l'application

- Dans le dossier contenant les fichiers téléchargés, éditer le fichier ``config.py``. Vous trouverez les paramètres de connexion à la base de données. Remplir ces paramètres en fonction de vos valeurs.
- Enregistrer les modifications.

### 1.4. Lancement

- De retour dans la console dans le dossier où la ligne ``python3 -m env venv`` a été lancée, exécuter la ligne de commande ``env\Scripts\activate``.
- A ce moment, on rentre dans l'environnement de travail.
- On commence par charger les librairies nécessaires au fonctionnement de l'application avec la ligne de commande ``pip install -r requirements.txt``. Il n'est utile de lancer cette commande qu'une seule fois tant qu'il n'y a pas de changements ou d'ajouts dans la liste des librairies.
- Ensuite, on lance l'application avec la ligne de commande ``python run.py``.
- Dans un navigateur web, rentrer l'url http://localhost:5000/ pour accéder à l'application.

## 2. Ubuntu

### 2.1. Préparation de l'environnement de travail

- Dans le terminal, executer la ligne de commande ``sudo apt-get install libpq-dev``. Executer ensuite la ligne de commande ``sudo apt-get install python-virtualenv``.
- Cloner le répertoire GeoConstats avec la ligne de commande ``git clone https://github.com/PnEcrins/GeoConstats.git``
- Dans le terminal, placez-vous dans le dossier GeoConstats ``cd GeoConstats`` et exécuter la commande suivante : ``virtualenv -p /usr/bin/python3 env``.

### 2.2. Préparation de la base de données
- Copier le fichier ``settings.ini.sample`` et le nommer ``settings.ini``
- Editer le fichier ``settings.ini`` avec les informations de la base de données.
- Dans le terminal, executer la ligne de commande ``./install_db.sh``.

### 2.3. Mise en relation de la base de données avec l'application

- Dans le dossier contenant les fichiers téléchargés, éditer le fichier ``config.py.sample`` et le renommer ``config.py``. Vous trouverez les paramètres de connexion à la base de données. Remplir ces paramètres en fonction de vos valeurs.
- Enregistrer les modifications.

#### 2.4. Lancement

- De retour dans la console dans le dossier GeoConstats, activer le virtualenv avec la ligne de commande ``source env/bin/activate``
- A ce moment, on rentre dans l'environnement de travail.
- On commence par charger les librairies nécessaires au fonctionnement de l'application avec la ligne de commande : ``pip install -r requirements.txt``. Il n'est utile de lancer cette commande qu'une seule fois tant qu'il n'y a pas de changements ou d'ajouts dans la liste des librairies.
- Ensuite, on lance l'application avec la ligne de commande : ``python3 run.py``.
- Dans un navigateur web, rentrer l'url http://localhost:5000/ pour accéder à l'application.

**Auteur** : Raphaël Bres / Juillet 2020

Inspiré de l'application Flask-leaflet-example (https://github.com/PnEcrins/Flask-leaflet-example)
