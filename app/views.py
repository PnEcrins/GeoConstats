
from sqlalchemy import and_

from flask import Blueprint, render_template, session, redirect, url_for, request, make_response, jsonify, current_app
from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import BadRequest
from .env import DB
from app.models import BibAreaType, Constats, bib_type_animaux, LAreas
from app.forms import ConstatForm, FilterForm
from sqlalchemy import func, extract
import json
from shapely.geometry import Point
from geoalchemy2.shape import from_shape
from datetime import datetime
from geojson import FeatureCollection
import io
import csv
from pypnusershub.db.models import Application,AppUser
from pypnusershub.routes import check_auth
from .forms import ConstatForm
from .schema import ConstatSchema, ConstatSchemaDownload

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
    form = FilterForm(MultiDict(filter_query))
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
    if "type_constat" in filter_query and filter_query["type_constat"] != "None":
        try:
            is_declaratif = bool(int(filter_query["type_constat"]))
        except Exception as e:
            raise BadRequest(str(e))
        query = query.filter(Constats.declaratif == is_declaratif)
    
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
        declaratif=form.declaratif.data,
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
    if nivDroit[0]>2 or id_role==dataGeom.id_role:
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
    query = Constats.query
    schema = ConstatSchemaDownload()
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
    if "type_constat" in filter_query and filter_query["type_constat"] != "None":
        try:
            is_declaratif = bool(int(filter_query["type_constat"]))
        except Exception as e:
            raise BadRequest(str(e))
        query = query.filter(Constats.declaratif == is_declaratif)
    constats = [schema.dump(d) for d in query.order_by(Constats.date_attaque.desc()).all()]
    # #TELECHARGEMENT FICHIER
    if len(constats) > 0:   
        si = io.StringIO()
        cw = csv.DictWriter(si, delimiter=";", fieldnames=constats[0].keys())
        cw.writeheader()
        cw.writerows(constats)
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=constats-"+datetime.now().strftime('%d-%b-%Y--%H-%M')+".csv"
        output.headers["Content-type"] = "text/csv"
        return output
    return "No data"
   
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
    print(geojson_constat["properties"])
    return render_template('constat.html', title='Map', constat=geojson_constat)
 
    
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
        LAreas
    ).filter(
        LAreas.id_type == 26
    )
    if current_app.config.get("CODE_DEPARTMENT", None):
        nb_constat_by_dep = nb_constat_by_dep.filter(
            LAreas.area_code.in_(current_app.config["CODE_DEPARTMENT"])
        )
    nb_constat_by_dep = nb_constat_by_dep.group_by(LAreas.area_name)


    nb_constat_by_sect = DB.session.query(
        LAreas.area_name, func.sum(Constats.nb_victimes_mort), func.sum(Constats.nb_indemnises), func.count(Constats.id_constat), func.sum(Constats.nb_jour_agent)
    ).select_from(
        LAreas
    ).filter(LAreas.id_type == 30).group_by(LAreas.area_name)

    query_constat_by_sect_by_animal_type = DB.session.query(
        LAreas.area_name, func.sum(Constats.nb_indemnises), bib_type_animaux.nom
    ).select_from(
        LAreas
    ).filter(
        LAreas.id_type == 30
    )
    filter_query = request.args.to_dict()
    current_year = datetime.now().year
    form=FilterForm(date=current_year)
    form.date.choices.insert(0, (0,""))
    
    # we must add filter in the join condition and not in where clause if we want the outer join to work (have all secteurs/dep)
    filters = []    
    if 'date' in filter_query and filter_query['date'] != "0":
            filters.append(extract('year',Constats.date_constat) == int(filter_query['date']))
    if 'animaux' in filter_query:
        if filter_query['animaux'] != "__None":
            filters.append(Constats.type_animaux == filter_query['animaux'])
    if 'statut' in filter_query and filter_query['statut'] != "__None":
            filters.append(Constats.statut == filter_query['statut'])
    if 'localisation' in filter_query:
        if filter_query['localisation'] == "1":
            filters.append(Constats.dans_coeur==True)
        elif filter_query['localisation'] == "2":
            filters.append(Constats.dans_aa==True)
        elif filter_query['localisation'] == "3":
            filters.append(Constats.dans_aa==False and Constats.dans_coeur==False)
    if "type_constat" in filter_query and filter_query["type_constat"] != "None":
        try:
            is_declaratif = bool(int(filter_query["type_constat"]))
        except Exception as e:
            raise BadRequest(str(e))
        filters.append(Constats.declaratif == is_declaratif)
   
                                                                                
    nb_constat_by_dep =  nb_constat_by_dep.outerjoin(
        Constats, and_(
            Constats.id_departement == LAreas.id_area, *filters
        ) 
    ).group_by(LAreas.area_name).all()
    nb_constat_by_sect = nb_constat_by_sect.outerjoin(
        Constats, and_(
            Constats.id_secteur == LAreas.id_area, *filters
        )
    ).group_by(LAreas.area_name).all()

    data = query_constat_by_sect_by_animal_type.outerjoin(
        Constats, and_(
            Constats.id_secteur == LAreas.id_area, *filters
        )
    ).outerjoin(
        bib_type_animaux, bib_type_animaux.id == Constats.type_animaux
    ).group_by(LAreas.area_name, bib_type_animaux.nom)
    
    data = data.all()
    constat_by_sect_by_animal_type = {}
    for item in data:
        constat_by_sect_by_animal_type.setdefault(item[0], {"total": 0})
        constat_by_sect_by_animal_type[item[0]]["total"] += item[1] or 0
        constat_by_sect_by_animal_type[item[0]][item[2]] = item[1]

    return render_template(
        'dashboard.html',
        nb_constat_by_dep=nb_constat_by_dep,
        nb_constat_by_sect=nb_constat_by_sect,
        constat_by_sect_by_animal_type=constat_by_sect_by_animal_type,
        form=form
    )


@routes.route('/areas')
@check_auth(2)
def get_areas():
    params = request.args.to_dict()
    area_type_code = params.get("area_type_code", "")
    data = DB.session.query(
        LAreas.area_name,
        func.st_asgeojson(
                func.st_transform(
                    func.st_simplify(LAreas.geom, 10),
                    4326
                ),
        )   
    ).join(
        BibAreaType, BibAreaType.id_type == LAreas.id_type
    ).filter(BibAreaType.type_code == area_type_code).all()

    features = []
    for d in data:
        geojson = json.loads(d[1])
        geojson["properties"] = d[0]
        features.append(geojson)
    
    return jsonify(FeatureCollection(features))

