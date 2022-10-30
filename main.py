from flask import render_template, Flask
from website.models import User
import pymongo


app = Flask(__name__, template_folder='website/templates',static_folder='website/static')



@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login/')
def login():
    return render_template("login.html")

@app.route('/register/')
def register_main():
    return render_template("register.html")

@app.route('/user/register/', methods=['POST'])
def register():
    return User().register()

@app.route('/about-us/')
def about():
    return render_template("test.html")

@app.route('/menu/')
def menu():
    return render_template("menu.html")

if __name__ == '__main__':
    app.run(debug=True, port=3000)
