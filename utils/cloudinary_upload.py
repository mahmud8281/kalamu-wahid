import os
import cloudinary
import cloudinary.uploader

def configure_cloudinary():
    cloudinary.config(
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key    = os.environ.get('CLOUDINARY_API_KEY'),
        api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
        secure     = True
    )

def upload_image(file, folder='kalamu_wahid'):
    """
    Upload a file to Cloudinary and return the secure URL.
    Returns (url, public_id) or (None, None) if failed.
    """
    try:
        configure_cloudinary()
        result = cloudinary.uploader.upload(
            file,
            folder          = folder,
            allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            transformation  = [
                {'quality': 'auto'},
                {'fetch_format': 'auto'},
            ]
        )
        return result['secure_url'], result['public_id']
    except Exception as e:
        print(f'Cloudinary upload error: {e}')
        return None, None

def delete_image(public_id):
    """Delete an image from Cloudinary by public_id."""
    try:
        configure_cloudinary()
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f'Cloudinary delete error: {e}')
        return False