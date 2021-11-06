import os
import pandas as pd

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
import re
import psycopg2
import time
import datetime

from helpers import login_required, apology


from flask_sqlalchemy import SQLAlchemy

# dydx public end points imports
from dydx3 import Client
from web3 import Web3


# Configure application
app = Flask(__name__)
try:
    app.config.from_object(os.environ['APP_SETTINGS'])
except KeyError:
    pass
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#default='postgres://localhost/postgres',  # E.g., for local dev
database_url = os.getenv(
    'DATABASE_URL'
)

#database="funding_stats", user='postgres', password='password', host='127.0.0.1', port='5432'
try:
    conn = psycopg2.connect(
        database=database_url
        
    )

    cursor = conn.cursor()
except:
    print("there's something wrong")


# not too sure what this does
if __name__ == '__main__':
    app.run()


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up dydx API initialisation
client = Client(
    host='https://api.dydx.exchange',
    # web3=Web3('...'),
    # stark_private_key='01234abcd...',
)


# Get list of instruments

all_markets = client.public.get_markets()

market_list = all_markets["markets"]

# and append them to a list...
instruments_list = []
for key, value in market_list.items():
    instruments_list.append(key)


#The format for dictionary within a dictionary
#market_list["BTC-USD"]["nextFundingRate"]

conn = psycopg2.connect(
    database="funding_stats", user='postgres', password='password', host='127.0.0.1', port='5432'
)

cursor = conn.cursor()


"""
   Extract a list of instrument pairs - only ran once!
   Make a getmarkets function for each pair, calling the var "instrument"
   Make a sql_execute function for each pair, taking the var instrument as argument

"""

def getmarkets(instrument):
    try:
        markets_dict = client.public.get_markets(market=instrument)
        markets = markets_dict["markets"]
        return markets
    except:
        print("getmarkets doesnt work")

getmarkets("BTC-USD")

def sql_execute(instrument):
    cursor.execute("""
    INSERT INTO funding (market, indexprice, nextfundingRate, nextfundingat) VALUES(%s, %s, %s, %s)
    """,
    (markets[instrument]["market"], markets[instrument]["indexPrice"], markets[instrument]["nextFundingRate"], markets[instrument]["nextFundingAt"]))


# fetch data from API and execute insert statement to Postgres database
while True:
    for instrument in market_list:
        getmarkets(instrument)
        markets = getmarkets(instrument)

        sql_execute(instrument)

    conn.commit()

    print(datetime.datetime.now().minute)

    time.sleep(60 - datetime.datetime.now().second)


"""
# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")
"""

# This line has to be added after db has already been initalised
#from models import Result


@app.route("/")
def index():

    # TO DO...
    return(markets["BTC-USD"]["market"])


@app.route("/buy", methods=["GET", "POST"])
def buy():
    # TODO
    return redirect("/login")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
