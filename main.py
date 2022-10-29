from flask import Blueprint, render_template, request, flash, jsonify, Flask
from flask_login import login_required, current_user, UserMixin
from flask_sqlalchemy import *
import json

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SECRET_KEY'] = "key"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/regsiter', methods=['GET', 'POST'])
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=3000)