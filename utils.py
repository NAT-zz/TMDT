import random
import string
from sqlalchemy.sql.functions import func
from models import*
from __init__ import app, db,  mail, s
from flask_login import current_user
from flask import url_for, abort
from flask_mail import Message

def get_all_brands():
    return Brand.query.all()

def get_productbyid(pid):
    return Product.query.get(pid)

def get_lastest_products(number = None):
    products = Product.query.order_by(Product.id.desc()).limit(number)
    return products

def get_bestseller_products(number = None):
    products = Product.query.order_by(Product.price.asc()).limit(number)
    products = products[::-1]
    return products

def get_mostpopular_product(number = None):
    products = Product.query.order_by(Product.amount.desc()).limit(number)
    return products
   
def count_productbybid(bid):
    return Product.query.filter(Product.brand_id==bid).count()
    
def count_product():
    return Product.query.count()

def get_product(kw=None, brand_id=None, page = None, sort = None):
    products = Product.query

    if kw:
        products = products.filter(Product.name.contains(kw))
    
    if brand_id:
        products = products.filter(Product.brand_id==brand_id)
    
    if sort:
        if sort == "lowtohigh":
            products = products.order_by(Product.price.asc())
        else:
            products = products.order_by(Product.price.desc())

    if page:
        size = app.config["PAGE_SIZE"]
        start = (page-1)*size
        end = start + size
        return products.all()[start:end]
    return products.all()

def add_user(fullname, username, phone, email, password): 
    get_user = Users.query.filter(Users.username == username).all()
    if not get_user:
        user = Users(name = fullname,
                    active = 0, 
                    username = username, 
                    password = password,
                    phone = phone,
                    email = email)
        db.session.add(user)
        try:
            if email_verification(email):
                db.session.commit()
                return True
            return False      
        except:
            return False
    else:
        return False

def email_verification(email):
    try:
        token = s.dumps(email, salt='email-verification')
        link = url_for('complete_registration', token=token, _external=True)
        msg = Message('E-mail Verification',
                      recipients=[email],
                      html=f"<div>please click on the link below to complete the verification:"
                           f"<br/>{link}</div>")
        mail.send(msg)
        return True

    except Exception as ex:
        print(ex)
        return False

def create_password(email, password=None):
    if password is None:
        # then create an account for this user
        password = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        print(password)
        # send password to user via Gmail
        try:
            msg = Message('Password for Login',
                          recipients=[email],
                          html=f"<div>This is your password: <b>{password}</b></div>")
            with app.open_resource("%s/static/images/product-showcase.jpg" % app.root_path) as logo:
                msg.attach('laptopUTE.jpg', 'image/jpeg', logo.read())

            mail.send(msg)
        except Exception as ex:
            print(ex)
            abort(500)
        
        return password


def change_password(username, oldpassword, newpassword):
    get_user = Users.query.filter(Users.username == username, Users.password==oldpassword).first()
    if get_user:
        get_user.password = newpassword
        try:
            db.session.commit()
            return True      
        except:
            return False
    else:
        return False

def edit_infor(username, fullname, email, phone):
    get_user = Users.query.filter(Users.username == username).first()
    if get_user:
        get_user.name = fullname
        get_user.email = email
        get_user.phone = phone
        try:
            db.session.commit()
            return True
        except:
            return False
    else:
        return False


