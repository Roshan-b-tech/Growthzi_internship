from datetime import datetime
from bson import ObjectId

class CartItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'quantity': self.quantity
        }
    
    @staticmethod
    def from_dict(data):
        return CartItem(
            product_id=data['product_id'],
            quantity=data['quantity']
        )

class Cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        cart = Cart(data['user_id'])
        cart.items = [CartItem.from_dict(item) for item in data['items']]
        cart.created_at = data['created_at']
        cart.updated_at = data['updated_at']
        return cart
    
    @staticmethod
    def get_by_user_id(db, user_id):
        cart_data = db.carts.find_one({'user_id': user_id})
        if cart_data:
            return Cart.from_dict(cart_data)
        return None
    
    def add_item(self, product_id, quantity):
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                break
        else:
            self.items.append(CartItem(product_id, quantity))
        self.updated_at = datetime.utcnow()
    
    def remove_item(self, product_id):
        self.items = [item for item in self.items if item.product_id != product_id]
        self.updated_at = datetime.utcnow()
    
    def update_item_quantity(self, product_id, quantity):
        for item in self.items:
            if item.product_id == product_id:
                item.quantity = quantity
                break
        self.updated_at = datetime.utcnow()
    
    def clear(self):
        self.items = []
        self.updated_at = datetime.utcnow()
    
    def save(self, db):
        cart_data = self.to_dict()
        db.carts.update_one(
            {'user_id': self.user_id},
            {'$set': cart_data},
            upsert=True
        )
    
    def get_total(self, db):
        total = 0
        for item in self.items:
            product = Product.get_by_id(db, item.product_id)
            if product:
                total += product.price * item.quantity
        return total 