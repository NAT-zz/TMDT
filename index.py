import json
import requests
from flask import render_template, request, redirect, session, jsonify
from __init__ import app, my_login, CART_KEY, s, client, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
from admin import*
from models import Users
from flask_login import login_user, logout_user
import utils
import math
from itsdangerous import SignatureExpired
from momo import MoMo
from paypal import CaptureOrder, CreateOrder

#current user
@my_login.user_loader
def user_load(user_id):
    return Users.query.get(user_id)

@app.route("/loginadmin", methods=["POST"])
def login_execute():
    err_msg = ""
    username = request.form.get('username')
    password = request.form.get('password')

    user = Users.query.filter(Users.username==username, Users.password==password).first()

    if user:
        if user.role == MyRole.ADMIN:
            login_user(user)
    return redirect("/admin")

@app.route("/user-login", methods = ["POST", "GET"])
def normaluser_login():
    if not current_user.is_authenticated:
        err_msg = ""
        if request.method == "POST":
            username = request.form.get("username")
            pwd = request.form.get("password")

            user = Users.query.filter(Users.username == username, Users.password == pwd).first()
            if user:
                if user.active == 1:
                    login_user(user)
                    return redirect(request.args.get("next", "/"))
                else:
                    if utils.email_verification(user.email):
                        err_msg = "Email has been sent!, You need to verify your email first!"
                    else:
                        err_msg = "The system has some errors!. PLease try later"
            else:
                err_msg = "Incorrect Username or Password"

        return render_template("page-login.html", err_msg=err_msg)
    return redirect("/")
    
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/user-login/google")
def loginWithGoogle():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/user-login/google/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        # unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = Users.query.filter(Users.email == users_email).first()

    if not user:
        password = utils.create_password(users_email)

        user = Users(name = users_name,
                    active = 1, 
                    username = users_email, 
                    password = password,
                    phone = "0123456789",
                    email = users_email)
        db.session.add(user)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect("/")


@app.route("/user-register", methods=["POST", "GET"])
def register():
    err_msg = ""
    if request.method == 'POST':
        try:
            password = request.form.get("password")    
            confirm_password = request.form.get("confirm-password")
            if password.strip() == confirm_password.strip():
                data = request.form.copy()
                del data['confirm-password']

                if utils.add_user(**data):
                    return redirect("/user-login")
                else:
                    err_msg = "Check your information again/Username might already exit"
            else:
                err_msg = "Password not match"
        except:
            err_msg = "System error"

    return render_template("page-reg-page.html", err_msg = err_msg)

@app.route("/user-register/complete")
def complete_registration():
    try:
        token = request.args.get("token")
        email = s.loads(token, salt="email-verification", max_age=60)  # max_age: milliseconds
        user = Users.query.filter(Users.email == email).first()
        user.active = True
        db.session.add(user)
        db.session.commit()
        return "<h1>Your Email has been verified</h1>"
    except SignatureExpired:
        return "<h1>The token is expired</h1>"

@app.route("/user-logout")
def normaluser_logout():
    logout_user()
    return redirect("/user-login")

@app.route("/user-forget-password")
def normaluer_forget_password():
    if not current_user.is_authenticated:
        return render_template("page-forgotton-password.html")
    return redirect("/")

@app.route("/user-edit-account", methods=["POST", "GET"])
def normaluser_edit_account():
    if current_user.is_authenticated:
        err_msg = ""
        if request.method == 'POST':
            try:
                username = current_user.username
                fullname = request.form.get("fullname")
                email = request.form.get("email")
                phone = request.form.get("phone")
                data = request.form.copy()
                    
                if utils.edit_infor(username=username, fullname=fullname, email = email, phone = phone):
                    err_msg = "Updated Successfully"
                else:
                    err_msg = "Check your information again"
            except:
                err_msg = "System error"
        return render_template("shop-standart-forms.html",err_msg = err_msg)
    return redirect("/")

