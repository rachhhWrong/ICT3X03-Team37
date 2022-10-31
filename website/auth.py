from flask import Flask
from pymongo import MongoClient
#from main import app

# Database
#app.config['SECRET_KEY'] = 'testing'
client = MongoClient()
account_db = client["account"]
product_db = client["product"]
