# TODO: Refactoring
# TODO: Write decorator for required login
# TODO: Write documentation for functions

import os
import requests
from hashlib import sha256

from config import Config
from forms import LoginForm, SignUpForm, SearchForm, ReviewForm

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
    # hashing password and convert it to hex number
    # password in range from 6 to 40 char's
    return sha256(p.encode('utf-8')).hexdigest()


def check_session():
    # Redirect if user not logged out
    # TODO: REPLACE WITH DECORATOR
    try:
        if session['user']:
            return redirect(url_for('search', name=session['user']))
    except KeyError:
        session['user'] = None


def goodreads_rating(isbn):
    key = app.config["API_KEY"]
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": key, "isbns": isbn})
    rating = res.json()["books"][0]["average_rating"]
    reviews_count = res.json()["books"][0]["work_ratings_count"]
    return (rating, reviews_count)


@app.route("/", methods=['GET', 'POST'])
def index():
    # TODO: REPLACE WITH DECORATOR
    check_session()

    action = "Sign Up"  # Content for buttons and forms

    form = SignUpForm()
    if form.validate_on_submit():
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

        session['user'] = username
        return redirect(url_for('search', name=username))

    return render_template("index.html", title=action, form=form,
                           action=action)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # TODO: REPLACE WITH DECORATOR
    check_session()

    action = "Log In"  # Content for buttons and forms

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = passwd_hash(form.password.data)
        try:
            username = db.execute("""SELECT username FROM users WHERE
                                  email = :email AND password = :password""",
                                  {"email": email, "password": password}
                                  ).fetchone()[0]
        except TypeError:
            username = None
        if username:
            session['user'] = username
            return redirect(url_for('search', name=username))
        else:
            flash("Wrong email or password")

    return render_template("index.html", title=action, form=form,
                           action=action)


@app.route("/search")
@app.route("/search/<name>", methods=['GET', 'POST'])
def search(name=None):
    # name is None when link is clicked
    # TODO: REPLACE WITH DECORATOR
    if name is None:
        try:
            if session['user']:
                return redirect(url_for('search', name=session['user']))
        except KeyError:
            return redirect(url_for('login'))

    # if user is not auth then redirect them to login page
    # TODO: REPLACE WITH DECORATOR
    if session['user'] != name:
        return redirect(url_for('login'))

    form = SearchForm()
    if form.validate_on_submit():
        search_query = form.query.data
        s = '%' + search_query + '%'
        # TODO: Make a separate function
        books = db.execute("""SELECT * FROM books WHERE (isbn LIKE :s) OR
                           (title LIKE :s) OR
                           (author LIKE :s);""", {"s": s}).fetchall()
        return render_template("search.html", name=name, title="Search",
                               form=form, books=books)

    return render_template("search.html", name=name, title="Search", form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def book(book_id):
    # TODO: REPLACE WITH DECORATOR
    try:
        if session['user']:
            pass
    except KeyError:
        return redirect(url_for('login'))

    # TODO: Make a separate function
    book_data = db.execute("""SELECT * FROM books WHERE id = :id;""",
                           {"id": book_id}).fetchone()
    book_id = book_data['id']

    # TODO: Make a separate function
    uid = db.execute("""SELECT id FROM users WHERE username = :username;""",
                     {"username": session['user']}).fetchone()[0]

    # TODO: Make a separate function
    reviews_counter = int(db.execute("""SELECT COUNT(*) FROM reviews
                                     WHERE (book_id = :bid)
                                     AND (user_id = :uid);""",
                                     {"bid": book_id,
                                      "uid": uid}).fetchone()[0])

    # TODO: Make a separate function
    avg_rating = db.execute("""SELECT AVG(rating) FROM reviews
                            WHERE book_id = :book_id""", {"book_id": book_id}
                            ).fetchone()[0]
    avg_rating = round(float(avg_rating), 2) if avg_rating else 0

    # TODO: Make a separate function
    reviews = db.execute("""SELECT * FROM reviews WHERE book_id = :id""",
                         {"id": book_id})

    gr_rating = goodreads_rating(book_data['isbn'])

    form = ReviewForm()
    if form.validate_on_submit():
        if reviews_counter == 0:
            review = form.review.data
            rating = int(form.rating.data)
            # TODO: Make a separate function
            db.execute("""INSERT INTO reviews (user_id, book_id, review,
                       rating) VALUES (:uid, :book_id, :review, :rating)""",
                       {"uid": uid, "book_id": book_id, "review": review,
                        "rating": rating})
            db.commit()
        else:
            flash("You have already left a review")

    return render_template('book.html', title=book_data['title'],
                           book=book_data, form=form, reviews=reviews,
                           rating=avg_rating, gr_rating=gr_rating)


if __name__ == "__main__":
    app.run(debug=True)
