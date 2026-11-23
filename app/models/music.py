from app import db

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    
    songs = db.relationship('Song', backref='category', lazy='dynamic')

class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    genre = db.Column(db.String(64))
    song_type = db.Column(db.String(64)) # e.g., single, playlist, dj_mix
    duration = db.Column(db.String(16))
    cover_art = db.Column(db.String(256))
    external_url = db.Column(db.String(256))
    
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    favorited_by = db.relationship('Favorite', backref='song', lazy='dynamic')

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'song_id', name='_user_song_uc'),)