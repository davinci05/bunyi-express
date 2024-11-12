from app import create_app
from app.models import db
from app.models.user import User 
from app.models.note import Note  
from werkzeug.security import generate_password_hash

app = create_app()


def create_default_admin() -> None:
    # Create default admin user if not exists
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
        default_admin = User(username='admin', password=hashed_password, admin=True)
        db.session.add(default_admin)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        create_default_admin()

    app.run(debug=True)
