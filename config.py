import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kalamu-wahid-secret-key-2024'

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kalamu_tailoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping':    True,
        'pool_recycle':     300,
        'connect_args':     {'check_same_thread': False},
    }
    SQLALCHEMY_RECORD_QUERIES = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Caching
    SEND_FILE_MAX_AGE_DEFAULT = 31536000