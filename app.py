from flask import Flask, render_template, url_for, request


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("homepage.html")

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

    return render_template("submit.html")





if __name__ == "__main__":
    app.run(debug=True)