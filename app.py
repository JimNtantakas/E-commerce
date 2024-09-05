from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from pymongo import MongoClient
import gridfs
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os




load_dotenv()
app = Flask(__name__)

SECRET_KEY = os.getenv("MY_SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['MONGO_URI'] = MONGO_URI

#client = MongoClient('localhost', 27017)
client = MongoClient(app.config['MONGO_URI'])
db = client["flask_database"]
products = db['products']
users = db['users']
fs = gridfs.GridFS(db)

@app.before_request
def save_last_visited_page():
    if request.endpoint not in ('login', 'static/js/like-button.js','static','photo') and request.method == 'GET':
        session['last_url'] = request.url

@app.route('/photo/<photo_id>')
def photo(photo_id):
    photo = fs.get(ObjectId(photo_id))
    return photo


@app.route("/")
def home():
    all_products = products.find()
    
    rated_products = products.find(({"total_rating": {"$ne": ""}}))
    products_sorted_by_rating = rated_products.sort("total_rating", -1)
    most_viewed_products = products.find().sort("views", -1)
    
    return render_template(
        "homepage.html",
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        products=all_products,
        products_sorted_by_rating = products_sorted_by_rating,
        most_viewed_products = most_viewed_products,
        user_liked_products=get_user_liked_products(),
        products_in_cart = get_cart_products_number()
    )
     
        
@app.route("/selling")
def selling():
    if not session.get("username"):
        return redirect(url_for('login'))
    return render_template(
        "selling.html",
        x="Account",
        page="account",
        products_in_cart=get_cart_products_number(),
        categories= get_categories()
        )


@app.route("/submit-review", methods=['POST'])
def submit_review():
    user = users.find_one({'username': session.get("username")})
    product_id = request.form.get('product_id')
    rating = float(request.form.get('review-rating'))
    text = request.form.get('review-text')
    
    #for user
    new_rated_product = {
        "product_id": ObjectId(product_id), 
        "rating": rating,
        "comment": text
    }
    users.update_one(
        {"_id": user['_id']},
        {"$push": {"rated_products": new_rated_product}}
    )
    
    #for product
    new_rating = {
        "user_id": user['_id'], 
        "rating": rating,
        "comment": text
    }
    products.update_one(
        {"_id": ObjectId(product_id)},
        {"$push": {"ratings": new_rating}}
    )
    products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"total_rating": product_total_rating(product_id) if product_total_rating(product_id)!="" else 0 }}
    )
    
    return redirect(url_for("product_details",product_id=product_id))


@app.route("/edit-review", methods=['POST'])
def edit_review():
    user = users.find_one({'username': session.get("username")})
    product_id = request.form.get('product_id')
    rating = float(request.form.get('review-rating'))
    text = request.form.get('review-text')
    
    new_edited_product = {
        "product_id": ObjectId(product_id), 
        "rating": rating,
        "comment": text
    }
    users.update_one(
        {"_id": user['_id'], "rated_products.product_id": ObjectId(product_id)},
        {"$set": {
            "rated_products.$.rating": new_edited_product["rating"],
            "rated_products.$.comment": new_edited_product["comment"]
        }}
    )
    

    products.update_one(
        {"_id": ObjectId(product_id), "ratings.user_id": user['_id']},
        {"$set": {"ratings.$.rating": rating, "ratings.$.comment": text}}
    )
    products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"total_rating": product_total_rating(product_id) if product_total_rating(product_id)!="" else 0}}
    )
    
    return redirect(url_for("product_details",product_id=product_id))


@app.route("/delete-review", methods=['POST'])
def delete_review():
    user = users.find_one({"username": session.get("username")})
    product_id = request.form.get('product_id')
        
    users.update_one(
        {"_id": user['_id']},
        {"$pull": {"rated_products": {"product_id": ObjectId(product_id)}}}
    )
    
    products.update_one(
        {"_id": ObjectId(product_id)},
        {"$pull": {"ratings": {"user_id": user['_id']}}}
    )
    products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"total_rating": product_total_rating(product_id) if product_total_rating(product_id)!="" else 0}}
    )
    
    return redirect(url_for("product_details",product_id=product_id))


