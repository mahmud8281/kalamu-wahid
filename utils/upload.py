import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

def safe_save(file, upload_folder, prefix='upload'):
    """
    Validate and save an uploaded image file safely.
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

    # generate random safe filename
    filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"

    # make sure folder exists
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filename