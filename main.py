from flask import render_template, Flask, request
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

@app.route('/analyst/')
def analyst():
    return render_template("data_analyst_page.html")

@app.route('/account/')
def account():
    return render_template("edit_account_page.html")

@app.route('/about-us/')
def about():
    return render_template("about.html")

@app.route('/all-products/')
def allproducts():
    return render_template("all_products.html")


@app.route('/indiv-product/id=<int:id>', methods=['GET', 'POST'])
def showgood(id):
    id = request.args.get('id')
    return render_template("indiv_product.html")

@app.route('/user/signup/', methods=['POST'])
def signup():
    return User().signup()


if __name__ == '__main__':
    app.run(debug=True, port=3000)
