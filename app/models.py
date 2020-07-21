from .env import DB
from geoalchemy2 import Geometry

class Constats(DB.Model):
    __tablename__ = "t_constats"
    __table_args__={"schema":"constats_loups"}
    id_constat = DB.Column(DB.Integer, primary_key=True,autoincrement=True)
    date_attaque = DB.Column(DB.Date)
    date_constat = DB.Column(DB.Date)
    nom_agent1 = DB.Column(DB.String)
    nom_agent2 = DB.Column(DB.String)
    proprietaire = DB.Column(DB.String)
    type_animaux = DB.Column(DB.Integer)
    nb_victimes_mort = DB.Column(DB.Integer)
    nb_victimes_blesse = DB.Column(DB.Integer)
    statut = DB.Column(DB.Integer)
    id_secteur=DB.Column(DB.Integer)
    the_geom_point= DB.Column(Geometry("GEOMETRY", 2154))
class Declaratif(DB.Model):
    __tablename__="t_constats_declaratifs"
    __table_args__={"schema":"constats_loups"}
    id_constat_d=DB.Column(DB.Integer, primary_key=True)
    date_attaque_d = DB.Column(DB.Date)
    date_constat_d = DB.Column(DB.Date)
    lieu_dit=DB.Column(DB.String)
    proprietaire_d = DB.Column(DB.String)
    type_animaux_d = DB.Column(DB.String)
    nb_victimes_mort_d = DB.Column(DB.Integer)
    nb_victimes_blesse_d = DB.Column(DB.Integer)
    statut_d = DB.Column(DB.String(10))
    geom=DB.Column(Geometry("GEOMETRY",2154))    

class bib_statut(DB.Model):   
    __tablename__="bib_statut"
    __table_args__={"schema":"constats_loups"}
    id=DB.Column(DB.Integer, primary_key=True)
    nom=DB.Column(DB.String)
class bib_type_animaux(DB.Model):   
    __tablename__="bib_type_animaux"
    __table_args__={"schema":"constats_loups"}
    id=DB.Column(DB.Integer, primary_key=True)
    nom=DB.Column(DB.String)    
class l_areas(DB.Model):
    __tablename__="l_areas"
    __table_args__={"schema":"ref_geo"}
    id_area=DB.Column(DB.Integer, primary_key=True,autoincrement=True)
    area_name=DB.Column(DB.String)
    area_code=DB.Column(DB.String)    