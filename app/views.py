from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from .env import DB
from app.models import Constats,Declaratif,bib_statut, bib_type_animaux
from app.forms import LoginForm, DeclaForm
from sqlalchemy import func
import json
from shapely.geometry import Point, shape
from shapely import wkb
from shapely.ops import transform
from geoalchemy2.shape import to_shape, from_shape

app = Flask(__name__)


@app.route("/")
@app.route("/map")
def map():
    """
    Lance la "page d'acceuil" avec une carte + une liste avec toutes les données
    """
    dataGeom = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326))).order_by(Constats.id_constat).all()
    cnsts=[]
    for d in dataGeom:
        geojson=json.loads(d[1])
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
    return render_template('map.html', title='Map', Constats=cnsts)

@app.route('/form',methods=['GET', 'POST'])
def form():
    """
    Lance la page de formulaire d'ajout de données
    """
    form = LoginForm()
    form.statut.choices=[]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]
    form.type_animaux.choices=[]
    dataAnimaux=DB.session.query(bib_type_animaux)
    for da in dataAnimaux:
        form.type_animaux.choices+=[(da.id,da.nom)]    
    return render_template('add.html', title="Add_to_database", form=form )

@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Réalise l'ajout de données dans la BD
    """
    data=request.json
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(data['geom']['lng'],data['geom']['lat']),4326),2154)))
    json2154=json.loads(p2154[0][0])
    constats = Constats(
        date_attaque=data['date_attaque'],
        date_constat=data['date_constat'],
        nom_agent1=data['nom_agent1'],
        nom_agent2=data['nom_agent2'],
        proprietaire=data['proprietaire'],
        type_animaux=data['type_animaux'],
        nb_victimes_mort=data['nb_victimes_mort'],
        nb_victimes_blesse=data['nb_victimes_blesse'],
        statut=data['statut'],
        the_geom_point=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154)
    )    
    DB.session.add(constats)
    DB.session.commit()
    return redirect(url_for('map'))

@app.route('/update/<idc>', methods=['GET', 'POST'])
def update(idc):
    """
    Lance la page de mise à jour d'une donnée
    """
    dataGeom = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326))).filter(Constats.id_constat==idc).all()
    geojson=json.loads(dataGeom[0][1])
    dico={}
    dico['geometry']=geojson
    dico['properties']={}
    dico['properties']['id_constat']=dataGeom[0][0].id_constat
    dico['properties']['date_attaque']=dataGeom[0][0].date_attaque
    dico['properties']['date_constat']=dataGeom[0][0].date_constat
    dico['properties']['nom_agent1']=dataGeom[0][0].nom_agent1
    dico['properties']['nom_agent2']=dataGeom[0][0].nom_agent2
    dico['properties']['proprietaire']=dataGeom[0][0].proprietaire
    dico['properties']['type_animaux']=dataGeom[0][0].type_animaux
    dico['properties']['nb_victimes_mort']=dataGeom[0][0].nb_victimes_mort
    dico['properties']['nb_victimes_blesse']=dataGeom[0][0].nb_victimes_blesse
    dico['properties']['statut']=dataGeom[0][0].statut
    form = LoginForm()
    form.statut.choices=[]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]
    form.type_animaux.choices=[]
    dataAnimaux=DB.session.query(bib_type_animaux)
    for da in dataAnimaux:
        form.type_animaux.choices+=[(da.id,da.nom)] 
    form.type_animaux.default=dataGeom[0][0].type_animaux
    form.statut.default=dataGeom[0][0].statut
    form.process()        
    return render_template('update.html', title='Map',form=form,Constats=dico)

@app.route('/updateDB',methods=['GET', 'POST'])
def updateDB():
    """
    Réalise les mises à jour dans la BD
    """
    data=request.json
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(data['geom']['lng'],data['geom']['lat']),4326),2154)))
    json2154=json.loads(p2154[0][0])    
    cst=DB.session.query(Constats).filter(Constats.id_constat==data['id_constat']).one()
    cst.date_attaque=data['date_attaque']
    cst.date_constat=data['date_constat']
    cst.nom_agent1=data['nom_agent1']
    cst.nom_agent2=data['nom_agent2']
    cst.proprietaire=data['proprietaire']
    cst.type_animaux=data['type_animaux']
    cst.nb_victimes_mort=data['nb_victimes_mort']
    cst.nb_victimes_blesse=data['nb_victimes_blesse']
    cst.statut=data['statut']
    cst.the_geom_point=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154)
    DB.session.commit()       
    return redirect(url_for('map'))
    
@app.route('/delete/<idc>', methods=['GET', 'POST'])
def delete(idc):
    """
    Réalise la suppression d'un constat
    """
    dataGeom = DB.session.query(Constats).filter(Constats.id_constat==idc).delete()
    DB.session.commit()
    return redirect(url_for('map'))

@app.route('/decla')
def decla():
    dataGeom = DB.session.query(Declaratif)
    decla=[]
    for d in dataGeom:
        dico={}
        dico['id_constat_d']=d.id_constat_d
        dico['date_attaque_d']=d.date_attaque_d
        dico['date_constat_d']=d.date_constat_d
        dico['lieu_dit']=d.lieu_dit
        dico['proprietaire_d']=d.proprietaire_d
        dico['type_animaux_d']=d.type_animaux_d
        dico['nb_victimes_mort_d']=d.nb_victimes_mort_d
        dico['nb_victimes_blesse_d']=d.nb_victimes_blesse_d
        dico['statut_d']=d.statut_d
        decla.append(dico)
        print(dico)
    return render_template('decla.html', title='Declaratif', Declaratifs=decla)
@app.route('/deleteDecla/<idc>',methods=['GET', 'POST'])
def deleteDecla(idc):
    dataGeom = DB.session.query(Declaratif).filter(Declaratif.id_constat_d==idc).delete()
    DB.session.commit()
    return redirect(url_for('decla'))

@app.route ('/formDecla',methods=['GET', 'POST'])
def formDecla():
    form = DeclaForm()
    form.statut_d.choices=[]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut_d.choices+=[(ds.id,ds.nom)]
    form.type_animaux_d.choices=[]
    dataAnimaux=DB.session.query(bib_type_animaux)
    for da in dataAnimaux:
        form.type_animaux_d.choices+=[(da.id,da.nom)]  
    return render_template('addDecla.html', title="Add_to_database", form=form )

@app.route('/addDecla', methods=['GET', 'POST'])
def addDecla():
    data=request.json
    decla=Declaratif(
        date_attaque_d=data['date_attaque_d'],
        date_constat_d=data['date_constat_d'],
        lieu_dit=data['lieu_dit'],
        proprietaire_d=data['proprietaire_d'],
        type_animaux_d=data['type_animaux_d'],
        nb_victimes_mort_d=data['nb_victimes_mort_d'],
        nb_victimes_blesse_d=data['nb_victimes_blesse_d'],
        statut_d=data['statut_d']            
    )
    DB.session.add(decla)
    DB.session.commit()
    return redirect(url_for('decla'))

@app.route('/updateDecla/<idc>', methods=['GET', 'POST'])
def updateDecla(idc):
     dataGeom = DB.session.query(Declaratif).filter(Declaratif.id_constat_d==idc).all()
     dico={}
     dico['id_constat_d']=dataGeom[0].id_constat_d
     dico['date_attaque_d']=dataGeom[0].date_attaque_d
     dico['date_constat_d']=dataGeom[0].date_constat_d
     dico['lieu_dit']=dataGeom[0].lieu_dit
     dico['proprietaire_d']=dataGeom[0].proprietaire_d
     dico['type_animaux_d']=dataGeom[0].type_animaux_d
     dico['nb_victimes_mort_d']=dataGeom[0].nb_victimes_mort_d
     dico['nb_victimes_blesse_d']=dataGeom[0].nb_victimes_blesse_d
     dico['statut_d']=dataGeom[0].statut_d     
     form = DeclaForm()
     form.statut_d.choices=[]
     dataStatut=DB.session.query(bib_statut)
     for ds in dataStatut:
        form.statut_d.choices+=[(ds.id,ds.nom)]
     form.type_animaux_d.choices=[]
     dataAnimaux=DB.session.query(bib_type_animaux)
     for da in dataAnimaux:
        form.type_animaux_d.choices+=[(da.id,da.nom)]
     form.type_animaux_d.default=dataGeom[0].type_animaux_d
     form.statut_d.default=dataGeom[0].statut_d
     form.process()
     return render_template('updateDecla.html', title='Map',form=form,Declaratif=dico)

@app.route('/updateDBDecla',methods=['GET', 'POST'])
def updateDBDecla():
    data=request.json
    cst=DB.session.query(Declaratif).filter(Declaratif.id_constat_d==data['id_constat_d']).one()
    cst.date_attaque_d=data['date_attaque_d']
    cst.date_constat_d=data['date_constat_d']
    cst.lieu_dit=data['lieu_dit']
    cst.proprietaire_d=data['proprietaire_d']
    cst.type_animaux_d=data['type_animaux_d']
    cst.nb_victimes_mort_d=data['nb_victimes_mort_d']
    cst.nb_victimes_blesse_d=data['nb_victimes_blesse_d']
    cst.statut_d=data['statut_d']
    DB.session.commit()       
    return redirect(url_for('decla'))    