from datetime import date, datetime
from re import T

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Enum, func, or_)
from sqlalchemy.orm import backref, relationship
import enum
from flask_login import UserMixin

from sqlalchemy.sql.expression import column, null, true

from __init__ import db
class MyRole(enum.Enum):
    USER = 1
    ADMIN = 0

class Users (db.Model, UserMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key= True, autoincrement= True)
    active = Column(Integer, nullable= False)
    name = Column(String(30), nullable= False)
    join_date = Column(DateTime, default=datetime.now())
    username = Column(String(30), nullable=False, unique= True)
    password = Column(String(100), nullable=False)
    phone = Column(String(12), nullable= False, default="123456")
    email = Column(String(30), nullable=False, default="nguoidung@gmail.con")
    role =  Column(Enum(MyRole), default = MyRole.USER)

    receipt = relationship("Receipt", backref="user", lazy=True)
    ship = relationship("Order", backref="user", lazy=True)
    def __str__(self) -> str:
        return self.name

class Brand(db.Model):
    __tablename__ = "brand"
    id = Column(Integer, primary_key=True, autoincrement= True)
    name = Column(String(10), nullable=False)
    icon = Column(String(100), nullable=True)
    
    product = relationship('Product', backref=('brand'), lazy=True)
    def __str__(self) -> str:
        return self.name

class Product(db.Model):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, default="Laptop-1")
    price = Column(Float, nullable=False, default=100)
    brand_id = Column(Integer, ForeignKey(Brand.id), nullable=False)

    image = Column(String(100), nullable=True)
    amount = Column(Integer, default=50)
    screen = Column(String(30), nullable=False, default="OLED 24inch")
    chip = Column(String(30), nullable=False, default="Core i5 8thGen")
    ram = Column(Integer, nullable=False, default=8)
    rom = Column(Integer, nullable=False, default=512)
    weight = Column(Float, nullable=False, default=2.2)
    description = Column(String(500), nullable=True)

    detail = relationship("ReceiptDetail", backref= "product", lazy=True)
    def __str__(self) -> str:
        return self.name

class Receipt(db.Model):
    __tablename__ = "receipt"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    # 0: ongoing, 1: draft, 2: successful
    status = Column(Integer, default=0)
    created_date = Column(DateTime, default=datetime.now())

    detail = relationship("ReceiptDetail", backref="receipt", lazy = True)
    ship = relationship("Order", backref="receipt", lazy=True)

class ReceiptDetail(db.Model):
    __tablename__ = "receiptdetail"
    id = Column(Integer, primary_key=True, autoincrement=True)
    receitp_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)

    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)

class Order(db.Model):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cityname = Column(String(30), nullable=False, default="TP. Hồ Chí Minh")
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False)
    price = Column(Float, nullable=False, default=30.0)

class Shipping(db.Model):
    __tablename__ = "ship"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cityname = Column(String(50), nullable=False)
    price = Column(Float, nullable= False, default= 50)

if __name__ == '__main__':
    db.create_all()

    #-------CHỈ CHẠY 1 LẦN - CHẠY = TERMINAL---------

    #Admin mặc định
    # user = Users(name = "tuannguyen", 
    #             active = 1,
    #             username = "admin", password = "123", 
    #             phone = "123", email = "tuan@gmail.com", role = "ADMIN")
    # db.session.add(user)
    # db.session.commit()

    # ship = Shipping(cityname = "Hồ Chí Minh", price = 20)
    # ship1 = Shipping(cityname = "Hà Nội", price = 30)
    # ship2 = Shipping(cityname = "Biên Hòa", price = 40)
    # ship3 = Shipping(cityname = "Cần Thơ", price = 50)
    # ship4 = Shipping(cityname = "Phú Thọ", price = 60)
    # ship5 = Shipping(cityname = "Buôn Ma Thuật", price = 70)
    # ship6 = Shipping(cityname = "Vũng Tàu", price = 30)

    # db.session.add(ship)
    # db.session.add(ship1)
    # db.session.add(ship2)
    # db.session.add(ship3)
    # db.session.add(ship4)
    # db.session.add(ship5)
    # db.session.add(ship6)

    db.session.commit()

