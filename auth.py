import sqlite3
from datetime import datetime

from flask import (  # type: ignore[import]
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (  # type: ignore[import]
    generate_password_hash,
    check_password_hash
)

from database import DATABASE_PATH


auth = Blueprint("auth", __name__)


# ---------------------------------------
# Register
# ---------------------------------------
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Basic Validation
        if not full_name or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            connection.close()
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users
            (
                full_name,
                email,
                password,
                created_at
            )

            VALUES (?, ?, ?, ?)
        """,
        (
            full_name,
            email,
            hashed_password,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        connection.close()

        flash("Registration successful! Please login.", "success")

        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ---------------------------------------
# Login
# ---------------------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        connection.close()

        if user is None:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["id"]
        session["user_name"] = user["full_name"]

        flash("Login successful!", "success")

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ---------------------------------------
# Logout
# ---------------------------------------
@auth.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "info")

    return redirect(url_for("home"))