@app.route("/user-change-password", methods=["POST", "GET"])
def normaluser_change_password():
    err_msg = ""
    if request.method == 'POST':
        try:
            oldpassword = request.form.get("old-password")
            newpassword = request.form.get("new-password")    
            confirm_password = request.form.get("confirm-password")
            username = current_user.username

            if newpassword.strip() == confirm_password.strip():
                if utils.change_password(username=username, 
                                        oldpassword=oldpassword,
                                        newpassword=newpassword):
                    logout_user()
                    return redirect("/user-login")
                else:
                    err_msg = "Check your information again"
            else:
                err_msg = "Password mismatch"
        except:
            err_msg = "System error"
    return render_template("change-password.html", err_msg=err_msg)
    
@app.context_processor
def common_context():
    cart_stats = utils.cart_stats(session.get("cart"))
    brands = utils.get_all_brands() 
    lastest_products = utils.get_lastest_products(6)
    bestseller_products = utils.get_bestseller_products(6)

    return {
        "brand": brands,
        "new_products":lastest_products,
        "bestseller_products": bestseller_products,
        "cart_stats": cart_stats
    }
@app.context_processor
def quick_func():
    def count_productbybid(bid):
        return utils.count_productbybid(bid)
    return dict(count_productbybid = count_productbybid)

@app.route("/item-detail")
def detail():
    product_id = request.args.get("product-id")
    product = utils.get_productbyid(pid=product_id)

    similar_products = utils.get_product(brand_id=product.brand_id)

    return render_template('item-detail.html',
                            this_product = product,
                            similar_products = similar_products)
                            
@app.route("/product-list")
def product_list():
    brand_id = request.args.get("brand-id")
    kw = request.args.get("kw")
    sort = request.args.get("sort")

    if brand_id:
        count = utils.count_productbybid(bid=brand_id)
    else:
        count = utils.count_product()
    size = app.config["PAGE_SIZE"]
    page = int(request.args.get("page", 1))

    all_product = utils.get_product(brand_id = brand_id, kw = kw, page = page, sort=sort)
    return render_template('shop-product-list.html',
                            all_products = all_product,
                            bid = brand_id,
                            pagenum = math.ceil(count/size),
                            page = page,
                            kw = kw,
                            total_product_count = count)

@app.route("/contact")
def contact():
    return render_template("page-contacts.html")

@app.route("/careers")
def careers():
    return render_template("page-careers.html")

@app.route("/cart")
def cart():
    if current_user.is_authenticated:
        return render_template("shop-shopping-cart.html")
    return redirect("/")

@app.route("/api/add-item-cart", methods = ["POST"]) 
def add_to_cart():
    cart = session.get(CART_KEY) #<- key là "cart"
    # Nếu chưa bỏ j vào giở
    if not cart:
        cart = {}
    
    data = request.json
    product_id = str(data["product_id"])

    if product_id in cart: #sản phẩm đã từng bỏ vào giỏ
        p = cart[product_id]
        p['quantity'] = p['quantity'] + 1
    else:
        cart[product_id] = { 
            "product_id" : data["product_id"],
            "product_name" : data["product_name"],
            "product_price" : data["product_price"],
            "product_image" : data["product_image"],
            "product_chip" : data["product_chip"],
            "product_ram" : data["product_ram"],
            "quantity" : 1
        }

    # debug đặt breakpoint
    # import pdb 
    # pdb.set_trace()

    session[CART_KEY] = cart
    return jsonify(utils.cart_stats(cart))

@app.route("/api/update-cart-item", methods=["put"])
def update_cart_item():
    cart = session.get(CART_KEY)
    if cart:
        data = request.json
        try:
            product_id = str(data["product_id"])
            quantity = data['quantity']
        except IndexError or KeyError as ex:
            print(ex)
        else:
            if product_id in cart:
                p = cart[product_id]
                p['quantity'] = quantity
                session[CART_KEY] = cart
            return jsonify({
                "error_code": 200,
                "cart_stats": utils.cart_stats(cart)
            })

    return jsonify({
        "error_code": 404
    })

