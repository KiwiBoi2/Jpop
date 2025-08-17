from flask import Blueprint, render_template, url_for, request, flash, redirect, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Note
from . import db
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# set blueprint
views = Blueprint("views", __name__)

# setting up Spotify API credentials
SPOTIFY_CLIENT_ID = "77a4da10d3ad41b9adc3d504c339e0eb"
SPOTIFY_CLIENT_SECRET = "c493e81ce8744f8b9815e585348c3ce7"

# init spotify client
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
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
        # stray kids spotify artist id
        artist_id = "2dIgFjalVxs4ThymZ67YCE"
        songs_data = []
        
        # get all albums
        albums = []
        album_types = ['album','single','appears_on']
        
        for album_type in album_types:
            results = spotify.artist_albums(artist_id, album_type=album_type)
            albums.extend(results['items'])
            
            while results['next']:
                results = spotify.next(results)
                albums.extend(results['items'])
        
        print(f"Found {len(albums)} albums for artist {artist_id}")

        # get all songs
        for album in albums:
            tracks = spotify.album_tracks(album['id'])
            
            for track in tracks['items']:
                # check main artist
                if any(artist['id'] == artist_id for artist in track['artists']):
                    duration_ms = track['duration_ms']
                    minutes = duration_ms // (1000 * 60)
                    seconds = (duration_ms % (1000 * 60)) // 1000
                    
                    song = {
                        "title": track['name'],
                        "album": album['name'],
                        "date": album['release_date'],
                        "duration": f"{minutes}:{seconds:02d}",
                        "preview_url": track['preview_url'],
                        "spotify_url": track['external_urls']['spotify']
                    }
                    songs_data.append(song)
        
            # Sort songs by date (newest first)
        songs_data.sort(key=lambda x: x["date"], reverse=True)
        
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