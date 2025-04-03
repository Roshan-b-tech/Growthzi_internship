from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.order import Order
from ..models.cart import Cart
from ..models.user import User
from ..models.coupon import Coupon
from .. import jwt
from ..tasks import send_order_confirmation, send_order_status_update

orders_bp = Blueprint('orders', __name__)

def admin_required():
    current_user_id = get_jwt_identity()
    user = User.get_by_id(jwt.db, current_user_id)
    if not user or user.role != 'admin':
        return False
    return True

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    cart = Cart.get_by_user_id(jwt.db, current_user_id)
    
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    data = request.get_json()
    if 'shipping_address' not in data:
        return jsonify({'error': 'Missing shipping address'}), 400
    
    try:
        # Apply coupon if provided
        total_amount = cart.get_total(jwt.db)
        if 'coupon_code' in data:
            coupon = Coupon.get_by_code(jwt.db, data['coupon_code'])
            if coupon and coupon.is_valid():
                discount = coupon.calculate_discount(total_amount)
                total_amount -= discount
                coupon.increment_usage(jwt.db)
            else:
                return jsonify({'error': 'Invalid or expired coupon'}), 400
        
        # Create order
        order_id = Order.create_from_cart(
            jwt.db,
            current_user_id,
            cart,
            data['shipping_address']
        )
        
        # Send order confirmation email
        send_order_confirmation.delay(current_user_id, order_id)
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    orders, total = Order.get_by_user_id(jwt.db, current_user_id, page, per_page)
    
    return jsonify({
        'orders': [order.to_dict() for order in orders],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    current_user_id = get_jwt_identity()
    order = Order.get_by_id(jwt.db, order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if user is authorized to view this order
    if order.user_id != current_user_id and not admin_required():
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(order.to_dict()), 200

@orders_bp.route('/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    if not admin_required():
        return jsonify({'error': 'Admin privileges required'}), 403
    
    order = Order.get_by_id(jwt.db, order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    data = request.get_json()
    if 'status' not in data:
        return jsonify({'error': 'Missing status'}), 400
    
    try:
        old_status = order.status
        order.update_status(jwt.db, data['status'])
        
        # Send status update email if status changed
        if old_status != order.status:
            send_order_status_update.delay(order.user_id, order_id, order.status)
        
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@orders_bp.route('/<order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    current_user_id = get_jwt_identity()
    order = Order.get_by_id(jwt.db, order_id)
    
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    # Check if user is authorized to cancel this order
    if order.user_id != current_user_id and not admin_required():
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Only allow cancellation of pending orders
    if order.status != Order.STATUS_PENDING:
        return jsonify({'error': 'Order cannot be cancelled'}), 400
    
    try:
        order.update_status(jwt.db, Order.STATUS_CANCELLED)
        
        # Send cancellation email
        send_order_status_update.delay(order.user_id, order_id, order.status)
        
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 