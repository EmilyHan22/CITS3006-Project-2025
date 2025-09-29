from flask import Flask
from models import db, User
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_db(app, reset=False):
    """Initialize the database with tables. If reset=True, drop and recreate."""
    with app.app_context():
        if reset:
            db.drop_all()
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            admin_user = User(
                email='admin@example.com',
                password='admin123',
                display_name='Douglas McGee',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@example.com / admin123")

def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter_by(email=email).first()

def create_user(email, password, display_name, role='user'):
    """Create a new user"""
    user = User(email=email, password=password, display_name=display_name, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    return User.query.get(user_id)


