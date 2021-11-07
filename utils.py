from math import prod
from models import*
from __init__ import app, db
from flask_login import current_user
import hashlib

def get_all_brands():
    return Brand.query.all()

def get_productbyid(pid):
    return Product.query.get(pid)

def get_lastest_products(number = None):
    products = Product.query.order_by(Product.id.desc()).limit(number)
    products = products[::-1]
    return products

def get_bestseller_products(number = None):
    products = Product.query.order_by(Product.price.asc()).limit(number)
    products = products[::-1]
    return products

def get_mostpopular_product(number = None):
    products = Product.query.order_by(Product.amount.desc()).limit(number)
    products = products[::-1]
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
                    username = username, 
                    password = password,
                    phone = phone,
                    email = email)
        db.session.add(user)
        try:
            db.session.commit()
            return True      
        except:
            return False
    else:
        return False
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


# # Thống kê cart
# def cart_stats(cart):
#     total_quantity, total_amount = 0, 0

#     if cart:
#         for p in cart.values():
#             total_quantity += p['quantity']
#             total_amount += p['quantity']*p['product_price']

#     return {
#         "total_quantity": total_quantity,
#         "total_amount" : total_amount
#     }

# def add_receipt(cart):
#     if cart:
#         try:
#             receipt = Receipt(user = current_user)  
#             db.session.add(receipt)
            
#             for item in cart.values():
#                 detail = ReceiptDetail(receipt = receipt, product_id = item['product_id']
#                 , quantity = item['quantity'], unit_price = item['product_price']) 
#                 db.session.add(detail)
#         except Exception as ex:
#             print("ERROR: " + str(ex))
#         db.session.commit() 
#         return True 
    
#     return False



#Thêm dữ liệu
# c = Category('Mobile') 
# db.session.add(c)
# db.session.commit()


# Lấy từ CSDL theo khóa chính (id)
# c = Category.query.get(1) 
# = select* from Category where id = 1
# Thêm vào b với khóa ngoại
# p = Product(name = 'iphone', price=30, category = c) 
# db.session.add(p)
# db.session.commit()

# p = Product.query.get(2)
# p.__dict__ : xem hết thông tin
# p.category : xem thông tin p thuộc category nào
# p.category.__dict__ : xem thông tin category đó
# => tác dụng của backref

#Cập nhật 
# c.name = 'tuan'
# db.session.add(c)
# db.session.commit()
#Xóa
# db.session.delete(c)
# db.session.commit()

#Loc
#c = Category.query.filter(Category.name.contains("t"))
#Product.query.filter(Product.name.contains('iphone')).all()
#Product.query.filter(Product.name.startswith('g')).all()
#Product.query.filter(Product.name.endswith('y')).all()

#Lấy sản phẩm có giá lớn hơn 15
#Product.query.filter(Product.price.__gt__(15)).all() 
#Lấy sản phẩm có giá nhở hơn 35
#Product.query.filter(Product.price.__lt__(35)).all() 

#Lấy all sản phẩm sort tăng dần theo id
#Product.query.order_by(Product.id).all()
#Lấy all sản phẩm sort giảm dần theo 
#Product.query.order_by(-Product.id).all()  

#Lấy all sản phẩm với các điều kiện nối = and
#Product.query.filter(Product.price.__lt__(35), Product.name.contains('iphone')).order_by(Product.id).all()
#Lấy al sản phẩm với các điều kiện nối = or
#Product.query.filter(or_(Product.price.__lt__(35), Product.name.contains('iphone'))).order_by(Product.id).all()
#join 2 bảng
#Product.query.join(Category, Product.category_id==Category.id).filter(Category.name.contains('t')).add_column(Category.name).all()
#Tìm giá trị lớn nhất
#db.session.query(func.max(Product.price)).first()