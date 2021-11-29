from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import select, func

from .env import DB
from geoalchemy2 import Geometry
from pypnusershub.db.models import User
from sqlalchemy.orm import column_property


class BibAreaType(DB.Model):
    __tablename__ = "bib_areas_types"
    __table_args__ = {"schema": "ref_geo"}
    id_type = DB.Column(DB.Integer, primary_key=True)
    type_code = DB.Column(DB.String)
    
class LAreas(DB.Model):
    __tablename__ = "l_areas"
    __table_args__ = {"schema": "ref_geo"}
    id_area = DB.Column(DB.Integer, primary_key=True)
    id_type = DB.Column(DB.Integer, ForeignKey("ref_geo.bib_areas_types.id_type"))
    area_name = DB.Column(DB.Unicode)
    area_code = DB.Column(DB.Unicode)
    geom = DB.Column(Geometry("GEOMETRY", 2154))
    source = DB.Column(DB.Unicode)
    enable = DB.Column(DB.Boolean, nullable=False, default=True)

class Constats(DB.Model):
    __tablename__ = "t_constats"
    __table_args__={"schema":"constats_loups"}
    id_constat = DB.Column(DB.Integer, primary_key=True,autoincrement=True)
    date_attaque = DB.Column(DB.Date)
    date_constat = DB.Column(DB.Date)
    nom_agent1 = DB.Column(DB.String)
    nom_agent2 = DB.Column(DB.String)
    proprietaire = DB.Column(DB.String)
    type_animaux = DB.Column(DB.Integer, ForeignKey("constats_loups.bib_type_animaux.id"))
    nb_victimes_mort = DB.Column(DB.Integer)
    nb_victimes_blesse = DB.Column(DB.Integer)
    nb_disparus = DB.Column(DB.Integer)
    nb_indemnises = DB.Column(DB.Integer)
    statut = DB.Column(DB.Integer, ForeignKey("constats_loups.bib_statut.id"))
    nb_jour_agent=DB.Column(DB.Float)
    id_secteur=DB.Column(DB.Integer, ForeignKey(LAreas.id_area))
    id_commune=DB.Column(DB.Integer, ForeignKey(LAreas.id_area))
    id_departement=DB.Column(DB.Integer, ForeignKey(LAreas.id_area))
    dans_coeur=DB.Column(DB.Boolean)
    dans_aa=DB.Column(DB.Boolean)
    id_role=DB.Column(DB.Integer, ForeignKey(User.id_role))
    the_geom_point= DB.Column(Geometry("GEOMETRY", 2154))
    declaratif = DB.Column(DB.Boolean)
    comment = DB.Column(DB.String)
    
    statut_rel = DB.relationship(
        "bib_statut", lazy="joined"
    )
    type_animaux_rel = DB.relationship(
        "bib_type_animaux", lazy="joined"
    )
    digitizer = DB.relationship(
        User, lazy="joined"
    )
    secteur = DB.relationship(
        LAreas, lazy="select", foreign_keys=[id_secteur]
    )
    commune = DB.relationship(
        LAreas, lazy="select", foreign_keys=[id_commune], 
    )
    departement = DB.relationship(
        LAreas, lazy="select", foreign_keys=[id_departement]
    )
    geom_4326 = column_property(
        func.st_transform(the_geom_point, 4326)
    )


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
    statut_d = DB.Column(DB.String(10), ForeignKey("constats_loups.bib_statut.id"))
    id_secteur_d=DB.Column(DB.Integer)
    id_commune_d=DB.Column(DB.Integer)
    departement_d=DB.Column(DB.String)
    dans_coeur_d=DB.Column(DB.Boolean)
    dans_aa_d=DB.Column(DB.Boolean)
    id_role=DB.Column(DB.Integer)
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
