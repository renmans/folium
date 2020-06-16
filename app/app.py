import requests

from config import Config
from forms import LoginForm

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(app.config["DB_URL"])
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pass
    return render_template("index.html", title="Sign Up", form=LoginForm())


if __name__ == "__main__":
    app.run(debug=True)
