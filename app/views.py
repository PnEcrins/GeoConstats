from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from .env import DB
from app.models import Constats,Declaratif,bib_statut, bib_type_animaux, l_areas
from app.forms import ConstatForm, DeclaForm, FilterForm
from sqlalchemy import func, extract
import json
from shapely.geometry import Point, shape
from shapely import wkb
from shapely.ops import transform
from geoalchemy2.shape import to_shape, from_shape
from datetime import datetime
import pyexcel as pe
import io
import csv

app = Flask(__name__)



@app.route("/")
@app.route("/map")
def map():
    """
    Lance la "page d'acceuil" avec une carte + une liste avec toutes les données
    """
    #Recuperation des filtres et requete sur la table
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
    dataAnnee=DB.session.query(func.distinct(extract('year',Constats.date_constat)).label("date"))
    query = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326)))
    
    form=FilterForm()
    form.animaux.choices=[(0,"")]
    for da in dataAnimaux:
        form.animaux.choices+=[(da.id,da.nom)]  
    #Solution envisagee: demarer les id dans la base a 2 au lieu de 1 et donner le 1 au blanc dans le python   
    form.statut.choices=[(0,"")]
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]
    form.date.choices=[(0,"")]   
    for dy in dataAnnee:
        form.date.choices+=[(int(dy[0]),int(dy[0]))]       
    if 'date' in filter_query:
        if filter_query['date'] != "0":
            #Filtre différent pour date car meme si il est null il est envoye dans l'url. Le 1er if est utile au chargement car il n'apparait pas dans l'url
            query = query.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "0":
            query = query.filter(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query:
        if filter_query['statut'] != "0":
            query = query.filter(Constats.statut == filter_query['statut'])   
    dataGeom =  query.order_by(Constats.id_constat).all()  


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
        for da in dataAnimaux:
            if da.id==d[0].type_animaux:
                dico['properties']['type_animaux']=da.nom
        dico['properties']['nb_victimes_mort']=d[0].nb_victimes_mort
        dico['properties']['nb_victimes_blesse']=d[0].nb_victimes_blesse
        for ds in dataStatut:
            if ds.id==d[0].statut:
                dico['properties']['statut']=ds.nom
        dico['properties']['nb_jour_agent']=d[0].nb_jour_agent
        for dsec in dataSecteur:
            if dsec.id_area == d[0].id_secteur:
                dico['properties']['secteur']=dsec.area_name
            if dsec.id_area == d[0].id_commune:
                dico['properties']['commune']=dsec.area_name            
        cnsts.append(dico)        
    return render_template('map.html', title='Map', Constats=cnsts,form=form)

@app.route('/form',methods=['GET', 'POST'])
def form():
    """
    Lance la page de formulaire d'ajout de données
    """
    form = ConstatForm()
    form.statut.choices=[(0,"")]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]
    form.type_animaux.choices=[(0,"")]
    dataAnimaux=DB.session.query(bib_type_animaux)
    for da in dataAnimaux:
        form.type_animaux.choices+=[(da.id,da.nom)]    
    return render_template('add.html', title="Add_to_database", form=form )

