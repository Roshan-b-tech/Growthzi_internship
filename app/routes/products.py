from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.product import Product
from ..models.user import User
from .. import jwt
import json
from bson import ObjectId

products_bp = Blueprint('products', __name__)

def admin_required():
    current_user_id = get_jwt_identity()
    user = User.get_by_id(jwt.db, current_user_id)
    if not user or user.role != 'admin':
        return False
    return True

@products_bp.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    products, total = Product.get_all(current_app.db, page, per_page)
    return jsonify({
        'products': [product.to_dict() for product in products],
        'total': total,
        'page': page,
        'per_page': per_page
    })

@products_bp.route('/featured', methods=['GET'])
def get_featured_products():
    # For now, just return the first 5 products as featured
    # In a real application, you would have a 'featured' flag in the product model
    products = Product.get_all(current_app.db, 1, 5)[0]
    return jsonify({
        'products': [product.to_dict() for product in products]
    })

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'name' not in data or 'price' not in data or 'stock' not in data or 'category' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        price = float(data['price'])
        stock = int(data['stock'])
        if price <= 0 or stock < 0:
            return jsonify({'error': 'Price and stock must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid price or stock value'}), 400
    
    product = Product(
        name=data['name'],
        price=price,
        stock=stock,
        category=data['category'],
        description=data.get('description', ''),
        image_url=data.get('image_url')
    )
    
    product.save(current_app.db)
    return jsonify(product.to_dict()), 201

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.get_by_id(current_app.db, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(product.to_dict())
    except:
        return jsonify({'error': 'Invalid product ID'}), 400

@products_bp.route('/', methods=['PUT'])
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