from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, default=False)

@app.route('/')
def index():
    if 'user_id' not in request.cookies:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    # Clear the user_id cookie
    response = make_response(redirect(url_for('login')))
    response.set_cookie('user_id', '', expires=0)
    return response

@app.route('/delete_all_users')
def delete_all_users():
    if 'user_id' not in request.cookies:
        return redirect(url_for('login'))
    
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    
    if not user or not user.admin:
        flash('Unauthorized access.')
        return redirect(url_for('index'))
    
    try:
        num_deleted = User.query.delete()
        db.session.commit()
        flash(f'Successfully deleted {num_deleted} users.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting users: {e}')
    
    return redirect(url_for('index'))

@app.route('/submit_user', methods=['POST'])
def submit_user():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user or not user.admin:
        return redirect(url_for('login'))
    else:
        print(request.form)
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        
        print("request form:", request.form['admin'])
        admin = request.form['admin'] == 'true'

        new_user = User(username=username, password=password, admin=admin)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
    

@app.route('/submit_note', methods=['POST'])
def submit_note():
    if 'user_id' not in request.cookies:
        return redirect(url_for('login'))
    location = request.form['location']
    content = request.form['content']
    new_note = Note(location=location, content=content)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    if not user or not user.admin:
        return redirect(url_for('login'))
    notes = Note.query.order_by(Note.timestamp.desc()).all()
    users = User.query.order_by(User.username.desc()).all()

    return render_template('admin.html', notes=notes, users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            print(user.username, ":", user.password)  # Debug
            if check_password_hash(user.password, password):
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('user_id', str(user.id))
                return resp
            else:
                flash('Login failed. Check your username and/or password.')
        else:
            flash('Login failed. User not found.')
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
      db.create_all()

      # Create default admin user if not exists
      if not User.query.filter_by(username='admin').first():
          hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
          default_admin = User(username='admin', password=hashed_password, admin=True)
          db.session.add(default_admin)
          db.session.commit()
    app.run(debug=True)