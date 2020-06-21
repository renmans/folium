import os
from csv import reader
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def importer():
    with open("books.csv", "r") as f:
        f.readline()
        books = reader(f)
        for isbn, title, author, year in books:
            db.execute("""INSERT INTO books (isbn, title, author, year)
                       VALUES (:isbn, :title, :author, :year);""",
                       {"isbn": isbn, "title": title, "author": author,
                        "year": year})
    db.commit()


if __name__ == "__main__":
    importer()
