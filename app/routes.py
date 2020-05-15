from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from .env import DB
from app.models import Constats
from app.forms import LoginForm
from sqlalchemy import func
import json
from shapely.geometry import mapping
from geoalchemy2.shape import to_shape

app = Flask(__name__)

app.config['SECRET_KEY'] = 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://raph:Raphael18@localhost:5432/geoConstat"

with app.app_context():
    from .models import Constats
    from app.forms import LoginForm
    from .env import DB
    DB.init_app(app)
    #DB.create_all()

    Constats.query.all()


@app.route("/")
@app.route("/map")
def map(): 
    data = DB.session.query(Constats).all()
    print(data[0].geometry)
    wkt=to_shape(data[0].geometry)
    geojson=mapping(wkt)
    print(geojson)
    return render_template('map.html', title='Map', Constats=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = LoginForm()
    if form.validate_on_submit():
        data = request.form
        constats = Constats(
            date=data['date'],
            nbVictimes=data['nbVictimes'],
            moment=data['moment'],
            chien=data['chien'],
            berger=data['berger'],
            valide=data['valide'],
        )
        DB.session.add(constats)
        DB.session.commit()
        return render_template('map.html')
    else:
        return render_template('add.html', title="Add_to_database", form=form )
