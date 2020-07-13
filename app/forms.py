from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, DateField, SubmitField, SelectField, HiddenField
from app.models import Constats,Declaratif, bib_statut, bib_type_animaux
from .env import DB
from wtforms.validators import DataRequired
from datetime import date
    

class LoginForm(FlaskForm):
    date_attaque = DateField('date_attaque', format='%Y/%m/%d',default=date.today)
    date_constat = DateField('date_constat', format='%Y/%m/%d',default=date.today)
    nom_agent1 = StringField('nom_agent1')
    nom_agent2 = StringField('nom_agent2')
    proprietaire = StringField('proprietaire')
    type_animaux = SelectField('type_animaux',choices=[])
    nb_victimes_mort = IntegerField('nb_victimes_mort')
    nb_victimes_blesse = IntegerField('nb_victimes_blesse')
    statut = SelectField('situation',choices=[])
    submit = SubmitField('Confirmer le consat')
class DeclaForm(FlaskForm):
    date_attaque_d = DateField('date_attaque_d', format='%Y/%m/%d',validators=[DataRequired(message="You need to enter the date")])
    date_constat_d = DateField('date_constat_d', format='%Y/%m/%d',validators=[DataRequired(message="You need to enter the date")])
    lieu_dit=StringField('lieu_dit')
    proprietaire_d = StringField('proprietaire')
    type_animaux_d = SelectField('type_animaux',choices=[])
    nb_victimes_mort_d = IntegerField('nb_victimes_mort')
    nb_victimes_blesse_d = IntegerField('nb_victimes_blesse')
    statut_d = SelectField('situation',choices=[])
    submit = SubmitField('Confirmer le consat')    
