from flask import Blueprint, render_template, url_for, request, flash, redirect, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Note
from . import db
from datetime import datetime
import musicbrainzngs

# set blueprint
views = Blueprint("views", __name__)

# setting up musicbrainz for album and artist information
musicbrainzngs.set_useragent(
    "StrayKids", 
    "1.0", 
    "aaronclh@outlook.com"
)

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
    try:
        artist_id = "142b343d-bf5a-428c-a64f-6d1a7566bbe9"
        songs_data = []
        offset = 0
        limit = 100

        while True:
            print(f"Fetching releases from offset: {offset}")
            result = musicbrainzngs.browse_releases(
                artist=artist_id,
                includes=["recordings", "artist-credits", "media", "release-groups"],
                release_type=["album", "ep", "single"],
                limit=limit,
                offset=offset
            )
            
            if 'release-list' not in result or not result['release-list']:
                break
                
            releases = result['release-list']
            print(f"Found {len(releases)} releases in this batch")
            
            for release in releases:
                if "medium-list" in release:
                    for medium in release["medium-list"]:
                        if "track-list" in medium:
                            for track in medium["track-list"]:
                                try:
                                    # Convert milliseconds to minutes:seconds if available
                                    duration = track.get("length", "N/A")
                                    if duration != "N/A":
                                        duration = int(duration)
                                        minutes = duration // (1000 * 60)
                                        seconds = (duration % (1000 * 60)) // 1000
                                        duration = f"{minutes}:{seconds:02d}"

                                    song = {
                                        "title": track.get("recording", {}).get("title") or track.get("title", "Unknown Title"),
                                        "album": release.get("title", "Unknown Album"),
                                        "date": release.get("date", "N/A"),
                                        "duration": duration
                                    }
                                    songs_data.append(song)
                                except Exception as track_error:
                                    print(f"Error processing track: {track_error}")
                                    continue
            
            if len(releases) < limit:
                break
                
            offset += limit

        # Sort songs by date (newest first)
        songs_data.sort(key=lambda x: x["date"] if x["date"] != "N/A" else "0000", reverse=True)
        
        print(f"Total songs found: {len(songs_data)}")
        
        return render_template("songs.html", user=current_user, songs=songs_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template("songs.html", user=current_user, songs=[], error=str(e))


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