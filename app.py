from flask import Flask, send_from_directory, render_template
from config import Config
from extensions import db, login_manager, limiter
from datetime import datetime
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    from models.user_model         import User
    from models.measurement_model  import Measurement
    from models.order_model        import Order
    from models.gallery_model      import GalleryImage
    from models.product_model      import (Product, ProductOrder,
                                           WalkInCustomer,
                                           WalkInMeasurement)
    from models.feedback_model     import Feedback
    from models.appointment_model  import Appointment
    from models.notification_model import Notification

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        import re
        if not re.match(r'^[\w\-\.]+$', filename):
            return "Invalid filename", 404
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.context_processor
    def inject_globals():
        unread = 0
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                unread = Notification.query.filter_by(
                    user_id = current_user.id,
                    is_read = False
                ).count()
        except Exception:
            unread = 0
        return {
            'now':          datetime.now(),
            'unread_count': unread
        }

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options']  = 'nosniff'
        response.headers['X-Frame-Options']         = 'SAMEORIGIN'
        response.headers['X-XSS-Protection']        = '1; mode=block'
        response.headers['Referrer-Policy']         = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy']      = 'geolocation=(), microphone=()'
        if not app.debug:
            response.headers['Strict-Transport-Security'] = \
                'max-age=31536000; includeSubDomains'
        return response

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
def server_error(e):
    import traceback
    print('500 ERROR:', traceback.format_exc())
    return render_template('errors/500.html'), 500

    @app.errorhandler(429)
    def rate_limit_handler(e):
        return render_template('errors/429.html'), 429

    from routes.auth_routes         import auth
    from routes.customer_routes     import customer
    from routes.admin_routes        import admin
    from routes.order_routes        import order
    from routes.measurement_routes  import measurement
    from routes.shop_routes         import shop
    from routes.admin_shop_routes   import admin_shop
    from routes.print_routes        import print_bp
    from routes.feedback_routes     import feedback_bp
    from routes.appointment_routes  import appointment_bp
    from routes.lang_routes         import lang_bp
    from routes.notification_routes import notification_bp

    app.register_blueprint(auth)
    app.register_blueprint(customer)
    app.register_blueprint(admin)
    app.register_blueprint(order)
    app.register_blueprint(measurement)
    app.register_blueprint(shop)
    app.register_blueprint(admin_shop)
    app.register_blueprint(print_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(lang_bp)
    app.register_blueprint(notification_bp)

    with app.app_context():
        db.create_all()
        create_default_admin(app)

    # create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app


def create_default_admin(app):
    from models.user_model import User
    with app.app_context():
        existing = User.query.filter_by(email='admin@kalamu.com').first()
        if not existing:
            admin_user = User(
                full_name = 'CEO Admin',
                email     = 'admin@kalamu.com',
                phone     = '07082815719',
                role      = 'admin'
            )
            admin_user.set_password('Muhammad9891@')
            db.session.add(admin_user)
            db.session.commit()
            print('=' * 50)
            print('ADMIN CREATED SUCCESSFULLY')
            print('Email:    admin@kalamu.com')
            print('Password: Muhammad9891@')
            print('=' * 50)
        else:
            print('Admin already exists — skipping creation')


application = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port, debug=False)