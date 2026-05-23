from extensions import db

class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category    = db.Column(db.String(100), nullable=False)
    price       = db.Column(db.Float, default=0.0)
    unit        = db.Column(db.String(50), default='piece')
    in_stock    = db.Column(db.Boolean, default=True)
    image       = db.Column(db.String(200))
    featured    = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())

    orders = db.relationship('ProductOrder', backref='product', lazy=True)


class ProductOrder(db.Model):
    __tablename__ = 'product_orders'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id       = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    customer_name    = db.Column(db.String(100))
    customer_phone   = db.Column(db.String(20))
    quantity         = db.Column(db.Float, default=1)
    unit             = db.Column(db.String(50))
    delivery_method  = db.Column(db.String(50))
    delivery_address = db.Column(db.Text)
    note             = db.Column(db.Text)
    status           = db.Column(db.String(50), default='Pending')
    total_price      = db.Column(db.Float, default=0.0)
    amount_paid      = db.Column(db.Float, default=0.0)
    created_at       = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='product_orders', lazy=True,
                           foreign_keys=[user_id])


class WalkInCustomer(db.Model):
    __tablename__ = 'walkin_customers'

    id         = db.Column(db.Integer, primary_key=True)
    full_name  = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    address    = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    measurement = db.relationship('WalkInMeasurement',
                                  backref='customer', lazy=True,
                                  uselist=False)


class WalkInMeasurement(db.Model):
    __tablename__ = 'walkin_measurements'

    id             = db.Column(db.Integer, primary_key=True)
    customer_id    = db.Column(db.Integer,
                               db.ForeignKey('walkin_customers.id'),
                               nullable=False)
    chest          = db.Column(db.String(50))
    shoulder       = db.Column(db.String(50))
    sleeve         = db.Column(db.String(50))
    waist          = db.Column(db.String(50))
    neck           = db.Column(db.String(50))
    hip            = db.Column(db.String(50))
    shirt_length   = db.Column(db.String(50))
    trouser_length = db.Column(db.String(50))
    notes          = db.Column(db.Text)
    taken_by       = db.Column(db.String(100))
    updated_at     = db.Column(db.DateTime,
                               server_default=db.func.now(),
                               onupdate=db.func.now())