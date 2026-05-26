import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kw-dev-secret-change-in-production'

    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'
    SESSION_COOKIE_SECURE      = os.environ.get('FLASK_ENV') == 'production'

    SQLALCHEMY_DATABASE_URI        = 'sqlite:///kalamu_tailoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES      = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        'pool_pre_ping':  True,
        'pool_recycle':   300,
        'connect_args':   {'check_same_thread': False},
    }

    # Reduce to 5MB to prevent memory issues on free plan
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    if os.environ.get('RENDER'):
        UPLOAD_FOLDER = '/tmp/uploads'
    else:
        UPLOAD_FOLDER = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'uploads')

    ALLOWED_EXTENSIONS     = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    SEND_FILE_MAX_AGE_DEFAULT = 31536000