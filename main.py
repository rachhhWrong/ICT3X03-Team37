from flask import render_template, Flask
from website.models import User
import pymongo


app = Flask(__name__, template_folder='website/templates',static_folder='website/static')

@app.route('/favicon.ico')
def favicon():
    app.send_static_file('favicon.ico')

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login/')
def login():
    return render_template("login.html")

@app.route('/register/')
def register():
    return render_template("register.html")

@app.route('/user/register/', methods=['POST'])
def registerUser():
    return User().register()

@app.route('/about-us/')
def about():
    return render_template("about.html")

@app.route('/all-goods/')
def allgoods():
    return render_template("allgoods.html")



if __name__ == '__main__':
    app.run(debug=True, port=3000)
