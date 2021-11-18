from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SubmitField, SelectField, HiddenField, FloatField
from wtforms.fields.html5 import DateField
from app.models import Constats,Declaratif, bib_statut, bib_type_animaux
from .env import DB
from wtforms.validators import DataRequired, InputRequired
from datetime import date
from wtforms.ext.sqlalchemy.fields import QuerySelectField




def get_animals_type():
    return  DB.session.query(bib_type_animaux).all()
def get_statuts():
    return  DB.session.query(bib_statut).all()


class ConstatForm(FlaskForm):
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
        get_label="nom"
    )
    nb_victimes_mort = IntegerField('Nb de victime(s) morte(s)', default=0)
    nb_victimes_blesse = IntegerField('Nb de victime(s) blessée(s)', default=0)
    statut = QuerySelectField(
        "Situation",
        query_factory=get_statuts,
        get_label="nom"
    )
    nb_jour_agent=FloatField('Nb jour agent', default=0.0)
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
class FilterForm(FlaskForm):
    date=SelectField('Année du constat')
    animaux=SelectField("Type d'animaux victimes",choices=[])
    statut=SelectField("Statut du constat",choices=[])
    localisation=SelectField("Localisation du constat",choices=[(0,""),(1,"Coeur du parc"),(2,"Dans l'aire d'adhésion"),(3,"Hors du parc")])
    secteur=SelectField("Secteur du constat",choices=[])
    commune=SelectField("Commune du constat",choices=[])