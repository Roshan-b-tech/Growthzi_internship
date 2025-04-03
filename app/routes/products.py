from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.product import Product
from ..models.user import User
from .. import jwt
import json

products_bp = Blueprint('products', __name__)

def admin_required():
    current_user_id = get_jwt_identity()
    user = User.get_by_id(jwt.db, current_user_id)
    if not user or user.role != 'admin':
        return False
    return True

@products_bp.route('/', methods=['GET'])
def get_products():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Try to get from cache
    cache_key = f'products_page_{page}_per_page_{per_page}'
    cached_data = current_app.redis.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    # If not in cache, get from database
    products, total = Product.get_all(current_app.db, page=page, per_page=per_page)
    
    result = {
        'products': [product.to_dict() for product in products],
        'total': total,
        'page': page,
        'per_page': per_page
    }
    
    # Cache the result
    current_app.redis.setex(cache_key, 300, json.dumps(result))  # Cache for 5 minutes
    
    return jsonify(result)

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    # Try to get from cache
    cache_key = f'product_{product_id}'
    cached_data = current_app.redis.get(cache_key)
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    product = Product.get_by_id(current_app.db, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    result = product.to_dict()
    
    # Cache the result
    current_app.redis.setex(cache_key, 300, json.dumps(result))  # Cache for 5 minutes
    
    return jsonify(result)

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'description', 'price', 'stock', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    product = Product(
        name=data['name'],
        description=data['description'],
        price=float(data['price']),
        stock=int(data['stock']),
        category=data['category'],
        image_url=data.get('image_url')
    )
    
    product.save(current_app.db)
    
    # Clear product list cache
    current_app.redis.delete(*current_app.redis.keys('products_page_*'))
    
    return jsonify(product.to_dict()), 201

@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    product = Product.get_by_id(current_app.db, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update fields
    if 'name' in data:
        product.name = data['name']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = float(data['price'])
    if 'category' in data:
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
    
    product.save(current_app.db)
    
    # Clear caches
    current_app.redis.delete(f'product_{product_id}')
    current_app.redis.delete(*current_app.redis.keys('products_page_*'))
    
    return jsonify(product.to_dict())

@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    product = Product.get_by_id(current_app.db, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    product.delete(current_app.db)
    
    # Clear caches
    current_app.redis.delete(f'product_{product_id}')
    current_app.redis.delete(*current_app.redis.keys('products_page_*'))
    
    return '', 204

@products_bp.route('/<product_id>/stock', methods=['PUT'])
@jwt_required()
def update_stock(product_id):
    if not admin_required():
        return jsonify({'error': 'Admin access required'}), 403
    
    product = Product.get_by_id(current_app.db, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    data = request.get_json()
    if not data or 'stock' not in data:
        return jsonify({'error': 'Stock value required'}), 400
    
    try:
        stock = int(data['stock'])
        if stock < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid stock value'}), 400
    
    product.stock = stock
    product.save(current_app.db)
    
    # Clear caches
    current_app.redis.delete(f'product_{product_id}')
    current_app.redis.delete(*current_app.redis.keys('products_page_*'))
    
    return jsonify(product.to_dict()) 