from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import Config

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    # Register blueprints 
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    # from app.routes.auth import auth_bp
    # app.register_blueprint(auth_bp)
    
    # from app.routes.main import main_bp
    # app.register_blueprint(main_bp)

    return app