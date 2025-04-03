from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.coupon import Coupon
from ..models.user import User
from .. import jwt
from datetime import datetime, timedelta

coupons_bp = Blueprint('coupons', __name__)

def admin_required():
    current_user_id = get_jwt_identity()
    user = User.get_by_id(jwt.db, current_user_id)
    if not user or user.role != 'admin':
        return False
    return True

@coupons_bp.route('/', methods=['POST'])
@jwt_required()
def create_coupon():
    if not admin_required():
        return jsonify({'error': 'Admin privileges required'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ['code', 'discount_type', 'discount_value']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate discount type
    if data['discount_type'] not in ['percentage', 'fixed']:
        return jsonify({'error': 'Invalid discount type'}), 400
    
    # Validate discount value
    try:
        discount_value = float(data['discount_value'])
        if discount_value <= 0:
            raise ValueError('Discount value must be positive')
        if data['discount_type'] == 'percentage' and discount_value > 100:
            raise ValueError('Percentage discount cannot exceed 100%')
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    
    # Parse dates if provided
    try:
        start_date = datetime.fromisoformat(data['start_date']) if 'start_date' in data else None
        end_date = datetime.fromisoformat(data['end_date']) if 'end_date' in data else None
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Create coupon
    coupon = Coupon(
        code=data['code'],
        discount_type=data['discount_type'],
        discount_value=discount_value,
        min_purchase=float(data.get('min_purchase', 0)),
        max_discount=float(data.get('max_discount')) if 'max_discount' in data else None,
        start_date=start_date,
        end_date=end_date,
        usage_limit=int(data.get('usage_limit')) if 'usage_limit' in data else None
    )
    
    # Check if coupon code already exists
    if Coupon.get_by_code(jwt.db, coupon.code):
        return jsonify({'error': 'Coupon code already exists'}), 409
    
    coupon.save(jwt.db)
    
    return jsonify(coupon.to_dict()), 201

@coupons_bp.route('/', methods=['GET'])
@jwt_required()
def get_coupons():
    if not admin_required():
        return jsonify({'error': 'Admin privileges required'}), 403
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    coupons, total = Coupon.get_all(jwt.db, page, per_page)
    
    return jsonify({
        'coupons': [coupon.to_dict() for coupon in coupons],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@coupons_bp.route('/<code>', methods=['GET'])
def get_coupon(code):
    coupon = Coupon.get_by_code(jwt.db, code)
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    
    return jsonify(coupon.to_dict()), 200

@coupons_bp.route('/validate', methods=['POST'])
def validate_coupon():
    data = request.get_json()
    if 'code' not in data:
        return jsonify({'error': 'Missing coupon code'}), 400
    
    coupon = Coupon.get_by_code(jwt.db, data['code'])
    if not coupon:
        return jsonify({'error': 'Invalid coupon code'}), 404
    
    if not coupon.is_valid():
        return jsonify({'error': 'Coupon is not valid'}), 400
    
    return jsonify({
        'valid': True,
        'coupon': coupon.to_dict()
    }), 200

@coupons_bp.route('/<code>', methods=['PUT'])
@jwt_required()
def update_coupon(code):
    if not admin_required():
        return jsonify({'error': 'Admin privileges required'}), 403
    
    coupon = Coupon.get_by_code(jwt.db, code)
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'discount_type' in data:
        if data['discount_type'] not in ['percentage', 'fixed']:
            return jsonify({'error': 'Invalid discount type'}), 400
        coupon.discount_type = data['discount_type']
    
    if 'discount_value' in data:
        try:
            discount_value = float(data['discount_value'])
            if discount_value <= 0:
                raise ValueError('Discount value must be positive')
            if coupon.discount_type == 'percentage' and discount_value > 100:
                raise ValueError('Percentage discount cannot exceed 100%')
            coupon.discount_value = discount_value
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    
    if 'min_purchase' in data:
        try:
            coupon.min_purchase = float(data['min_purchase'])
        except ValueError:
            return jsonify({'error': 'Invalid minimum purchase amount'}), 400
    
    if 'max_discount' in data:
        try:
            coupon.max_discount = float(data['max_discount']) if data['max_discount'] else None
        except ValueError:
            return jsonify({'error': 'Invalid maximum discount amount'}), 400
    
    if 'start_date' in data:
        try:
            coupon.start_date = datetime.fromisoformat(data['start_date'])
        except ValueError:
            return jsonify({'error': 'Invalid start date format'}), 400
    
    if 'end_date' in data:
        try:
            coupon.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        except ValueError:
            return jsonify({'error': 'Invalid end date format'}), 400
    
    if 'usage_limit' in data:
        try:
            coupon.usage_limit = int(data['usage_limit']) if data['usage_limit'] else None
        except ValueError:
            return jsonify({'error': 'Invalid usage limit'}), 400
    
    coupon.save(jwt.db)
    
    return jsonify(coupon.to_dict()), 200

@coupons_bp.route('/<code>', methods=['DELETE'])
@jwt_required()
def delete_coupon(code):
    if not admin_required():
        return jsonify({'error': 'Admin privileges required'}), 403
    
    coupon = Coupon.get_by_code(jwt.db, code)
    if not coupon:
        return jsonify({'error': 'Coupon not found'}), 404
    
    jwt.db.coupons.delete_one({'code': code})
    
    return jsonify({'message': 'Coupon deleted successfully'}), 200 