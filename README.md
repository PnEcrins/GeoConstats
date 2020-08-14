# GeoConstats

## 1. Préparation de l'environnement de travail

- Dans le terminal, executer la ligne de commande ``sudo apt-get install libpq-dev``. Executer ensuite la ligne de commande ``sudo apt-get install python-virtualenv``.
- Cloner le répertoire GeoConstats avec la ligne de commande ``git clone https://github.com/PnEcrins/GeoConstats.git``
- Dans le terminal, placez-vous dans le dossier GeoConstats ``cd GeoConstats`` et exécuter la commande suivante : ``virtualenv -p /usr/bin/python3 env``.

## 2. Préparation de la base de données
- Copier le fichier ``settings.ini.sample`` et le nommer ``settings.ini`` avec la ligne de commande ``cp settings.ini.sample settings.ini``
- Editer le fichier ``settings.ini`` avec les informations de la base de données avec la ligne de commande `` nano settings.ini``. Une fois les informations saisies, enregistrer le fichier en appuyant sur ctrl + o puis entrer puis crtl + x.
- Dans le terminal, executer la ligne de commande ``./install_db.sh``.

## 3. Mise en relation de la base de données avec l'application

- Dans le dossier contenant les fichiers téléchargés, copier ``config.py.sample`` et le renommer ``config.py`` avec la ligne ``cp config.py.sample config.py``. Remplir les paramètres de connexion à la base de données et l'url de l'application. Remplir ces paramètres en fonction de vos valeurs. Enregistrer avec ctrl + o puis entrer puis quitter le fichier avec ctrl + x.

## 4. Lancement de l'application

- Ouvrir le fichier ``geoconstats_supervisor.conf`` avec la ligne de commande `` nano geoconstats_supervisor.conf``et remplacer ``<MY_APP_PATH>`` par le chemin de la racine de l'application
- Copier ce fichier dans la conf supervisor: ``sudo cp geoconstats_supervisor.conf /etc/supervisor/conf.d``
- Relancer le supervisor `` sudo supervisorctl reread`` `` sudo supervisorctl reload``

## 5. Réalisation de la configuration apache

- Créer un nouveau site: ``sudo nano /etc/apache2/sites-available/geoconstats.conf``
- Coller la configuration suivante:

    
    <Location /geoconstats >
      ProxyPass http://127.0.0.1:5000
      ProxyPassReverse http://127.0.0.1:5000
    </Location>

- Lancer les commandes suivantes:

    
    ``sudo a2enmod proxy``
    ``sudo a2enmod proxy_http``
   `` sudo a2ensite geoconstats``


## 6. Lancement en mode dev

- De retour dans la console dans le dossier GeoConstats, activer le virtualenv avec la ligne de commande ``source env/bin/activate``
- A ce moment, on rentre dans l'environnement de travail.
- On commence par charger les librairies nécessaires au fonctionnement de l'application avec la ligne de commande : ``pip install -r requirements.txt``. Il n'est utile de lancer cette commande qu'une seule fois tant qu'il n'y a pas de changements ou d'ajouts dans la liste des librairies.
- Ensuite, on lance l'application avec la ligne de commande : ``python3 run.py``.
- Dans un navigateur web, rentrer l'url http://localhost:5000/ pour accéder à l'application.

**Auteur** : Raphaël Bres / Juillet 2020

Inspiré de l'application Flask-leaflet-example (https://github.com/PnEcrins/Flask-leaflet-example)
