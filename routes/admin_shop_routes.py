from flask import (Blueprint, render_template, request,
                   flash, redirect, url_for, jsonify)
from flask_login import login_required, current_user
from extensions import db
from models.product_model import (Product, ProductOrder,
                                  WalkInCustomer, WalkInMeasurement)
from models.measurement_model import Measurement
from models.user_model import User
from functools import wraps
from datetime import datetime
from config import Config
import os

admin_shop = Blueprint('admin_shop', __name__, url_prefix='/admin/shop')

CATEGORIES = ['Shadda', 'Yadi', 'Caps', 'Ready-made', 'Embroidery']

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def clean(value):
    if not value:
        return ''
    return str(value).strip()

# ── products ────────────────────────────────────────────────
@admin_shop.route('/')
@login_required
@admin_required
def products():
    all_products = Product.query.order_by(
        Product.created_at.desc()).all()
    return render_template('admin/shop/products.html',
                           products   = all_products,
                           categories = CATEGORIES)

@admin_shop.route('/add', methods=['POST'])
@login_required
@admin_required
def add_product():
    files     = request.files.getlist('images')
    name      = clean(request.form.get('name', ''))
    category  = clean(request.form.get('category', ''))
    price     = float(request.form.get('price') or 0)
    unit      = request.form.get('unit', 'piece')
    desc      = clean(request.form.get('description', ''))
    featured  = request.form.get('featured') == 'on'
    in_stock  = request.form.get('in_stock') == 'on'
    stock_qty = int(request.form.get('stock_qty') or 0)

    print(f'PRODUCT UPLOAD — files received: {len(files)}')
    for i, f in enumerate(files):
        print(f'  File {i}: "{f.filename}" | type: {f.content_type}')

    if not files or all(f.filename == '' for f in files):
        flash('Please select at least one image.', 'danger')
        return redirect(url_for('admin_shop.products'))

    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key    = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    use_cloudinary = bool(cloud_name and api_key and api_secret)

    print(f'Cloudinary configured: {use_cloudinary}')

    uploaded = 0
    rejected = 0

    for i, file in enumerate(files):
        if not file or file.filename == '':
            print(f'File {i}: skipped — empty')
            continue
        try:
            print(f'Processing file {i}: {file.filename}')

            if use_cloudinary:
                from utils.cloudinary_upload import (
                    upload_image as cloud_upload,
                    compress_image
                )
                import cloudinary
                import cloudinary.uploader
                cloudinary.config(
                    cloud_name = cloud_name,
                    api_key    = api_key,
                    api_secret = api_secret,
                    secure     = True
                )
                # compress before upload
                compressed = compress_image(file)
                compressed.seek(0)
                result    = cloudinary.uploader.upload(
                    compressed,
                    folder        = 'kalamu_wahid/products',
                    resource_type = 'image',
                )
                url       = result['secure_url']
                public_id = result['public_id']
                print(f'Cloudinary product upload OK: {url}')

                p = Product(
                    name        = name,
                    description = desc,
                    category    = category,
                    price       = price,
                    unit        = unit,
                    in_stock    = in_stock,
                    stock_qty   = stock_qty,
                    featured    = featured if i == 0 else False,
                    image       = url,
                    public_id   = public_id
                )
                db.session.add(p)
                db.session.commit()
                uploaded += 1

            else:
                import uuid
                from werkzeug.utils import secure_filename
                ALLOWED  = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                original = secure_filename(file.filename)
                if not original or '.' not in original:
                    print(f'File {i}: rejected — no extension')
                    rejected += 1
                    continue
                ext = original.rsplit('.', 1)[1].lower()
                if ext not in ALLOWED:
                    print(f'File {i}: rejected — bad ext {ext}')
                    rejected += 1
                    continue
                filename = f"product_{uuid.uuid4().hex}.{ext}"
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file.seek(0)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                print(f'Local save OK: {filename}')
                p = Product(
                    name        = name,
                    description = desc,
                    category    = category,
                    price       = price,
                    unit        = unit,
                    in_stock    = in_stock,
                    stock_qty   = stock_qty,
                    featured    = featured if i == 0 else False,
                    image       = filename
                )
                db.session.add(p)
                db.session.commit()
                uploaded += 1

        except Exception as e:
            import traceback
            print(f'PRODUCT UPLOAD ERROR file {i}: {e}')
            print(traceback.format_exc())
            db.session.rollback()
            rejected += 1

    print(f'DONE: {uploaded} uploaded, {rejected} rejected')

    if uploaded:
        flash(f'{uploaded} product(s) added under "{name}".', 'success')
    if rejected:
        flash(f'{rejected} file(s) failed to upload. Check image size.', 'danger')
    return redirect(url_for('admin_shop.products'))

