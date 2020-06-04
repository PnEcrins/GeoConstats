from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from .env import DB
from app.models import Constats
from app.forms import LoginForm
from sqlalchemy import func
import json
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

app = Flask(__name__)

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://raph:Raphael18@localhost:5432/geoConstat"

with app.app_context():
    from .models import Constats
    from app.forms import LoginForm
    from .env import DB
    DB.init_app(app)
    #DB.create_all()

    Constats.query.all()


@app.route("/")
@app.route("/map")
def map():
    dataGeom = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326))).all()
    cnsts=[]
    for d in dataGeom:
        geojson=geojson=json.loads(d[1])
        print(geojson)
        dico={}
        dico['geometry']=geojson
        dico['properties']={}
        dico['properties']['id_constat']=d[0].id_constat
        dico['properties']['date_attaque']=d[0].date_attaque
        dico['properties']['date_constat']=d[0].date_constat
        dico['properties']['nom_agent1']=d[0].nom_agent1
        dico['properties']['nom_agent2']=d[0].nom_agent2
        dico['properties']['proprietaire']=d[0].proprietaire
        dico['properties']['type_animaux']=d[0].type_animaux
        dico['properties']['nb_victimes_mort']=d[0].nb_victimes_mort
        dico['properties']['nb_victimes_blesse']=d[0].nb_victimes_blesse
        dico['properties']['statut']=d[0].statut
        cnsts.append(dico)        
    print(cnsts)
    return render_template('map.html', title='Map', Constats=cnsts)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = LoginForm()
    if form.validate_on_submit():
        data = request.form
        constats = Constats(
            date_attaque=data['date_attaque'],
            date_constat=data['date_constat'],
            nom_agent1=data['nom_agent1'],
            nom_agent2=data['nom_agent2'],
            proprietaire=data['proprietaire'],
            type_animaux=data['type_animaux'],
            nb_victimes_mort=data['nb_victimes_mort'],
            nb_victimes_blesse=data['nb_victimes_blesse'],
            statut=data['statut']
            #geom : a convertir en wkb et en 2154
        )
        DB.session.add(constats)
        DB.session.commit()
        return render_template('map.html')
    else:
        return render_template('add.html', title="Add_to_database", form=form )
