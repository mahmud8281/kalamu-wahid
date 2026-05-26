@admin.route('/gallery/upload', methods=['POST'])
@login_required
@admin_required
def upload_image():
    files    = request.files.getlist('images')
    title    = clean(request.form.get('title', ''))
    category = clean(request.form.get('category', 'General'))
    featured = request.form.get('featured') == 'on'

    if not files or all(f.filename == '' for f in files):
        flash('Please select at least one image.', 'danger')
        return redirect(url_for('admin.gallery'))

    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key    = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')

    print(f'GALLERY UPLOAD — Cloudinary: {bool(cloud_name)}')

    use_cloudinary = bool(cloud_name and api_key and api_secret)
    uploaded = 0
    rejected = 0

    for i, file in enumerate(files):
        if not file or file.filename == '':
            continue
        try:
            print(f'Uploading gallery file {i}: {file.filename}')
            if use_cloudinary:
                import cloudinary
                import cloudinary.uploader
                cloudinary.config(
                    cloud_name = cloud_name,
                    api_key    = api_key,
                    api_secret = api_secret,
                    secure     = True
                )
                file.seek(0)
                result    = cloudinary.uploader.upload(
                    file,
                    folder        = 'kalamu_wahid/gallery',
                    resource_type = 'image',
                )
                url       = result['secure_url']
                public_id = result['public_id']
                print(f'Gallery upload OK: {url}')
                img = GalleryImage(
                    title     = f"{title} {i+1}".strip()
                                if len(files) > 1 else title,
                    category  = category,
                    filename  = url,
                    public_id = public_id,
                    featured  = featured if i == 0 else False
                )
                db.session.add(img)
                uploaded += 1
            else:
                import uuid
                from werkzeug.utils import secure_filename
                ALLOWED  = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                original = secure_filename(file.filename)
                ext      = original.rsplit('.', 1)[1].lower() \
                           if '.' in original else ''
                if ext not in ALLOWED:
                    rejected += 1
                    continue
                filename = f"gallery_{uuid.uuid4().hex}.{ext}"
                os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
                file.seek(0)
                file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
                img = GalleryImage(
                    title    = f"{title} {i+1}".strip()
                               if len(files) > 1 else title,
                    category = category,
                    filename = filename,
                    featured = featured if i == 0 else False
                )
                db.session.add(img)
                uploaded += 1
        except Exception as e:
            import traceback
            print(f'Gallery upload ERROR: {e}')
            print(traceback.format_exc())
            rejected += 1

    db.session.commit()
    if uploaded:
        flash(f'{uploaded} image(s) uploaded successfully.', 'success')
    if rejected:
        flash(f'{rejected} file(s) failed.', 'danger')
    return redirect(url_for('admin.gallery'))


@admin.route('/gallery/delete/<int:image_id>', methods=['POST'])
@login_required
@admin_required
def delete_image(image_id):
    img = GalleryImage.query.get_or_404(image_id)
    if img.public_id:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
                api_key    = os.environ.get('CLOUDINARY_API_KEY'),
                api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
                secure     = True
            )
            cloudinary.uploader.destroy(img.public_id)
        except Exception as e:
            print(f'Cloudinary delete error: {e}')
    else:
        filepath = os.path.join(Config.UPLOAD_FOLDER, img.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    db.session.delete(img)
    db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin.gallery'))