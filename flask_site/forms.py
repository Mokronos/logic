from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, Form

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(min=10), validators.InputRequired()])


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.InputRequired()])
    password = PasswordField('Password', [validators.Length(min=10), validators.InputRequired(),
                                          validators.EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Repeat Password', [validators.Length(min=10), validators.InputRequired()])
