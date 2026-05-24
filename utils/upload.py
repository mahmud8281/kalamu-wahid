import os
import uuid
import imghdr
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_MIMETYPES  = {'png', 'jpeg', 'gif', 'webp'}

def safe_save(file, upload_folder, prefix='upload'):
    """
    Validate file is truly an image using magic bytes,
    rename to random UUID to prevent path traversal,
    and save safely.
    Returns new filename or None if invalid.
    """
    if not file or not file.filename:
        return None

    original = secure_filename(file.filename)
    if not original or '.' not in original:
        return None

    ext = original.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None

    # read magic bytes to verify real file type
    file_bytes = file.read(512)
    file.seek(0)

    real_type = imghdr.what(None, h=file_bytes)
    if real_type not in ALLOWED_MIMETYPES:
        return None

    # generate random safe filename
    filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filename