from flask import Blueprint, request, redirect, url_for, render_template
from ..models.note import Note
from ..models.user import User
from ..models import db

note_bp = Blueprint('note_bp', __name__)

@note_bp.route('/submit_note', methods=['POST'])
def submit_note():
    if 'user_id' not in request.cookies:
        return redirect(url_for('auth_bp.login'))
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)

    location = request.form['location']
    content = request.form['content']
    username = user.username
    new_note = Note(location=location, content=content, username=username)
    db.session.add(new_note)
    db.session.commit()
    return redirect(url_for('note_bp.index'))

@note_bp.route('/')
def index():
    if 'user_id' not in request.cookies:
        return redirect(url_for('auth_bp.login'))
    return render_template('index.html')
