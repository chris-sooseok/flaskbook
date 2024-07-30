from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Username is required."),
                                                   Length(min=1, max=30, message="Username is min 1, max 30")])
    email = StringField('Email', validators=[DataRequired("Email is required."),Email(message="Email is required."),])
    password = PasswordField('Password', validators=[DataRequired("Password is required."),])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired("Email is required."),Email(message="Email is required."),])
    password = PasswordField('Password', validators=[DataRequired("Password is required."),])
    submit = SubmitField('Log In')