def cart_stats(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for p in cart.values():
            total_quantity += p['quantity']
            total_amount += p['quantity']*p['product_price']

    return {
        "total_quantity": total_quantity,
        "total_amount" : total_amount
    }

def add_receipt(cart, cityname):
    if cart:
        try:
            receipt = Receipt(user = current_user) 
            db.session.add(receipt)
            
            sub_total = 0
            for item in cart.values():
                detail = ReceiptDetail(receipt = receipt, product_id = item['product_id']
                , quantity = item['quantity'], unit_price = item['product_price']) 
                sub_total+=item['product_price']*item['quantity']
                db.session.add(detail)

                pro = Product.query.get(int(item['product_id']))
                pro.amount -= int(item['quantity'])
            
            if cityname: 
                ship = Shipping.query.filter(Shipping.cityname == cityname).first()
                total = sub_total + ship.price
                order = Order(cityname = cityname, user = current_user, receipt = receipt, price = total)
                db.session.add(order)
        except Exception as ex:
            print("ERROR: " + str(ex))
        db.session.commit() 
        return True 
    
    return False

def get_ordersbyuid(uid):
    user_order = Order.query.filter(Order.user_id==uid).all()
    return user_order

def get_receiptsbyuid(uid):
    user_receipt = Receipt.query.filter(Receipt.user_id==uid).all()
    return user_receipt

def get_receiptdetail():
    detail = ReceiptDetail.query.all()
    return detail

def get_totalprice(uid):
    receipt = get_receiptsbyuid(uid)
    detail = get_receiptdetail()

    thisdict = {}
    for r in receipt:
        price = 0 
        for d in detail:
            if r.id == d.receitp_id:
                price += d.quantity*d.unit_price
        thisdict[r.id] = price
    return thisdict

def get_allshipping():
    return Shipping.query.all()

def product_stats_by_cate():
    return    db.session.query(Brand.id, Brand.name, func.count(Product.id))\
                .join(Product, Product.brand_id==Brand.id, isouter = True)\
                .group_by(Brand.id, Brand.name).all()

def product_stats(from_date = None, to_date = None):
    stats =  db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.unit_price*ReceiptDetail.quantity))

    if from_date:
        stats = stats.filter(Receipt.created_date.__ge__(from_date))
    if to_date:
        stats = stats.filter(Receipt.created_date.__le__(to_date))

    return  stats.join(ReceiptDetail, ReceiptDetail.product_id==Product.id, isouter = True)\
            .join(Receipt, ReceiptDetail.receitp_id==Receipt.id, isouter = True)\
            .group_by(Product.id, Product.name).all()

#Th??m d??? li???u
# c = Category('Mobile') 
# db.session.add(c)
# db.session.commit()


# L???y t??? CSDL theo kh??a ch??nh (id)
# c = Category.query.get(1) 
# = select* from Category where id = 1
# Th??m v??o b v???i kh??a ngo???i
# p = Product(name = 'iphone', price=30, category = c) 
# db.session.add(p)
# db.session.commit()

# p = Product.query.get(2)
# p.__dict__ : xem h???t th??ng tin
# p.category : xem th??ng tin p thu???c category n??o
# p.category.__dict__ : xem th??ng tin category ????
# => t??c d???ng c???a backref

#C???p nh???t 
# c.name = 'tuan'
# db.session.add(c)
# db.session.commit()
#X??a
# db.session.delete(c)
# db.session.commit()

#Loc
#c = Category.query.filter(Category.name.contains("t"))
#Product.query.filter(Product.name.contains('iphone')).all()
#Product.query.filter(Product.name.startswith('g')).all()
#Product.query.filter(Product.name.endswith('y')).all()

#L???y s???n ph???m c?? gi?? l???n h??n 15
#Product.query.filter(Product.price.__gt__(15)).all() 
#L???y s???n ph???m c?? gi?? nh??? h??n 35
#Product.query.filter(Product.price.__lt__(35)).all() 

#L???y all s???n ph???m sort t??ng d???n theo id
#Product.query.order_by(Product.id).all()
#L???y all s???n ph???m sort gi???m d???n theo 
#Product.query.order_by(-Product.id).all()  

#L???y all s???n ph???m v???i c??c ??i???u ki???n n???i = and
#Product.query.filter(Product.price.__lt__(35), Product.name.contains('iphone')).order_by(Product.id).all()
#L???y al s???n ph???m v???i c??c ??i???u ki???n n???i = or
#Product.query.filter(or_(Product.price.__lt__(35), Product.name.contains('iphone'))).order_by(Product.id).all()
#join 2 b???ng
#Product.query.join(Category, Product.category_id==Category.id).filter(Category.name.contains('t')).add_column(Category.name).all()
#T??m gi?? tr??? l???n nh???t
#db.session.query(func.max(Product.price)).first()