from flask import *
from flask import Flask, redirect, request, render_template, jsonify
from datetime import datetime
from website import auth
from website.models import *
import os
import bcrypt
import stripe
import pymongo
from bson import ObjectId

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
    #Gets userID of user logged in
    users = mongo.db.users
    user_email = session['email']
    userId = users.find_one( { 'email': user_email }, { '_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0 })
    #Clean retrieved userId
    strUserId = str(userId)
    clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')

    userCart = mongo.db.cart
    cart = userCart.find( { 'user_id': clean_userId})
    return render_template("cart.html", users=userId, userCart=cart)


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
    if 'email' not in session:
        product = mongo.db.products
        retrieve_product = product.find_one({'product_id':id})
        return render_template("indiv_product.html", product=retrieve_product)
    else:
        product = mongo.db.products
        retrieve_product = product.find_one({'product_id':id})
        session['product_id'] = id
        return render_template("indiv_product.html", product=retrieve_product)
        

@app.route('/addToCart', methods=['GET', 'POST'])
def addToCart():
    allproducts = mongo.db.products
    findproduct = allproducts.find()
    if 'email' not in session:
        flash("Please login first!", category='error')
        return render_template("login.html")
    else:
        #connecting to tables
        users = mongo.db.users
        userCart = mongo.db.cart
        #Retrieving and cleaning user ID based on email stored in session
        user_email = session['email']
        userId = users.find_one( { 'email': user_email }, { '_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0 })
        strUserId = str(userId)
        clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
        #Get quantity of product to add
        quantity = request.form.get('quantity')
        #Get ProductID for query
        productId = session['product_id']
        #Cleaning of Product name, price
        productName = allproducts.find_one({'product_id':productId}, { '_id': 0, 'product_name': 1})
        C_productName = str(productName).replace("{'product_name': '", "").replace("'}", '')
        productPrice = allproducts.find_one({'product_id':productId}, { '_id': 0, 'product_price': 1})
        C_productPrice = str(productPrice).replace("{'product_price': ", "").replace("}", '')
        #Insert into DB
        userCart.insert_one({'user_id':clean_userId, 'product_id': productId, 'product_name': C_productName, 'product_price': int(C_productPrice), 'product_quantity': int(quantity)})
        return render_template("all_products.html", allproducts=findproduct)

@app.route('/removeFromCart')
def removeFromCart():
    userCart = mongo.db.cart
    users = mongo.db.users
    user_email = session['email']
    userId = users.find_one( { 'email': user_email }, { '_id': 1, 'name': 0, 'email': 0, 'password': 0, 'address': 0, 'mobile': 0 })
    strUserId = str(userId)
    clean_userId = strUserId.replace("{'_id': ObjectId('", "").replace("')}", '')
    productId = request.args.get('productId')
    userCart.delete_one({'user_id': clean_userId, 'product_id': productId})
    return redirect(url_for('cart'))


@app.route('/checkout/')
def displayCart():

    user = mongo.db.users
    cart = mongo.db.cart
    order = mongo.db.orders
    product = mongo.db.products

    loginuserid = "6364c1b91b3c2c688f6b73ab"
    price_id = ""

    #find totalamount for each user in cartdb
    price = cart.aggregate([{"$group":{"_id":"$user_id","totalAmount": {"$sum":{"$multiply":["$product_price", "$product_quantity"]}}, "count":{"$sum":"1"}}}])

    #find user id from the current session and cart
    retrieve_cart = cart.find({"user_id":loginuserid})

    #Clean retrieved cart
    strOrderDetails = str(list(price))

    #extract user_id and totalamount value only 
    clean_orderDetails = strOrderDetails.replace("[{'_id': '", "")
    clean_orderDetails1 = clean_orderDetails.replace("', 'totalAmount': ", " ")
    clean_orderDetails2 = clean_orderDetails1.replace(", 'count': 0}, {'_id': '", " ")
    clean_orderDetails3 = clean_orderDetails2.replace(", 'count': 0}]", " ")

    #split user_id and totalvalue into 2 value for prepratation of insertion into order db
    split_details = clean_orderDetails3.split( )
    for userid,total in zip(split_details[0::2], split_details[1::2]):

        #retrieve name from user db and clean
        retrieve_user = user.find_one({ '_id':ObjectId(userid) }, { 'name': 1, '_id': 0})
        userdetails= str(retrieve_user)
        clean_username = userdetails.replace("{'name': '", "")
        clean_username1 = clean_username.replace("'}", "")

        #find all products id for each user in cartdb
        allproducts_details = cart.find({'user_id':userid}, {'product_id':1,'product_quantity':1, '_id':0})
        
        for productdetail in allproducts_details:
            #extract prod_id and quantity value only and clean
            productdetailStr = str(productdetail)
            clean_productdetail = productdetailStr.replace("{'product_id': '", "")
            clean_productdetail1 = clean_productdetail.replace("', 'product_quantity':", "")
            clean_productdetail2 = clean_productdetail1.replace("}", "")
            
            #split prod_id and quantity into 2 value for prepratation of insertion into order db
            split_productdetails = clean_productdetail2.split( )
            for prodid,quantity in zip(split_productdetails[0::2], split_productdetails[1::2]):
                #insert user_id, name and totalprice into order db
                order.insert_one({'user_id':userid,'name': clean_username1,'total_amount': total, "order_time": datetime.now(), 'order': {'product_id': prodid, 'product_quantity': quantity}})
                
                #find price_id
                retrieve_priceid = product.find({'product_id':prodid},{'price_id':1, '_id':0})
                for priceid in retrieve_priceid:
                    priceidStr = str(priceid)
                    clean_priceid = priceidStr.replace("{'price_id': '", "")
                    clean_priceid1 = clean_priceid.replace("'}", "")

                    productslist={'price': '', 'quantity': '', }
                    productslist["price"]=clean_priceid1
                    productslist["quantity"]=quantity
                    
                    #flash(productslist)
                    
    #retrieve total        
    retrieve_total = order.find_one({'user_id':loginuserid})

    return render_template("checkout.html", order=retrieve_total, cart=retrieve_cart)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    
    try:
        
        productslist={'price': 'price_1LzHWUDkn7CDktELXGaYF398', 'quantity': '1',}
        productslist1={'price': 'price_1M0R2BDkn7CDktELlg1CQOGi', 'quantity': '2'}

        checkout_session = stripe.checkout.Session.create(
            line_items=[productslist, productslist1],
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