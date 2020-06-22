import os
# import requests
from hashlib import sha256

from config import Config
from forms import LoginForm, SignUpForm, SearchForm

from flask import (Flask, render_template, redirect, url_for, session, flash)
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def passwd_hash(p):
    return sha256(p.encode('utf-8')).hexdigest()


@app.route("/", methods=['GET', 'POST'])
def index():
    # Redirect if user not logged out
    if session['user']:
        return redirect(url_for('search', name=session['user']))

    action = "Sign Up"  # Content for buttons and forms

    form = SignUpForm()
    if form.validate_on_submit():
        # hashing password and convert it to hex number
        # password in range from 6 to 40 char's
        email = form.email.data
        username = form.username.data
        password = passwd_hash(form.password.data)

        try:
            db.execute("""INSERT INTO users (email, username, password)
                       VALUES (:email, :username, :password)""",
                       {"email": email, "username": username,
                        "password": password})
            db.commit()
        except IntegrityError:
            flash("Seems like this account already exists")
            return render_template("index.html", title=action, form=form,
                                   action=action)

        # TODO: Access only for auth users
        session['user'] = username
        print(username)
        return redirect(url_for('search', name=username))

    return render_template("index.html", title=action, form=form,
                           action=action)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # Redirect if user not logged out
    if session['user']:
        return redirect(url_for('search', name=session['user']))

    action = "Log In"  # Content for buttons and forms

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = passwd_hash(form.password.data)
        username = db.execute("""SELECT username FROM users WHERE
                              email = :email AND password = :password""",
                              {"email": email, "password": password}
                              ).fetchone()[0]
        if username:
            session['user'] = username
            print(username)
            return redirect(url_for('search', name=username))

    return render_template("index.html", title=action, form=form,
                           action=action)


@app.route("/<name>/search", methods=['GET', 'POST'])
def search(name):
    # if user is not auth then redirect them to login page
    if session['user'] != name:
        return redirect(url_for('login'))

    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.query.data
        s = '%' + search_query + '%'
        books = db.execute("""SELECT * FROM books WHERE (isbn LIKE :s) OR
                           (title LIKE :s) OR
                           (author LIKE :s);""", {"s": s}).fetchall()
        return render_template("search.html", name=name, title="Search",
                               form=form, books=books)

    return render_template("search.html", name=name, title="Search", form=form)


if __name__ == "__main__":
    app.run(debug=True)
