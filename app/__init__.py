from flask import Flask, send_from_directory, jsonify
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
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize extensions
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0"
)
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
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.products import products_bp
    from .routes.orders import orders_bp
    from .routes.coupons import coupons_bp
    from .routes.cart import cart_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(coupons_bp, url_prefix='/api/coupons')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    
    # Token blacklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_data):
        jti = jwt_data['jti']
        return app.db.token_blocklist.find_one({'jti': jti}) is not None
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to the E-commerce API',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products',
                'cart': '/api/cart',
                'orders': '/api/orders',
                'coupons': '/api/coupons'
            }
        })
    
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