@admin_shop.route('/edit/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def edit_product(product_id):
    p    = Product.query.get_or_404(product_id)
    file = request.files.get('image')

    if file and file.filename:
        from utils.cloudinary_upload import (is_cloudinary_configured,
                                             upload_image as cloud_upload)
        from utils.upload import safe_save
        if is_cloudinary_configured():
            url, public_id = cloud_upload(
                file, folder='kalamu_wahid/products')
            if url:
                p.image     = url
                p.public_id = public_id
        else:
            filename = safe_save(
                file, Config.UPLOAD_FOLDER, prefix='product')
            if filename:
                p.image = filename

    p.name        = clean(request.form.get('name', ''))
    p.description = clean(request.form.get('description', ''))
    p.category    = clean(request.form.get('category', ''))
    p.price       = float(request.form.get('price') or 0)
    p.unit        = request.form.get('unit', 'piece')
    p.in_stock    = request.form.get('in_stock') == 'on'
    p.featured    = request.form.get('featured') == 'on'
    p.stock_qty   = int(request.form.get('stock_qty') or 0)

    if p.stock_qty <= 0 and p.stock_qty != 0:
        p.in_stock = False

    db.session.commit()
    flash(f'"{p.name}" updated.', 'success')
    return redirect(url_for('admin_shop.products'))

@admin_shop.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    p = Product.query.get_or_404(product_id)
    if p.public_id:
        from utils.cloudinary_upload import delete_image as cloud_delete
        cloud_delete(p.public_id)
    elif p.image and not p.image.startswith('http'):
        path = os.path.join(Config.UPLOAD_FOLDER, p.image)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(p)
    db.session.commit()
    flash('Product deleted.', 'success')
    return redirect(url_for('admin_shop.products'))

@admin_shop.route('/toggle-stock/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def toggle_stock(product_id):
    p          = Product.query.get_or_404(product_id)
    p.in_stock = not p.in_stock
    db.session.commit()
    return redirect(url_for('admin_shop.products'))

# ── product orders ───────────────────────────────────────────
@admin_shop.route('/orders')
@login_required
@admin_required
def product_orders():
    status = request.args.get('status', 'all')[:20]
    query  = ProductOrder.query
    if status != 'all':
        query = query.filter_by(status=status)
    orders = query.order_by(ProductOrder.created_at.desc()).all()
    return render_template('admin/shop/product_orders.html',
                           orders         = orders,
                           current_status = status)

@admin_shop.route('/orders/update/<int:order_id>', methods=['POST'])
@login_required
@admin_required
def update_order(order_id):
    o             = ProductOrder.query.get_or_404(order_id)
    o.status      = clean(request.form.get('status', ''))
    o.amount_paid = float(request.form.get('amount_paid') or 0)
    db.session.commit()
    flash(f'Order #{order_id} updated.', 'success')
    return redirect(url_for('admin_shop.product_orders'))

# ── measurements ─────────────────────────────────────────────
@admin_shop.route('/measurements')
@login_required
@admin_required
def measurements():
    reg_customers = User.query.filter_by(role='customer').all()
    walkin        = WalkInCustomer.query.order_by(
        WalkInCustomer.created_at.desc()).all()
    search        = request.args.get('search', '').strip()[:100]
    if search:
        reg_customers = [c for c in reg_customers if
                         search.lower() in c.full_name.lower() or
                         search in c.phone]
        walkin = WalkInCustomer.query.filter(
            WalkInCustomer.full_name.ilike(f'%{search}%') |
            WalkInCustomer.phone.ilike(f'%{search}%')
        ).all()
    return render_template('admin/shop/measurements.html',
                           reg_customers = reg_customers,
                           walkin        = walkin,
                           search        = search)

@admin_shop.route('/measurements/registered/<int:user_id>',
                  methods=['GET', 'POST'])
@login_required
@admin_required
def edit_registered_measurement(user_id):
    customer    = User.query.get_or_404(user_id)
    measurement = Measurement.query.filter_by(user_id=user_id).first()
    fields      = ['chest', 'shoulder', 'sleeve', 'waist',
                   'neck', 'hip', 'shirt_length', 'trouser_length']
    if request.method == 'POST':
        if measurement:
            for f in fields:
                setattr(measurement, f, request.form.get(f))
        else:
            measurement = Measurement(user_id=user_id)
            for f in fields:
                setattr(measurement, f, request.form.get(f))
            db.session.add(measurement)
        db.session.commit()
        flash(f'Measurements saved for {customer.full_name}.', 'success')
        return redirect(url_for('admin_shop.measurements'))
    return render_template('admin/shop/take_measurement.html',
                           customer    = customer,
                           measurement = measurement,
                           is_walkin   = False)

@admin_shop.route('/measurements/walkin/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_walkin():
    if request.method == 'POST':
        c = WalkInCustomer(
            full_name = clean(request.form.get('full_name', '')),
            phone     = clean(request.form.get('phone', '')),
            address   = clean(request.form.get('address', ''))
        )
        db.session.add(c)
        db.session.flush()
        fields = ['chest', 'shoulder', 'sleeve', 'waist',
                  'neck', 'hip', 'shirt_length', 'trouser_length']
        m = WalkInMeasurement(
            customer_id = c.id,
            notes       = clean(request.form.get('notes', '')),
            taken_by    = current_user.full_name
        )
        for f in fields:
            setattr(m, f, request.form.get(f))
        db.session.add(m)
        db.session.commit()
        flash(f'Walk-in customer "{c.full_name}" created.', 'success')
        return redirect(url_for('admin_shop.measurements'))
    return render_template('admin/shop/take_measurement.html',
                           customer    = None,
                           measurement = None,
                           is_walkin   = True)

@admin_shop.route('/measurements/walkin/<int:customer_id>',
                  methods=['GET', 'POST'])
@login_required
@admin_required
def edit_walkin_measurement(customer_id):
    customer    = WalkInCustomer.query.get_or_404(customer_id)
    measurement = WalkInMeasurement.query.filter_by(
        customer_id=customer_id).first()
    fields = ['chest', 'shoulder', 'sleeve', 'waist',
              'neck', 'hip', 'shirt_length', 'trouser_length']
    if request.method == 'POST':
        if measurement:
            for f in fields:
                setattr(measurement, f, request.form.get(f))
            measurement.notes    = clean(request.form.get('notes', ''))
            measurement.taken_by = current_user.full_name
        else:
            measurement = WalkInMeasurement(
                customer_id = customer_id,
                notes       = clean(request.form.get('notes', '')),
                taken_by    = current_user.full_name
            )
            for f in fields:
                setattr(measurement, f, request.form.get(f))
            db.session.add(measurement)
        db.session.commit()
        flash(f'Measurements updated for {customer.full_name}.', 'success')
        return redirect(url_for('admin_shop.measurements'))
    return render_template('admin/shop/take_measurement.html',
                           customer    = customer,
                           measurement = measurement,
                           is_walkin   = True)

@admin_shop.route('/measurements/walkin/delete/<int:customer_id>',
                  methods=['POST'])
@login_required
@admin_required
def delete_walkin(customer_id):
    c = WalkInCustomer.query.get_or_404(customer_id)
    db.session.delete(c)
    db.session.commit()
    flash('Walk-in customer removed.', 'success')
    return redirect(url_for('admin_shop.measurements'))

@admin_shop.route('/measurements/search-customers')
@login_required
@admin_required
def search_customers():
    q       = request.args.get('q', '').strip()[:100]
    results = []
    if q:
        customers = User.query.filter(
            User.role == 'customer',
            (User.full_name.ilike(f'%{q}%') |
             User.phone.ilike(f'%{q}%'))
        ).limit(8).all()
        results = [{'id': c.id, 'name': c.full_name, 'phone': c.phone}
                   for c in customers]
    return jsonify(results)