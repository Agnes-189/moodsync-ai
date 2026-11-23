import pytest
from app import create_app, db
from app.config import Config
from app.models.user import User
from app.models.music import Category, Song, Favorite

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed test category and song
            cat = Category(name='Afrobeat', description='Test category')
            db.session.add(cat)
            db.session.flush()
            song = Song(
                title='Test Track',
                artist='Test Artist',
                genre='Afro-fusion',
                category_id=cat.id,
                external_url='https://example.com'
            )
            db.session.add(song)
            db.session.commit()
            yield client
            db.drop_all()

def test_unauthenticated_redirect(client):
    """Unauthenticated users cannot access protected dashboard routes[cite: 9]."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_registration_and_password_hashing(client):
    """New account is created and password is stored as a hash[cite: 8, 9]."""
    response = client.post('/register', data={
        'username': 'musicfan',
        'email': 'fan@example.com',
        'password': 'securepassword123',
        'confirm_password': 'securepassword123'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    user = User.query.filter_by(email='fan@example.com').first()
    assert user is not None
    assert user.password_hash != 'securepassword123'
    assert user.check_password('securepassword123')

def test_login_search_and_favorites(client):
    """Login works, search matches tracks, and duplicate favorites are prevented[cite: 9]."""
    # Register & Login
    client.post('/register', data={
        'username': 'listener',
        'email': 'listener@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    client.post('/login', data={
        'email': 'listener@example.com',
        'password': 'password123'
    })

    # Test Search
    search_res = client.get('/search?q=Test')
    assert b'Test Track' in search_res.data

    # Test Add Favorite
    song = Song.query.first()
    client.post(f'/favorite/{song.id}')
    assert Favorite.query.count() == 1

    # Test Remove Favorite (Toggle)
    client.post(f'/favorite/{song.id}')
    assert Favorite.query.count() == 0