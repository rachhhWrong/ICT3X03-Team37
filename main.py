from flask import *
from flask_pymongo import PyMongo
from website import auth
from website.models import *
import os
import bcrypt

app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
# app.config['MONGO_DBNAME'] = "TISBAKERY"
# app.config['MONGO_URI'] = "mongodb://localhost:27017/account"
# mongo = PyMongo(app)
mongo = auth.start_mongo_client(app)


@app.route('/favicon.ico')
def favicon():
    app.send_static_file('favicon.ico')


@app.route('/')
def home():
    session.get('username')
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_users = users.find_one({"name": request.form['username']})
        try:
            if existing_users is None:
                hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert_one({'name': request.form['username'], 'password': hashpass})
                session['username'] = request.form['username']

                flash('Registered!')
                print('registered', )
                return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash('Invalid Email or Email Exist')
            return redirect(url_for('register'))

    return render_template("register.html")


@app.route('/login')
def login_page():
    if 'username' in session:
        # print("Logged in as: " + session['username'])
        return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/submit', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    try:
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user['password']:
                session['username'] = request.form['username']
                # print(session['username'])
                return redirect(url_for('allproducts'))
    except:
        flash('Wrong email or password!')
        print("Wrong email or password!")
        return redirect(url_for('login_page'))

    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    # print(session['username'])
    return redirect('/')


@app.route('/navbar')
def nav_logout():
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to logout</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + "click here to login</b></a>"


@app.route('/test/')
def test():
    return render_template("test.html")


@app.route('/analyst/')
def analyst():
    return render_template("data_analyst_page.html")


@app.route('/account/')
def account():
    return render_template("account_page.html")


@app.route('/account/edit_account')
def edit_account():
    return render_template("edit_account_page.html")


@app.route('/checkout/')
def checkout():
    return render_template("checkout.html")


@app.route('/cart/')
def cart():
    return render_template("cart.html")


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



if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, port=3000)
else:
    from random import SystemRandom
    import string

    app.secret_key = ''.join(
        SystemRandom().choice(string.ascii_letters + string.digits) \
        for _ in range(32)
    )
