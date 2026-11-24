from app import create_app, db

# 1. Import music models FIRST so the 'song' table exists in memory
from app.models.music import Category, Song, Favorite

# 2. THEN import user models which rely on the song table
from app.models.user import User, MoodEntry, RecommendationFeedback

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")