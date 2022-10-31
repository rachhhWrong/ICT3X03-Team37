from flask import *
from website.models import *
import bcrypt
import firebase_admin
#from firebase_admin import auth, credentials
import pyrebase

app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
#cred = credentials.Certificate('tisbakery-service.json')

fbConfig = {'apiKey': "AIzaSyBPVALZE3ag3wNSK4REMwE0oPWmbIAiT9g",
  'authDomain': "tisbakery.firebaseapp.com",
  'projectId': "tisbakery",
  'storageBucket': "tisbakery.appspot.com",
  'messagingSenderId': "275241827055",
  'appId': "1:275241827055:web:2ef12ef5c2ac2aa563b91a",
  'measurementId': "G-E5XZ79LR6N",
                  'databaseURL':'https://tisbakery-default-rtdb.asia-southeast1.firebasedatabase.app/'}

fb = pyrebase.initialize_app(fbConfig)
auth = fb.auth()
db = fb.database()


@app.route('/favicon.ico')
def favicon():
    app.send_static_file('favicon.ico')


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])

            flash('Registered!')
            print('registered', )
            return redirect(url_for('login_page'))
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


@app.route('/submit', methods=['POST', 'GET'])
def login():
    if ('user' in session):
        print("INSESSION", session['user'])
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            session['email'] = email
            session['logged_in'] = True
            print('logged in')
            get_id = auth.get_account_info(user['idToken'])
            print('INFO', get_id)
            return redirect(url_for('allproducts'))
        except:
            flash('Wrong email or password!')
            print("Wrong email or password!")
            return redirect(url_for('login_page'))





@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('user')
    print('OUTSESSION')
    return redirect('/')


@app.route('/navbar')
def nav_logout():
    if 'username' in session:
        username = session['email']
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


@app.route('/account/edit_account', methods=["GET","POST"])
def edit_account():
    user = session['user']
    email = session['email']
    if request.method == "POST":
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        mobile = request.form['mobile']
        address1 = request.form['address1']
        address2 = request.form['address2']
        postal = request.form['postal']

        data = {'firstname':firstname,'lasname':lastname,'mobile':mobile,'address1':address1,'address2':address2,'postal':postal}
        current_user = auth.current_user
        print(user)
        db.child("users").child(user).set(data)

        return redirect(url_for('account'))

    return render_template("edit_account_page.html", email = email)


@app.route('/checkout/')
def checkout():
    return render_template("checkout.html")


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


@app.route('/cart/')
def cart():
    return render_template("cart.html")


if __name__ == '__main__':
    app.secret_key = 'secret'
    app.run(debug=True, port=3000)
