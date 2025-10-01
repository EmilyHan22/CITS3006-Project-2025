from flask import Flask
from models import db, User, Client, AreaDataPoint, BarDataPoint, PieSlice
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
                password='ADmIn0192',
                display_name='Douglas McGee',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@example.com / admin123")

        # Seed clients if empty
        if Client.query.count() == 0:
            clients = [
                Client(name='Tiger Nixon', position='System Architect', office='Edinburgh', age=61, start_date='2011/04/25', salary='$320,800'),
                Client(name='Garrett Winters', position='Accountant', office='Tokyo', age=63, start_date='2011/07/25', salary='$170,750'),
                Client(name='Ashton Cox', position='Junior Technical Author', office='San Francisco', age=66, start_date='2009/01/12', salary='$86,000'),
                Client(name='Cedric Kelly', position='Senior Javascript Developer', office='Edinburgh', age=22, start_date='2012/03/29', salary='$433,060'),
                Client(name='Airi Satou', position='Accountant', office='Tokyo', age=33, start_date='2008/11/28', salary='$162,700'),
                Client(name='Brielle Williamson', position='Integration Specialist', office='New York', age=61, start_date='2012/12/02', salary='$372,000'),
                Client(name='Herrod Chandler', position='Sales Assistant', office='San Francisco', age=59, start_date='2012/08/06', salary='$137,500'),
                Client(name='Rhona Davidson', position='Integration Specialist', office='Tokyo', age=55, start_date='2010/10/14', salary='$327,900'),
                Client(name='Colleen Hurst', position='Javascript Developer', office='San Francisco', age=39, start_date='2009/09/15', salary='$205,500'),
                Client(name='Sonya Frost', position='Software Engineer', office='Edinburgh', age=23, start_date='2008/12/13', salary='$103,600'),
            ]
            db.session.add_all(clients)
            db.session.commit()
            print("Seeded clients table")

        # Seed additional non-admin users
        extra_users = [
            ('user1@example.com', 'password1', 'Alex Johnson', 'user'),
            ('user2@example.com', 'password2', 'Sam Lee', 'user'),
        ]
        for email, pwd, name, role in extra_users:
            if not User.query.filter_by(email=email).first():
                db.session.add(User(email=email, password=pwd, display_name=name, role=role))
        db.session.commit()

        # Seed area chart
        if AreaDataPoint.query.count() == 0:
            area_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            area_values = [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000]
            points = [AreaDataPoint(label=l, value=v) for l, v in zip(area_labels, area_values)]
            db.session.add_all(points)
            db.session.commit()
            print("Seeded area chart data")

        # Seed bar chart
        if BarDataPoint.query.count() == 0:
            bar_labels = ['January', 'February', 'March', 'April', 'May', 'June']
            bar_values = [4215, 5312, 6251, 7841, 9821, 14984]
            points = [BarDataPoint(label=l, value=v) for l, v in zip(bar_labels, bar_values)]
            db.session.add_all(points)
            db.session.commit()
            print("Seeded bar chart data")

        # Seed pie chart
        if PieSlice.query.count() == 0:
            slices = [
                PieSlice(label='Direct', value=55),
                PieSlice(label='Social', value=30),
                PieSlice(label='Referral', value=15),
            ]
            db.session.add_all(slices)
            db.session.commit()
            print("Seeded pie chart data")

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





