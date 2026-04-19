"""
Defines all HTTP API endpoints for the web application:
- Audio upload and processing pipeline
- Dashboard data retrieval

The main interface between the frontend and backend services.
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .services import get_user_by_username, create_user

main = Blueprint("main", __name__)


@main.route("/login", methods=["GET", "POST"])
def login():
    """
    GET: Render login page
    POST: Check credentials, if correct, then go to dashboard
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)
        if user and user.password == password:
            login_user(user)
            print("User logged in: %s", username)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

        flash("Invalid username or password.", "error")
        print("Failed login attempt for username: %s", username)

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    """
    Log out the user, go to login page
    """
    print("User logged out: %s", current_user.username)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


@main.route("/register", methods=["GET", "POST"])
def register():
    """
    GET: Render register page
    POST: Create new user, redirect to login
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                create_user(username, password)
                flash("Account created. Please log in.", "success")
                return redirect(url_for("main.login"))
            except ValueError as exc:
                flash(str(exc), "error")

    return render_template("register.html")


@main.route("/upload", methods=["POST"])
@login_required
def upload_audio():
    """
    Receives audio file from frontend, sends it to ML service,
    and returns transcription result.
    """
    file = request.files.get("audio")

    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        transcript = transcribe_audio(file)
    except RequestException as e:
        return jsonify({"error": str(e)}), 500

    return (
        jsonify(
            {
                "transcript": transcript,
            }
        ),
        200,
    )
    # maybe more fields later. talk with frontend and ml-client.



@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Retrieves stored speech analysis records.
    """
    return jsonify({"message": "Placeholder!!!"}), 200
