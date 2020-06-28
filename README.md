# folium
Website with Book Reviews

## Running
```
git clone https://github.com/renmans/folium.git
pip3 install -r requirements.txt
set FLASK_APP = app.py
set DATABASE_URL = PostgreSQL URI
set SECRET_KEY = Your secret key or os.urandom(<int>)
set API_KEY = Your api key for GoodReads
flask run
```

## Demo
Folium on [Heroku](https://folium-app.herokuapp.com/)

![Log In](/static/img/login.png)

![Search](/static/img/search.png)

![Book Page](/static/img/book.png)

## API

#### Get information about a book by ISBN

**URL:** /api/\<isbn\>

**HTTP method:** GET

**Parameters:**
* isbn: The ISBN of the book to lookup.

Response example:
```
{
    "title": "Memory",
    "author": "Doug Lloyd",
    "year": 2015,
    "isbn": "1632168146",
    "review_count": 28,
    "average_score": 5.0
}
```

## TODO
* ~~Registration~~
* ~~Login~~
* ~~Logout~~
* ~~Import~~
* ~~Search~~
* ~~Book Page~~
* ~~Review Submission~~
* ~~Goodreads Review Data~~
* ~~API Access~~
