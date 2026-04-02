from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-in-production')
app.permanent_session_lifetime = timedelta(days=7)

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['quiz_app']

# Collections
users_col = db['users']
scores_col = db['scores']
questions_col = db['questions']

# Indexes for performance
users_col.create_index('username', unique=True)
users_col.create_index('email', unique=True)
scores_col.create_index([('username', 1), ('language', 1)])
scores_col.create_index('played_at')
questions_col.create_index([('language', 1), ('level', 1)])

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

from models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Register Blueprints
from routes.auth import auth_bp
from routes.quiz import quiz_bp
from routes.leaderboard import leaderboard_bp
from routes.main import main_bp

app.register_blueprint(auth_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(leaderboard_bp)
app.register_blueprint(main_bp)

# Seed questions on startup if database is empty
from data.seed import seed_questions
seed_questions()

# Jinja2 extras
app.jinja_env.globals['enumerate'] = enumerate

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', '1') == '1')
