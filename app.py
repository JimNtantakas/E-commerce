from flask import Flask, render_template, url_for, redirect, request, session, flash, send_file, jsonify
from pymongo import MongoClient
import gridfs
from werkzeug.security import generate_password_hash, check_password_hash
import io
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'Mysecretkey'

client = MongoClient('localhost', 27017)
db = client["flask_database"]
products = db['products']
users = db['users']
fs = gridfs.GridFS(db)


@app.route('/photo/<photo_id>')
def photo(photo_id):
    photo = fs.get(ObjectId(photo_id))
    return photo
    #return send_file(io.BytesIO(photo.read()), mimetype=photo.content_type)


@app.route("/")
def home():
    all_products = products.find()
    if session.get("username"):
        user = users.find_one({"username": session["username"]})
        user_liked_products = user.get('liked_products', [])
    else:
        user_liked_products=[]
    return render_template(
        "homepage.html",
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        products=all_products,
        user_liked_products=user_liked_products
    )
        
@app.route("/selling")
def selling():
    if session.get("username"):
        return render_template("selling.html", x="Account", page="account")
    else:
        return render_template("login.html")


@app.route("/submit", methods=['POST'])
def submit():
    title = request.form.get("title")
    categories = request.form.get("categories") 
    description = request.form.get("description")
    photo_ids = []
    files = request.files.getlist('photos')
    for file in files:
        if file:
            photo_id = fs.put(file, filename=file.filename)
            photo_ids.append(photo_id)
    product = {"title": title,
               "categories": categories,
               "description": description,
               "photos": photo_ids,
               "likes": 0
               }
    products.insert_one(product)
    return render_template("submit.html",x="Account" ,page="account")


@app.route("/account.html")
def account():
    return render_template("account.html")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:           
            flash('Invalid username or password!', 'danger')
    return render_template("login.html")
    
    
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        if users.find_one({"username": username}):
            flash('Username already exists!', 'danger')
        else:
            users.insert_one({"username": username, "password": hashed_password, "liked_products": 0})
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('home'))
    return render_template("register.html")


@app.route("/like", methods=['POST'])
def like():
    if not session.get("username"):
        return jsonify({"success": False, "message": "You must be logged in to like a product."}), 403
    user = users.find_one({"username": session["username"]})
    
    data = request.get_json()
    product_id = data['product_id']
    product = products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"success": False, "message": "Product not found."}), 404
    
    if ObjectId(product_id) in user.get('liked_products', []):
        products.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"likes": -1}}
        )
        users.update_one(
            {"_id": user['_id']},
            {"$pull": {"liked_products": ObjectId(product_id)}},
            )
        liked = False
        message = "You unliked this product."
    else:
        products.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"likes": 1}}
        )
        
        users.update_one(
            {"_id": user['_id']},
            {"$push": {"liked_products": ObjectId(product_id)}}
            )
        liked = True
        message = "You liked this product."
        
    updated_product = products.find_one({"_id": ObjectId(product_id)})
    return jsonify({"success": True, "liked": liked, "likes": updated_product["likes"], "message": message})



@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for('home'))


#@app.route("/search")
#def search():
#    pass
    



if __name__ == "__main__":
    app.run(debug=True)