@app.route('/add', methods=['GET', 'POST'])
def add():
    """
    Réalise l'ajout de données dans la BD
    """
    data = request.form 
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(float(data['geomlng']),float(data['geomlat'])),4326),2154)))
    json2154=json.loads(p2154[0][0])
    changeAnimaux=data['type_animaux']
    if data['type_animaux']=="0":
        changeAnimaux=None
    changeStatut=data['statut']
    if data['statut']=="0":
        changeStatut=1        
    constats = Constats(
        date_attaque=data['date_attaque'],
        date_constat=data['date_constat'],
        nom_agent1=data['nom_agent1'],
        nom_agent2=data['nom_agent2'],
        proprietaire=data['proprietaire'],
        type_animaux=changeAnimaux,
        nb_victimes_mort=data['nb_victimes_mort'],
        nb_victimes_blesse=data['nb_victimes_blesse'],
        statut=changeStatut,
        nb_jour_agent=data['nb_jour_agent'],
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
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
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
    for da in dataAnimaux:
        if da.id==dataGeom[0][0].type_animaux:
            dico['properties']['type_animaux_name']=da.nom    
    dico['properties']['nb_victimes_mort']=dataGeom[0][0].nb_victimes_mort
    dico['properties']['nb_victimes_blesse']=dataGeom[0][0].nb_victimes_blesse
    dico['properties']['statut']=dataGeom[0][0].statut
    for ds in dataStatut:
       if ds.id==dataGeom[0][0].statut:
           dico['properties']['statut_name']=ds.nom
    dico['properties']['nb_jour_agent']=dataGeom[0][0].nb_jour_agent       
    for dsec in dataSecteur:
       if dsec.id_area == dataGeom[0][0].id_secteur:
           dico['properties']['secteur']=dsec.area_name
       if dsec.id_area == dataGeom[0][0].id_commune:
           dico['properties']['commune']=dsec.area_name    
    form = ConstatForm()
    form.statut.choices=[(0,"")]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]
    form.type_animaux.choices=[(0,"")]
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
    data=request.form
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(float(data['geomlng']),float(data['geomlat'])),4326),2154)))
    json2154=json.loads(p2154[0][0])    
    changeAnimaux=data['type_animaux']
    if data['type_animaux']=="0":
        changeAnimaux=None
    changeStatut=data['statut']
    if data['statut']=="0":
        changeStatut=1
    cst=DB.session.query(Constats).filter(Constats.id_constat==data['id_constat']).one()
    cst.date_attaque=data['date_attaque']
    cst.date_constat=data['date_constat']
    cst.nom_agent1=data['nom_agent1']
    cst.nom_agent2=data['nom_agent2']
    cst.proprietaire=data['proprietaire']
    cst.type_animaux=changeAnimaux
    cst.nb_victimes_mort=data['nb_victimes_mort']
    cst.nb_victimes_blesse=data['nb_victimes_blesse']
    cst.statut=changeStatut
    cst.nb_jour_agent=data['nb_jour_agent']
    cst.the_geom_point=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154)
    DB.session.commit()       
    return redirect(url_for('map'))
    
@app.route('/delete/<idc>', methods=['GET', 'POST'])
def delete(idc):
    """
    Réalise la suppression d'un constat déclaratif
    """
    dataGeom = DB.session.query(Constats).filter(Constats.id_constat==idc).delete()
    DB.session.commit()
    return redirect(url_for('map'))

