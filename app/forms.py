from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, DateField, SubmitField
from app.models import Constats
from .env import DB
from wtforms.validators import DataRequired
from shapely.geometry import point,polygon,linestring,asShape
from geoalchemy2.shape import from_shape

class LoginForm(FlaskForm):
    date_attaque = DateField('date_attaque')
    date_constat = DateField('date_constat')
    nom_agent1 = StringField('nom_agent1')
    nom_agent2 = StringField('nom_agent2')
    proprietaire = StringField('proprietaire')
    type_animaux = StringField('type_animaux')
    nb_victimes_mort = IntegerField('nb_victimes_mort')
    nb_victimes_blesse = IntegerField('nb_victimes_blesse')
    situation = StringField('situation')
    submit = SubmitField('Add to database')

    def validate_situation(self, situation):
        constats = Constats.query.filter_by(situation=situation.data).first()
        if constat is not None:
            raise ValidationError('Please use a different situation.')
    
    def validate_nb_victimes_mort(self, nb_victimes_mort):
        constats = Constats.query.filter_by(nb_victimes_mort=nb_victimes_mort.data).first()
        if constats is not None:
            raise ValidationError('Please use a different email address.')
                
    def validate_dateAttaque(self, date_attaque):
        constats = Constats.query.filter_by(date_attaque=date_attaque.data).first()
        if constats is not None:
            raise ValidationError('Please use a different name address.')
    def validate_date(self, date_constat):
        constats = Constats.query.filter_by(date_constat=date_constat.data).first()
        if constats is not None:
            raise ValidationError('Please use a different name address.')    
