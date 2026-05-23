from flask import Flask, send_from_directory
from config import Config
from extensions import db, login_manager
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from models.user_model import User
    from models.measurement_model import Measurement
    from models.order_model import Order
    from models.gallery_model import GalleryImage
    from models.product_model import Product, ProductOrder, WalkInCustomer, WalkInMeasurement

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    from routes.auth_routes import auth
    from routes.customer_routes import customer
    from routes.admin_routes import admin
    from routes.order_routes import order
    from routes.measurement_routes import measurement
    from routes.shop_routes import shop
    from routes.admin_shop_routes import admin_shop
    from routes.print_routes import print_bp

    app.register_blueprint(auth)
    app.register_blueprint(customer)
    app.register_blueprint(admin)
    app.register_blueprint(order)
    app.register_blueprint(measurement)
    app.register_blueprint(shop)
    app.register_blueprint(admin_shop)
    app.register_blueprint(print_bp)

    with app.app_context():
        db.create_all()
        create_default_admin(app)

    return app

def create_default_admin(app):
    from models.user_model import User
    with app.app_context():
        if not User.query.filter_by(role='admin').first():
            admin = User(
                full_name = 'CEO Admin',
                email     = 'admin@kalamu.com',
                phone     = '08000000000',
                role      = 'admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('=' * 40)
            print('Admin created!')
            print('Email:    admin@kalamu.com')
            print('Password: admin123')
            print('=' * 40)

application = create_app()

if __name__ == '__main__':
    application.run(debug=True)