@app.route("/submit", methods=['POST'])
def submit():
    seller_username = session.get("username")
    user = users.find_one({"username": seller_username})
    seller_id = user['_id']
    title = request.form.get("title")
    categories = request.form.getlist("categories[]")
    description = request.form.get("description")
    ratings = []
    
    photo_ids = []
    main_image = request.files.get('main-image')
    if main_image:
        photo_id = fs.put(main_image, filename=main_image.filename)
        photo_ids.append(photo_id)
    
    files = request.files.getlist('photos')
    quantity = request.form.get('quantity')
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
               "quantity": int(quantity),
               "price": str(price),
               "views": 0,
               "total_rating": 0,
               "ratings": ratings
               }
    products.insert_one(product)
    users.update_one(
            {'_id': user['_id']},
            {'$push': {'published_products': ObjectId(product['_id'])}}
            )
    
    product_id = product["_id"]
    return redirect(url_for("submit_informations", product_id=str(product_id)))


@app.route("/submit-changes", methods=['POST'])
def submit_changes():
    product_id = request.form.get('product_id')
    product = products.find_one({"_id": ObjectId(product_id)})
    title = request.form.get("title")
    categories = request.form.getlist("categories[]")
    description = request.form.get("description")
    
    
    main_image = request.files.get('main-image')
    photo_ids = []
    
    delete_image_ids = request.form.getlist('delete-images')
    if delete_image_ids:
        #remove all the checked images
        for image_id in delete_image_ids:
            fs.delete(ObjectId(image_id))
            products.update_one(
                {"_id": ObjectId(product_id)},
                {"$pull": {"photos": ObjectId(image_id)}}
            )
    product = products.find_one({"_id": ObjectId(product_id)})
    
    
    if main_image:
        # if main_image changes put it first
        photo_id = fs.put(main_image, filename=main_image.filename)
        photo_ids.append(photo_id)
        for photo_id in product['photos']:
            photo_ids.append(photo_id)
    else:
        for photo_id in product['photos']:
            photo_ids.append(photo_id)
            
    

    files = request.files.getlist('photos')
    for file in files:
        if file:
            photo_id = fs.put(file, filename=file.filename)
            photo_ids.append(photo_id)
    
    #for photo_id in product['photos']:
        #fs.delete(ObjectId(photo_id))    
    quantity = request.form.get('quantity')
    price = request.form.get('price')
    updated_product = {
        "title": title,
        "categories": categories,
        "description": description,
        "photos": photo_ids,
        "likes": product['likes'],
        "seller_id": product['seller_id'],
        "quantity": int(quantity),
        "price": str(price),
        "views": product['views']
    } 
    products.update_one(
        {"_id": product['_id']},
        {"$set": updated_product}
    )
    return redirect(url_for("product_details",product_id=product_id))
    
   
@app.route('/liked-products', methods=['GET'])
def get_liked_products():
    if session.get('username'):
        user_liked_products = []
        user = users.find_one({"username": session["username"]})
        liked_products_ids = user.get('liked_products', [])
        if len(liked_products_ids)>0:
            for id in liked_products_ids:
                product = products.find_one({"_id": ObjectId(id)})
                if product:
                    product['_id'] = str(product['_id'])
                    product['photos'] = [str(photo_id) for photo_id in product['photos']]
                    product['seller_id'] = str(product['seller_id'])
                    product['seller_id'] = str(product['seller_id'])
                    for rating in product['ratings']:
                            rating['user_id'] = str(rating['user_id'])
                    user_liked_products.append(product)
    else:
        return "You need to log in"
    return user_liked_products

@app.route('/cart-products', methods=['GET'])
def get_cart_products():
    if session.get('username'):
        cart_products = []
        user = users.find_one({"username": session["username"]})
        cart_products_ids = user.get('cart_products', [])
        for id in cart_products_ids:
            product = products.find_one({"_id": ObjectId(id)})
            if product:
                product['liked'] = False
                if product['_id'] in get_user_liked_products():
                    product['liked'] = True
                product['_id'] = str(product['_id'])
                product['photos'] = [str(photo_id) for photo_id in product['photos']]
                product['seller_id'] = str(product['seller_id'])
                for rating in product['ratings']:
                        rating['user_id'] = str(rating['user_id'])
                cart_products.append(product)
    else:
        return "You need to log in"
    return cart_products   


