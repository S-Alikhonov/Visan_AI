from email.policy import default
from src import db,login_manager
from datetime import datetime,timedelta
from flask_login import UserMixin
import uuid



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(32),unique=True)
    email = db.Column(db.String(255),unique=True,nullable=False)
    password = db.Column(db.String(255),nullable=False)
    secret_key = db.Column(db.String(32),nullable=False,default=f'{uuid.uuid4()}')
    heatmaps = db.relationship('Insights',backref='author',lazy=True)
    
class Insights(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    time_interval = db.Column(db.DateTime,nullable=False,default=datetime.now)
    heatmap = db.Column(db.String(255),nullable=False)
    people_count = db.Column(db.Integer,nullable=False)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    