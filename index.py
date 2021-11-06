import re
from flask import render_template, request, redirect, session, jsonify
from sqlalchemy import util
from __init__ import app, my_login, CART_KEY
from admin import*
from models import Users
from flask_login import login_user, logout_user
import utils
import hashlib
import math
import cloudinary
import cloudinary.uploader

#current user
@my_login.user_loader
def user_load(user_id):
    return Users.query.get(user_id)

@app.route("/login", methods=["POST"])
def login_execute():
    username = request.form.get('username')
    password = request.form.get('password')
    #password = str(hashlib.md5(pwd.encode("utf-8")).digest())

    user = Users.query.filter(Users.username==username, Users.password==password).first()

    if user:
        login_user(user)
    return redirect("/admin")

@app.context_processor
def common_context():
    # cart_stats = utils.cart_stats(session.get("cart"))
    # "cart_stats": cart_stats
    brands = utils.get_all_brands() 
    lastest_products = utils.get_lastest_products(6)
    bestseller_products = utils.get_bestseller_products(6)

    return {
        "brand": brands,
        "new_products":lastest_products,
        "bestseller_products": bestseller_products,
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
#sdf
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

@app.route("/") 
def home():
    mostpupular_products = utils.get_mostpopular_product(6)

    return render_template('home.html', 
                            mostpupular_products = mostpupular_products)  

if __name__ == '__main__':
    app.run(debug=True)