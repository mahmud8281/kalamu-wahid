from extensions import db

class GalleryImage(db.Model):
    __tablename__ = 'gallery'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100))
    category    = db.Column(db.String(50))
    filename    = db.Column(db.String(200), nullable=False)
    featured    = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())