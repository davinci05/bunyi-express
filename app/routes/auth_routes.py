from flask import Blueprint, request, redirect, url_for, render_template, flash, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from ..models.note import Note
from ..models import db

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            resp = make_response(redirect(url_for('note_bp.index')))
            resp.set_cookie('user_id', str(user.id))
            return resp
        else:
            flash('Login failed. Check your username and/or password.')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth_bp.login')))
    response.set_cookie('user_id', '', expires=0)
    return response

@auth_bp.route('/admin')
def admin():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user or not user.admin:
        return redirect(url_for('auth_bp.login'))
    notes = Note.query.order_by(Note.timestamp.desc()).all()
    users = User.query.order_by(User.username.desc()).all()

    return render_template('admin.html', notes=notes, users=users)