@app.route('/download', methods=['GET', 'POST'])
def download():
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
    query = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326)))
    
    if 'date' in filter_query:
        if filter_query['date'] != "":
            query = query.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query:
        query = query.filter(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query:
        query = query.filter(Constats.statut == filter_query['statut'])   
    dataGeom =  query.order_by(Constats.id_constat).all()  
    
    cnsts=[]
    for d in dataGeom:
        geojson=json.loads(d[1])
        dico={}
        dico['id_constat']=d[0].id_constat
        dico['date_attaque']=d[0].date_attaque
        dico['date_constat']=d[0].date_constat
        dico['nom_agent1']=d[0].nom_agent1
        dico['nom_agent2']=d[0].nom_agent2
        dico['proprietaire']=d[0].proprietaire
        for da in dataAnimaux:
            if da.id==d[0].type_animaux:
                dico['type_animaux']=da.nom
        dico['nb_victimes_mort']=d[0].nb_victimes_mort
        dico['nb_victimes_blesse']=d[0].nb_victimes_blesse
        for ds in dataStatut:
            if ds.id==d[0].statut:
                dico['statut']=ds.nom
        dico['nb_jour_agent']=d[0].nb_jour_agent
        for dsec in dataSecteur:
            if dsec.id_area == d[0].id_secteur:
                dico['secteur']=dsec.area_name
            if dsec.id_area == d[0].id_commune:
                dico['commune']=dsec.area_name         
        dico['x']=geojson['coordinates'][1]
        dico['y']=geojson['coordinates'][0]
        cnsts.append(dico)       
    si = io.StringIO()
    cw = csv.DictWriter(si,fieldnames=dico.keys())
    cw.writeheader()
    cw.writerows(cnsts)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=constats-"+datetime.now().strftime('%d-%b-%Y--%H-%M')+".csv"
    output.headers["Content-type"] = "text/csv"
    return output
   
@app.route('/data/<idc>')
def data(idc):
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
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
    for da in dataAnimaux:
        if da.id==dataGeom[0][0].type_animaux:
            dico['properties']['type_animaux_name']=da.nom    
    dico['properties']['nb_victimes_mort']=dataGeom[0][0].nb_victimes_mort
    dico['properties']['nb_victimes_blesse']=dataGeom[0][0].nb_victimes_blesse
    dico['properties']['statut']=dataGeom[0][0].statut
    for ds in dataStatut:
       if ds.id==dataGeom[0][0].statut:
           dico['properties']['statut_name']=ds.nom
    dico['properties']['nb_jour_agent']=dataGeom[0][0].nb_jour_agent       
    for dsec in dataSecteur:
       if dsec.id_area == dataGeom[0][0].id_secteur:
           dico['properties']['secteur']=dsec.area_name
       if dsec.id_area == dataGeom[0][0].id_commune:
           dico['properties']['commune']=dsec.area_name  
    return render_template('data.html', title='Map',Constats=dico)
    
    
    
@app.route('/decla')
def decla():
    """
    Lance la page de consultation des constats déclaratifs avec une carte + une liste avec toutes les données
    """    
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
    dataAnnee=DB.session.query(func.distinct(extract('year',Declaratif.date_constat_d)).label("date"))
    query = DB.session.query(Declaratif,func.ST_AsGeoJson(func.ST_Transform(Declaratif.geom,4326)))
    
    form=FilterForm()
    form.animaux.choices=[(0,"")]
    for da in dataAnimaux:
        form.animaux.choices+=[(da.id,da.nom)] 
    form.statut.choices=[(0,"")]    
    for ds in dataStatut:
        form.statut.choices+=[(ds.id,ds.nom)]  
    form.date.choices=[(0,"")]   
    for dy in dataAnnee:
        form.date.choices+=[(int(dy[0]),int(dy[0]))]    
    if 'date' in filter_query:
        if filter_query['date'] != "0":
            query = query.filter(extract('year',Declaratif.date_constat_d) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "0":
            query = query.filter(Declaratif.type_animaux_d == filter_query['animaux'])
    if 'statut' in filter_query:
        if filter_query['statut'] != "0":
            query = query.filter(Declaratif.statut_d == filter_query['statut'])       
    dataGeom=query.order_by(Declaratif.id_constat_d).all()
 
    decla=[]
    for d in dataGeom:
        geojson=json.loads(d[1])
        dico={}
        dico['geometry']=geojson
        dico['properties']={}
        dico['properties']['id_constat_d']=d[0].id_constat_d
        dico['properties']['date_attaque_d']=d[0].date_attaque_d
        dico['properties']['date_constat_d']=d[0].date_constat_d
        dico['properties']['lieu_dit']=d[0].lieu_dit
        dico['properties']['proprietaire_d']=d[0].proprietaire_d
        for da in dataAnimaux:
            if da.id==d[0].type_animaux_d:
                dico['properties']['type_animaux_d']=da.nom
        dico['properties']['nb_victimes_mort_d']=d[0].nb_victimes_mort_d
        dico['properties']['nb_victimes_blesse_d']=d[0].nb_victimes_blesse_d
        for ds in dataStatut:
            if ds.id==d[0].statut_d:        
                dico['properties']['statut_d']=ds.nom
        for dsec in dataSecteur:
            if dsec.id_area == d[0].id_secteur_d:
                dico['properties']['secteur_d']=dsec.area_name  
            if dsec.id_area == d[0].id_commune_d:
                dico['properties']['commune_d']=dsec.area_name                 
        decla.append(dico)
    return render_template('decla.html', title='Declaratif', Declaratifs=decla,form=form)

@app.route('/deleteDecla/<idc>',methods=['GET', 'POST'])
def deleteDecla(idc):
    """
    Réalise la suppression d'un constat déclaratif
    """
    dataGeom = DB.session.query(Declaratif).filter(Declaratif.id_constat_d==idc).delete()
    DB.session.commit()
    return redirect(url_for('decla'))

@app.route ('/formDecla',methods=['GET', 'POST'])
def formDecla():
    """
    Lance la page de formulaire d'ajout de données
    """
    form = DeclaForm()
    form.statut_d.choices=[(0,"")]
    dataStatut=DB.session.query(bib_statut)
    for ds in dataStatut:
        form.statut_d.choices+=[(ds.id,ds.nom)]
    form.type_animaux_d.choices=[(0,"")]
    dataAnimaux=DB.session.query(bib_type_animaux)
    for da in dataAnimaux:
        form.type_animaux_d.choices+=[(da.id,da.nom)]  
    return render_template('addDecla.html', title="Add_to_database", form=form )

@app.route('/addDecla', methods=['GET', 'POST'])
def addDecla():
    """
    Réalise l'ajout de données dans la BD
    """
    data=request.form
    print(data)
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(data['geomlng'],data['geomlat']),4326),2154)))
    json2154=json.loads(p2154[0][0])    
    changeAnimaux=data['type_animaux_d']
    if data['type_animaux_d']=="0":
        changeAnimaux=None
    changeStatut=data['statut_d']
    if data['statut_d']=="0":
        changeStatut=1    
    decla=Declaratif(
        date_attaque_d=data['date_attaque_d'],
        date_constat_d=data['date_constat_d'],
        lieu_dit=data['lieu_dit'],
        proprietaire_d=data['proprietaire_d'],
        type_animaux_d=changeAnimaux,
        nb_victimes_mort_d=data['nb_victimes_mort_d'],
        nb_victimes_blesse_d=data['nb_victimes_blesse_d'],
        statut_d=changeStatut,      
        geom=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154)
    )
    DB.session.add(decla)
    DB.session.commit()
    return redirect(url_for('decla'))