@app.route('/published-products', methods=['GET'])
def get_published_products():
    if session.get('username'):
        published_products = []
        user = users.find_one({"username": session["username"]})
        published_products_ids = user.get('published_products', [])
        for id in published_products_ids:
            product = products.find_one({"_id": ObjectId(id)})
            if product:
                product['liked'] = False
                if product['_id'] in get_user_liked_products():
                    product['liked'] = True
                product['_id'] = str(product['_id'])
                product['photos'] = [str(photo_id) for photo_id in product['photos']]
                product['seller_id'] = str(product['seller_id'])
                for rating in product['ratings']:
                        rating['user_id'] = str(rating['user_id'])
                published_products.append(product)
    else:
        return "You need to log in"

    return published_products


@app.route('/rated-products', methods=['GET'])
def get_rated_products():
    if session.get('username'):
        rated_products = []
        user = users.find_one({"username": session["username"]})
        rated_products_ids = [item['product_id'] for item in user.get('rated_products', [])]
        for id in rated_products_ids:
            product = products.find_one({"_id": ObjectId(id)})
            if product:
                product['total_rating'] = product_total_rating(product['_id'])
                product['_id'] = str(product['_id'])
                product['photos'] = [str(photo_id) for photo_id in product['photos']]
                product['seller_id'] = str(product['seller_id'])
                for rating in product['ratings']:
                    rating['user_id'] = str(rating['user_id'])
                rated_products.append(product)
    else:
        return "You need to log in"
    return rated_products
        
        
def get_user_liked_products():
    user_liked_products=[]
    if session.get("username"):
        user = users.find_one({"username": session["username"]})
        user_liked_products = user.get('liked_products', [])
    return user_liked_products


def get_categories():
    categories = [
        {"name": "Fashion", "subcategories": ["Men", "Women", "Kids", "Shoes", "Clothes", "Jewellery", "Fashion Accessories"]},
        {"name": "Tech", "subcategories": ["Phones", "Tablets", "Computers", "Gaming", "Electronics", "Tech Accessories"]},
        {"name": "Home - Garden", "subcategories": ["Household Appliances", "Tools", "Furniture", "Lighting", "Cleaning Supplies", "Garden"]},
        {"name": "Books", "subcategories": ["Literature", "Fiction", "Science", "School", "Fairy Tales", "Comics"]},
        {"name": "Hobby - Sports", "subcategories": ["Sports", "Camping", "Gym Equipment"]},
        {"name": "Pets", "subcategories": ["Dogs", "Cats", "Fish", "Birds", "Rodents", "Reptiles"]},
    ]
    return categories

def get_cart_products_number():
    if session.get("username"):
        sum = 0
        user = users.find_one({"username": session["username"]})
        all_products = products.find()
        all_products_ids = [product['_id'] for product in all_products]
        for product_id in user['cart_products']:
            if product_id in all_products_ids:
                sum += 1      
        return sum
    else:
        return 0
    
    
