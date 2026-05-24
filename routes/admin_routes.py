from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.order_model import Order
from models.user_model import User
from models.measurement_model import Measurement
from models.gallery_model import GalleryImage
from models.feedback_model import Feedback
from models.notification_model import Notification
from utils.notifications import notify_order_status
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import urllib.parse
from config import Config

admin = Blueprint('admin', __name__, url_prefix='/admin')

WHATSAPP_NUMBER = '2348000000000'  # ← replace with real number

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def ceo_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_ceo():
            flash('CEO/MD access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    orders    = Order.query.order_by(Order.created_at.desc()).all()
    customers = User.query.filter_by(role='customer').all()
    staff     = User.query.filter_by(role='staff').all()

    pending   = Order.query.filter_by(status='Pending').count()
    progress  = Order.query.filter_by(status='In Progress').count()
    ready     = Order.query.filter_by(status='Ready').count()
    delivered = Order.query.filter_by(status='Delivered').count()

    total_revenue = db.session.query(
        func.sum(Order.amount)).scalar() or 0
    total_paid    = db.session.query(
        func.sum(Order.amount_paid)).scalar() or 0
    total_balance = total_revenue - total_paid

    monthly_data = []
    for i in range(5, -1, -1):
        d   = datetime.now() - timedelta(days=30 * i)
        rev = db.session.query(func.sum(Order.amount)).filter(
            func.strftime('%Y-%m', Order.created_at) == d.strftime('%Y-%m')
        ).scalar() or 0
        monthly_data.append({
            'month':   d.strftime('%b'),
            'revenue': float(rev)
        })

    style_data = db.session.query(
        Order.style_type,
        func.count(Order.id).label('count')
    ).group_by(Order.style_type).order_by(
        func.count(Order.id).desc()).all()

    total_feedback = Feedback.query.count()
    new_feedback   = Feedback.query.order_by(
        Feedback.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        orders=orders, customers=customers, staff=staff,
        pending=pending, progress=progress,
        ready=ready, delivered=delivered,
        total_revenue=total_revenue,
        total_paid=total_paid,
        total_balance=total_balance,
        monthly_data=monthly_data,
        style_data=style_data,
        total_feedback=total_feedback,
        new_feedback=new_feedback)

@admin.route('/orders')
@login_required
@admin_required
def orders():
    status     = request.args.get('status', 'all')
    all_orders = Order.query.order_by(
        Order.created_at.desc()).all() \
        if status == 'all' else \
        Order.query.filter_by(status=status).order_by(
            Order.created_at.desc()).all()
    return render_template('admin/orders.html',
                           orders=all_orders,
                           current_status=status)

@admin.route('/update-status/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_status(order_id):
    o          = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    old_status = o.status
    o.status   = new_status
    db.session.commit()

    # notify customer only if status actually changed
    if new_status != old_status:
        notify_order_status(o)

    flash(f'Order #{order_id} updated to {o.status}.', 'success')
    return redirect(request.referrer or url_for('admin.orders'))

@admin.route('/update-payment/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_payment(order_id):
    o             = Order.query.get_or_404(order_id)
    o.amount_paid = float(request.form.get('amount_paid') or 0)
    db.session.commit()
    flash(f'Payment updated for Order #{order_id}.', 'success')
    return redirect(request.referrer or url_for('admin.orders'))

@admin.route('/delete-order/<int:order_id>', methods=['POST'])
@login_required
@ceo_required
def delete_order(order_id):
    o = Order.query.get_or_404(order_id)
    db.session.delete(o)
    db.session.commit()
    flash(f'Order #{order_id} deleted.', 'success')
    return redirect(url_for('admin.orders'))

@admin.route('/customers')
@login_required
@admin_required
def customers():
    all_customers = User.query.filter_by(role='customer').order_by(
        User.created_at.desc()).all()
    return render_template('admin/customers.html',
                           customers=all_customers)

@admin.route('/customer/<int:user_id>')
@login_required
@admin_required
def customer_detail(user_id):
    customer    = User.query.get_or_404(user_id)
    orders      = Order.query.filter_by(user_id=user_id).order_by(
        Order.created_at.desc()).all()
    measurement = Measurement.query.filter_by(user_id=user_id).first()
    return render_template('admin/customer_detail.html',
                           customer=customer,
                           orders=orders,
                           measurement=measurement)

@admin.route('/payments')
@login_required
@admin_required
def payments():
    all_orders    = Order.query.order_by(Order.created_at.desc()).all()
    total_revenue = db.session.query(
        func.sum(Order.amount)).scalar() or 0
    total_paid    = db.session.query(
        func.sum(Order.amount_paid)).scalar() or 0
    total_balance = total_revenue - total_paid
    return render_template('admin/payments.html',
                           orders=all_orders,
                           total_revenue=total_revenue,
                           total_paid=total_paid,
                           total_balance=total_balance)

@admin.route('/gallery')
@login_required
@admin_required
def gallery():
    images = GalleryImage.query.order_by(
        GalleryImage.uploaded_at.desc()).all()
    return render_template('admin/gallery.html', images=images)

@admin.route('/gallery/upload', methods=['POST'])
@login_required
@admin_required
def upload_image():
    ALLOWED  = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    files    = request.files.getlist('images')
    title    = request.form.get('title', '')
    category = request.form.get('category', 'General')
    featured = request.form.get('featured') == 'on'

    if not files or all(f.filename == '' for f in files):
        flash('Please select at least one image.', 'danger')
        return redirect(url_for('admin.gallery'))

    uploaded = 0
    rejected = 0
    for i, file in enumerate(files):
        if file and '.' in file.filename and \
           file.filename.rsplit('.', 1)[1].lower() in ALLOWED:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename  = f"gallery_{timestamp}_{i}_{file.filename}"
            file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
            img = GalleryImage(
                title    = f"{title} {i+1}".strip()
                           if len(files) > 1 else title,
                category = category,
                filename = filename,
                featured = featured if i == 0 else False
            )
            db.session.add(img)
            uploaded += 1
        else:
            rejected += 1

    db.session.commit()
    if uploaded:
        flash(f'{uploaded} image(s) uploaded.', 'success')
    if rejected:
        flash(f'{rejected} file(s) rejected.', 'danger')
    return redirect(url_for('admin.gallery'))

@admin.route('/gallery/delete/<int:image_id>', methods=['POST'])
@login_required
@admin_required
def delete_image(image_id):
    img      = GalleryImage.query.get_or_404(image_id)
    filepath = os.path.join(Config.UPLOAD_FOLDER, img.filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(img)
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin.gallery'))

@admin.route('/staff')
@login_required
@ceo_required
def staff():
    all_staff = User.query.filter_by(role='staff').all()
    return render_template('admin/staff.html', staff=all_staff)

@admin.route('/staff/add', methods=['POST'])
@login_required
@ceo_required
def add_staff():
    if User.query.filter_by(
            email=request.form.get('email')).first():
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin.staff'))
    s = User(
        full_name = request.form.get('full_name'),
        email     = request.form.get('email'),
        phone     = request.form.get('phone'),
        role      = 'staff'
    )
    s.set_password(request.form.get('password'))
    db.session.add(s)
    db.session.commit()
    flash('Staff account created.', 'success')
    return redirect(url_for('admin.staff'))

@admin.route('/staff/delete/<int:user_id>', methods=['POST'])
@login_required
@ceo_required
def delete_staff(user_id):
    s = User.query.get_or_404(user_id)
    db.session.delete(s)
    db.session.commit()
    flash('Staff account removed.', 'success')
    return redirect(url_for('admin.staff'))

@admin.route('/whatsapp/<int:user_id>')
@login_required
@admin_required
def whatsapp_customer(user_id):
    customer = User.query.get_or_404(user_id)
    orders   = Order.query.filter_by(user_id=user_id).all()
    balance  = sum(o.amount - o.amount_paid for o in orders)
    ready    = [o for o in orders if o.status == 'Ready']

    msg = f"Assalamu Alaikum {customer.full_name},\n\n"
    if ready:
        msg += "Your order(s) are ready for collection:\n"
        for o in ready:
            msg += f"  • Order #{o.id} — {o.style_type}\n"
        msg += "\nPlease come pick up at your earliest convenience.\n\n"
    if balance > 0:
        msg += f"Outstanding balance: ₦{balance:,.0f}\n\n"
    msg += "Thank you for choosing Kalamu Wahid Tailoring Synergy. 🧵"

    number = customer.phone.replace(
        '+','').replace(' ','').replace('-','')
    if number.startswith('0'):
        number = '234' + number[1:]
    wa_url = (f"https://wa.me/{number}?"
              f"text={urllib.parse.quote(msg)}")
    return redirect(wa_url)