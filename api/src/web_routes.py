import uuid
from src import app,bcrypt,db
from flask import render_template,request,redirect,url_for,flash
from src.models import Insights,User
from flask_login import login_required, login_user,current_user,logout_user
from src.forms import RegisterForm,LoginForm
import plotly
import plotly.express as px
import pandas as pd
import json
from datetime import datetime,date,timedelta
from src import db
from sqlalchemy import func

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('home.html',title='Home page')


@app.route('/dash',methods=['POST','GET'])
@login_required
def dash():
    if request.method == 'POST':
        input_date = request.form.get('date')
        try:
            input_date = datetime.strptime(input_date,'%d/%m/%Y')
        except:
            return redirect(url_for('dash'))
            pass
    else :
        input_date = datetime.now()
    insights =Insights.query.filter(func.date(Insights.time_interval)==input_date.date()).all()
    data = [[insight.people_count,insight.time_interval.strftime('%H:00')] for insight in insights]
    if input_date.day == date.today().day:
        given_date = 'Today'
    elif input_date.day == (date.today() - timedelta(days=1)).day:
        given_date = 'Yesterday'
    else:
        given_date = input_date.date().strftime("%d %B, %Y")
    if len(data)>0:
        df = pd.DataFrame(data)
        #chart
        figure = px.bar(df,x=1,y=df.columns[0],
                        labels={'0':'number of visitors','1':'time interval'},
                        
                       )
        figure.update_layout(title_x=0.5,
                             yaxis = dict(dtick = 1),
                             paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)')
        graph = json.dumps(figure,cls=plotly.utils.PlotlyJSONEncoder)
        images = [[insight.heatmap,insight.time_interval.strftime('%H:00')] for insight in insights]
    else:
        graph=None
        images=None
    
    return render_template('dashboard.html',graph=graph,images=images,given_date=given_date,title='Dashboard')


@app.route('/account',methods=['POST','GET'])
@login_required
def account():
    if request.method == 'POST':
        current_user.secret_key = str(uuid.uuid4())
        db.session.commit()
    return render_template('account.html')
@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        ## password ecryption
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created successfully, you can login now!','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Sign Up',form=form)


@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login was unsuccessful. Please check your email and password!','danger')
          
    return render_template('login.html',title='Login',form=form)

@app.route('/logout',methods=['POST','GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))

