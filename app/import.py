from csv import reader
import sqlalchemy


def importer(file_obj):
    books = reader(file_obj)
    for isbn, title, author, year in books:
        pass


if __name__ == "__main__":
    with open("books.csv", "r") as f:
        importer(f)
