from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    email = StringField('Email', [DataRequired(), Length(min=6, max=35)])
    password = PasswordField('Password',
                             [DataRequired(), Length(min=6, max=40)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign Up')


class SignUpForm(LoginForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=25)])


class SearchForm(FlaskForm):
    query = StringField('Search Query', [DataRequired()], render_kw={
        "placeholder": "ISBN, Title or Author",
        "class": "form-control"
    })
    search = SubmitField('Search')
