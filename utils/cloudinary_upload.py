import os
import io

def is_cloudinary_configured():
    return bool(
        os.environ.get('CLOUDINARY_CLOUD_NAME') and
        os.environ.get('CLOUDINARY_API_KEY') and
        os.environ.get('CLOUDINARY_API_SECRET')
    )

def configure_cloudinary():
    import cloudinary
    cloudinary.config(
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key    = os.environ.get('CLOUDINARY_API_KEY'),
        api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
        secure     = True
    )

def compress_image(file, max_size_kb=800, max_dimension=1200):
    """
    Compress image in memory before uploading.
    Reduces memory usage and speeds up upload.
    """
    try:
        from PIL import Image
        file.seek(0)
        img = Image.open(file)

        # convert RGBA to RGB if needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # resize if too large
        w, h = img.size
        if w > max_dimension or h > max_dimension:
            img.thumbnail((max_dimension, max_dimension),
                          Image.Resampling.LANCZOS)

        # save compressed to buffer
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=75, optimize=True)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f'Compression error: {e}')
        file.seek(0)
        return file

def upload_image(file, folder='kalamu_wahid'):
    """
    Compress then upload to Cloudinary.
    Returns (url, public_id) or (None, None) if failed.
    """
    try:
        import cloudinary.uploader
        configure_cloudinary()

        # compress first to save memory
        compressed = compress_image(file)

        result = cloudinary.uploader.upload(
            compressed,
            folder        = folder,
            resource_type = 'image',
        )
        return result['secure_url'], result['public_id']
    except Exception as e:
        print(f'Cloudinary upload error: {e}')
        return None, None

def delete_image(public_id):
    """Delete an image from Cloudinary by public_id."""
    try:
        import cloudinary.uploader
        configure_cloudinary()
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f'Cloudinary delete error: {e}')
        return False