from extensions import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name         = db.Column(db.String(100), nullable=False)
    phone        = db.Column(db.String(20),  nullable=False)
    email        = db.Column(db.String(120))
    date         = db.Column(db.String(20),  nullable=False)
    time         = db.Column(db.String(20),  nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    notes        = db.Column(db.Text)
    status       = db.Column(db.String(30),  default='Pending')
    created_at   = db.Column(db.DateTime,    server_default=db.func.now())

    user = db.relationship('User', backref='appointments', lazy=True,
                           foreign_keys=[user_id])