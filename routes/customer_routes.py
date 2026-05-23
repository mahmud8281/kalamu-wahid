from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.order_model import Order
from models.measurement_model import Measurement
from models.gallery_model import GalleryImage
from models.product_model import Product
from werkzeug.security import check_password_hash

customer = Blueprint('customer', __name__)

@customer.route('/')
def home():
    gallery  = GalleryImage.query.order_by(GalleryImage.uploaded_at.desc()).all()
    featured = GalleryImage.query.filter_by(featured=True).all()
    products = Product.query.filter_by(
        in_stock=True, featured=True).limit(4).all()
    return render_template('home.html',
                           gallery=gallery,
                           featured=featured,
                           products=products)

@customer.route('/dashboard')
@login_required
def dashboard():
    orders      = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(Order.created_at.desc()).all()
    measurement = Measurement.query.filter_by(
        user_id=current_user.id).first()
    return render_template('customer/dashboard.html',
                           orders=orders,
                           measurement=measurement)

@customer.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            current_user.full_name = request.form.get('full_name')
            current_user.phone     = request.form.get('phone')
            db.session.commit()
            flash('Profile updated successfully.', 'success')

        elif action == 'change_password':
            old_pw  = request.form.get('old_password')
            new_pw  = request.form.get('new_password')
            confirm = request.form.get('confirm_password')
            if not current_user.check_password(old_pw):
                flash('Current password is incorrect.', 'danger')
            elif new_pw != confirm:
                flash('New passwords do not match.', 'danger')
            elif len(new_pw) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('Password changed successfully.', 'success')

        return redirect(url_for('customer.profile'))

    orders      = Order.query.filter_by(user_id=current_user.id).all()
    measurement = Measurement.query.filter_by(
        user_id=current_user.id).first()
    total_spent = sum(o.amount_paid for o in orders)
    return render_template('customer/profile.html',
                           orders=orders,
                           measurement=measurement,
                           total_spent=total_spent)