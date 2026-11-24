import csv
import os
from app import db
from app.models.music import Category, Song

def import_catalog_from_csv(csv_filename='catalog.csv'):
    """Imports verified catalog records from a CSV file in music_data/"""
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    filepath = os.path.join(base_dir, 'music_data', csv_filename)
    
    if not os.path.exists(filepath):
        print(f"Error: Could not find {filepath}")
        return False

    imported_count = 0
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Check if song already exists to prevent duplicates
            if Song.query.filter_by(external_url=row['external_url']).first():
                continue
                
            # Find the matching category
            category = Category.query.filter_by(name=row['category_name']).first()
            if not category:
                print(f"Warning: Category '{row['category_name']}' not found. Skipping track.")
                continue

            new_song = Song(
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                song_type=row['song_type'],
                duration=row.get('duration', ''),
                cover_art=row['cover_art'],
                external_url=row['external_url'],
                provider=row.get('provider', 'Unknown'),
                is_verified=row.get('is_verified', 'True').lower() == 'true',
                mood_tags=row.get('mood_tags', ''),
                category_id=category.id
            )
            db.session.add(new_song)
            imported_count += 1
            
    db.session.commit()
    print(f"Successfully imported {imported_count} tracks from {csv_filename}!")
    return True