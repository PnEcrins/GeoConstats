from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, DateField, SubmitField
from app.models import Constats,Declaratif
from .env import DB
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    date_attaque = DateField('date_attaque', format='%Y/%m/%d')
    date_constat = DateField('date_constat', format='%Y/%m/%d')
    nom_agent1 = StringField('nom_agent1')
    nom_agent2 = StringField('nom_agent2')
    proprietaire = StringField('proprietaire')
    type_animaux = StringField('type_animaux')
    nb_victimes_mort = IntegerField('nb_victimes_mort')
    nb_victimes_blesse = IntegerField('nb_victimes_blesse')
    statut = StringField('situation')
    submit = SubmitField('Confirmer le consat')
class DeclaForm(FlaskForm):
    date_attaque_d = DateField('date_attaque_d', format='%Y/%m/%d')
    date_constat_d = DateField('date_constat_d', format='%Y/%m/%d')
    lieu_dit=StringField('lieu_dit')
    proprietaire_d = StringField('proprietaire')
    type_animaux_d = StringField('type_animaux')
    nb_victimes_mort_d = IntegerField('nb_victimes_mort')
    nb_victimes_blesse_d = IntegerField('nb_victimes_blesse')
    statut_d = StringField('situation')
    submit = SubmitField('Confirmer le consat')    
