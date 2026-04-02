from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        errors = []
        if len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.username_exists(username):
            errors.append('Username already taken.')
        if User.email_exists(email):
            errors.append('Email already registered.')

        if errors:
            for e in errors:
                flash(e, 'error')
        else:
            user = User.create(username, email, password)
            login_user(user)
            flash('Account created! Welcome to CodeQuiz!', 'success')
            return redirect(url_for('main.home'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
