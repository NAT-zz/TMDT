from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_login import LoginManager
import cloudinary


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:tuan0512@localhost/tmdt?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.secret_key = "(A*FA(GAGASDA*&"


# app.config["CLOUDINARY_INFO"] = {
#     "cloud_name" : "natscloud",
#     "api_key" : "669999992192735",
#     "api_secret": "7-zbW0Pat43_axsYVZ2ULRTe5zY"
# }

# Configure through environment variables:
app.config["PAYPAL-SANDBOX-CLIENT-ID"] = "Aa6Hn8C93yInGY6oa-St9YgzwOxToXoD_-iqvbmpcn8vl-0qVFqF0Qr6Z5F6DjWVSR4OMuaFNVg7ewEk"
app.config["PAYPAL-SANDBOX-CLIENT-SECRET"] = "EJSfWZBrSsHIkqFwB-jPlgpFQNlaw5BG2TQEarvw6cY9JSg4noNbyERKqvHy21Na-C33CuYX_J8J4Csj"


app.config["PAGE_SIZE"] = 9
db = SQLAlchemy(app=app)
my_login = LoginManager(app=app)

# cloudinary.config(cloud_name = app.config["CLOUDINARY_INFO"]['cloud_name'],
#                 api_key = app.config["CLOUDINARY_INFO"]['api_key'],
#                 api_secret = app.config["CLOUDINARY_INFO"]['api_secret'])


CART_KEY = "cart"

# partner_code = "MOMOYTDW20211109"
# access_key = "kG8pmfc4K4M3bFqm"
# secret_key = "nI3noEFbEHynhTR683yqDEqf100Hp1Z0"
# api_endpoint = "https://test-payment.momo.vn/gw_payment/transactionProcessor"

momo = {
    "endpoint": "https://test-payment.momo.vn/gw_payment/transactionProcessor",
    "partnerCode": "MOMOORNE20211031",
    "accessKey": "ULvMSUhENodZ2stN",
    "secretKey": "i3tq9bB1lPHpIwsat6hPMgUoj5yCiLPv",
    "orderInfo": "pay with MoMo",
    "returnUrl": "http://127.0.0.1:5000/momo/payment-result",
    "notifyUrl": "http://127.0.0.1:5000/momo/payment-result",
    "amount": "",
    "orderId": "",
    "requestId": "",
    "requestType": "captureMoMoWallet",
    "extraData": ""
}
