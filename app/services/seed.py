from app import db
from app.models.music import Category, Song

def seed_database():
    # Only seed if categories don't exist yet
    if Category.query.first():
        return

    categories_data = [
        {"name": "Afrobeat", "description": "Afrobeats hits, Nigerian Afrobeats, Afro-fusion, African hits."},
        {"name": "Kenyan Music", "description": "Kenyan R&B, Gengetone, Kenyan hip-hop, Kenyan hits."},
        {"name": "Amapiano", "description": "Soulful Amapiano, private school piano, log-drum sounds."},
        {"name": "R&B", "description": "Kenyan R&B, African R&B, international R&B, slow jams."},
        {"name": "DJ Mixes", "description": "Afrobeat mixes, Amapiano mixes, Kenyan mixes, party mixes."},
        {"name": "Chill & Relax", "description": "Acoustic, lo-fi, instrumentals, ambient."}
    ]

    category_map = {}
    for cat in categories_data:
        new_cat = Category(name=cat["name"], description=cat["description"])
        db.session.add(new_cat)
        db.session.flush() # Get the ID before committing
        category_map[cat["name"]] = new_cat.id

    demo_songs = [
        {
            "title": "[DEMO] Lagos Midnight Groove",
            "artist": "Demo Artist Collective",
            "genre": "Afro-fusion",
            "song_type": "single",
            "duration": "03:24",
            "cover_art": "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?w=400&q=80",
            "external_url": "https://open.spotify.com",
            "category_id": category_map["Afrobeat"]
        },
        {
            "title": "[DEMO] Nairobi Rain & Soul",
            "artist": "254 Acoustic Sessions",
            "genre": "Kenyan R&B",
            "song_type": "single",
            "duration": "04:05",
            "cover_art": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400&q=80",
            "external_url": "https://www.youtube.com",
            "category_id": category_map["Kenyan Music"]
        },
        {
            "title": "[DEMO] Pretoria Log-Drum Sunset",
            "artist": "Piano Kings Demo",
            "genre": "Private School Piano",
            "song_type": "single",
            "duration": "06:15",
            "cover_art": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=400&q=80",
            "external_url": "https://soundcloud.com",
            "category_id": category_map["Amapiano"]
        },
        {
            "title": "[DEMO] Weekend Afro-Piano Club Mix Vol. 1",
            "artist": "DJ MoodSync",
            "genre": "Amapiano Mixes",
            "song_type": "dj_mix",
            "duration": "45:00",
            "cover_art": "https://images.unsplash.com/photo-1571266028243-e4733b0f0bb0?w=400&q=80",
            "external_url": "https://www.mixcloud.com",
            "category_id": category_map["DJ Mixes"]
        },
        {
            "title": "[DEMO] Velvet Slow Jams",
            "artist": "Midnight Echo",
            "genre": "Slow Jams",
            "song_type": "playlist",
            "duration": "32:10",
            "cover_art": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=400&q=80",
            "external_url": "https://open.spotify.com",
            "category_id": category_map["R&B"]
        },
        {
            "title": "[DEMO] Lo-Fi Study Beats",
            "artist": "Chill Wave",
            "genre": "Lo-fi",
            "song_type": "single",
            "duration": "02:48",
            "cover_art": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=400&q=80",
            "external_url": "https://www.youtube.com",
            "category_id": category_map["Chill & Relax"]
        }
    ]

    for song in demo_songs:
        db.session.add(Song(**song))

    db.session.commit()