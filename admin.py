from flask import redirect
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView, form
from flask_login import current_user, logout_user

from __init__ import admin, db
from models import*


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin")
    def is_accessible(self):
        return current_user.is_authenticated
class DoanhThu(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render("admin/stats.html") 
        
# class BangGiaVeModelView(AuthenticatedView):
#     can_export = True
#     can_view_details = True
#     column_editable_list = ('SoGhe', 'GiaVe')

#     column_default_sort = [('SoGhe', False), ('GiaVe', True)]
#     column_filters = ('GiaVe', 'chuyenbay', "SoGhe", "HangVe")
#     column_searchable_list = ('HangVe', 'SoGhe')

#     column_labels = dict(HangVe = "Hạng",
#                         GiaVe = "Giá",
#                         SoGhe = "Số Ghế",
#                         chuyenbay = "Chuyến Bay")
#     column_descriptions = dict(HangVe = "Thường, Thương Gia,...",
#                                 GiaVe = "500.000VND - 1.000.000VND",
#                                 SoGhe = "Tối Đa 50")
#     can_set_page_size = True

class UserModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True
    column_editable_list = ("name", "username", "phone", "email", "password")

    column_filters = ("id", "receipt", "ship", "name", "username", Receipt.id, Ship.id)
    column_default_sort = [("id", True)]
    column_searchable_list = ("id", "name", "username", "phone", "email", Receipt.id, Ship.id)
    column_descriptions = dict(
        username = "Username must be unique"
    )
    can_set_page_size = True

class BrandModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("name", "product", "icon")
    column_filters = ("id", "name", "product")
    column_default_sort = [("id", True)]
    column_searchable_list = ("id", "name", "icon")
    can_set_page_size = True

class ProductModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("name", "price", "brand_id", "image", "amount", "screen", "chip", "ram", "rom", "weight", "description")
    column_filters = ("name", "price", "brand_id", "image", "amount", "screen", "chip", "ram", "rom", "weight", "detail")
    column_default_sort = [("id", True), ("price", True), ("amount", True), ("ram", True), ("rom", True), ("weight", True)]

    column_searchable_list = ("id", "name", "screen", "chip", "ram", "rom", "weight")
    can_set_page_size = True

class ReceiptModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True

    column_filers = ("id", "detail", "ship", "product", "user_id", "user", Users.name)
    column_default_sort = [("id", True), ("user_id", True)]
    column_searchable_list = ("id", "user_id", Users.name)    
    can_set_page_size = True

class ReceiptDetailModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("quantity", "unit_price")
    column_default_sort = [("id", True), ("quantity", True)]
    column_filters = ("id", "quantity", "unit_price", "receipt", "product")

    column_searchable_list = ("id","product_id", "quantity", "unit_price")
    can_set_page_size = True

class ShipModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("cityname", "price")
    column_default_sort = [("id", True)]
    column_filters = ("id", "cityname", "user", "receipt", "price")

    column_searchable_list = ("cityname", "price", Users.name, Receipt.id, Product.name)
    can_set_page_size = True

class IncomeModelView(AuthenticatedView):
    can_export = True
    can_view_details = True
    column_display_pk = True
    can_create = False
    can_edit = False

admin.add_view(UserModelView(Users ,db.session, name = "Users"))
admin.add_view(BrandModelView(Brand, db.session, name = "Brands"))
admin.add_view(ProductModelView(Product,db.session, name = "Products"))
admin.add_view(ReceiptModelView(Receipt, db.session, name = "Receipts"))
admin.add_view(ReceiptDetailModelView(ReceiptDetail, db.session, name = "ReceiptDetail"))
admin.add_view(ShipModelView(Ship, db.session, name = "Ship"))
admin.add_view(IncomeModelView(Income, db.session, name = "Stats"))
admin.add_view(LogoutView(name = "LogOut"))