@app.route('/updateDecla/<idc>', methods=['GET', 'POST'])
def updateDecla(idc):
     """
     Lance la page de mise à jour d'une donnée
     """
     dataStatut=DB.session.query(bib_statut)
     dataAnimaux=DB.session.query(bib_type_animaux)
     dataSecteur=DB.session.query(l_areas)
     dataGeom = DB.session.query(Declaratif,func.ST_AsGeoJson(func.ST_Transform(Declaratif.geom,4326))).filter(Declaratif.id_constat_d==idc).all()
     geojson=json.loads(dataGeom[0][1])
     dico={}
     dico['geometry']=geojson
     dico['properties']={}
     dico['properties']['id_constat_d']=dataGeom[0][0].id_constat_d
     dico['properties']['date_attaque_d']=dataGeom[0][0].date_attaque_d
     dico['properties']['date_constat_d']=dataGeom[0][0].date_constat_d
     dico['properties']['lieu_dit']=dataGeom[0][0].lieu_dit
     dico['properties']['proprietaire_d']=dataGeom[0][0].proprietaire_d
     dico['properties']['type_animaux_d']=dataGeom[0][0].type_animaux_d
     for da in dataAnimaux:
         if da.id==dataGeom[0][0].type_animaux_d:
             dico['properties']['type_animaux_name']=da.nom  
     dico['properties']['nb_victimes_mort_d']=dataGeom[0][0].nb_victimes_mort_d
     dico['properties']['nb_victimes_blesse_d']=dataGeom[0][0].nb_victimes_blesse_d
     dico['properties']['statut_d']=dataGeom[0][0].statut_d
     for ds in dataStatut:
         if ds.id==dataGeom[0][0].statut_d:
             dico['properties']['statut_name']=ds.nom
     for dsec in dataSecteur:
         if dsec.id_area == dataGeom[0][0].id_secteur_d:
             dico['properties']['secteur_d']=dsec.area_name
         if dsec.id_area == dataGeom[0][0].id_commune_d:
             dico['properties']['commune_d']=dsec.area_name         
     form = DeclaForm()
     form.statut_d.choices=[(0,"")]
     dataStatut=DB.session.query(bib_statut)
     for ds in dataStatut:
        form.statut_d.choices+=[(ds.id,ds.nom)]
     form.type_animaux_d.choices=[(0,"")]
     dataAnimaux=DB.session.query(bib_type_animaux)
     for da in dataAnimaux:
        form.type_animaux_d.choices+=[(da.id,da.nom)]
     form.type_animaux_d.default=dataGeom[0][0].type_animaux_d
     form.statut_d.default=dataGeom[0][0].statut_d
     form.process()
     return render_template('updateDecla.html', title='Map',form=form,Declaratif=dico)

@app.route('/updateDBDecla',methods=['GET', 'POST'])
def updateDBDecla():
    """
    Réalise les mises à jour dans la BD
    """
    data=request.form
    p2154=DB.session.query(func.ST_AsGeoJson(func.ST_Transform(func.ST_SetSRID(func.ST_Point(data['geomlng'],data['geomlat']),4326),2154)))
    json2154=json.loads(p2154[0][0])
    changeAnimaux=data['type_animaux_d']
    if data['type_animaux_d']=="0":
        changeAnimaux=None
    changeStatut=data['statut_d']
    if data['statut_d']=="0":
        changeStatut=1    
    cst=DB.session.query(Declaratif).filter(Declaratif.id_constat_d==data['id_constat_d']).one()
    cst.date_attaque_d=data['date_attaque_d']
    cst.date_constat_d=data['date_constat_d']
    cst.lieu_dit=data['lieu_dit']
    cst.proprietaire_d=data['proprietaire_d']
    cst.type_animaux_d=changeAnimaux
    cst.nb_victimes_mort_d=data['nb_victimes_mort_d']
    cst.nb_victimes_blesse_d=data['nb_victimes_blesse_d']
    cst.statut_d=changeStatut
    cst.geom=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154)
    DB.session.commit()       
    return redirect(url_for('decla'))    
