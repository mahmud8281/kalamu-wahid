from extensions import db

class Order(db.Model):
    __tablename__ = 'orders'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    style_type      = db.Column(db.String(100), nullable=False)
    description     = db.Column(db.Text)
    design_image    = db.Column(db.String(200))
    delivery_method = db.Column(db.String(50))
    delivery_address= db.Column(db.Text)
    payment_method  = db.Column(db.String(50))
    amount          = db.Column(db.Float, default=0.0)
    amount_paid     = db.Column(db.Float, default=0.0)
    status          = db.Column(db.String(50), default='Pending')
    notes           = db.Column(db.Text)
    created_at      = db.Column(db.DateTime, server_default=db.func.now())