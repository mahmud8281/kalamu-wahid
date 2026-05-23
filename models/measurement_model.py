from extensions import db

class Measurement(db.Model):
    __tablename__ = 'measurements'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chest          = db.Column(db.String(50))
    shoulder       = db.Column(db.String(50))
    sleeve         = db.Column(db.String(50))
    waist          = db.Column(db.String(50))
    neck           = db.Column(db.String(50))
    hip            = db.Column(db.String(50))
    shirt_length   = db.Column(db.String(50))
    trouser_length = db.Column(db.String(50))
    updated_at     = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())