@app.route('/downloadDecla', methods=['GET', 'POST'])
def downloadDecla():
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
    query = DB.session.query(Declaratif,func.ST_AsGeoJson(func.ST_Transform(Declaratif.geom,4326)))
    
    if 'date' in filter_query:
        if filter_query['date'] == None:
            query = query.filter(extract('year',Declaratif.date_constat_d) == int(filter_query['date']))
    if 'animaux' in filter_query:
        query = query.filter(Declaratif.type_animaux_d == filter_query['animaux'])
    if 'statut' in filter_query:
        query = query.filter(Declaratif.statut_d == filter_query['statut'])   
    dataGeom =  query.order_by(Declaratif.id_constat_d).all()  
    
    cnsts=[]
    for d in dataGeom:
        geojson=json.loads(d[1])
        dico={}
        dico['id_constat']=d[0].id_constat_d
        dico['date_attaque']=d[0].date_attaque_d
        dico['date_constat']=d[0].date_constat_d
        dico['lieu_dit']=d[0].lieu_dit
        dico['proprietaire']=d[0].proprietaire_d
        for da in dataAnimaux:
            if da.id==d[0].type_animaux_d:
                dico['type_animaux']=da.nom
        dico['nb_victimes_mort']=d[0].nb_victimes_mort_d
        dico['nb_victimes_blesse']=d[0].nb_victimes_blesse_d
        for ds in dataStatut:
            if ds.id==d[0].statut_d:
                dico['statut']=ds.nom
        for dsec in dataSecteur:
            if dsec.id_area == d[0].id_secteur_d:
                dico['secteur']=dsec.area_name
            if dsec.id_area == d[0].id_commune_d:
                dico['commune']=dsec.area_name          
        dico['x']=geojson['coordinates'][1]
        dico['y']=geojson['coordinates'][0]
        cnsts.append(dico)       
    si = io.StringIO()
    cw = csv.DictWriter(si,fieldnames=dico.keys())
    cw.writeheader()
    cw.writerows(cnsts)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=constats-"+datetime.now().strftime('%d-%b-%Y--%H-%M')+".csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/dataDecla/<idc>')
def dataDecla(idc):
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataSecteur=DB.session.query(l_areas)
    dataGeom = DB.session.query(Declaratif,func.ST_AsGeoJson(func.ST_Transform(Declaratif.geom,4326))).filter(Declaratif.id_constat_d==idc).all()
    geojson=json.loads(dataGeom[0][1])
    dico={}
    dico['geometry']=geojson
    dico['properties']={}
    dico['properties']['id_constat']=dataGeom[0][0].id_constat_d
    dico['properties']['date_attaque']=dataGeom[0][0].date_attaque_d
    dico['properties']['date_constat']=dataGeom[0][0].date_constat_d
    dico['properties']['lieu_dit']=dataGeom[0][0].lieu_dit
    dico['properties']['proprietaire']=dataGeom[0][0].proprietaire_d
    dico['properties']['type_animaux']=dataGeom[0][0].type_animaux_d
    for da in dataAnimaux:
        if da.id==dataGeom[0][0].type_animaux_d:
            dico['properties']['type_animaux_name']=da.nom    
    dico['properties']['nb_victimes_mort']=dataGeom[0][0].nb_victimes_mort_d
    dico['properties']['nb_victimes_blesse']=dataGeom[0][0].nb_victimes_blesse_d
    dico['properties']['statut']=dataGeom[0][0].statut_d
    for ds in dataStatut:
       if ds.id==dataGeom[0][0].statut_d:
           dico['properties']['statut_name']=ds.nom    
    for dsec in dataSecteur:
       if dsec.id_area == dataGeom[0][0].id_secteur_d:
           dico['properties']['secteur']=dsec.area_name
       if dsec.id_area == dataGeom[0][0].id_commune_d:
           dico['properties']['commune']=dsec.area_name  
    return render_template('dataDecla.html', title='Map',Decla=dico)