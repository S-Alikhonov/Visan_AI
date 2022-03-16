from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
app = Flask(__name__)
api  = Api(app)
app.config['SECRET_KEY'] = 'its my secret key that is needed to be changed immediately'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view ='login'
@app.before_first_request

def create_tables():
    db.create_all()
from src import web_routes
from src.routes import Heatmap

api.add_resource(Heatmap,'/api/<string:secret_key>')