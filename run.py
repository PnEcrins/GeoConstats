from datetime import datetime
from app.env import DB, MA
from flask import Flask, Blueprint

class ReverseProxied(object):
    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "") or self.script_name
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]
        scheme = environ.get("HTTP_X_SCHEME", "") or self.scheme
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_SERVER", "") or self.server
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)

app_globals = {}

def init_app():
    if app_globals.get('app', False):
        app = app_globals['app']
    else:
        app = Flask(__name__)
    app.config.from_object('config')
    app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=app.config['URL_APPLICATION'])

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
    app.run(debug=True)
