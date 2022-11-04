from flask import *

from website import auth
from website.models import *
import os
import bcrypt

app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# never send cookies to third-party sites
app.config["SESSION_COOKIE_SAMESITE"] = 'Strict'
# There are more configs set for non-debug mode; see bottom of file

mongo = auth.start_mongo_client(app)

@app.after_request
def add_security_headers(response):
    if __name__ == '__main__':
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


@app.route('/test/')
def test():
    return render_template("test.html")


@app.route('/analyst/')
def analyst():
    return render_template("data_analyst_page.html")


@app.route('/account/')
def account():
    return render_template("account_page.html")


@app.route('/account/edit_account/')
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
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    return render_template("all_products.html", allproducts=findproduct)


@app.route('/indiv-product/id=<int:id>', methods=['GET', 'POST'])
def showgood(id):
    product = mongo.db.products
    retrieve_product = product.find_one({'product_id':id})
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

    app.secret_key = ''.join(
        SystemRandom().choice(string.ascii_letters + string.digits) \
        for _ in range(32)
    )
    
    # cookies expire after 15 minutes inactivity
    app.config["PERMANENT_SESSION_LIFETIME"] = 900
    # require HTTPS to load cookies
    app.config["SESSION_COOKIE_SECURE"] = True
