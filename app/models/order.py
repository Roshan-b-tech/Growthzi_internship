from datetime import datetime
from bson import ObjectId

class OrderItem:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }
    
    @staticmethod
    def from_dict(data):
        return OrderItem(
            product_id=data['product_id'],
            quantity=data['quantity'],
            price=data['price']
        )

class Order:
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    
    def __init__(self, user_id, items, total_amount, shipping_address):
        self.user_id = user_id
        self.items = items
        self.total_amount = total_amount
        self.shipping_address = shipping_address
        self.status = self.STATUS_PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total_amount': self.total_amount,
            'shipping_address': self.shipping_address,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        order = Order(
            user_id=data['user_id'],
            items=[OrderItem.from_dict(item) for item in data['items']],
            total_amount=data['total_amount'],
            shipping_address=data['shipping_address']
        )
        order.status = data['status']
        order.created_at = data['created_at']
        order.updated_at = data['updated_at']
        return order
    
    @staticmethod
    def get_by_id(db, order_id):
        order_data = db.orders.find_one({'_id': ObjectId(order_id)})
        if order_data:
            return Order.from_dict(order_data)
        return None
    
    @staticmethod
    def get_by_user_id(db, user_id, page=1, per_page=10):
        skip = (page - 1) * per_page
        orders = list(db.orders.find({'user_id': user_id}).skip(skip).limit(per_page))
        total = db.orders.count_documents({'user_id': user_id})
        return [Order.from_dict(order) for order in orders], total
    
    def update_status(self, db, new_status):
        if new_status not in [self.STATUS_PENDING, self.STATUS_PROCESSING, 
                            self.STATUS_SHIPPED, self.STATUS_DELIVERED, 
                            self.STATUS_CANCELLED]:
            raise ValueError('Invalid status')
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        db.orders.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'status': self.status, 'updated_at': self.updated_at}}
        )
    
    def save(self, db):
        order_data = self.to_dict()
        result = db.orders.insert_one(order_data)
        return str(result.inserted_id)
    
    @staticmethod
    def create_from_cart(db, user_id, cart, shipping_address):
        items = []
        total_amount = 0
        
        for cart_item in cart.items:
            product = Product.get_by_id(db, cart_item.product_id)
            if product and product.stock >= cart_item.quantity:
                items.append(OrderItem(
                    product_id=product._id,
                    quantity=cart_item.quantity,
                    price=product.price
                ))
                total_amount += product.price * cart_item.quantity
                product.update_stock(db, -cart_item.quantity)
            else:
                raise ValueError(f'Insufficient stock for product {product.name}')
        
        order = Order(user_id, items, total_amount, shipping_address)
        order_id = order.save(db)
        cart.clear()
        cart.save(db)
        return order_id 