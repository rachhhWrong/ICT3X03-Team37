from flask import Flask
# from pymongo import MongoClient
from flask_pymongo import PyMongo
#from main import app
from os import environ as env

# sanitize input by allowing only alphanumerics
DBNAME = env.get("MONGO_INITDB_DATABASE", "")
DBNAME = DBNAME if DBNAME.isalnum() else None
DBUSER = env.get("MONGO_NONROOT_USERNAME", "")
DBUSER = DBUSER if DBUSER.isalnum() else None
DBPASS = env.get("MONGO_NONROOT_PASSWORD", "")
DBPASS = DBPASS if DBPASS.isalnum() else None

if DBNAME is None:
    raise EnvironmentError("DB Name Not Set in environment variables!")
if DBUSER is None:
    raise EnvironmentError("DB Service User Not Set in environment variables!")
if DBPASS is None:
    raise EnvironmentError("DB Service Password Not Set in environment variables!")

# Database
#app.config['SECRET_KEY'] = 'testing'
# client = MongoClient()
client = None
# account_db = client["account"]
# product_db = client["product"]
def start_mongo_client(app):
    app.config['MONGO_DBNAME'] = DBNAME
    app.config['MONGO_URI'] = f"mongodb://database:27017/{DBNAME}"
    global client
    client = PyMongo(app,
        username=DBUSER,
        password=DBPASS,
        authSource=DBNAME
    )
    return client
