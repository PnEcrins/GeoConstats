from datetime import datetime
from app.env import DB, MA
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from urllib.parse import urlsplit


app_globals = {}

def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)
    app.config.from_object('config')
    api_uri = urlsplit(app.config['URL_APPLICATION'])
    app.config['APPLICATION_ROOT'] = api_uri.path
    app.config['PREFERRED_URL_SCHEME'] = api_uri.scheme
    # app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=app.config['URL_APPLICATION'])
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

    @app.context_processor
    def inject_year():
        return {
            "current_year": datetime.now().year
        }
    with app.app_context():
        
        DB.init_app(app)
        DB.app = app
        app.config['DB'] = DB
        MA.init_app(app)
        
        from pypnusershub import routes
        app.register_blueprint(routes.routes, url_prefix='/pypn/auth')    

        from app.views import routes
        app.register_blueprint(routes, url_prefix='/')
    
    return app

app=init_app()

if __name__ == "__main__":
    app.run(debug=True, port=5002)
