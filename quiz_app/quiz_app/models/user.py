from flask_login import UserMixin
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.email = user_data['email']
        self.password_hash = user_data['password_hash']
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.photo = user_data.get('photo', None)  # Store photo filename

    @property
    def avatar_url(self):
        if self.photo:
            return f'/static/uploads/{self.photo}'
        else:
            return None

    def update_photo(self, filename):
        from app import users_col
        users_col.update_one({'_id': ObjectId(self.id)}, {'$set': {'photo': filename}})
        self.photo = filename



    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        from app import users_col
        try:
            user_data = users_col.find_one({'_id': ObjectId(user_id)})
            return User(user_data) if user_data else None
        except:
            return None

    @staticmethod
    def get_by_username(username):
        from app import users_col
        user_data = users_col.find_one({'username': username})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_email(email):
        from app import users_col
        user_data = users_col.find_one({'email': email})
        return User(user_data) if user_data else None

    @staticmethod
    def create(username, email, password):
        from app import users_col
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'created_at': datetime.utcnow(),
            'photo': None  # Default no photo
        }
        result = users_col.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

    @staticmethod
    def username_exists(username):
        from app import users_col
        return users_col.find_one({'username': username}) is not None

    @staticmethod
    def email_exists(email):
        from app import users_col
        return users_col.find_one({'email': email}) is not None
