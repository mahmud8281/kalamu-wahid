import os
from datetime import timedelta

class Config:
    # ── Security ─────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kw-dev-secret-change-in-production'

    # Session security
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_HTTPONLY    = True
    SESSION_COOKIE_SAMESITE    = 'Lax'
    SESSION_COOKIE_SECURE      = os.environ.get('FLASK_ENV') == 'production'

    # ── Database ──────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI        = 'sqlite:///kalamu_tailoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES      = False
    SQLALCHEMY_ENGINE_OPTIONS      = {
        'pool_pre_ping':  True,
        'pool_recycle':   300,
        'connect_args':   {'check_same_thread': False},
    }

    # ── Uploads ───────────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # ── Performance ───────────────────────────────────────────
    SEND_FILE_MAX_AGE_DEFAULT = 31536000