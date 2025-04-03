from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
from redis import Redis
from celery import Celery
from .config import Config
import os

# Initialize extensions
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
celery = Celery()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize MongoDB
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client.get_database()
    
    # Initialize Redis
    app.redis = Redis.from_url(app.config['REDIS_URL'])
    
    # Initialize extensions
    jwt.init_app(app)
    limiter.init_app(app)
    CORS(app)
    mail.init_app(app)
    
    # Configure Celery
    celery.conf.update(app.config)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.products import products_bp
    from .routes.orders import orders_bp
    from .routes.coupons import coupons_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(coupons_bp, url_prefix='/api/coupons')
    
    # Root route
    @app.route('/')
    def index():
        return {
            'name': 'E-commerce API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products',
                'orders': '/api/orders',
                'coupons': '/api/coupons'
            }
        }
    
    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # Return no content for favicon requests
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app 