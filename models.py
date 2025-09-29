from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import codecs

db = SQLAlchemy()

def rot13_encrypt(text):
    """Encrypt text using ROT13"""
    return codecs.encode(text, 'rot13')

def rot13_decrypt(text):
    """Decrypt text using ROT13 (ROT13 is symmetric)"""
    return codecs.encode(text, 'rot13')

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email, password, display_name, role='user'):
        self.email = email
        self.password = rot13_encrypt(password)
        self.display_name = display_name
        self.role = role
    
    def check_password(self, password):
        """Check if provided password matches the stored ROT13 encrypted password"""
        return rot13_decrypt(self.password) == password
    
    def to_dict(self):
        """Convert user object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


