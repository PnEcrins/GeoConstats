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
    data=DB.session.query(Constats).all()
    dataGeom = DB.session.query(func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326))).all()
    cnsts=[]
    #print(dataGeom[0])
    #print(data)
    cpt=0
    for i in data:
        #print(wkt)
        #print(dataGeom[cpt])
        geojson=dataGeom[cpt]
        cpt=cpt+1
        dico={}
        dico['geometry']=geojson
        dico['properties']={}
        dico['properties']['id_constat']=i.id_constat
        dico['properties']['date_attaque']=i.date_attaque
        dico['properties']['date_constat']=i.date_constat
        dico['properties']['nom_agent1']=i.nom_agent1
        dico['properties']['nom_agent2']=i.nom_agent2
        dico['properties']['proprietaire']=i.proprietaire
        dico['properties']['type_animaux']=i.type_animaux
        dico['properties']['nb_victimes_mort']=i.nb_victimes_mort
        dico['properties']['nb_victimes_blesse']=i.nb_victimes_blesse
        dico['properties']['statut']=i.statut
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
            nb_victimes_mort=data['nb_victimes_mort'],
            moment=data['moment'],
            chien=data['chien'],
            berger=data['berger'],
            valide=data['valide'],
        )
        DB.session.add(constats)
        DB.session.commit()
        return render_template('map.html')
    else:
        return render_template('add.html', title="Add_to_database", form=form )
