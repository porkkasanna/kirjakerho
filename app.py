import sqlite3
import secrets
import math
import re
import time

from flask import Flask
from flask import abort, flash, g, make_response, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import markupsafe

import config
import db
import clubs
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        forbidden()

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        forbidden()

def forbidden():
    abort(403)

def not_found():
    abort(404)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    club_count = clubs.club_count()
    page_count = math.ceil(club_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    bookclubs = clubs.get_clubs(page, page_size)
    now = time.strftime("%Y-%m-%d", time.localtime())
    return render_template("index.html", bookclubs=bookclubs, page=page,
                           page_count=page_count, now=now)

@app.route("/search")
def search():
    query = request.args.get("query")
    query_from = request.args.get("query_from")
    page = request.args.get("page")

    if not page:
        page = 1

    page = int(page)
    page_size = 10
    query_count = clubs.query_count(query, query_from)
    page_count = math.ceil(query_count / page_size)
    page_count = max(page_count, 1)

    if page < 1 or page > page_count:
        return redirect("/search")

    results = clubs.search(query, query_from, page, page_size) if query else []
    return render_template("search.html", query=query, q_from=query_from,
                           query_count=query_count, results=results, page=page,
                           page_count=page_count)

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
        users.add_user(username, password_hash)
    except sqlite3.IntegrityError:
        flash("Käyttäjätunnus on varattu", "error")
        return redirect("/register")

    flash("Käyttäjätunnus luotiin onnistuneesti")
    return redirect("/login")

@app.route("/remove_user/<int:user_id>", methods=["GET", "POST"])
def remove_user(user_id):
    require_login()
    user = users.get_user(user_id)

    if not user:
        not_found()
    if user["id"] != session["user_id"]:
        forbidden()

    if request.method == "GET":
        return render_template("remove_user.html", user=user)

    if request.method == "POST":
        require_login()
        check_csrf()
        if "remove" in request.form:
            users.remove_user(user_id)
            return redirect("/logout")

    return redirect("/user/" + str(user_id))

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        not_found()
    bookclubs = users.get_clubs(user_id)
    club_count = users.club_count(user_id)
    reviews = users.get_reviews(user_id)
    review_count = users.review_count(user_id)
    now = time.strftime("%Y-%m-%d", time.localtime())
    return render_template("user.html", user=user, bookclubs=bookclubs,
                           club_count=club_count, reviews=reviews,
                           review_count=review_count, now=now)

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        require_login()
        check_csrf()
        file = request.files["image"]
        user_id = session["user_id"]

        if not file:
            flash("Tiedosto puuttuu", "error")
            return render_template("add_image.html")

        if not file.filename.endswith(".png"):
            flash("Väärä tiedostomuoto. Käytä PNG-muotoista kuvaa.", "error")
            return render_template("add_image.html")

        image = file.read()
        users.update_image(user_id, image)

    return redirect("/user/" + str(user_id))

@app.route("/add_image_default", methods=["POST"])
def add_image_default():
    require_login()
    check_csrf()
    user_id = session["user_id"]
    filename = "static/" + request.form["image"]
    pattern = r"^static/image((0[1-9])|(1[0-9])|20)\.png$"
    filename_matches = re.fullmatch(pattern, filename)

    if filename_matches:
        with open(filename, "rb") as file:
            image = file.read()

        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

    flash("Tiedostoa ei löydy", "error")
    return redirect("/add_image")

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        not_found()

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
        user_id = users.login(username, password)

        if user_id:
            session["username"] = username
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            flash("Sisäänkirjautuminen onnistui", "message")
            return redirect("/")

        flash("Väärä käyttäjätunnus tai salasana", "error")
        return redirect("/login")

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    del session["csrf_token"]
    return redirect("/")

@app.route("/create_club", methods=["POST", "GET"])
def create_club():
    require_login()

    if request.method == "GET":
        all_classes = clubs.get_all_classes()
        return render_template("create_club.html", classes=all_classes)

    if request.method == "POST":
        require_login()
        check_csrf()
        user_id = session["user_id"]
        title = request.form["title"]
        author = request.form["author"]
        deadline = request.form["deadline"]

        if not title or not author or len(title) > 50 or len(author) > 50:
            forbidden()

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                parts = entry.split(":")
                classes.append((parts[0], parts[1]))

        try:
            club_id = clubs.add_club(user_id, title, author, deadline, classes)
        except sqlite3.IntegrityError:
            forbidden()

        return redirect("/bookclub/" + str(club_id))

@app.route("/bookclub/<int:club_id>")
def show_club(club_id):
    bookclub = clubs.get_club(club_id)
    if not bookclub:
        not_found()

    pattern = r"(\d+)-(\d+)-(\d+)"
    replacement = r"\3.\2.\1."
    deadline = re.sub(pattern, replacement, bookclub["deadline"])

    review_count = clubs.review_count(club_id)
    reviews = clubs.get_reviews(club_id)
    classes = clubs.get_classes(club_id)
    return render_template("show_club.html", bookclub=bookclub, deadline=deadline,
                           reviews=reviews, review_count=review_count,
                           classes=classes)

@app.route("/user/bookclubs/<int:user_id>")
@app.route("/user/bookclubs/<int:user_id>/page/<int:page>")
def show_user_clubs(user_id, page=1):
    page_size = 10
    club_count = users.club_count(user_id)
    page_count = math.ceil(club_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/user/bookclubs/" + str(user_id) + "/page/1")
    if page > page_count:
        return redirect("/user/bookclubs/" + str(user_id) +
                        "/page/" + str(page_count))

    user = users.get_user(user_id)
    bookclubs = users.get_clubs(user_id, page, page_size)
    now = time.strftime("%Y-%m-%d", time.localtime())
    return render_template("user_clubs.html", bookclubs=bookclubs, user=user,
                           page=page, page_count=page_count, now=now)

@app.route("/edit_club/<int:club_id>", methods=["GET", "POST"])
def edit_club(club_id):
    require_login()
    bookclub = clubs.get_club(club_id)
    all_classes = clubs.get_all_classes()
    club_classes = clubs.get_classes(club_id)

    if not bookclub:
        not_found()
    if bookclub["user_id"] != session["user_id"]:
        forbidden()

    if request.method == "GET":
        return render_template("edit_club.html", bookclub=bookclub,
                               all_classes=all_classes, classes=club_classes)

    if request.method == "POST":
        require_login()
        check_csrf()
        title = request.form["title"]
        author = request.form["author"]
        deadline = request.form["deadline"]

        if not title or not author:
            forbidden()
        if len(title) > 50 or len(author) > 50:
            forbidden()
        if not deadline:
            deadline = bookclub["deadline"]

        classes = []
        for entry in request.form.getlist("classes"):
            if entry:
                parts = entry.split(":")
                classes.append((parts[0], parts[1]))

        clubs.update_club(club_id, title, author, deadline, classes)
        return redirect("/bookclub/" + str(club_id))

@app.route("/remove_club/<int:club_id>", methods=["GET", "POST"])
def remove_club(club_id):
    require_login()
    bookclub = clubs.get_club(club_id)

    if not bookclub:
        not_found()
    if bookclub["user_id"] != session["user_id"]:
        forbidden()

    if request.method == "GET":
        return render_template("remove_club.html", bookclub=bookclub)

    if request.method == "POST":
        require_login()
        check_csrf()
        if "remove" in request.form:
            clubs.remove_club(club_id)
            return redirect("/")

        return redirect("/bookclub/" + str(club_id))

@app.route("/new_review", methods=["POST"])
def new_review():
    require_login()
    closed = request.form["closed"]
    if closed == 1:
        forbidden()

    stars = request.form["stars"]
    content = request.form["content"]
    club_id = request.form["club_id"]
    user_id = session["user_id"]
    sent_at = time.strftime("%d.%m.%Y, kello %H:%M", time.localtime())

    clubs.add_review(stars, content, club_id, user_id, sent_at)
    return redirect("/bookclub/" + str(club_id))

@app.route("/bookclub/reviews/<int:club_id>")
@app.route("/bookclub/reviews/<int:club_id>/page/<int:page>")
def show_reviews(club_id, page=1):
    page_size = 10
    review_count = clubs.review_count(club_id)
    page_count = math.ceil(review_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/bookclub/reviews/" + str(club_id) + "/page/1")
    if page > page_count:
        return redirect("/bookclub/reviews/" + str(club_id) +
                        "/page/" + str(page_count))

    bookclub = clubs.get_club(club_id)
    reviews = clubs.get_reviews(club_id, page, page_size)
    return render_template("reviews.html", reviews=reviews, bookclub=bookclub,
                           page=page, page_count=page_count)

@app.route("/user/reviews/<int:user_id>")
@app.route("/user/reviews/<int:user_id>/page/<int:page>")
def show_user_reviews(user_id, page=1):
    page_size = 10
    review_count = users.review_count(user_id)
    page_count = math.ceil(review_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/user/reviews/" + str(user_id) + "/page/1")
    if page > page_count:
        return redirect("/user/reviews/" + str(user_id) +
                        "/page/" + str(page_count))

    user = users.get_user(user_id)
    reviews = users.get_reviews(user_id, page, page_size)
    return render_template("user_reviews.html", reviews=reviews, user=user,
                           page=page, page_count=page_count)

@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    require_login()
    review = clubs.get_review(review_id)

    if not review:
        not_found()
    if review["user_id"] != session["user_id"]:
        forbidden()

    if request.method == "GET":
        return render_template("edit_review.html", review=review)

    if request.method == "POST":
        require_login()
        check_csrf()
        stars = request.form["stars"]
        content = request.form["content"]
        modified_at = time.strftime("%d.%m.%Y, kello %H:%M", time.localtime())

        if not stars or not content:
            forbidden()
        if "back" not in request.form:
            clubs.update_review(review_id, stars, content, modified_at)

        return redirect("/bookclub/" + str(review["club_id"]))

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    require_login()
    review = clubs.get_review(review_id)

    if not review:
        not_found()
    if review["user_id"] != session["user_id"]:
        forbidden()

    if request.method == "GET":
        return render_template("remove_review.html", review=review)

    if request.method == "POST":
        require_login()
        check_csrf()
        if "remove" in request.form:
            clubs.remove_review(review_id)
        return redirect("/bookclub/" + str(review["club_id"]))
