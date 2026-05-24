from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.notification_model import Notification

notification_bp = Blueprint('notification_bp', __name__)

@notification_bp.route('/notifications')
@login_required
def all_notifications():
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    # mark all as read
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return render_template('notifications.html',
                           notifications=notifications)

@notification_bp.route('/notifications/mark-read/<int:notif_id>')
@login_required
def mark_read(notif_id):
    n = Notification.query.get_or_404(notif_id)
    if n.user_id == current_user.id:
        n.is_read = True
        db.session.commit()
    return redirect(n.link or url_for('customer.dashboard'))

@notification_bp.route('/notifications/count')
@login_required
def unread_count():
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({'count': count})

@notification_bp.route('/notifications/clear')
@login_required
def clear_all():
    Notification.query.filter_by(
        user_id=current_user.id
    ).delete()
    db.session.commit()
    return redirect(url_for('notification_bp.all_notifications'))