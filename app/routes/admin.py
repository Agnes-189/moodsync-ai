import os
import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.models.music import Category, Song

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a'}

def _allowed_audio(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AUDIO_EXTENSIONS

@admin_bp.route('/catalog', methods=['GET', 'POST'])
@login_required
def catalog_manager():
    categories = Category.query.all()

    if request.method == 'POST':
        action = request.form.get('action', 'single')

        if action == 'csv':
            csv_file = request.files.get('csv_file')
            if not csv_file or not csv_file.filename.endswith('.csv'):
                flash('Please upload a valid .csv file.', 'warning')
                return redirect(url_for('admin.catalog_manager'))

            stream = io.StringIO(csv_file.stream.read().decode('UTF8'), newline=None)
            reader = csv.DictReader(stream)
            added_count = 0

            for row in reader:
                cat_name = row.get('category', '').strip()
                category = Category.query.filter_by(name=cat_name).first()
                if not category and cat_name:
                    category = Category(name=cat_name, description=f"{cat_name} collection")
                    db.session.add(category)
                    db.session.flush()

                if category and row.get('title') and row.get('artist'):
                    song = Song(
                        title=row['title'].strip(),
                        artist=row['artist'].strip(),
                        genre=row.get('genre', cat_name).strip(),
                        song_type=row.get('song_type', 'track').strip(),
                        duration=row.get('duration', '').strip(),
                        cover_art=row.get('cover_art', '').strip() or 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500',
                        audio_file=row.get('audio_file', '').strip() or None,
                        external_url=row.get('external_url', '').strip() or None,
                        provider=row.get('provider', 'MoodSync Stream').strip(),
                        mood_tags=row.get('mood_tags', '').strip(),
                        category_id=category.id
                    )
                    db.session.add(song)
                    added_count += 1

            db.session.commit()
            flash(f'Successfully imported {added_count} tracks from CSV!', 'success')
            return redirect(url_for('admin.catalog_manager'))

        # Single track creation with optional MP3 file upload
        title = request.form.get('title', '').strip()
        artist = request.form.get('artist', '').strip()
        genre = request.form.get('genre', '').strip()
        song_type = request.form.get('song_type', 'track').strip()
        duration = request.form.get('duration', '').strip()
        cover_art = request.form.get('cover_art', '').strip() or 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500'
        external_url = request.form.get('external_url', '').strip() or None
        provider = request.form.get('provider', 'MoodSync Stream').strip()
        mood_tags = request.form.get('mood_tags', '').strip()
        category_id = request.form.get('category_id', type=int)

        audio_rel_path = None
        uploaded_audio = request.files.get('audio_file')
        if uploaded_audio and uploaded_audio.filename:
            if _allowed_audio(uploaded_audio.filename):
                safe_name = secure_filename(uploaded_audio.filename)
                audio_dir = os.path.join(current_app.root_path, 'static', 'audio')
                os.makedirs(audio_dir, exist_ok=True)
                uploaded_audio.save(os.path.join(audio_dir, safe_name))
                audio_rel_path = f"audio/{safe_name}"
            else:
                flash('Unsupported audio format. Please upload MP3, WAV, OGG, or M4A.', 'warning')
                return redirect(url_for('admin.catalog_manager'))

        if title and artist and category_id:
            new_song = Song(
                title=title,
                artist=artist,
                genre=genre or 'General',
                song_type=song_type,
                duration=duration,
                cover_art=cover_art,
                audio_file=audio_rel_path,
                external_url=external_url,
                provider=provider,
                mood_tags=mood_tags,
                category_id=category_id
            )
            db.session.add(new_song)
            db.session.commit()
            flash(f'Added "{title}" to MoodSync AI catalog!', 'success')
        else:
            flash('Title, Artist, and Category are required.', 'warning')

        return redirect(url_for('admin.catalog_manager'))

    songs = Song.query.order_by(Song.id.desc()).all()
    return render_template('admin.html', title='Catalog Manager', categories=categories, songs=songs)

@admin_bp.route('/delete-song/<int:song_id>', methods=['POST'])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    db.session.delete(song)
    db.session.commit()
    flash(f'Deleted "{song.title}" from catalog.', 'info')
    return redirect(url_for('admin.catalog_manager'))