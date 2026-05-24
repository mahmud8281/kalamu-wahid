from extensions import db

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120))
    category   = db.Column(db.String(50), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='feedback', lazy=True,
                           foreign_keys=[user_id])