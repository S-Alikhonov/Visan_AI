from flask_restful import Resource
from flask import request
from src import db
from src.models import Insights,User
import uuid

class Heatmap(Resource):
    
    def get(self,secret_key):
        return {"message":"hello world"}
    
    def post(self,secret_key):
        user = User.query.filter(User.secret_key==secret_key).first()
        if user:
            heatmap = request.form['heatmap']
            count = request.form['count']
            file = request.files['media']
            filename = f'{uuid.uuid4()}.jpg'
            file.save(f'api/src/static/uploads/{filename}')
            print(heatmap)
            
            insight = Insights(people_count=count,heatmap=filename,author_id=user.id)
            db.session.add(insight)
            db.session.commit()
            return {"heatmap":heatmap,'count':count}
        else:
            return {"message":'provide the appropriate secret key'}
        
        