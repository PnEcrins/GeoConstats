from .env import DB
from geoalchemy2 import Geometry
from sqlalchemy.schema import FetchedValue


class UsersView(DB.Model):
    __tablename__ = 'v_userslist_forall_applications'
    __table_args__ = {'schema': 'utilisateurs'}

    id_role = DB.Column(DB.Integer, primary_key=True)
    identifiant = DB.Column(DB.String)
    nom_role = DB.Column(DB.String)
    id_organisme = DB.Column(DB.Integer)
    id_application = DB.Column(DB.Integer)
    id_droit_max = DB.Column(DB.Integer)  