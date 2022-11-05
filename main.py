import json

import pyotp
from flask import *
from datetime import datetime
from website import auth
from website.models import *
import os
import bcrypt


app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
# never send cookies to third-party sites
app.config["SESSION_COOKIE_SAMESITE"] = 'Strict'
# There are more configs set for non-debug mode; see bottom of file

mongo = auth.start_mongo_client(app)


@app.after_request
def add_security_headers(response):
    if __name__ == '__main__' and not os.environ.get("DEPLOY_MODE", None):
        # only use these headers in deployment mode
        return
    # require HTTPS
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    # do not allow this website to be embedded inside another website
    # prevent clickjacking attack
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # disable content type auto-detection on browser
    # prevents scripts or webpages being loaded through image or text
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response


@app.route('/favicon.ico')
def favicon():
    app.send_static_file('favicon.ico')


@app.route('/')
def home():
    session.get('email')
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_users = users.find_one({"email": request.form['email']})
        try:
            if existing_users is None:
                hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert_one({'name': request.form['name'], 'email': request.form['email'], 'password': hashpass,
                                  'address': request.form['address'], 'mobile': request.form['mobile']})
                session.permanent = True
                session['email'] = request.form['email']
                flash('Registered!', category='success')
                print('registered', )
                return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash('Invalid Email or Email Exist', category='error')
            return redirect(url_for('register'))

    return render_template("register.html")


@app.route('/analyst_login', methods=['POST', 'GET'])
def analyst_login():
    analyst = mongo.db.analyst
    logs = mongo.db.logs
    if request.method == 'POST':
        analyst_user = analyst.find_one({'email': request.form['email']})
        if analyst_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), analyst_user['password']) == analyst_user[
                'password']:
                time_in = "UTC " + datetime.now().strftime("%X")
                logs.insert_one(
                    {'email': analyst_user['email'], 'date': datetime.now().strftime("%x"), 'login_time': time_in})
                session['email'] = request.form['email']
                flash('Login Success', category='success')
                return redirect(url_for("login"))
            else:
                flash('Login Failed', category='error')
        else:
            flash('Account does not exist', category='error')

    return render_template("analyst_login.html")



@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users
    logs = mongo.db.logs
    if request.method == 'POST':
        login_user = users.find_one({'email': request.form['email']})
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user[
                'password']:
                time_in = "UTC " + datetime.now().strftime("%X")
                logs.insert_one(
                    {'email': login_user['email'], 'date': datetime.now().strftime("%x"), 'login_time': time_in})
                session['email'] = request.form['email']
                flash('Login Success', category='success')
                return redirect(url_for("allproducts"))
            else:
                flash('Login Failed', category='error')
        else:
            flash('Account does not exist', category='error')

    return render_template("login.html", boolean=True)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    flash('Successfully Logged Out', category='success')
    # print(session['username'])
    return redirect('/')



@app.route('/test/')
def test():
    return render_template("test.html")


@app.route('/analyst/', methods=['GET', 'POST'])
def analyst():
    order = mongo.db.orders
    counter = 0
    order_arr = []
    order_big_arr = []
    logs = mongo.db.logs
    for i in order.find():
        counter += 1
        order_arr.append(counter)
        order_arr.append(str(i['name']))
        order_arr.append(str(i['order']))
        order_arr.append(str(i['_id']))
        order_big_arr.append(order_arr)
        order_arr = []
    counter = 0
    log_arr = []
    log_big_arr = []
    for i in logs.find():
        counter += 1
        log_arr.append(counter)
        log_arr.append(str(i['email']))
        log_arr.append(str(i['date']))
        log_arr.append(str(i['login_time']))
        log_big_arr.append(log_arr)
        log_arr = []
    return render_template("data_analyst_page.html", log_big_arr=log_big_arr, order_big_arr=order_big_arr)


@app.route('/account/')
def account():
    email = session.get('email')
    users = mongo.db.users
    user = users.find_one({'email': email})
    name = user['name']
    address = user['address']
    mobile = user['mobile']
    return render_template("account_page.html", name=name, address=address, mobile=mobile)


@app.route('/edit_account/', methods=['GET', 'POST'])
def edit_account():
    email = session.get('email')
    users = mongo.db.users
    user = users.find_one({'email': email})
    name = user['name']
    address = user['address']
    mobile = user['mobile']
    if request.method == 'POST':
        if user:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.find_one_and_update({'email': session['email']}, {
                '$set': {'name': request.form['name'], 'email': request.form['email'], 'password': hashpass,
                         'address': request.form['address'], 'mobile': request.form['mobile']}})
            session['email'] = request.form['email']
            return redirect(url_for('home'))
    return render_template("edit_account_page.html", name=name, address=address, mobile=mobile)


@app.route('/delete_account/', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'email': session['email']})
        if user:
            users.delete_one({'email': session['email']})
            session.pop('email', None)
            flash('Account Successfully Deleted!', category='success')
            return redirect(url_for('home'))
    return redirect(url_for('home'))


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
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    return render_template("all_products.html", allproducts=findproduct)


@app.route('/indiv-product/id=<int:id>', methods=['GET', 'POST'])
def showgood(id):
    product = mongo.db.products
    retrieve_product = product.find_one({'product_id': id})
    return render_template("indiv_product.html", product=retrieve_product)


@app.route('/menu/')
def menu():
    return render_template("menu.html")


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, port=3000)
else:
    # deployment mode settings
    from random import SystemRandom
    import string

    if skey := os.environ.get("SECRET_KEY", None):
        app.secret_key = skey
    else:
        app.secret_key = ''.join(
            SystemRandom().choice(string.ascii_letters + string.digits) \
            for _ in range(32)
        )
    if mode := os.environ.get("DEPLOY_MODE", None):
        # cookies expire after 15 minutes inactivity
        app.config["PERMANENT_SESSION_LIFETIME"] = 900
        # require HTTPS to load cookies
        app.config["SESSION_COOKIE_SECURE"] = True