@app.route("/api/delete-cart-item/<product_id>", methods=["delete"])
def delete_cart_item(product_id):
    cart = session.get(CART_KEY)
    if cart:
        if product_id in cart:
            del cart[product_id]
            session[CART_KEY] = cart
            return jsonify({
                "error_code": 200,
                "cart_stats": utils.cart_stats(cart)
            })
    
    return jsonify({
        "error_code": 404
    })

@app.route("/api/pay/<cityname>", methods = ["POST", "GET"])
def pay(cityname):
    cart = session.get(CART_KEY)

    if cart:
        if utils.add_receipt(cart, cityname = cityname):
            del session[CART_KEY]
            return jsonify({
                "error_code": 200
            })
    return jsonify({
        "error_code": 404
    })

@app.route("/api/cancel-order", methods=["POST"])
def cancel_order():
    try:
        order_id = request.json["order_id"]
        order = Receipt.query.filter(Receipt.id == order_id).first()
        order.status = 2 # cancel
        db.session.add(order)
        db.session.commit()
        return jsonify({
            "error_code": 200
        })
    except Exception as ex:
        print(ex)
        return jsonify({
            "error_code": 404
        }) 
    
@app.route("/api/reorder", methods=["POST"])
def reorder():
    try:
        cart = session.get(CART_KEY)
        if not cart:
            cart = {}

        order_id = request.json["order_id"]
        order = Receipt.query.filter(Receipt.id == order_id).first()

        for item in order.detail:
            product_id = str(item.product.id)

            if product_id in cart: #sản phẩm đã từng bỏ vào giỏ
                p = cart[product_id]
                p['quantity'] = p['quantity'] + item.quantity
            else:
                cart[product_id] = { 
                    "product_id" : product_id,
                    "product_name" : item.product.name,
                    "product_price" : item.product.price,
                    "product_image" : item.product.image,
                    "product_chip" : item.product.chip,
                    "product_ram" : item.product.ram,
                    "quantity" : item.quantity
                }

        session[CART_KEY] = cart

        return jsonify({
            **(utils.cart_stats(cart)), # spread operator
            "error_code": 200
        })
    except Exception as ex:
        print(ex)
        return jsonify({
            "error_code": 404
        }) 

@app.route("/orders")
def history_orders():
    if current_user.is_authenticated:
        receipt = utils.get_receiptsbyuid(current_user.id)
        detail = utils.get_receiptdetail()
        product = utils.get_product()
        
        ship = utils.get_allshipping()
        order = utils.get_ordersbyuid(current_user.id)

        total_price = utils.get_totalprice(current_user.id)
        return render_template("shop-wishlist.html", 
                                receipt = receipt,
                                detail = detail,
                                product = product,
                                total_price = total_price,
                                ship = ship,
                                order = order)
    return redirect("/")
@app.route("/user-checkout")
def checkout():
    if current_user.is_authenticated:
        shipping = utils.get_allshipping()
        return render_template("shop-checkout.html", allship = shipping)
    return redirect("/")

@app.route("/pay-with-momo")
def pay_with_momo():
    data = MoMo().payment_order()
    return redirect(data['payUrl'])

@app.route("/momo/payment-result")
def payment_result():
    return redirect("/user-checkout")

@app.route('/api/create-paypal-transaction', methods=['post'])
def create_paypal_transaction():
    resp = CreateOrder().create_order(debug=True)
    return jsonify({"id": resp.result.id})

@app.route('/api/capture-paypal-transaction', methods=['post'])
def capture_paypal_transaction():
    order_id = request.json['orderID']
    resp = CaptureOrder().capture_order(order_id)
    status_code = resp.status_code
    return jsonify({
        "error_code": status_code
    })
   

@app.route("/") 
def home():
    mostpupular_products = utils.get_mostpopular_product(6)

    return render_template('home.html', 
                            mostpupular_products = mostpupular_products)  

if __name__ == '__main__':
    app.run(debug=True)