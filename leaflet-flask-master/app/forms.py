from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField, DateField, SubmitField
from app.models import Constats
from .env import DB
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    date = DateField('date')
    nbVictimes = IntegerField('nbVictimes')
    moment = StringField('moment')
    chien = BooleanField('chien')
    berger = BooleanField('berger')
    valide = StringField('valide')
    submit = SubmitField('Add to database')

    def validate_valide(self, valide):
        constats = Constats.query.filter_by(valide=valide.data).first()
        if constat is not None:
            raise ValidationError('Please use a different surname.')
    """
    def validate_email(self, email):
        constats = Constats.query.filter_by(email=email.data).first()
        if constats is not None:
            raise ValidationError('Please use a different email address.')
                
    def validate_name(self, name):
        constats = Constats.query.filter_by(name=name.data).first()
        if constats is not None:
            raise ValidationError('Please use a different name address.')
    """
