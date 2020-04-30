from app import app, DB
from app.models import Constats

@app.shell_context_processor
def make_shell_context():
    return {'DB': DB, 'Constats': Constats}
