from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, limiter
from models.user_model import User
from utils.sanitize import clean

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit('10 per hour')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        full_name = clean(request.form.get('full_name', ''))
        email     = clean(request.form.get('email', ''))
        phone     = clean(request.form.get('phone', ''))
        password  = request.form.get('password', '')
        confirm   = request.form.get('confirm_password', '')

        # validation
        if not full_name or not email or not phone:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email.lower()).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            full_name = full_name,
            email     = email.lower(),
            phone     = phone
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('customer.dashboard'))

    if request.method == 'POST':
        email    = clean(request.form.get('email', '')).lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter your email and password.', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            from flask import session
            login_user(user)
            session.permanent = True
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('customer.dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))