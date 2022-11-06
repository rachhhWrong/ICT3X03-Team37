import json
import urllib

import pyotp
from flask import *
from flask import Flask, redirect, request, render_template, jsonify
from datetime import datetime
from random import randint
from flask_mail import Mail, Message

from website import auth
from functools import wraps
import os
import bcrypt
import stripe
import pymongo
from bson import ObjectId

stripe.api_key = 'sk_test_51LyrlYDkn7CDktELAXteTo9GDPzeeDDG8vNEnDaU7MttLaEYrPyXLjHtXcBtlAiXDX8RUUWqcONKPsDRJv0miTYS00bf8yHq4N'
# domain_url = "http://127.0.0.1:5000/"
domain_url = "https://bakes.tisbakery.ml/"
line_items1 = []
app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
# never send cookies to third-party sites
# would prefer Strict, but it breaks navigating back from Stripe
app.config["SESSION_COOKIE_SAMESITE"] = 'Lax'
# There are more configs set for non-debug mode; see bottom of file

mongo = auth.start_mongo_client(app)
asgi_app = None

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'bakes.tisbakery@gmail.com'
app.config['MAIL_PASSWORD'] = 'hzyfwwmocqgnhctg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
otp = randint(100000, 999999)


@app.before_request
def add_antiforgery_token():
    if request.method == 'GET' and session.get('CSRFToken') is None:
        session['CSRFToken'] = ''.join(
            SystemRandom().choice(string.ascii_letters + string.digits) \
            for _ in range(32)
        )


@app.before_request
def check_antiforgery_token():
    if request.method == 'POST':
        session_token = session.get('CSRFToken')
        request_token = request.form.get('CSRFToken')
        nope = False
        if session_token is None:
            app.logger.warning(
                "Form Submit Attempt missing CSRF SESSION token for URL %s from %s",
                request.full_path, request.remote_addr
            )
            nope = True
        elif request.form:
            if not request_token:
                app.logger.warning(
                    "Form Submit Attempt missing CSRF REQUEST token for URL %s from %s",
                    request.full_path, request.remote_addr
                )
                nope = True
            elif session_token != request_token:
                app.logger.warning(
                    "Form Submit Attempt CSRF token MISMATCH for URL %s from %s",
                    request.full_path, request.remote_addr
                )
                nope = True

        if nope:
            abort(403, description="Request Kinda Sus. Impostor Request has been reported.")


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


def user_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))

    return wrap


def analyst_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'analyst_logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You ned to login first')
            return redirect(url_for('login'))

    return wrap


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
                                  'address': request.form['address'], 'mobile': request.form['mobile'],
                                  'verified': 0})
                email = request.form['email']
                session['verify_email'] = request.form['email']
                session.permanent = True
                # session['user_logged_in'] = True
                flash('Please verify emai; address!', category='success')
                print('registered', )
                return redirect(url_for('validate', email=email))
        except Exception as e:
            print(e)
            flash('Invalid Inputs', category='error')
            return redirect(url_for('register'))

    return render_template("register.html", CSRFToken=session.get('CSRFToken'))


@app.route('/validate/', methods=['POST', 'GET'])
def validate():
    email = session['verify_email']
    msg = Message(subject='OTP', sender='bakes.tisbakery@gmail.com', recipients=[email])
    msg.body = str(otp)
    otp_check = []
    otp_check.append(otp)
    mail.send(msg)
    users = mongo.db.users
    user = users.find_one({"email": email})
    #d_email = urllib.parse.unquote(email)
    if request.method == 'POST':
        user_otp = request.form['otp']
        if otp_check[0] == int(user_otp):
            if user:
                users.update_one({'email': email}, {'$set': {'verified': 1}})
                flash('Account validated!', category='success')
                return redirect(url_for('home'))


    return render_template("validate.html", CSRFToken=session.get('CSRFToken'))

