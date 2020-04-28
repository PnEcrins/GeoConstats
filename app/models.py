from .env import DB
from geoalchemy2 import Geometry

class Constats(DB.Model):
    __tablename__ = "constats"
    id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.Date)
    nbVictimes = DB.Column(DB.Integer)
    moment = DB.Column(DB.String(4))
    chien = DB.Column(DB.Boolean)
    berger = DB.Column(DB.Boolean)
    valide = DB.Column(DB.String(10))
    geometry = DB.Column(Geometry("GEOMETRY", 2154))
    
    def __repr__(self):
        return '<Constats {}>'.format(self.date)
    
    def __repr__(self):
        return '<Constats {}>'.format(self.valide)
