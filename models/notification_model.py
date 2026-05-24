from extensions import db

class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False, index=True)
    title      = db.Column(db.String(150), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    type       = db.Column(db.String(50), default='info')
    is_read    = db.Column(db.Boolean, default=False, index=True)
    link       = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='notifications',
                           lazy=True, foreign_keys=[user_id])