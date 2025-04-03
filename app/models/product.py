from datetime import datetime
from bson import ObjectId

class Product:
    def __init__(self, name, description, price, category, stock, image_url=None):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.stock = stock
        self.image_url = image_url
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'stock': self.stock,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            category=data['category'],
            stock=data['stock'],
            image_url=data.get('image_url')
        )
        product.created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        product.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat()))
        if '_id' in data:
            product._id = data['_id']
        return product
    
    @staticmethod
    def get_by_id(db, product_id):
        product_data = db.products.find_one({'_id': ObjectId(product_id)})
        if product_data:
            return Product.from_dict(product_data)
        return None
    
    @staticmethod
    def get_all(db, page=1, per_page=10):
        skip = (page - 1) * per_page
        query = {}
        
        products = list(db.products.find(query).skip(skip).limit(per_page))
        total = db.products.count_documents(query)
        
        return [Product.from_dict(product) for product in products], total
    
    def save(self, db):
        product_data = self.to_dict()
        if hasattr(self, '_id'):
            db.products.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': product_data}
            )
        else:
            result = db.products.insert_one(product_data)
            self._id = result.inserted_id
    
    def delete(self, db):
        if hasattr(self, '_id'):
            db.products.delete_one({'_id': ObjectId(self._id)})
    
    def update_stock(self, db, quantity):
        self.stock += quantity
        self.updated_at = datetime.utcnow()
        db.products.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': {'stock': self.stock, 'updated_at': self.updated_at.isoformat()}}
        ) 