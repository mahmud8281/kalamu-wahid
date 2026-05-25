import os

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

def upload_image(file, folder='kalamu_wahid'):
    try:
        import cloudinary.uploader
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
    try:
        import cloudinary.uploader
        configure_cloudinary()
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f'Cloudinary delete error: {e}')
        return False