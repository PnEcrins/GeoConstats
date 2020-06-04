from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, DateField, SubmitField
from app.models import Constats
from .env import DB
from wtforms.validators import DataRequired
from shapely.geometry import point,polygon,linestring,asShape
from geoalchemy2.shape import from_shape

class LoginForm(FlaskForm):
    date_attaque = DateField('date_attaque', format='%d/%m/%Y')
    date_constat = DateField('date_constat', format='%d/%m/%Y')
    nom_agent1 = StringField('nom_agent1')
    nom_agent2 = StringField('nom_agent2')
    proprietaire = StringField('proprietaire')
    type_animaux = StringField('type_animaux')
    nb_victimes_mort = IntegerField('nb_victimes_mort')
    nb_victimes_blesse = IntegerField('nb_victimes_blesse')
    statut = StringField('statut')
    submit = SubmitField('Add to database')
