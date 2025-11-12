from flask import Flask
from flask import abort, flash, render_template, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import sqlite3
import config
import db
import clubs

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

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
    return render_template("show_club.html", bookclub=bookclub)

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