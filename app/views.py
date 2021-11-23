from collections import defaultdict

from flask import Blueprint, render_template, session, redirect, url_for, request, make_response, jsonify, current_app
from flask.helpers import flash
from werkzeug.datastructures import MultiDict
from geojson import Feature, FeatureCollection

from .env import DB
from app.models import Constats,Declaratif,bib_statut, bib_type_animaux, LAreas
from app.forms import ConstatForm, DeclaForm, FilterForm
from sqlalchemy import func, extract
import json
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import date, datetime
import io
import csv
from pypnusershub.db.models import Application,AppUser
from pypnusershub.routes import check_auth
from .forms import ConstatForm
from .schema import ConstatSchema, LAreasSchema

routes = Blueprint('routes',__name__)

@routes.route("/")
@routes.route("/login")
def login():
    dataApp=DB.session.query(Application.id_application).filter(Application.code_application=='GC').one()
    if dataApp:
        bonApp=dataApp[0]
        current_app.config["ID_APP"] = bonApp
    return render_template('login.html',id_app=bonApp)

@routes.route("/map")
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def map(id_role):
    """
    Lance la "page d'acceuil" avec une carte + une liste avec toutes les données
    """
    filter_query = request.args.to_dict()
    query = Constats.query
    #FORMULAIRE DE FILTRAGE
    form = FilterForm()
    form.date.choices.insert(0, (0,""))
    if 'date' in filter_query:
        if filter_query['date'] != "0":
            query = query.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query and filter_query["animaux"] != "__None":
        query = query.filter(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query and filter_query['statut'] != "__None":
        query = query.filter(Constats.statut == filter_query['statut'])   
    if 'localisation' in filter_query:
        if filter_query['localisation'] == "1":
            query =  query.filter(Constats.dans_coeur==True)   
        elif filter_query['localisation'] == "2":  
            query =  query.filter(Constats.dans_aa == True)
        elif filter_query['localisation'] == "3":  
            query =  query.filter(Constats.dans_aa == False and Constats.dans_coeur == False)
    if 'secteur' in filter_query and filter_query['secteur'] != "__None":
            query = query.filter(Constats.id_secteur == filter_query['secteur'])  
    if 'commune' in filter_query and filter_query['commune'] != "__None":
        query = query.filter(Constats.id_commune == filter_query['commune'])                             
    
    dataGeom =  query.order_by(Constats.date_attaque.desc()).all()  
    constat_schema = ConstatSchema()
    geojsons = [constat_schema.dump(d) for d in dataGeom]   
    return render_template('map.html', title='Map', constats=geojsons, form=form)

@routes.route('/form/<int:idc>',methods=['POST','GET'])
@routes.route('/form',methods=['POST','GET'])
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def form(idc=None, id_role=None):
    """
    Lance la page de formulaire d'ajout de données
    """
    # if edition
    if idc:
        constat = Constats.query.get(idc)
        constat_dict = ConstatSchema().dump(constat)
        geom = constat_dict["geometry"]
        constat_dict = constat_dict["properties"]
        constat_dict["geom_4326"] = geom
        not_none_dict = {}
        for key, val in constat_dict.items():
            if val:
                not_none_dict[key] = val
        form = ConstatForm(MultiDict(not_none_dict))
        form.type_animaux.data = constat.type_animaux_rel
        form.statut.data = constat.statut_rel
    else:
        form_data = session.get("form_data", None)
        form = ConstatForm(MultiDict(form_data))
        if form_data:
            form.validate()
    return render_template('add.html', title="Add_to_database", form=form)

@routes.route('/add', methods=['POST'])
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def add(id_role):
    """
    Réalise l'ajout de données dans la BD
    """
    #TRAITEMENT FORMULAIRE

    form = ConstatForm(request.form)
    valid = form.validate()
    if not valid:
        session["form_data"] = request.form
        return redirect(
            url_for("routes.form")
        )
    data = request.form

    p2154=DB.session.query(
        func.ST_AsGeoJson(
            func.ST_Transform(
                func.ST_SetSRID(
                    func.ST_Point(float(data['geomlng']),float(data['geomlat'])),
                    4326
                ),
            2154)
            )
        )
    json2154=json.loads(p2154[0][0])
    constat = Constats(
        date_attaque=form.date_attaque.data,
        date_constat=form.date_constat.data,
        nom_agent1=form.nom_agent1.data,
        nom_agent2=form.nom_agent2.data,
        proprietaire=form.proprietaire.data,
        type_animaux=form.type_animaux.data.id,
        nb_victimes_mort=form.nb_victimes_mort.data,
        nb_victimes_blesse=form.nb_victimes_blesse.data,
        nb_disparus=form.nb_disparus.data,
        nb_indemnises=form.nb_indemnises.data,
        statut=form.statut.data.id,
        nb_jour_agent=form.nb_jour_agent.data,
        the_geom_point=from_shape(Point(json2154['coordinates'][0],json2154['coordinates'][1]),srid=2154),
        id_role=id_role,
        comment=form.comment.data
    )
    if form.id_constat.data:
        constat_before_update = Constats.query.get(form.id_constat.data)
        # TODO : check droit d'update
        app = DB.session.query(Application).filter(Application.code_application=='GC').one()

        nivDroit = DB.session.query(
            AppUser.id_droit_max
        ).filter(AppUser.id_role==id_role).filter(AppUser.id_application == app.id_application).one()[0]

        if nivDroit > 2 or constat_before_update.id_role == id_role:
            constat.id_constat = form.id_constat.data
            DB.session.merge(constat)
        else:
            return render_template('noRight.html')
    else:
        DB.session.add(constat)
    DB.session.commit()
    if "form_data" in session:
        session.pop("form_data")
    return redirect(url_for('routes.map'))


    
@routes.route('/delete/<idc>', methods=['GET', 'POST'])
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def delete(idc,id_role):
    """
    Réalise la suppression d'un constat déclaratif
    """
    #REQUETES
    dataGeom = DB.session.query(Constats).filter(Constats.id_constat==idc).one()
    dataApp=DB.session.query(Application.id_application).filter(Application.code_application=='GC').one()
    nivDroit=DB.session.query(AppUser.id_droit_max).filter(AppUser.id_role==id_role).filter(AppUser.id_application==dataApp[0]).one()
    if nivDroit[0]>2 or id_role==dataGeom[0][0].id_role:
        dataGeom = DB.session.query(Constats).filter(Constats.id_constat==idc).delete()
        DB.session.commit()
        return redirect(url_for('routes.map'))
    else:
        return render_template('noRight.html')    

@routes.route('/download', methods=['GET', 'POST'])
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def download(id_role):
    #REQUETES
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataArea=DB.session.query(LAreas)
    dataApp=DB.session.query(Application.id_application).filter(Application.code_application=='GC').one()
    dataUser=DB.session.query(AppUser.prenom_role,AppUser.nom_role).filter(AppUser.id_role==id_role).filter(AppUser.id_application==dataApp[0]).one()
    query = DB.session.query(Constats,func.ST_AsGeoJson(func.ST_Transform(Constats.the_geom_point,4326)))
    #FORMULAIRE
    if 'date' in filter_query:
        if filter_query['date'] != "0":
            query = query.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "0":
            query = query.filter(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query:
        if filter_query['statut'] != "0":
            query = query.filter(Constats.statut == filter_query['statut']) 
    if 'localisation' in filter_query:
        if filter_query['localisation'] == "1":
            query =  query.filter(Constats.dans_coeur==True)   
        elif filter_query['localisation'] == "2":  
            query =  query.filter(Constats.dans_aa == True)
        elif filter_query['localisation'] == "3":  
            query =  query.filter(Constats.dans_aa == False and Constats.dans_coeur == False)
    if 'secteur' in filter_query:
        if filter_query['secteur'] != "0":
            query = query.filter(Constats.id_secteur == filter_query['secteur'])  
    if 'commune' in filter_query:
        if filter_query['commune'] != "0":
            query = query.filter(Constats.id_commune == filter_query['commune'])
    dataGeom=query.order_by(Constats.date_attaque.desc()).all()
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
        dico['type_animaux']=None
        for da in dataAnimaux:
            if da.id==d[0].type_animaux:
                dico['type_animaux']=da.nom
        dico['nb_victimes_mort']=d[0].nb_victimes_mort
        dico['nb_victimes_blesse']=d[0].nb_victimes_blesse
        dico['statut']=None
        for ds in dataStatut:
            if ds.id==d[0].statut:
                dico['statut']=ds.nom
        dico['nb_jour_agent']=d[0].nb_jour_agent
        for dsec in dataArea:
            if dsec.id_area == d[0].id_secteur:
                dico['secteur']=dsec.area_name
            if dsec.id_area == d[0].id_commune:
                dico['commune']=dsec.area_name
        dico['departement']=d[0].departement          
        if d[0].dans_coeur:
            dico['localisation']="Dans le coeur"
        elif d[0].dans_aa:
            dico['localisation']="Dans l'aire d'adhésion"
        else:
            dico['localisation']="Hors du parc"
        dico['createur']=dataUser.prenom_role+" "+dataUser.nom_role                               
        dico['x']=geojson['coordinates'][1]
        dico['y']=geojson['coordinates'][0]
        cnsts.append(dico)
    #TELECHARGEMENT FICHIER       
    si = io.StringIO()
    cw = csv.DictWriter(si,fieldnames=dico.keys())
    cw.writeheader()
    cw.writerows(cnsts)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=constats-"+datetime.now().strftime('%d-%b-%Y--%H-%M')+".csv"
    output.headers["Content-type"] = "text/csv"
    return output
   
@routes.route('/constat/<int:idc>')
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def constat(idc, id_role):
    q = Constats.query
    constat = Constats.query.get_or_404(idc)
    constat_schema = ConstatSchema()
    geojson_constat = constat_schema.dump(constat)
    return render_template('data.html', title='Map', constat=geojson_constat)

@routes.route('/decla')
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def decla(id_role):
    """
    Lance la page de consultation des constats déclaratifs avec une carte + une liste avec toutes les données
    """    
    #REQUETES
    filter_query = request.args.to_dict()
    dataStatut=DB.session.query(bib_statut)
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataArea=DB.session.query(LAreas)
    dataSecteur=DB.session.query(LAreas).filter(LAreas.id_type==30).filter(Declaratif.id_secteur_d==LAreas.id_area).all()
    dataCommune=DB.session.query(LAreas).filter(LAreas.id_type==25).filter(Declaratif.id_commune_d==LAreas.id_area)    
    dataAnnee=DB.session.query(func.distinct(extract('year',Declaratif.date_constat_d)).label("date")).order_by(extract('year',Declaratif.date_constat_d).desc())
    dataApp=DB.session.query(Application.id_application).filter(Application.code_application=='GC').one()
    dataUser=DB.session.query(AppUser.prenom_role,AppUser.nom_role).filter(AppUser.id_role==id_role).filter(AppUser.id_application==dataApp[0]).one()
    nivDroit=DB.session.query(AppUser.id_droit_max).filter(AppUser.id_role==id_role).filter(AppUser.id_application==dataApp[0]).one()
    listUser=DB.session.query(AppUser.prenom_role,AppUser.nom_role,AppUser.id_role).filter(AppUser.id_application==dataApp[0]).all()
    query = DB.session.query(Declaratif,func.ST_AsGeoJson(func.ST_Transform(Declaratif.geom,4326)))
    #FORMULAIRE
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
            dataCommune=dataCommune.filter(extract('year',Declaratif.date_constat_d) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "0":
            query = query.filter(Declaratif.type_animaux_d == filter_query['animaux'])
            dataCommune=dataCommune.filter(Declaratif.type_animaux_d == filter_query['animaux'])
    if 'statut' in filter_query:
        if filter_query['statut'] != "0":
            query = query.filter(Declaratif.statut_d == filter_query['statut'])  
            dataCommune=dataCommune.filter(Declaratif.statut_d == filter_query['statut']) 
    if 'localisation' in filter_query:
        if filter_query['localisation'] == "1":
            query =  query.filter(Declaratif.dans_coeur_d==True)   
            dataCommune=dataCommune.filter(Declaratif.dans_coeur_d==True)
        elif filter_query['localisation'] == "2":  
            query =  query.filter(Declaratif.dans_aa_d == True)
            dataCommune=dataCommune.filter(Declaratif.dans_aa_d == True)
        elif filter_query['localisation'] == "3":  
            query =  query.filter(Declaratif.dans_aa_d == False and Declaratif.dans_coeur_d == False)  
            dataCommune=dataCommune.filter(Declaratif.dans_aa_d == False and Declaratif.dans_coeur_d == False)
    if 'secteur' in filter_query:
        if filter_query['secteur'] != "0":
            query = query.filter(Declaratif.id_secteur_d == filter_query['secteur'])  
            dataCommune=dataCommune.filter(Declaratif.id_secteur_d == filter_query['secteur'])
    if 'commune' in filter_query:
        if filter_query['commune'] != "0":
            query = query.filter(Declaratif.id_commune_d == filter_query['commune'])                           
    dataGeom=query.order_by(Declaratif.date_attaque_d.desc()).all()
    dataCommune=dataCommune.order_by(LAreas.area_name).all()
    #l'ajout des choix au formulaire de filtrage pour commune et secteur se fait après pour ajouter les autres filtres
    form.secteur.choices=[(0,"")]    
    for dsec in dataSecteur:
        form.secteur.choices+=[(dsec.id_area,dsec.area_name)]   
    form.commune.choices=[(0,"")]    
    for dcom in dataCommune:
        form.commune.choices+=[(dcom.id_area,dcom.area_name)]     
    #TRAITEMENT DONNEES
    decla=[]
    for d in dataGeom:
        geojson=json.loads(d[1])
        dico={}
        dico['user']={}
        for u in listUser:
            if u.id_role == d[0].id_role:
                dico['user']['nom_d']=u.nom_role
                dico['user']['prenom_d']=u.prenom_role
        dico['user']['right']=nivDroit[0]>2 or id_role==d[0].id_role              
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
        for dsec in dataArea:
            if dsec.id_area == d[0].id_secteur_d:
                dico['properties']['secteur_d']=dsec.area_name  
            if dsec.id_area == d[0].id_commune_d:
                dico['properties']['commune_d']=dsec.area_name
        dico['properties']['departement_d']=d[0].departement_d          
        if d[0].dans_coeur_d:
            dico['properties']['localisation_d']="Dans le coeur"
        elif d[0].dans_aa_d:
            dico['properties']['localisation_d']="Dans l'aire d'adhésion"
        else:
            dico['properties']['localisation_d']="Hors du parc"                       
        decla.append(dico)
    return render_template('decla.html', title='Declaratif', Declaratifs=decla,form=form)

@routes.route('/deleteDecla/<idc>',methods=['GET', 'POST'])
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def deleteDecla(idc,id_role):
    """
    Réalise la suppression d'un constat déclaratif
    """
    #REQUETES
    dataGeom = DB.session.query(Declaratif).filter(Declaratif.id_constat_d==idc).one()
    dataApp=DB.session.query(Application.id_application).filter(Application.code_application=='GC').one()
    nivDroit=DB.session.query(AppUser.id_droit_max).filter(AppUser.id_role==id_role).filter(AppUser.id_application==dataApp[0]).one()
    if nivDroit[0]>2 or id_role==dataGeom[0][0].id_role:
        dataGeom = DB.session.query(Declaratif).filter(Declaratif.id_constat_d==idc).delete()
        DB.session.commit()
        return redirect(url_for('routes.decla'))
    else:
        return render_template('noRight.html')     

 
    
@routes.route('/noRight')
def noRight(idc):
    return render_template('noRight.html')

@routes.route('/dashboard')
@check_auth(
    2,
    True,
    redirect_on_expiration='/login',
    redirect_on_invalid_token='/login',
    redirect_on_insufficient_right='/noRight',
    )
def dashboard(id_role):
    #REQUETES

    nb_constat_by_dep = DB.session.query(
        LAreas.area_name, func.sum(Constats.nb_victimes_mort), func.sum(Constats.nb_indemnises), func.count(Constats.id_constat)
    ).select_from(
        Constats
    ).join(
        LAreas, LAreas.id_area == Constats.id_departement
    ).filter(
        LAreas.id_type == 25
    ).group_by(LAreas.area_name)

    nb_constat_by_sect = DB.session.query(
        LAreas.area_name, func.sum(Constats.nb_victimes_mort), func.sum(Constats.nb_indemnises), func.count(Constats.id_constat)
    ).select_from(
        LAreas
    ).outerjoin(
        Constats, LAreas.id_area == Constats.id_secteur
    ).filter(LAreas.id_type == 30).group_by(LAreas.area_name)

    query_constat_by_sect_by_animal_type = DB.session.query(
        LAreas.area_name, func.count(Constats.id_constat), bib_type_animaux.nom
    ).select_from(
        LAreas
    ).outerjoin(
        Constats, LAreas.id_area == Constats.id_secteur,
    ).outerjoin(
        bib_type_animaux, bib_type_animaux.id == Constats.type_animaux
    ).filter(
        LAreas.id_type == 30
    )

    


    # for r, val in res.items():
    #     print(r)
    #     print(val)
    # print("LAAA", res)


    dataArea=DB.session.query(LAreas).filter(LAreas.id_type==30).all()
    dataSecC=DB.session.query(Constats.id_secteur,func.count(Constats.id_constat).label("nombre"))
    dataAnimaux=DB.session.query(bib_type_animaux)
    dataAnneeC=DB.session.query(func.distinct(extract('year',Constats.date_constat)).label("date")).order_by(extract('year',Constats.date_constat).desc())
    dataAniC=DB.session.query(Constats.id_secteur,Constats.type_animaux,func.sum(Constats.nb_victimes_mort).label("nombre"))
    #FORMULAIRE
    filter_query = request.args.to_dict()

    current_year = datetime.now().year
    form=FilterForm(date=current_year)
    form.date.choices.insert(0, (0,""))
    # form.date.data = (datetime.now().year, datetime.now().year)
      
    if 'date' in filter_query:
        if filter_query['date'] != "0":
            nb_constat_by_dep =  nb_constat_by_dep.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
            dataSecC =  dataSecC.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
            dataAniC =  dataAniC.filter(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "0":
            nb_constat_by_dep =  nb_constat_by_dep.filter(Constats.type_animaux == filter_query['animaux'])
            dataSecC =  dataSecC.filter(Constats.type_animaux == filter_query['animaux'])
            dataAniC =  dataAniC.filter(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query:
        if filter_query['statut'] != "0":
            nb_constat_by_dep =  nb_constat_by_dep.filter(Constats.statut == filter_query['statut'])   
            dataSecC =  dataSecC.filter(Constats.statut == filter_query['statut'])   
            dataAniC =  dataAniC.filter(Constats.statut == filter_query['statut'])   
    if 'localisation' in filter_query:
        if filter_query['localisation'] == "1":
            nb_constat_by_dep =  nb_constat_by_dep.filter(Constats.dans_coeur==True)   
            dataSecC =  dataSecC.filter(Constats.dans_coeur==True)   
            dataAniC =  dataAniC.filter(Constats.dans_coeur==True)   
        elif filter_query['localisation'] == "2":
            nb_constat_by_dep =  nb_constat_by_dep.filter(Constats.dans_aa==True)   
            dataSecC =  dataSecC.filter(Constats.dans_aa==True)   
            dataAniC =  dataAniC.filter(Constats.dans_aa==True)   
        elif filter_query['localisation'] == "3":
            nb_constat_by_dep =  nb_constat_by_dep.filter(Constats.dans_aa==False and Constats.dans_coeur==False)   
            dataSecC =  dataSecC.filter(Constats.dans_aa==False and Constats.dans_coeur==False)   
            dataAniC =  dataAniC.filter(Constats.dans_aa==False and Constats.dans_coeur==False)   
                                                                                
    nb_constat_by_dep =  nb_constat_by_dep.group_by(LAreas.area_name).all()     
    nb_constat_by_sect =  nb_constat_by_sect.group_by(LAreas.area_name).all()
    data = query_constat_by_sect_by_animal_type.group_by(LAreas.area_name, bib_type_animaux.nom).all()
    constat_by_sect_by_animal_type = {}
    for item in data:
        constat_by_sect_by_animal_type.setdefault(item[0], {"total": 0})
        constat_by_sect_by_animal_type[item[0]]["total"] += item[1]
        constat_by_sect_by_animal_type[item[0]][item[2]] = item[1]

    return render_template(
        'dashboard.html',
        title='Map', 
        nb_constat_by_dep=nb_constat_by_dep,
        nb_constat_by_sect=nb_constat_by_sect,
        constat_by_sect_by_animal_type=constat_by_sect_by_animal_type,
        form=form
    )
