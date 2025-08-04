from flask import Blueprint, render_template, url_for, request, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Note
from . import db
from datetime import datetime

# set blueprint
views = Blueprint("views", __name__)


# default/home route
@views.route("/")
@views.route("/home")
@views.route("/index")
def home():
    return render_template("home.html")


# albums route
@views.route("/albums")
def albums():
    return render_template("albums.html")

# artists route
@views.route("/artists")
def artists():
    return render_template("artists.html")

# songs route
@views.route("/songs")
def songs():
    return render_template("songs.html")

# contact route
@views.route("/contact", methods=["POST", "GET"])
@login_required
def contact():
    if request.method == "POST":
        note = request.form.get("note")
        if len(note) < 1:
            flash("Comment field cannot be empty!", category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id, date=datetime.now())
            db.session.add(new_note)
            db.session.commit()
            flash("Comment Added!", category="success")
    
    return render_template("contact.html", user=current_user)