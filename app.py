from flask import Flask, render_template, url_for, redirect, request, session, flash, send_file, jsonify
from pymongo import MongoClient
import gridfs
from werkzeug.security import generate_password_hash, check_password_hash
import io
from bson.objectid import ObjectId
from PIL import Image

app = Flask(__name__)
app.secret_key = 'Mysecretkey'

client = MongoClient('localhost', 27017)
db = client["flask_database"]
products = db['products']
users = db['users']
fs = gridfs.GridFS(db)

@app.before_request
def save_last_visited_page():
    if request.endpoint not in ('login', 'static/js/like-button.js','static','photo') and request.method == 'GET':
        #print(f"Saving URL: {request.url}")
        session['last_url'] = request.url

@app.route('/photo/<photo_id>')
def photo(photo_id):
    photo = fs.get(ObjectId(photo_id))
    return photo
    #return send_file(io.BytesIO(photo.read()), mimetype=photo.content_type)



@app.route('/liked-products', methods=['GET'])
def get_liked_products():
    user_liked_products = []
    user = users.find_one({"username": session["username"]})
    liked_products_ids = user.get('liked_products', [])
    if len(liked_products_ids)>0 and session.get('username'):
        for id in liked_products_ids:
            product = products.find_one({"_id": ObjectId(id)})
            if product:
                product['_id'] = str(product['_id'])
                product['photos'] = [str(photo_id) for photo_id in product['photos']]
                product['seller_id'] = str(product['seller_id'])
                user_liked_products.append(product)
    #print(user_liked_products)
    return (user_liked_products)


def get_user_liked_products():
    if session.get("username"):
        user = users.find_one({"username": session["username"]})
        user_liked_products = user.get('liked_products', [])
    else:
        user_liked_products=[]
    return user_liked_products


@app.route("/")
def home():
    all_products = products.find()
    all_products = list(all_products)
    for product in all_products:
        #product["_id"] = str(product["_id"])
        product['photos'] = [str(photo_id) for photo_id in product['photos']]
        product['seller_id'] = str(product['seller_id'])
    return render_template(
        "homepage.html",
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        products=all_products,
        user_liked_products=get_user_liked_products()
    )
        
@app.route("/selling")
def selling():
    if not session.get("username"):
        return redirect(url_for('login'))
    return render_template("selling.html", x="Account", page="account")
 


@app.route("/submit", methods=['POST'])
def submit():
    seller_username = session.get("username")
    user = users.find_one({"username": seller_username})
    seller_id = user['_id']
    title = request.form.get("title")
    categories = request.form.get("categories") 
    description = request.form.get("description")
    photo_ids = []
    files = request.files.getlist('photos')
    price = request.form.get('price')
    for file in files:
        if file:
            photo_id = fs.put(file, filename=file.filename)
            photo_ids.append(photo_id)
    product = {"title": title,
               "categories": categories,
               "description": description,
               "photos": photo_ids,
               "likes": 0,
               "seller_id": seller_id,
               "price": str(price),
               "views": 0
               }
    products.insert_one(product)
    return render_template("submit.html",x="Account" ,page="account", product=product)


@app.route("/account")
def account():
    if session.get("username"):
        liked = get_liked_products()
        return render_template("account.html",x="Account",liked_products=liked, page="account")
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = users.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(session.get('last_url') or url_for('home'))
        else:           
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')
    
    
@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        if users.find_one({"username": username}):
            flash('Username already exists!', 'danger')
        else:
            users.insert_one({"username": username, "password": hashed_password, "liked_products": []})
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
    
    liked_products = user.get('liked_products', [])
    if liked_products != 0: 
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

    

@app.route("/products/<product_id>")
def product_details(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    user_liked_products = get_user_liked_products()
    liked = False
    
    products.find_one_and_update(
        {"_id":ObjectId(product_id)},
        {"$inc": {"views": 1}}                   
    )
    if user_liked_products:
        if product['_id'] in user_liked_products:
            liked = True
    if product:
        return render_template(
            "products.html",
            product=product,
            x="Account" if session.get("username") else "Login",
            page="account" if session.get("username") else "login",
            liked= liked
        )
    else:
        return "Product not found", 404
    


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    if len(query) < 3:
        #flash('Search query must be at least 3 characters long!', 'danger')
        return redirect(url_for('home'))
    
    search_results = products.find({
        "$or": [
            {"title": {"$regex": f"\\b{query}\\b", "$options": "i"}},
            {"categories": {"$regex": f"\\b{query}\\b", "$options": "i"}},
            {"description": {"$regex": f"\\b{query}\\b", "$options": "i"}}
        ]
    })

    search_results = list(search_results)
    for product in search_results:
        product['_id'] = str(product['_id'])
        product['photos'] = [str(photo_id) for photo_id in product['photos']]
    
    
    return render_template(
        "search-results.html",
        query=query,
        results=search_results,
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        user_liked_products=get_user_liked_products()
    )
   
    

if __name__ == "__main__":
    app.run(debug=True)