import os
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

os.environ["FLASK_SQLALCHEMY_DB"] = "app.env.DB"
DB = SQLAlchemy()
os.environ["FLASK_MARSHMALLOW"] = "app.env.MA"
MA = Marshmallow()