@app.route('/resend/', methods=['GET', 'POST'])
def resend():
    email = request.args.get('email')
    if request.method == 'POST':
        msg = Message(subject='OTP', sender='bakes.tisbakery@gmail.com', recipients=[email])
        msg.body = str(otp)
        mail.send(msg)
    return redirect(url_for('validate'))


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
                session['analyst_logged_in'] = True
                session.permanent = True
                flash('Login Success', category='success')
                return redirect(url_for("analyst"))
            else:
                flash('Login Failed', category='error')
        else:
            flash('Account does not exist', category='error')

    return render_template("analyst_login.html", CSRFToken=session.get('CSRFToken'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users
    logs = mongo.db.logs

    if session.get('analyst_logged_in'):
        return redirect(url_for("home"))
    if request.method == 'POST':
        login_user = users.find_one({'email': request.form['email']})
        if login_user and login_user['verified'] == 1:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['password']) == login_user[
                'password']:
                time_in = "UTC " + datetime.now().strftime("%X")
                logs.insert_one(
                    {'email': login_user['email'], 'date': datetime.now().strftime("%x"), 'login_time': time_in})
                session['email'] = request.form['email']
                session['user_logged_in'] = True
                session.permanent = True
                flash('Login Success', category='success')
                return redirect(url_for('allproducts'))
            else:
                flash('Login Failed', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", boolean=True, CSRFToken=session.get('CSRFToken'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    session.pop('user_logged_in', None)
    session.pop('analyst_logged_in', None)
    session.permanent = False
    flash('Successfully Logged Out', category='success')
    # print(session['username'])
    return redirect('/')


@app.route('/test/')
def test():
    return render_template("test.html")


@app.route('/analyst/', methods=['GET', 'POST'])
@analyst_login_required
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
    return render_template("data_analyst_page.html", log_big_arr=log_big_arr, order_big_arr=order_big_arr,
                           CSRFToken=session.get('CSRFToken'))


@app.route('/account/')
@user_login_required
def account():
    email = session.get('email')
    users = mongo.db.users
    user = users.find_one({'email': email})
    name = user['name']
    address = user['address']
    mobile = user['mobile']
    return render_template("account_page.html", name=name, address=address, mobile=mobile,
                           CSRFToken=session.get('CSRFToken'))


@app.route('/edit_account/', methods=['GET', 'POST'])
@user_login_required
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
    return render_template("edit_account_page.html", name=name, address=address, mobile=mobile,
                           CSRFToken=session.get('CSRFToken'))


@app.route('/delete_account/', methods=['GET', 'POST'])
@user_login_required
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


@app.route('/cart/')
@user_login_required
def cart():
    # Gets userID of user logged in
    users = mongo.db.users
    user_email = session.get('email')
    userId = users.find_one({'email': user_email},
                            {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
    # Clean retrieved userId
    strUserId = str(userId)
    clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')

    userCart = mongo.db.cart
    cart = userCart.find({'user_id': clean_userId})
    return render_template("cart.html", users=userId, userCart=cart, CSRFToken=session.get('CSRFToken'))


@app.route('/about-us/')
def about():
    return render_template("about.html")


@app.route('/all-products/')
def allproducts():
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    return render_template("all_products.html", allproducts=findproduct)


@app.route('/indiv-product/id=<id>', methods=['GET', 'POST'])
def showgood(id):
    if 'email' not in session:
        product = mongo.db.products
        retrieve_product = product.find_one({'product_id': id})
        return render_template("indiv_product.html", product=retrieve_product, CSRFToken=session.get('CSRFToken'))
    else:
        product = mongo.db.products
        retrieve_product = product.find_one({'product_id': id})
        session['product_id'] = id
        return render_template("indiv_product.html", product=retrieve_product, CSRFToken=session.get('CSRFToken'))


@app.route('/addToCart', methods=['GET', 'POST'])
@user_login_required
def addToCart():
    # connecting to tables
    allproducts = mongo.db.products
    users = mongo.db.users
    userCart = mongo.db.cart

    # Retrieving and cleaning user ID based on email stored in session
    findproduct = allproducts.find()
    user_email = session['email']
    userId = users.find_one({'email': user_email},
                            {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
    strUserId = str(userId)
    clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')

    # Get quantity of product to add
    quantity = request.form.get('quantity')

    # Get ProductID for query
    productId = session['product_id']

    # Cleaning of Product name, price
    productName = allproducts.find_one({'product_id': productId}, {'_id': 0, 'product_name': 1})
    C_productName = str(productName).replace("{'product_name': '", "").replace("'}", '')
    productPrice = allproducts.find_one({'product_id': productId}, {'_id': 0, 'product_price': 1})
    C_productPrice = str(productPrice).replace("{'product_price': ", "").replace("}", '')
    productPrice = int(C_productPrice)

    # Insert into DB
    userCart.insert_one(
        {'user_id': clean_userId, 'product_id': productId, 'product_name': C_productName, 'product_price': productPrice,
         'product_quantity': int(quantity)})
    return render_template("all_products.html", allproducts=findproduct, CSRFToken=session.get('CSRFToken'))


@app.route('/removeFromCart')
@user_login_required
def removeFromCart():
    userCart = mongo.db.cart
    users = mongo.db.users
    user_email = session['email']
    userId = users.find_one({'email': user_email},
                            {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
    strUserId = str(userId)
    clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
    productId = request.args.get('productId')
    userCart.delete_one({'user_id': clean_userId, 'product_id': productId})
    return redirect(url_for('cart'))


@app.route('/checkout/')
@app.route('/create-checkout-session', methods=['POST'])
def checkout():
    user = mongo.db.users
    cart = mongo.db.cart
    order = mongo.db.orders
    product = mongo.db.products

    if 'email' not in session:
        flash("Please login first!", category='error')
        return render_template("login.html")
    else:
        user_email = session['email']
        userId = user.find_one({'email': user_email},
                               {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
        strUserId = str(userId)
        loginuserid = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
        # loginuserid = "6364c1b91b3c2c688f6b73ab"

        # find totalamount for each user in cartdb
        price = cart.aggregate([{"$group": {"_id": "$user_id", "totalAmount": {
            "$sum": {"$multiply": ["$product_price", "$product_quantity"]}}, "count": {"$sum": "1"}}}])

        # find user id from the current session and cart
        retrieve_cart = cart.find({"user_id": loginuserid})

        # Clean retrieved cart
        strOrderDetails = str(list(price))

        # extract user_id and totalamount value only
        clean_orderDetails = strOrderDetails.replace("[{'_id': '", "")
        clean_orderDetails1 = clean_orderDetails.replace("', 'totalAmount': ", " ")
        clean_orderDetails2 = clean_orderDetails1.replace(", 'count': 0}, {'_id': '", " ")
        clean_orderDetails3 = clean_orderDetails2.replace(", 'count': 0}]", " ")

        # split user_id and totalvalue into 2 value for prepratation of insertion into order db
        split_details = clean_orderDetails3.split()
        for userid, total in zip(split_details[0::2], split_details[1::2]):

            # retrieve name from user db and clean
            retrieve_user = user.find_one({'_id': ObjectId(userid)}, {'name': 1, '_id': 0})
            userdetails = str(retrieve_user)
            clean_username = userdetails.replace("{'name': '", "")
            clean_username1 = clean_username.replace("'}", "")

            # find all products id for each user in cartdb
            allproducts_details = cart.find({'user_id': userid}, {'product_id': 1, 'product_quantity': 1, '_id': 0})

            for productdetail in allproducts_details:
                # extract prod_id and quantity value only and clean
                productdetailStr = str(productdetail)
                clean_productdetail = productdetailStr.replace("{'product_id': '", "")
                clean_productdetail1 = clean_productdetail.replace("', 'product_quantity':", "")
                clean_productdetail2 = clean_productdetail1.replace("}", "")

                # split prod_id and quantity into 2 value for prepratation of insertion into order db
                split_productdetails = clean_productdetail2.split()
                for prodid, quantity in zip(split_productdetails[0::2], split_productdetails[1::2]):
                    # insert user_id, name and totalprice into order db
                    order.insert_one({'user_id': userid, 'name': clean_username1, 'total_amount': total,
                                      "order_time": datetime.now(),
                                      'order': {'product_id': prodid, 'product_quantity': quantity}})

                    # find price_id
                    retrieve_priceid = product.find({'product_id': prodid}, {'price_id': 1, '_id': 0})
                    for priceid in retrieve_priceid:
                        priceidStr = str(priceid)
                        clean_priceid = priceidStr.replace("{'price_id': '", "")
                        clean_priceid1 = clean_priceid.replace("'}", "")

                        productslist = {'price': '', 'quantity': '', }
                        productslist["price"] = clean_priceid1
                        productslist["quantity"] = quantity

                    line_items1.append(productslist)
                    flash(line_items1)
                try:
                    # productslist = {'price': 'price_1LzHWUDkn7CDktELXGaYF398', 'quantity': '1', }
                    # productslist1 = {'price': 'price_1M0R2BDkn7CDktELlg1CQOGi', 'quantity': '2'}

                    checkout_session = stripe.checkout.Session.create(
                        line_items=line_items1,
                        mode='payment',
                        success_url=domain_url + "success",
                        cancel_url=domain_url + "cancel",
                    )
                except Exception as e:
                    return str(e)

                # return redirect(checkout_session.url, code=303, CSRFToken=session.get('CSRFToken'))
                return redirect(checkout_session.url, code=303)
        # retrieve total
        retrieve_total = order.find_one({'user_id': loginuserid})

        return render_template("checkout.html", order=retrieve_total, cart=retrieve_cart,
                               CSRFToken=session.get('CSRFToken'))


@app.route("/success")
def success():
    if 'email' not in session:
        flash("Please login first!", category='error')
        return render_template("login.html")
    else:
        user_email = session['email']
        userId = user.find_one({'email': user_email},
                               {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
        strUserId = str(userId)
        loginuserid = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
    return render_template("success.html")


@app.route("/cancel")
def cancelled():
    if 'email' not in session:
        flash("Please login first!", category='error')
        return render_template("login.html")
    else:
        user_email = session['email']
        userId = user.find_one({'email': user_email},
                               {'_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0})
        strUserId = str(userId)
        loginuserid = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
    return render_template("cancel.html")


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, port=3000)
else:
    # deployment mode settings
    from random import SystemRandom, randint
    import string
    from asgiref.wsgi import WsgiToAsgi

    if skey := os.environ.get("SECRET_KEY", None):
        app.secret_key = skey
    if mode := os.environ.get("DEPLOY_MODE", None):
        # cookies expire after 15 minutes inactivity
        app.config["PERMANENT_SESSION_LIFETIME"] = 900
        # require HTTPS to load cookies
        app.config["SESSION_COOKIE_SECURE"] = True

    # as we are using uvicorn+gunicorn for deployment
    # flask (a WSGI framework) must be adapted to ASGI
    asgi_app = WsgiToAsgi(app)
