from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from extensions import db
from models.product_model import Product, ProductOrder
from utils.notifications import notify_product_order
import urllib.parse

shop = Blueprint('shop', __name__)

CATEGORIES      = ['Shadda', 'Yadi', 'Caps', 'Ready-made', 'Embroidery']
WHATSAPP_NUMBER = '2347082815719'  # ← replace with real number

@shop.route('/shop')
def shop_home():
    category = request.args.get('category', 'all')
    search   = request.args.get('search', '').strip()

    query = Product.query.filter_by(in_stock=True)
    if category != 'all':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%'))

    products = query.order_by(
        Product.featured.desc(),
        Product.created_at.desc()
    ).all()
    featured = Product.query.filter_by(
        featured=True, in_stock=True).limit(4).all()

    return render_template('shop/shop.html',
                           products=products,
                           featured=featured,
                           categories=CATEGORIES,
                           current_category=category,
                           search=search)

@shop.route('/shop/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related = Product.query.filter_by(
        category=product.category,
        in_stock=True
    ).filter(Product.id != product_id).limit(4).all()
    return render_template('shop/product_detail.html',
                           product=product,
                           related=related)

@shop.route('/shop/request-order/<int:product_id>',
            methods=['GET', 'POST'])
def request_order(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        name     = request.form.get('customer_name')
        phone    = request.form.get('customer_phone')
        qty      = float(request.form.get('quantity') or 1)
        delivery = request.form.get('delivery_method')
        address  = request.form.get('delivery_address', '')
        note     = request.form.get('note', '')
        total    = qty * product.price if product.price else 0

        o = ProductOrder(
            user_id          = current_user.id
                               if current_user.is_authenticated else None,
            product_id       = product_id,
            customer_name    = name,
            customer_phone   = phone,
            quantity         = qty,
            unit             = product.unit,
            delivery_method  = delivery,
            delivery_address = address,
            note             = note,
            total_price      = total,
            status           = 'Pending'
        )
        db.session.add(o)
        db.session.commit()

        # notify admins
        notify_product_order(o)

        msg = (
            f"🛍️ *NEW PRODUCT ORDER — Kalamu Wahid*\n\n"
            f"👤 *Customer:* {name}\n"
            f"📞 *Phone:* {phone}\n"
            f"🆔 *Order #:* {o.id}\n\n"
            f"📦 *Product:* {product.name}\n"
            f"🏷️ *Category:* {product.category}\n"
            f"📏 *Quantity:* {qty} {product.unit}(s)\n"
            f"💰 *Total:* "
            f"{'₦{:,.0f}'.format(total) if total else 'Price on request'}\n"
            f"🚚 *Delivery:* {delivery}\n"
            f"📍 *Address:* {address or 'Pickup'}\n"
            f"📌 *Note:* {note or 'None'}"
        )
        wa_url = (f"https://wa.me/{WHATSAPP_NUMBER}?"
                  f"text={urllib.parse.quote(msg)}")

        flash('Order request submitted successfully!', 'success')
        return render_template('shop/order_confirm.html',
                               order=o,
                               product=product,
                               wa_url=wa_url)

    return render_template('shop/request_order.html',
                           product=product)

@shop.route('/shop/cart')
def cart():
    return render_template('shop/cart.html')