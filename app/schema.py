from geoalchemy2.shape import to_shape
from geojson import Feature
from marshmallow.decorators import post_dump
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import fields, pre_dump

from app.models import Constats, bib_statut, bib_type_animaux, LAreas
from pypnusershub.schemas import UserSchema
from .env import MA


class LAreasSchema(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = LAreas
        exclude = ("geom",)


class BibTypeAnimaux(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = bib_type_animaux


class BibStatutSchema(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = bib_statut


class ConstatSchema(MA.SQLAlchemyAutoSchema):
    class Meta:
        model = Constats
        exclude = ("the_geom_point",)
        include_fk = True

    comment = fields.String()
    the_geom_point = fields.Method("geom_to_shape")
    geom_4326 = fields.Method("geom_to_shape")
    statut_rel = MA.Nested(BibStatutSchema, dump_only=True)
    type_animaux_rel = MA.Nested(BibTypeAnimaux, dump_only=True)
    digitizer = MA.Nested(UserSchema, dump_only=True)
    commune = MA.Nested(LAreasSchema, dump_only=True)
    secteur = MA.Nested(LAreasSchema, dump_only=True)
    departement = MA.Nested(LAreasSchema, dump_only=True)

    def geom_to_shape(self, obj):
        return to_shape(obj.geom_4326)

    @post_dump(pass_many=True)
    def geojsonify(self, data, many, **kwargs):
        return Feature(geometry=data.pop("geom_4326"), properties=data)


class ConstatSchemaDownload(ConstatSchema):
    export_columns = [
        "id_constat",
        "date_attaque",
        "date_constat",
        "nom_agent1",
        "nom_agent2",
        "proprietaire",
        "type_animaux",
        "nb_victimes_mort",
        "nb_victimes_blesse",
        "nb_disparus",
        "nb_indemnises",
        "statut",
        "declaratif",
        "nb_jour_agent",
        "comment",
        "dans_aa",
        "dans_coeur",
        "departement",
        "commune",
        "secteur",
        "geom_4326",
        "digitizer",
    ]

    @post_dump(pass_many=True)
    def geojsonify(self, data, many, **kwargs):
        type_anim = data.pop("type_animaux_rel")
        data["type_animaux"] = type_anim.get("nom", "") if type_anim else ""
        statut = data.pop("statut_rel")
        data["statut"] = statut.get("nom", "") if statut else ""
        secteur = data.pop("secteur")
        data["secteur"] = secteur.get("area_name", "") if secteur else ""
        commune = data.pop("commune")
        data["commune"] = commune.get("area_name", "") if commune else ""
        digitizer = data.pop("digitizer")
        data["digitizer"] = digitizer.get("nom_complet", "") if digitizer else ""
        departement = data.pop("departement")
        data["departement"] = departement.get("area_name", "") if departement else ""
        return data
