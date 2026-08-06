from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

import models

auth_bp = Blueprint("auth", __name__)
login_manager = LoginManager()
login_manager.login_view = "auth.login"


class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.name = user_doc["name"]
        self.email = user_doc["email"]


@login_manager.user_loader
def load_user(user_id):
    user_doc = models.find_user_by_id(user_id)
    return User(user_doc) if user_doc else None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if models.find_user_by_email(email):
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")

        password_hash = generate_password_hash(password)
        user_id = models.create_user(name, email, password_hash)
        login_user(User(models.find_user_by_id(user_id)))
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user_doc = models.find_user_by_email(email)
        if user_doc and check_password_hash(user_doc["password_hash"], password):
            login_user(User(user_doc))
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
