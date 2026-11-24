import os
import re
import joblib
from sqlalchemy import or_
from app import db
from app.models.music import Song, Category
from app.models.user import MoodEntry, RecommendationFeedback

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, 'saved_models', 'mood_classifier.joblib')

MOOD_DIRECTIONS = {
    "happy": {
        "categories": ["Afrobeat", "Amapiano", "Dancehall"],
        "tags": ["upbeat", "happy", "uplifting", "joyful", "party"],
        "description": "Upbeat Afrobeat, Amapiano, and Dancehall rhythms to match your good vibes."
    },
    "relaxed": {
        "categories": ["Kenyan Music", "Chill & Relax", "R&B"],
        "tags": ["relaxed", "mellow", "chill", "acoustic", "lo-fi", "ambient"],
        "description": "Smooth Kenyan R&B, acoustic melodies, and chill tracks to help you unwind."
    },
    "heartbroken": {
        "categories": ["R&B", "Love & Romance"],
        "tags": ["heartbreak", "slow", "mellow", "emotional", "reflective"],
        "description": "Soulful slow jams and reflective R&B playlists for healing and reflection."
    },
    "energetic": {
        "categories": ["DJ Mixes", "Dancehall", "Amapiano"],
        "tags": ["energetic", "upbeat", "party", "hype", "log-drum"],
        "description": "High-energy DJ mixes, Dancehall, and heavy Amapiano log-drums to keep you moving."
    },
    "stressed": {
        "categories": ["Chill & Relax", "R&B", "Gospel"],
        "tags": ["chill", "mellow", "relaxed", "soothing", "acoustic"],
        "description": "Soothing instrumentals, gospel, and mellow R&B to help you decompress."
    },
    "romantic": {
        "categories": ["Love & Romance", "Kenyan Music", "R&B"],
        "tags": ["romantic", "love", "mellow", "sweet", "slow"],
        "description": "Sweet love songs and Kenyan R&B crafted for romantic moments."
    }
}

def _clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text)

def _rank_songs_for_user(songs, user):
    """Boost songs matching the user's favourite genres/categories and positive feedback."""
    if not user or not user.is_authenticated:
        return songs

    fav_songs = [fav.song for fav in user.favorites.all() if fav.song]
    fav_genres = {s.genre.lower() for s in fav_songs if s.genre}
    fav_cat_ids = {s.category_id for s in fav_songs if s.category_id}

    helpful_ids = {
        fb.song_id for fb in user.feedbacks.filter_by(is_helpful=True).all()
    }
    unhelpful_ids = {
        fb.song_id for fb in user.feedbacks.filter_by(is_helpful=False).all()
    }

    def score_song(song):
        score = 0
        if song.genre and song.genre.lower() in fav_genres:
            score += 2
        if song.category_id in fav_cat_ids:
            score += 2
        if song.id in helpful_ids:
            score += 3
        if song.id in unhelpful_ids:
            score -= 5
        return score

    return sorted(songs, key=score_song, reverse=True)

def predict_mood_and_recommend(user_text, user=None):
    if not os.path.exists(MODEL_PATH):
        return None

    artifact = joblib.load(MODEL_PATH)
    vectorizer = artifact["vectorizer"]
    classifier = artifact["classifier"]

    cleaned = _clean_text(user_text)
    vec = vectorizer.transform([cleaned])
    predicted_mood = classifier.predict(vec)[0]

    confidence = None
    if hasattr(classifier, "predict_proba"):
        probs = classifier.predict_proba(vec)[0]
        confidence = round(float(max(probs)) * 100, 1)

    # Save entry to user's Mood Journal
    entry_id = None
    if user and user.is_authenticated:
        entry = MoodEntry(
            user_id=user.id,
            mood_text=user_text,
            predicted_mood=predicted_mood,
            confidence_score=confidence
        )
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id

    direction = MOOD_DIRECTIONS.get(predicted_mood, MOOD_DIRECTIONS["happy"])

    filters = [Song.mood_tags.ilike(f"%{tag}%") for tag in direction["tags"]]
    matching_cats = Category.query.filter(Category.name.in_(direction["categories"])).all()
    if matching_cats:
        cat_ids = [c.id for c in matching_cats]
        filters.append(Song.category_id.in_(cat_ids))

    candidate_songs = Song.query.filter(or_(*filters)).all()
    ranked_songs = _rank_songs_for_user(candidate_songs, user)

    return {
        "entry_id": entry_id,
        "mood": predicted_mood,
        "confidence": confidence,
        "explanation": direction["description"],
        "matched_categories": direction["categories"],
        "songs": ranked_songs
    }