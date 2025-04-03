from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User:
    def __init__(self, email, password, name, role='customer'):
        self.email = email
        self.password = password  # Store plain password temporarily
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @staticmethod
    def from_dict(data):
        user = User(
            email=data['email'],
            password='',  # Password is not returned in dict
            name=data['name'],
            role=data.get('role', 'customer')
        )
        user.password = data['password']  # This is already hashed
        user.created_at = datetime.fromisoformat(data.get('created_at', datetime.utcnow().isoformat()))
        user.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.utcnow().isoformat()))
        if '_id' in data:
            user._id = data['_id']
        return user
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @staticmethod
    def get_by_id(db, user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    @staticmethod
    def get_by_email(db, email):
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def save(self, db):
        user_data = self.to_dict()
        user_data['password'] = generate_password_hash(self.password)
        if hasattr(self, '_id'):
            db.users.update_one(
                {'_id': ObjectId(self._id)},
                {'$set': user_data}
            )
        else:
            result = db.users.insert_one(user_data)
            self._id = result.inserted_id
    
    def update(self, db):
        user_data = self.to_dict()
        if hasattr(self, 'password') and self.password:
            user_data['password'] = generate_password_hash(self.password)
        db.users.update_one(
            {'_id': ObjectId(self._id)},
            {'$set': user_data}
        ) 