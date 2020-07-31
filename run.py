from app.env import DB
from flask import Flask, Blueprint

DB=DB


app_globals = {}

def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)

    with app.app_context():
        app.config.from_object('config')
        DB.init_app(app)
        DB.app = app
        app.config['DB'] = DB
        
        from pypnusershub import routes
        app.register_blueprint(routes.routes, url_prefix='/api/auth')    

        from app.views import routes
        app.register_blueprint(routes, url_prefix='/')
    
    return app

app=init_app()

if __name__ == "__main__":
    app.run(debug=True)
