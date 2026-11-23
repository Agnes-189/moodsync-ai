from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from app.models.music import Category, Song, Favorite

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def home():
    categories = Category.query.all()
    songs = Song.query.all()
    user_fav_ids = {fav.song_id for fav in current_user.favorites.all()}
    return render_template(
        'home.html', 
        title='Discover', 
        categories=categories, 
        songs=songs, 
        user_fav_ids=user_fav_ids,
        active_category=None
    )

@main_bp.route('/category/<int:category_id>')
@login_required
def category_filter(category_id):
    categories = Category.query.all()
    selected_category = Category.query.get_or_404(category_id)
    songs = Song.query.filter_by(category_id=category_id).all()
    user_fav_ids = {fav.song_id for fav in current_user.favorites.all()}
    return render_template(
        'home.html', 
        title=selected_category.name, 
        categories=categories, 
        songs=songs, 
        user_fav_ids=user_fav_ids,
        active_category=selected_category
    )

@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    categories = Category.query.all()
    user_fav_ids = {fav.song_id for fav in current_user.favorites.all()}
    
    if query:
        search_term = f"%{query}%"
        songs = Song.query.filter(
            or_(
                Song.title.ilike(search_term),
                Song.artist.ilike(search_term),
                Song.genre.ilike(search_term)
            )
        ).all()
    else:
        songs = Song.query.all()
        
    return render_template(
        'home.html', 
        title=f'Search: {query}' if query else 'Discover', 
        categories=categories, 
        songs=songs, 
        user_fav_ids=user_fav_ids,
        search_query=query
    )

@main_bp.route('/favorites')
@login_required
def favorites():
    categories = Category.query.all()
    user_favs = current_user.favorites.all()
    songs = [fav.song for fav in user_favs]
    user_fav_ids = {song.id for song in songs}
    return render_template(
        'home.html', 
        title='Your Library', 
        categories=categories, 
        songs=songs, 
        user_fav_ids=user_fav_ids,
        is_favorites_page=True
    )

@main_bp.route('/favorite/<int:song_id>', methods=['POST'])
@login_required
def toggle_favorite(song_id):
    song = Song.query.get_or_404(song_id)
    existing_fav = Favorite.query.filter_by(user_id=current_user.id, song_id=song.id).first()
    
    if existing_fav:
        db.session.delete(existing_fav)
        db.session.commit()
        flash(f'Removed "{song.title}" from your favourites.', 'info')
    else:
        new_fav = Favorite(user_id=current_user.id, song_id=song.id)
        db.session.add(new_fav)
        db.session.commit()
        flash(f'Added "{song.title}" to your favourites!', 'success')
        
    return redirect(request.referrer or url_for('main.home'))