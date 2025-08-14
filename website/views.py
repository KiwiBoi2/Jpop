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
@views.route("/members")
def members():
    return render_template("members.html", user=current_user)

# songs route
@views.route("/songs")
def songs():
    return render_template("songs.html", user=current_user)

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

@views.route("/delete-note/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@views.route("/edit-note/<int:note_id>", methods=["POST"])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    content = request.json.get('content')
    if not content or len(content.strip()) == 0:
        return jsonify({"error": "Content cannot be empty"}), 400
    
    try:
        note.data = content
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500