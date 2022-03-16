from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from src.models import User




class RegisterForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=30)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    password_confirm = PasswordField('Confirm Password',validators=[EqualTo('password'),DataRequired()])
    submit = SubmitField('Sign Up')
    
    #custom validation methods
    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('this username is taken, please choose another one.')
    
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('There is an account registered with this email, please login instead or use another email! ')
    
    

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')