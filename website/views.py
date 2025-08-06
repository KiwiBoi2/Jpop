from flask import Blueprint, render_template, url_for, request, flash, redirect, jsonify
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
    return render_template("home.html", user=current_user)


# albums route
@views.route("/albums")
def albums():
    return render_template("albums.html", user=current_user)

# artists route
@views.route("/artists")
def artists():
    return render_template("artists.html", user=current_user)

# songs route
@views.route("/songs")
def songs():
    return render_template("songs.html", user=current_user)

# contact route
@views.route("/contact", methods=["POST", "GET", "DELETE"])
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

@views.route("/delete-note/<int:note_id>", methods=["POST"])  
@login_required
def delete_note(note_id):
    note=Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        db.session.delete(note)
        db.session.commit()
        flash("Comment deleted!", category="success")
    else:
        flash("You do not have permission to delete this comment.", category="error")
    return redirect(url_for("views.contact"))

@views.route("/edit-note/<int:note_id>", methods=["POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get(note_id)
    if note and note.user_id == current_user.id:
        content = request.json.get('content')
        if content and len(content.strip()) > 0:
            note.data = content
            db.session.commit()
            flash("Comment updated!", category="success")
            return jsonify({"success": True})
    return jsonify({"success": False}), 400
