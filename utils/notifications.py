from extensions import db
from models.notification_model import Notification
from models.user_model import User

def notify(user_id, title, message, type='info', link=None):
    """Send a notification to a specific user."""
    n = Notification(
        user_id = user_id,
        title   = title,
        message = message,
        type    = type,
        link    = link
    )
    db.session.add(n)
    db.session.commit()

def notify_all_admins(title, message, type='info', link=None):
    """Send a notification to all admin and staff users."""
    admins = User.query.filter(
        User.role.in_(['admin', 'staff'])
    ).all()
    for admin in admins:
        n = Notification(
            user_id = admin.id,
            title   = title,
            message = message,
            type    = type,
            link    = link
        )
        db.session.add(n)
    db.session.commit()

def notify_order_placed(order):
    """Notify all admins when a new tailoring order is placed."""
    notify_all_admins(
        title   = f'🧵 New Order #{order.id}',
        message = (f'{order.user.full_name} placed a new '
                   f'{order.style_type} order worth '
                   f'₦{order.amount:,.0f}.'),
        type    = 'order',
        link    = '/admin/orders'
    )

def notify_order_status(order):
    """Notify customer when their order status changes."""
    messages = {
        'In Progress': (f'Your Order #{order.id} ({order.style_type}) '
                        f'is now being sewn by our tailor.'),
        'Ready':       (f'Great news! Your Order #{order.id} '
                        f'({order.style_type}) is ready for collection.'),
        'Delivered':   (f'Your Order #{order.id} ({order.style_type}) '
                        f'has been delivered. Thank you!'),
        'Pending':     (f'Your Order #{order.id} ({order.style_type}) '
                        f'has been received and is pending.'),
    }
    icons = {
        'In Progress': '🪡',
        'Ready':       '✅',
        'Delivered':   '🚚',
        'Pending':     '⏳',
    }
    msg  = messages.get(
        order.status,
        f'Your order #{order.id} status changed to {order.status}.'
    )
    icon = icons.get(order.status, '📦')
    notify(
        user_id = order.user_id,
        title   = f'{icon} Order #{order.id} — {order.status}',
        message = msg,
        type    = 'status',
        link    = f'/track-order/{order.id}'
    )

def notify_product_order(product_order):
    """Notify all admins when a new product order is placed."""
    notify_all_admins(
        title   = f'🛍️ New Product Order #{product_order.id}',
        message = (f'{product_order.customer_name} ordered '
                   f'{product_order.quantity} {product_order.unit}(s) '
                   f'of {product_order.product.name}.'),
        type    = 'product',
        link    = '/admin/shop/orders'
    )

def notify_appointment(appointment):
    """Notify all admins when a new appointment is booked."""
    notify_all_admins(
        title   = f'📅 New Appointment #{appointment.id}',
        message = (f'{appointment.name} booked a '
                   f'{appointment.service_type} on '
                   f'{appointment.date} at {appointment.time}.'),
        type    = 'appointment',
        link    = '/admin/appointments'
    )