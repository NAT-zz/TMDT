from flask import redirect, request
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib.sqla import ModelView, form
from flask_login import current_user, logout_user

from __init__ import db, app
from models import*
import models
import utils


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == MyRole.ADMIN

class MyAdminIndex(AdminIndexView):
    @expose("/")
    def index(self):
        return self.render('admin/index.html')
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == MyRole.ADMIN

admin = Admin(app=app, name = "UTE SHOP", template_mode = 'bootstrap4')
        
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect("/admin")
    def is_accessible(self):
        return current_user.is_authenticated

class DoanhThu(BaseView):
    @expose('/')
    def index(self):
        from_date = request.args.get("from_date")
        to_date = request.args.get("to_date")

        stats = utils.product_stats(from_date=from_date, to_date=to_date)
        return self.render("admin/stats.html", stats= stats) 

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == MyRole.ADMIN

class BrandStat(BaseView):
    @expose('/')
    def index(self):
        stats = utils.product_stats_by_cate()
        return self.render("admin/stats2.html", stats= stats)
         
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == MyRole.ADMIN


class UserModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True
    column_editable_list = ("name", "username", "phone", "email", "password")

    column_filters = ("id", "receipt", "ship", "name", "username", Receipt.id, Order.id)
    column_default_sort = [("id", True)]
    column_searchable_list = ("id", "name", "username", "phone", "email", Receipt.id, Order.id)
    column_descriptions = dict(
        username = "Username must be unique"
    )
    can_set_page_size = True

class BrandModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("name", "product", "icon")
    column_filters = ("id", "name", "product")
    column_default_sort = [("id", True)]
    column_searchable_list = ("id", "name", "icon")
    can_set_page_size = True

class ProductModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("name", "price", "brand_id", "image", "amount", "screen", "chip", "ram", "rom", "weight", "description")
    column_filters = ("name", "price", "brand_id", "image", "amount", "screen", "chip", "ram", "rom", "weight", "detail")
    column_default_sort = [("id", True), ("price", True), ("amount", True), ("ram", True), ("rom", True), ("weight", True)]

    column_searchable_list = ("id", "name", "screen", "chip", "ram", "rom", "weight")
    can_set_page_size = True

class ReceiptModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True

    column_filers = ("id", "detail", "ship", "product", "user_id", "user", Users.name)
    column_default_sort = [("id", True), ("user_id", True)]
    column_searchable_list = ("id", "user_id", Users.name)    
    can_set_page_size = True

class ReceiptDetailModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("quantity", "unit_price")
    column_default_sort = [("id", True), ("quantity", True)]
    column_filters = ("id", "quantity", "unit_price", "receipt", "product")

    column_searchable_list = ("id","product_id", "quantity", "unit_price")
    can_set_page_size = True

class OrderModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True

    column_editable_list = ("cityname", "price")
    column_default_sort = [("id", True)]
    column_filters = ("id", "cityname", "user", "receipt", "price")

    column_searchable_list = ("cityname", "price", Users.name, Receipt.id, Product.name)
    can_set_page_size = True

class ShippingModelView(AuthenticatedView):
    list_template = 'layout/layout_admin/list_admin.html'
    edit_template = 'layout/layout_admin/edit_admin.html'
    create_template = 'layout/layout_admin/create_admin.html'
    details_template = 'layout/layout_admin/details_admin.html'

    can_export = True
    can_view_details = True
    column_display_pk = True
    can_create = True
    can_edit = True
    column_editable_list = ("cityname", "price")

admin.add_view(UserModelView(Users ,db.session, name = "Users"))
admin.add_view(BrandModelView(Brand, db.session, name = "Brands"))
admin.add_view(ProductModelView(Product,db.session, name = "Products"))
admin.add_view(OrderModelView(Order, db.session, name = "Orders"))
admin.add_view(ReceiptModelView(Receipt, db.session, name = "Receipts"))
admin.add_view(ReceiptDetailModelView(ReceiptDetail, db.session, name = "ReceiptDetail"))
admin.add_view(ShippingModelView(Shipping, db.session, name="Shipping"))
admin.add_view(LogoutView(name = "LogOut"))

admin.add_view(DoanhThu(name = "Stats"))
admin.add_view(BrandStat(name = "Brand Stats"))




