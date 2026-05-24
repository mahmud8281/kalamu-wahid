from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from extensions import db, limiter
from models.feedback_model import Feedback
from utils.sanitize import clean

feedback_bp = Blueprint('feedback_bp', __name__)

CATEGORIES = ['Tailoring', 'Shop', 'Website', 'Delivery',
              'Measurements', 'Payment', 'General']

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name     = clean(request.form.get('name', ''))
        email    = clean(request.form.get('email', ''))
        category = clean(request.form.get('category', ''))
        message  = clean(request.form.get('message', ''))

        if not name or not message or not category:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('feedback_bp.feedback'))

        if category not in CATEGORIES:
            flash('Invalid category selected.', 'danger')
            return redirect(url_for('feedback_bp.feedback'))

        if len(message) > 1000:
            flash('Message is too long. Maximum 1000 characters.', 'danger')
            return redirect(url_for('feedback_bp.feedback'))

        f = Feedback(
            name     = name,
            email    = email,
            category = category,
            message  = message,
            user_id  = current_user.id
                       if current_user.is_authenticated else None
        )
        db.session.add(f)
        db.session.commit()
        flash('Thank you for your feedback! We appreciate it.', 'success')
        return redirect(url_for('feedback_bp.feedback'))

    all_feedback     = Feedback.query.order_by(
        Feedback.created_at.desc()).all()
    category_filter  = request.args.get('category', 'all')[:50]
    if category_filter != 'all':
        all_feedback = [f for f in all_feedback
                        if f.category == category_filter]

    counts = {cat: Feedback.query.filter_by(category=cat).count()
              for cat in CATEGORIES}

    return render_template('feedback.html',
                           feedback_list    = all_feedback,
                           categories       = CATEGORIES,
                           current_category = category_filter,
                           counts           = counts,
                           total            = Feedback.query.count())

@feedback_bp.route('/feedback/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('feedback_bp.feedback'))
    f = Feedback.query.get_or_404(feedback_id)
    db.session.delete(f)
    db.session.commit()
    flash('Feedback deleted.', 'success')
    return redirect(url_for('feedback_bp.feedback'))