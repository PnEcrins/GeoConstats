from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, SubmitField, SelectField, HiddenField, FloatField
from wtforms.fields.html5 import DateField
from app.models import Constats,Declaratif, bib_statut, bib_type_animaux
from .env import DB
from wtforms.validators import DataRequired
from datetime import date
    
class ConstatForm(FlaskForm):
    date_attaque = DateField('date_attaque', format='%d/%m/%Y',default=date.today)
    date_constat = DateField('date_constat', format='%d/%m/%Y',default=date.today)
    nom_agent1 = StringField('nom_agent1')
    nom_agent2 = StringField('nom_agent2')
    proprietaire = StringField('proprietaire')
    type_animaux = SelectField('type_animaux',choices=[])
    nb_victimes_mort = IntegerField('nb_victimes_mort')
    nb_victimes_blesse = IntegerField('nb_victimes_blesse')
    statut = SelectField('situation',choices=[])
    nb_jour_agent=FloatField('nb_jour_agent')
    submit = SubmitField('Confirmer le constat')
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