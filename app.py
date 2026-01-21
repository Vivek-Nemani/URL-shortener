from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL") or "sqlite:///urls.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(9), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column("long", db.String(), nullable=False)
    short = db.Column("short", db.String(10), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, long, short, user_id):
        self.long = long
        self.short = short
        self.user_id = user_id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        random_letters = random.choices(letters, k=6)
        random_string = "".join(random_letters)
        existing = Urls.query.filter_by(short=random_string).first()
        if not existing:
            return random_string


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 5 or len(username) > 9:
            flash("Username must be between 5 to 9 characters long", "danger")
            return render_template("signup.html", username=username)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("This username already exists. Please choose another.", "danger")
            return render_template("signup.html", username=username)

        if not password:
            flash("Password is required.", "danger")
            return render_template("signup.html", username=username)

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created. Welcome!", "success")
        return redirect(url_for("home"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("home"))

        flash("Invalid username or password.", "danger")
        return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/", methods=["POST", "GET"])
@login_required
def home():
    if request.method == "POST":
        url_received = request.form["nm"].strip()
        found_url = Urls.query.filter_by(
            long=url_received, user_id=current_user.id
        ).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))

        short_url = shorten_url()
        new_url = Urls(url_received, short_url, current_user.id)
        db.session.add(new_url)
        db.session.commit()
        return redirect(url_for("display_short_url", url=short_url))

    user_urls = Urls.query.filter_by(user_id=current_user.id).all()
    return render_template("url_page.html", urls=user_urls)

@app.route("/<short_url>")
def redirection(short_url):
    long_url = Urls.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    return "<h1>Url doesnt exist</h1>"


@app.route("/display/<url>")
@login_required
def display_short_url(url):
    full_short_url = request.url_root.rstrip("/") + "/" + url
    return render_template(
        "shorturl.html", short_url_display=url, full_short_url=full_short_url
    )


@app.route("/all_urls")
@login_required
def display_all():
    return render_template(
        "all_urls.html", vals=Urls.query.filter_by(user_id=current_user.id).all()
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
