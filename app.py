from flask import Flask, render_template, url_for, request, session
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client["flask_database"]
products = db['products']

@app.route("/")
def home():
    if session.get("name"):
        return render_template("homepage.html", x="Account", page="account")
    else:
        return render_template("homepage.html", x="Login", page="login")

@app.route("/selling")
def sell_page():
    return render_template("selling.html")


@app.route("/submit", methods=['POST'])
def submit():
    title = request.form.get("title")
    photos = request.form.get("photos")
    categories = request.form.get("categories") 
    product = {"title": title,
               "photos": photos,
               "categories": categories
               }
    products.insert_one(product)
    return render_template("submit.html")


@app.route("/account.html")
def account():
    return render_template("account.html")


@app.route("/login")
def login():
    return render_template("login.html")
    



if __name__ == "__main__":
    app.run(debug=True)