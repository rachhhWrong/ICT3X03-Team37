from flask import *
from flask import Flask, redirect, request, render_template, jsonify

from website import auth
from website.models import *
import os
import bcrypt
import stripe

stripe.api_key = 'sk_test_51LyrlYDkn7CDktELAXteTo9GDPzeeDDG8vNEnDaU7MttLaEYrPyXLjHtXcBtlAiXDX8RUUWqcONKPsDRJv0miTYS00bf8yHq4N'
domain_url = "http://127.0.0.1:5000/"

app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
mongo = auth.start_mongo_client(app)


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
                session['email'] = request.form['email']
                session['name'] = request.form['name']
                session['address'] = request.form['address']
                session['mobile'] = request.form['mobile']
                flash('Registered!', category='success')
                print('registered', )
                return redirect(url_for('home'))
        except Exception as e:
            print(e)
            flash('Invalid Email or Email Exist', category='error')
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route('/analyst_login')
def analyst_login():
    return render_template("analyst_login.html")

# to remove
@app.route('/sss')
def login_page():
    if 'email' in session:
        # print("Logged in as: " + session['username'])
        return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    users = mongo.db.users

    if request.method == 'POST':
        login_user = users.find_one({'email': request.form['email']})

        # print("lol",bcrypt.hashpw(request.form['password'].encode('utf-8'),login_user['password']) == login_user['password'])
        # pseudocode dont erase
        # analyst = mongo.db.analyst
        # analyst_user = analyst.find_one({'name': request.form['username']})
        if login_user:
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),login_user['password']) == login_user['password']:
                session['email'] = login_user['email']
                flash('Login Success', category='success')
                return redirect(url_for('allproducts'))
            else:
                flash('Login Failed', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", boolean=True)

# pseudocode dont erase
# if analyst_user:
#     if bcrypt.hashpw(request.form['password'].encode('utf-8'),login_user['password']) == login_user['password']:
#         session['username'] = request.form['username']
#         return redirect(url_for('analyst'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('email', None)
    flash('Successfully Logged Out', category='success')
    # print(session['username'])
    return redirect('/')

@app.route('/navbar')
def nav_logout():
    if 'email' in session:
        email = session['email']
        return 'Logged in as ' + email + '<br>' + "<b><a href = '/logout'>click here to logout</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + "click here to login</b></a>"

@app.route('/analyst/')
def analyst():
    return render_template("data_analyst_page.html")

@app.route('/account/')
def account():
    return render_template("account_page.html")


@app.route('/account/edit_account/')
def edit_account():
    return render_template("edit_account_page.html")


@app.route('/cart/')
def cart():
    if 'email' not in session:
        flash("Please login first!", category='error')
        return render_template("login.html")
    #allproducts = mongo.db.products
    #findproduct = allproducts.find()
    #allCart = mongo.db.cart
    #findCart = allCart.find()
    return render_template("cart.html")

 
    

@app.route('/addToCart', methods=['GET', 'POST'])
def addToCart():
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    if 'email' not in session:
        flash("Please login first!")
        return render_template("login.html", category='error')
    else:
        quantity = request.form.get('quantity')
        flash(quantity)
        return render_template("all_products.html", allproducts=findproduct)

@app.route('/about-us/')
def about():
    return render_template("about.html")

@app.route('/all-products/')
def allproducts():
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    return render_template("all_products.html", allproducts=findproduct)

@app.route('/indiv-product/id=<int:id>')
def showgood(id):
    product = mongo.db.products
    retrieve_product = product.find_one({'product_id':id})
    return render_template("indiv_product.html", product=retrieve_product)

@app.route('/indiv-product/id=<int:id>', methods=['POST'])
def addToCart1(id):
    if request.method == 'POST':
        product = mongo.db.products
        retrieve_product = product.find_one({'product_id':id})
        user = mongo.db.users
        retrieve_userid = user.find_one({'_id':'uid'})
        if 'email' in session:
            email = session['email']
    
    return render_template("indiv_product.html", product=retrieve_product)

@app.route('/checkout/')
def checkout():
    return render_template("checkout.html")

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                "price": "price_1LzFdTDkn7CDktELuFm41FkU",
                "quantity": 1,
            }],
            mode='payment',
            success_url=domain_url + "success",
            cancel_url=domain_url + "cancel",
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancel")
def cancelled():
    return render_template("cancel.html")

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
