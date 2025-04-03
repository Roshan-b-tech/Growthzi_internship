from datetime import datetime
from bson import ObjectId

class Coupon:
    def __init__(self, code, discount_type, discount_value, min_purchase=0, 
                 max_discount=None, start_date=None, end_date=None, 
                 usage_limit=None, used_count=0):
        self.code = code
        self.discount_type = discount_type  # 'percentage' or 'fixed'
        self.discount_value = discount_value
        self.min_purchase = min_purchase
        self.max_discount = max_discount
        self.start_date = start_date or datetime.utcnow()
        self.end_date = end_date
        self.usage_limit = usage_limit
        self.used_count = used_count
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'code': self.code,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'min_purchase': self.min_purchase,
            'max_discount': self.max_discount,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        coupon = Coupon(
            code=data['code'],
            discount_type=data['discount_type'],
            discount_value=data['discount_value'],
            min_purchase=data.get('min_purchase', 0),
            max_discount=data.get('max_discount'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            usage_limit=data.get('usage_limit'),
            used_count=data.get('used_count', 0)
        )
        coupon.created_at = data['created_at']
        coupon.updated_at = data['updated_at']
        return coupon
    
    @staticmethod
    def get_by_code(db, code):
        coupon_data = db.coupons.find_one({'code': code})
        if coupon_data:
            return Coupon.from_dict(coupon_data)
        return None
    
    def is_valid(self):
        now = datetime.utcnow()
        
        # Check if coupon has expired
        if self.end_date and now > self.end_date:
            return False
        
        # Check if coupon has started
        if self.start_date and now < self.start_date:
            return False
        
        # Check usage limit
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True
    
    def calculate_discount(self, total_amount):
        if not self.is_valid():
            return 0
        
        if total_amount < self.min_purchase:
            return 0
        
        if self.discount_type == 'percentage':
            discount = (total_amount * self.discount_value) / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        else:
            return self.discount_value
    
    def increment_usage(self, db):
        self.used_count += 1
        self.updated_at = datetime.utcnow()
        db.coupons.update_one(
            {'code': self.code},
            {'$set': {'used_count': self.used_count, 'updated_at': self.updated_at}}
        )
    
    def save(self, db):
        coupon_data = self.to_dict()
        db.coupons.update_one(
            {'code': self.code},
            {'$set': coupon_data},
            upsert=True
        )
    
    @staticmethod
    def get_all(db, page=1, per_page=10):
        skip = (page - 1) * per_page
        coupons = list(db.coupons.find().skip(skip).limit(per_page))
        total = db.coupons.count_documents({})
        return [Coupon.from_dict(coupon) for coupon in coupons], total 