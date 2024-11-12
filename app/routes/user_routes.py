from flask import Blueprint, request, redirect, url_for, flash
from ..models.user import User
from ..models import db
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/delete_user', methods=["POST"])
def delete_user():
    if 'user_id' not in request.cookies:
        return redirect(url_for('auth_bp.login'))
    
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    
    if not user or not user.admin:
        flash('Unauthorized access.')
        return redirect(url_for('auth_bp.login'))
    
    user_id_form = int(request.form["user_id"].replace("/", ""))
    try:
        user_to_delete = User.query.get(user_id_form)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('Successfully deleted user.')
        else:
            flash('User not found.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {e}')
    
    return redirect(url_for('auth_bp.admin'))

@user_bp.route('/new_user', methods=['POST'])
def new_user():
    user_id = request.cookies.get('user_id')
    if not user_id:
        return redirect(url_for('auth_bp.login'))
    user = User.query.get(user_id)
    if not user or not user.admin:
        return redirect(url_for('auth_bp.login'))

    username = request.form['username']
    password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
    admin = request.form['admin'] == 'true'

    new_user = User(username=username, password=password, admin=admin)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('auth_bp.admin'))
