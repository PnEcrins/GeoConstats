from app.views import app
from app.env import DB
app.config.from_object('config')
DB.init_app(app)
print(app.config)
if __name__ == "__main__":
    app.run(debug=True)
