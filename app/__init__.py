import os
from flask import Flask
from dotenv import load_dotenv
from .models import db
from .routes import note_bp, user_bp, auth_bp

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__,  instance_relative_config=True)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

    db.init_app(app)

    app.register_blueprint(note_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(auth_bp)

    return app
