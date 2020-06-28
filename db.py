import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def add_user(email, username, passwd):
    db.execute("""INSERT INTO users (email, username, password)
               VALUES (:email, :username, :password)""",
               {"email": email, "username": username, "password": passwd})
    db.commit()


def get_username(email, passwd):
    username = db.execute("""SELECT username FROM users WHERE email = :email
                          AND password = :password""",
                          {"email": email, "password": passwd}).fetchone()[0]
    return username


def get_books(query):
    books = db.execute("""SELECT * FROM books WHERE (isbn LIKE :query) OR
                       (title LIKE :query) OR (author LIKE :query);""",
                       {"query": query}).fetchall()
    return books


def get_book(bid):
    book = db.execute("""SELECT * FROM books WHERE id = :id;""",
                      {"id": bid}).fetchone()
    return book


def get_book_by_isbn(isbn):
    book = db.execute("""SELECT * FROM books WHERE isbn = :isbn;""",
                      {"isbn": isbn}).fetchone()
    return book


def get_uid(username):
    uid = db.execute("""SELECT id FROM users WHERE username = :username;""",
                     {"username": username}).fetchone()[0]
    return uid


def add_review(uid, bid, review, rating):
    db.execute("""INSERT INTO reviews (user_id, book_id, review, rating)
               VALUES (:uid, :book_id, :review, :rating)""",
               {"uid": uid, "book_id": bid, "review": review,
                "rating": rating})
    db.commit()


def get_review(bid, uid):
    review = db.execute("""SELECT COUNT(*) FROM reviews WHERE (book_id = :bid)
                        AND (user_id = :uid);""",
                        {"bid": bid, "uid": uid}).fetchone()[0]
    return int(review)


def get_reviews(bid):
    reviews = db.execute("""SELECT username, review, rating, createtime FROM
                         reviews LEFT JOIN users ON reviews.user_id = users.id
                         WHERE book_id = :id""", {"id": bid})
    return reviews


def get_avg_rating(bid):
    avg = db.execute("""SELECT AVG(rating) FROM reviews WHERE
                     book_id = :bid""",
                     {"bid": bid}).fetchone()[0]
    avg = round(float(avg), 2) if avg else 0
    return avg
