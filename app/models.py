from .env import DB
from geoalchemy2 import Geometry

class Constats(DB.Model):
    __tablename__ = "constats"
    id = DB.Column(DB.Integer, primary_key=True)
    date_attaque = DB.Column(DB.Date)
    date_constat = DB.Column(DB.Date)
    nom_agent1 = DB.Column(DB.String)
    nom_agent2 = DB.Column(DB.String)
    proprietaire = DB.Column(DB.String)
    type_animaux = DB.Column(DB.String)
    nb_victimes_mort = DB.Column(DB.Integer)
    nb_victimes_blesse = DB.Column(DB.Integer)
    statut = DB.Column(DB.String(10))
    geometry = DB.Column(Geometry("GEOMETRY", 2154))
    geom_4326=DB.Column(Geometry("GEOMETRY", 4326))
    def __repr__(self):
        return '<Constats {}>'.format(self.date)
    
    def __repr__(self):
        return '<Constats {}>'.format(self.valide)
