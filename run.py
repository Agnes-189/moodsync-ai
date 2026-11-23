from app import create_app, db
from app.models.user import User
from app.models.music import Category, Song, Favorite
from app.services.seed import seed_database

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Category': Category, 'Song': Song, 'Favorite': Favorite}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run()