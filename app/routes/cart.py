from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.cart import Cart
from ..models.product import Product

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    current_user_id = get_jwt_identity()
    cart = Cart.get_by_user_id(current_app.db, current_user_id)
    
    if not cart:
        cart = Cart(current_user_id)
        cart.save(current_app.db)
    
    return jsonify(cart.to_dict())

@cart_bp.route('/', methods=['POST'])
@jwt_required()
def add_to_cart():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'Missing product_id or quantity'}), 400
    
    try:
        quantity = int(data['quantity'])
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    # Check if product exists
    product = Product.get_by_id(current_app.db, data['product_id'])
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if product is in stock
    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400
    
    # Get or create cart
    cart = Cart.get_by_user_id(current_app.db, current_user_id)
    if not cart:
        cart = Cart(current_user_id)
    
    # Add item to cart
    cart.add_item(data['product_id'], quantity)
    cart.save(current_app.db)
    
    return jsonify(cart.to_dict()), 201

@cart_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(product_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return jsonify({'error': 'Missing quantity'}), 400
    
    try:
        quantity = int(data['quantity'])
        if quantity < 0:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid quantity'}), 400
    
    # Check if product exists
    product = Product.get_by_id(current_app.db, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Get cart
    cart = Cart.get_by_user_id(current_app.db, current_user_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    # If quantity is 0, remove the item
    if quantity == 0:
        cart.remove_item(product_id)
    else:
        # Check if product is in stock
        if product.stock < quantity:
            return jsonify({'error': 'Not enough stock available'}), 400
        cart.update_item_quantity(product_id, quantity)
    
    cart.save(current_app.db)
    return jsonify(cart.to_dict())

@cart_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    current_user_id = get_jwt_identity()
    
    # Get cart
    cart = Cart.get_by_user_id(current_app.db, current_user_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart.remove_item(product_id)
    cart.save(current_app.db)
    
    return jsonify(cart.to_dict())

@cart_bp.route('/', methods=['DELETE'])
@jwt_required()
def clear_cart():
    current_user_id = get_jwt_identity()
    
    # Get cart
    cart = Cart.get_by_user_id(current_app.db, current_user_id)
    if not cart:
        return jsonify({'error': 'Cart not found'}), 404
    
    cart.clear()
    cart.save(current_app.db)
    
    return jsonify(cart.to_dict()) 