@app.route("/submit-informations/<product_id>")
def submit_informations(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    if session.get("username"):
        user = users.find_one({"username": session["username"]})
        if ObjectId(product['_id']) in user['published_products']:
            return render_template("submit-informations.html", x="Account" ,page="account", product=product, products_in_cart = get_cart_products_number())
        else:
            return "Product not found, 404", 404 
    return redirect(url_for('home'))


@app.route("/account")
def account():
    if session.get("username"):
        user = users.find_one({"username": session.get("username")})
        liked = get_liked_products()
        total_rating, count = user_total_rating(user['_id'])
        return render_template("account.html",x="Account",liked_products=liked, page="account", products_in_cart=get_cart_products_number(), user=user, total_rating=total_rating, count=count)
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
            users.insert_one({
            "username": username,
            "password": hashed_password,
            "liked_products": [],
            "cart_products": [],
            "orders": [],
            "published_products": [],
            "rated_products": []
            })
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

    

def user_total_rating(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    total_rating = "-"
    count = 0
    sum = 0
    for published_product in user['published_products']:
        product = products.find_one({"_id": ObjectId(published_product)})
        if user['_id'] == product['seller_id']:
            for rating in product['ratings']:
                if rating['rating']:
                    sum += rating['rating']
                    count += 1           
    if count > 0 :
        total_rating = round(sum / count, 1)    
    return total_rating,count


def product_total_rating(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    total_rating = "-"
    count = 0
    sum = 0
    for rating in product['ratings']:
        if rating['rating']:
            sum += rating['rating']
            count += 1    
    if count > 0 :
        print(sum,count)
        total_rating = round(sum / count, 1)  
    return total_rating

@app.route("/products/<product_id>")
def product_details(product_id):
    if products.find_one({"_id": ObjectId(product_id)}):
        user = None
        owned = False
        product = products.find_one({"_id": ObjectId(product_id)})
        user_liked_products = get_user_liked_products()
        liked = False
        already_rated = False
        if session.get("username"):
            user = users.find_one({"username": session["username"]}) 
            if product["_id"] in user['published_products']:
                owned = True 
            for rating in product['ratings']:
                user_id = rating['user_id']
                if user['_id'] == ObjectId(user_id):
                    already_rated = True
                             
        total_rating = product_total_rating(product_id)       
                
        products.find_one_and_update(
            {"_id":ObjectId(product_id)},
            {"$inc": {"views": 1}}                   
        )
        if user_liked_products:
            if product['_id'] in user_liked_products:
                liked = True
 
        logged = False
        added_in_cart= False
        if session.get("username"):
            user = users.find_one({"username": session["username"]})  
            logged = True
            if ObjectId(product_id) in user["cart_products"]:
                added_in_cart = True
        
        return render_template(
            "products.html",
            owned = owned,
            already_rated = already_rated,
            product=product,
            seller = users.find_one({"_id": product['seller_id']}),
            x="Account" if session.get("username") else "Login",
            page="account" if session.get("username") else "login",
            liked= liked,
            products_in_cart = get_cart_products_number(),
            in_cart = added_in_cart,
            logged = logged,
            count = len(product['ratings']),
            total_rating = total_rating
        )
    else:
        return "Product not found, 404", 404
    
    
@app.route("/add-to-cart", methods=['POST'])
def add_to_cart():
    if not session.get("username"):
        return jsonify({"success": False, "message": "You must be logged in to add a product in cart."}), 403
    
    product_id = request.form.get('product_id')
    user = users.find_one({"username": session["username"]})
    if ObjectId(product_id) not in user['cart_products']:
        users.update_one(
            {'_id': user['_id']},
            {'$push': {'cart_products': ObjectId(product_id)}}
            )

    else:
        users.update_one(
            {'_id': user['_id']},
            {'$pull': {'cart_products': ObjectId(product_id)}}
            )
        
    return redirect(url_for('product_details', product_id=product_id))
    


@app.route("/search", methods=['GET'])
def search():
    query = request.args.get('query')
    min_price = request.args.get("min")
    max_price = request.args.get("max")
    sort_by = request.args.get("sort_by")
    
    if not min_price:
        min_price = 0
    if not max_price:
        max_price =  1000000000
    
    if not sort_by:
        sort_by = "Recent"  #default way of sorting products in search page

    if len(query) < 3:
        return redirect(url_for('home'))  
    
    if query == "latest listings":
        search_results = products.find()
    elif query == "top rated":
        search_results = products.find().sort("total_rating", -1)
    elif query == "most viewed":
        search_results = products.find().sort("views", -1)
    else:
        
        words = query.split()
        keyword_to_category = {
            "phone": "Phones","smartphone": "Phones","smartphones": "Phones","tablet": "Tablets","ipad": "Tablets","ipads": "Tablets","laptop": "Computers","laptops": "Computers",
            "dog": "Dogs","cat": "Cats","football": "Sports","soccer":"football","jewelleries":"Jewellery"
            # Add more keyword-to-category mappings as needed
        }
        
        for word in words:
            if word.lower() in keyword_to_category:
                words.append(keyword_to_category[word.lower()])
                
        regex_pattern = "|".join([f"\\b{word}\\b" for word in words])
        search_results = products.find({    
            "$and":[
                {"quantity": {"$gt": 0}},
                {
                    "$or": [
                        {"title": {"$regex": regex_pattern, "$options": "i"}},
                        {"categories": {"$regex": regex_pattern, "$options": "i"}},
                        {"description": {"$regex": regex_pattern, "$options": "i"}},
                    ]
                }
            ]
        })
        
    
    search_results = list(search_results)
    results = list(search_results)
    
    if min_price and max_price:
        search_results = []
        for product in results:
            if int(product['price'])>=int(min_price) and int(product['price'])<=int(max_price):
                search_results.append(product)
                
    if sort_by == "Ascending":
        search_results.sort(key=lambda x: int(x['price']))
    elif sort_by == "Descending":
        search_results.sort(key=lambda x: int(x['price']), reverse=True)    
    elif sort_by == "Rating":
        search_results.sort(key=lambda x: (x['total_rating']), reverse=True)    
    elif sort_by == "Older":
        search_results = search_results
    else:
        #Sort by recent
        search_results.reverse()
         
    for product in search_results:
        product['photos'] = [str(photo_id) for photo_id in product['photos']]
    return render_template(
        "search-results.html",
        query=query,
        min_price=min_price,
        max_price=max_price,
        sort_by = sort_by,
        results=search_results,
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        user_liked_products=get_user_liked_products(),
        products_in_cart = get_cart_products_number()
    )
   


@app.route("/filter", methods=['POST'])
def filter():
    query = request.form.get("query")
    min_price = request.form.get("min-price")
    max_price = request.form.get("max-price")
    sort_by = request.form.get("sort_by")
    
    return redirect(url_for('search', query=query, sort_by=sort_by, min=min_price, max=max_price))
    


@app.route("/categories", methods=['GET'])
def categories(): 
    return render_template(
        "categories.html",
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        products_in_cart = get_cart_products_number(),
        categories = get_categories()
    )


@app.route("/products/edit/<product_id>", methods=['GET'])
def edit(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    filenames = []
    for image_id in product['photos']:
        image = fs.find_one({"_id": image_id})
        if image:
            filenames.append(image.filename)
    
    return render_template(
        "edit-product.html",
        filenames = filenames,
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        categories= list(get_categories()),
        product_categories = product['categories'],
        product = product,
        products_in_cart=get_cart_products_number()
    )


@app.route("/products/delete/<product_id>", methods=['POST'])
def delete(product_id): 
    product = products.find_one({"_id": ObjectId(product_id)})
    for photo_id in product['photos']:
        fs.delete(ObjectId(photo_id))
        
    users.update_many(
        {"liked_products": ObjectId(product_id)},
        {"$pull": {"liked_products": ObjectId(product_id)}}
    )
    users.update_many(
        {"cart_products": ObjectId(product_id)},
        {"$pull": {"cart_products": ObjectId(product_id)}}
    )
    users.update_many(
        {"orders": ObjectId(product_id)},
        {"$pull": {"orders": ObjectId(product_id)}}
    )
    users.update_many(
        {"published_products": ObjectId(product_id)},
        {"$pull": {"published_products": ObjectId(product_id)}}
    )
    
    products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('home'))


@app.route("/review/<product_id>",methods=['GET'])
def review(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    already_rated = False
    if session.get("username"):
        user = users.find_one({"username": session["username"]}) 
        comment = ''
        rating = ''
        for rating in product['ratings']:
                user_id = rating['user_id']
                if user['_id'] == user_id:
                    already_rated = True
                    comment = rating['comment']
                    rating = rating['rating']
                    
        if product:
            return render_template(
                "review.html",
                x="Account" if session.get("username") else "Login",
                already_rated = already_rated,
                rating = rating,
                comment = comment,
                product = product,
                page="account" if session.get("username") else "login",
                products_in_cart = get_cart_products_number()
            )
        else:
            return "Product not found, 404", 404 
    return redirect(url_for('home'))



@app.route("/user/<user_id>")
def user_display(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    user_published_products = []
    for product_id in user['published_products']:
        product = products.find_one({"_id": ObjectId(product_id)})
        if product:
            product['photos'] = [str(photo_id) for photo_id in product['photos']]
            product['seller_id'] = str(product['seller_id'])
            user_published_products.append(product)
    total_rating, count = user_total_rating(user['_id'])
    return render_template(
        "user.html",
        user = user,
        user_published_products = user_published_products,
        total_rating = total_rating,
        count = count,
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        user_liked_products=get_user_liked_products(),
        products_in_cart = get_cart_products_number()
    )


@app.route("/reviews/<product_id>")
def all_reviews(product_id):
    product = products.find_one({"_id": ObjectId(product_id)})
    all_users_reviewed = []
    for rating in product['ratings']:
        user = users.find_one({"_id": rating['user_id']})
        all_users_reviewed.append(user)

    return render_template(
        "all-reviews.html",
        product = product,
        all_users_reviewed = all_users_reviewed,
        x="Account" if session.get("username") else "Login",
        page="account" if session.get("username") else "login",
        products_in_cart = get_cart_products_number()
    )









if __name__ == "__main__":
    app.run(debug=True)