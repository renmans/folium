# TODO: Write decorator for required login
# TODO: Write documentation for functions

# stdlib modules
import requests
from hashlib import sha256

# SQLAlchemy modules
from sqlalchemy.exc import IntegrityError

# Flask modules
from flask import (Flask, render_template, redirect, url_for, session, flash)
from flask_session import Session

# App modules
import db
from config import Config
from forms import LoginForm, SignUpForm, SearchForm, ReviewForm

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def passwd_hash(p):
    """Hashing password and convert it to hex number
    password in range from 6 to 40 char's"""
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
    """Take the book's ISBN and returns the rating on GoodReads"""
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
            db.add_user(email, username, password)
        except IntegrityError:
            flash("Seems like this account already exists")
            return render_template("index.html", title=action, form=form,
                                   action=action)

        # TODO: SAME CODE #1
        session['user'] = username  # Remember current user
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
            username = db.get_username(email, password)
        except TypeError:
            username = None

        # TODO: SAME CODE #1
        if username:
            session['user'] = username  # Remember current user
            return redirect(url_for('search', name=username))
        else:
            flash("Wrong email or password")

    return render_template("index.html", title=action, form=form,
                           action=action)


@app.route("/search")
@app.route("/search/<name>", methods=['GET', 'POST'])
def search(name=None):
    """Search function for a book by its ISBN, title, or author"""
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
        query = '%' + form.query.data + '%'
        books = db.get_books(query)

        return render_template("search.html", name=name, title="Search",
                               form=form, books=books)

    return render_template("search.html", name=name, title="Search", form=form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def book(bid):
    # TODO: REPLACE WITH DECORATOR
    try:
        if session['user']:
            pass
    except KeyError:
        return redirect(url_for('login'))

    # Information about the book
    book = db.get_book(bid)

    uid = db.get_uid(session['user'])

    # Book rating and reviews
    avg_rating = db.get_avg_rating(bid)
    reviews = db.get_reviews(bid)

    # Book rating on GoodReads
    gr_rating = goodreads_rating(book['isbn'])

    form = ReviewForm()
    if form.validate_on_submit():
        # Checks whether the user has reviewed this book
        review_counter = db.get_review(bid, uid)

        if review_counter == 0:
            review = form.review.data
            rating = int(form.rating.data)
            db.add_review(uid, bid, review, rating)
        else:
            flash("You have already left a review")

    return render_template('book.html', title=book['title'],
                           book=book, form=form, reviews=reviews,
                           rating=avg_rating, gr_rating=gr_rating)


if __name__ == "__main__":
    app.run(debug=True)
