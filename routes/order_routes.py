import os
import urllib.parse
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.order_model import Order
from models.measurement_model import Measurement
from config import Config
from utils.notifications import notify_order_placed, notify_order_status

order = Blueprint('order', __name__)

ALLOWED         = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
WHATSAPP_NUMBER = '2348000000000'  # ← replace with real number

def allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in ALLOWED)

def build_whatsapp_url(message):
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(message)}"

@order.route('/place-order', methods=['GET', 'POST'])
@login_required
def place_order():
    measurement = Measurement.query.filter_by(
        user_id=current_user.id).first()

    if request.method == 'POST':
        image_filename = None
        if 'design_image' in request.files:
            file = request.files['design_image']
            if file and allowed_file(file.filename):
                image_filename = f"order_{current_user.id}_{file.filename}"
                file.save(os.path.join(Config.UPLOAD_FOLDER, image_filename))

        new_order = Order(
            user_id          = current_user.id,
            style_type       = request.form.get('style_type'),
            description      = request.form.get('description'),
            design_image     = image_filename,
            delivery_method  = request.form.get('delivery_method'),
            delivery_address = request.form.get('delivery_address'),
            payment_method   = request.form.get('payment_method'),
            amount           = float(request.form.get('amount') or 0),
            notes            = request.form.get('notes'),
            status           = 'Pending'
        )
        db.session.add(new_order)
        db.session.commit()

        # notify admins
        notify_order_placed(new_order)

        m   = measurement
        msg = (
            f"🧵 *NEW TAILORING ORDER — Kalamu Wahid*\n\n"
            f"👤 *Customer:* {current_user.full_name}\n"
            f"📞 *Phone:* {current_user.phone}\n"
            f"🆔 *Order #:* {new_order.id}\n\n"
            f"👗 *Style:* {new_order.style_type}\n"
            f"📝 *Description:* {new_order.description or 'None'}\n"
            f"💰 *Amount:* ₦{new_order.amount:,.0f}\n"
            f"💳 *Payment:* {new_order.payment_method}\n"
            f"🚚 *Delivery:* {new_order.delivery_method}\n"
            f"📍 *Address:* {new_order.delivery_address or 'Pickup'}\n\n"
        )
        if m:
            msg += (
                f"📏 *Measurements:*\n"
                f"  Chest: {m.chest}\" | Shoulder: {m.shoulder}\"\n"
                f"  Sleeve: {m.sleeve}\" | Waist: {m.waist}\"\n"
                f"  Neck: {m.neck}\" | Hip: {m.hip}\"\n"
                f"  Shirt Length: {m.shirt_length}\" | "
                f"Trouser: {m.trouser_length}\"\n\n"
            )
        msg   += f"📌 *Notes:* {new_order.notes or 'None'}"
        wa_url = build_whatsapp_url(msg)

        flash('Order placed successfully!', 'success')
        return render_template('customer/order_confirm.html',
                               order=new_order,
                               wa_url=wa_url)

    return render_template('customer/place_order.html',
                           measurement=measurement)

@order.route('/my-orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(
        user_id=current_user.id
    ).order_by(Order.created_at.desc()).all()
    return render_template('customer/my_orders.html', orders=orders)

@order.route('/track-order/<int:order_id>')
@login_required
def track_order(order_id):
    o = Order.query.filter_by(
        id=order_id,
        user_id=current_user.id
    ).first_or_404()
    steps        = ['Pending', 'In Progress', 'Ready', 'Delivered']
    current_step = steps.index(o.status) if o.status in steps else 0
    return render_template('customer/track_order.html',
                           order=o,
                           steps=steps,
                           current_step=current_step)