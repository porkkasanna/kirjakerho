from flask import Flask
from flask import abort, flash, make_response, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from time import strftime, localtime

import markupsafe
import sqlite3
import config
import db
import clubs
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    bookclubs = clubs.get_clubs()
    return render_template("index.html", bookclubs=bookclubs)

@app.route("/search")
def search():
    query = request.args.get("query")
    results = clubs.search(query) if query else []
    return render_template("search.html", query=query, results=results)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if len(username) < 1:
        flash("Käyttäjätunnus on liian lyhyt", "error")
        return redirect("/register")
    
    if len(password1) < 1:
        flash("Salasana on liian lyhyt", "error")
        return redirect("/register")

    if password1 != password2:
        flash("Salasanat eivät täsmää", "error")
        return redirect("/register")
    
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("Käyttäjätunnus on varattu", "error")
        return redirect("/register")
    
    flash("Käyttäjätunnus luotiin onnistuneesti")
    return redirect("/login")

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    bookclubs = users.get_clubs(user_id)
    reviews = users.get_reviews(user_id)
    return render_template("user.html", user=user, bookclubs=bookclubs, reviews=reviews)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")
    
    if request.method == "POST":
        file = request.files["image"]
        user_id = session["user_id"]

        if not file.filename.endswith(".png"):
            flash("Väärä tiedostomuoto. Käytä PNG-muotoista kuvaa.", "error")
            return render_template("add_image.html")
        
        image = file.read()
        
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/add_image_default", methods=["POST"])
def add_image_default():
    require_login()

    user_id = session["user_id"]
    filename = "static/" + request.form["image"]

    with open(filename, "rb") as file:
        image = file.read()

    users.update_image(user_id, image)

    return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT password_hash FROM users WHERE username = ?"
        try:
            password_hash = db.query(sql, [username])[0][0]
        except:
            flash("Väärä käyttäjätunnus tai salasana", "error")
            return redirect("/login")

        if check_password_hash(password_hash, password):
            session["username"] = username
            sql = "SELECT id FROM users WHERE username = ?"
            user_id = db.query(sql, [username])[0][0]
            session["user_id"] = user_id
            return redirect("/")
        else:
            flash("Väärä käyttäjätunnus tai salasana", "error")
            return redirect("/login")

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")

@app.route("/create_club", methods=["POST", "GET"])
def create_club():
    require_login()

    if request.method == "GET":
        return render_template("create_club.html")

    if request.method == "POST":
        user_id = session["user_id"]
        title = request.form["title"]
        author = request.form["author"]
        deadline = request.form["deadline"]

        if not title or not author or len(title) > 50 or len(author) > 50:
            abort(403)

        try:
            club_id = clubs.add_club(user_id, title, author, deadline)
        except sqlite3.IntegrityError:
            abort(403)

        return redirect("/bookclub/" + str(club_id))

@app.route("/bookclub/<int:club_id>")
def show_club(club_id):
    bookclub = clubs.get_club(club_id)
    if not bookclub:
        abort(404)
    reviews = clubs.get_reviews(club_id)
    return render_template("show_club.html", bookclub=bookclub, reviews=reviews)

@app.route("/edit_club/<int:club_id>", methods=["GET", "POST"])
def edit_club(club_id):
    require_login()
    bookclub = clubs.get_club(club_id)

    if not bookclub:
        abort(404)
    if bookclub["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("edit_club.html", bookclub=bookclub)

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        deadline = request.form["deadline"]

        if not title or not author or len(title) > 50 or len(author) > 50:
            abort(403)

        clubs.update_club(club_id, title, author, deadline)
        return redirect("/bookclub/" + str(club_id))

@app.route("/remove_club/<int:club_id>", methods=["GET", "POST"])
def remove_club(club_id):
    require_login()
    bookclub = clubs.get_club(club_id)

    if not bookclub:
        abort(404)
    if bookclub["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_club.html", bookclub=bookclub)

    if request.method == "POST":
        if "remove" in request.form:
            clubs.remove_club(club_id)
            return redirect("/")
        else:
            return redirect("/bookclub/" + str(club_id))

@app.route("/new_review", methods=["POST"])
def new_review():
    require_login()
    stars = request.form["stars"]
    content = request.form["content"]
    club_id = request.form["club_id"]
    user_id = session["user_id"]
    sent_at = strftime("%d.%m.%Y, kello %H:%M", localtime())

    clubs.add_review(stars, content, club_id, user_id, sent_at)
    return redirect("/bookclub/" + str(club_id))

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    require_login()
    review = clubs.get_review(review_id)

    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    
    if request.method == "GET":
        return render_template("edit_review.html", review=review)
    
    if request.method == "POST":
        stars = request.form["stars"]
        content = request.form["content"]
        modified_at = strftime("%d.%m.%Y, kello %H:%M", localtime())

        if not stars or not content:
            abort(403)
        
        clubs.update_review(review_id, stars, content, modified_at)
        return redirect("/bookclub/" + str(review["club_id"]))

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    require_login()
    review = clubs.get_review(review_id)

    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        if "remove" in request.form:
            clubs.remove_review(review_id)
        return redirect("/bookclub/" + str(review["club_id"]))