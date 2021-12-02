from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SubmitField, SelectField, HiddenField, FloatField
from sqlalchemy import func, extract
from wtforms.fields.html5 import DateField
from app.models import Constats,Declaratif, LAreas, bib_statut, bib_type_animaux
from .env import DB
from wtforms.validators import DataRequired, InputRequired, Optional
from datetime import date
from wtforms.ext.sqlalchemy.fields import QuerySelectField




def get_animals_type():
    return  bib_type_animaux.query.all()
def get_statuts():
    return bib_statut.query.all()

class ConstatForm(FlaskForm):
    id_constat = HiddenField("id_constat")
    geom_4326 = HiddenField("geom_4326")
    date_attaque = DateField(
        'Date attaque', [InputRequired(message="Veuillez fournir une date")], format='%Y-%m-%d',
    )
    date_constat = DateField(
        'Date constat', 
        [InputRequired(message="Veuillez fournir une date")], 
        format='%Y-%m-%d',default=date.today,
    )
    nom_agent1 = StringField(
        "Nom de l'agent 1",
        [InputRequired(message="Veuillez fournir le nom d'au moin un agent")]
    )
    nom_agent2 = StringField("Nom de l'agent 2")
    proprietaire = StringField(
        'Propriétaire',
        [InputRequired(message="Veuillez fournir le nom du propriétaire")]
    )
    type_animaux = QuerySelectField(
        "Type d'animaux",
        query_factory=get_animals_type,
        get_label="nom",
        get_pk=lambda t : t.id
    )
    nb_victimes_mort = IntegerField('Nb de victime(s) morte(s)', [Optional()])
    nb_victimes_blesse = IntegerField('Nb de victime(s) blessée(s)', [Optional()])
    nb_disparus = IntegerField('Nb de disparu(s)', [Optional()])
    nb_indemnises = IntegerField("Nb d'indemnisé(s)", [Optional()])

    statut = QuerySelectField(
        "Situation",
        query_factory=get_statuts,
        get_label="nom"
    )
    nb_jour_agent=FloatField('Nb jour agent', [Optional()])
    declaratif = BooleanField("Déclaratif")
    comment = StringField("Commentaire",[Optional()])
    submit = SubmitField('Ajouter le constat', render_kw={"class":"btn btn-success"})

class DeclaForm(FlaskForm):
    date_attaque_d = DateField('date_attaque_d', format='%d/%m/%Y',default=date.today)
    date_constat_d = DateField('date_constat_d', format='%d/%m/%Y',default=date.today)
    lieu_dit=StringField('lieu_dit')
    proprietaire_d = StringField('proprietaire')
    type_animaux_d = SelectField('type_animaux',choices=[])
    nb_victimes_mort_d = IntegerField('nb_victimes_mort')
    nb_victimes_blesse_d = IntegerField('nb_victimes_blesse')
    statut_d = SelectField('situation',choices=[])
    submit = SubmitField('Confirmer le consat')    


def get_comm():
    return LAreas.query.filter_by(id_type=25).filter(Constats.id_commune==LAreas.id_area).all()

def get_secteur():
    return LAreas.query.filter_by(id_type=30).filter(Constats.id_secteur==LAreas.id_area).all()

def get_years():
    return DB.session.query(
        func.distinct(extract('year',Constats.date_constat)).label("date"),
        ).order_by(extract('year',Constats.date_constat).desc())

class FilterForm(FlaskForm):
    date = SelectField(
        'Année du constat', 
        choices=[
            (int(d[0]), int(d[0])) for d in DB.session.query(
                    func.distinct(extract('year',Constats.date_constat)).label("date")
                ).order_by(extract('year',Constats.date_constat).desc())
            ]
    )
    type_constat = SelectField(
        'Type de constat', 
        choices=[
            (None, "Tous"),
            (1, "Constat déclaratif"),
            (0, "Constat non déclaratif")
        ]
    )
    animaux = QuerySelectField(
        "Type d'animaux",
        query_factory=get_animals_type,
        allow_blank=True,
        get_label="nom"
    )   
    statut = QuerySelectField(
        "Statut du constat",
        query_factory=get_statuts,
        allow_blank=True,
        get_label="nom"
    )
    localisation=SelectField("Localisation du constat",choices=[(0,""),(1,"Coeur du parc"),(2,"Dans l'aire d'adhésion"),(3,"Hors du parc")])
    secteur=QuerySelectField(
        "Secteur du constat",
        allow_blank=True,
        get_label="area_name",
        query_factory=get_secteur,
    )
    commune=QuerySelectField(
        "Commune du constat",
        allow_blank=True,
        query_factory=get_comm,
        get_label="area_name"
    )