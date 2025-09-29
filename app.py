from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from sqlalchemy import text
import os
import json
import codecs
from datetime import datetime
import pathlib
from werkzeug.utils import secure_filename
from sqlalchemy import text

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# ROT13 encryption functions
def rot13_encrypt(text):
    """Encrypt text using ROT13"""
    return codecs.encode(text, 'rot13')

def rot13_decrypt(text):
    """Decrypt text using ROT13 (ROT13 is symmetric)"""
    return codecs.encode(text, 'rot13')

# User model
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

# Database helper functions
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

SAMPLE_ALERTS = [
    {
        'id': 1,
        'type': 'primary',
        'icon': 'fas fa-file-alt',
        'date': 'December 12, 2019',
        'message': 'A new monthly report is ready to download!'
    },
    {
        'id': 2,
        'type': 'success',
        'icon': 'fas fa-donate',
        'date': 'December 7, 2019',
        'message': '$290.29 has been deposited into your account!'
    },
    {
        'id': 3,
        'type': 'warning',
        'icon': 'fas fa-exclamation-triangle',
        'date': 'December 2, 2019',
        'message': "Spending Alert: We've noticed unusually high spending for your account."
    }
]

SAMPLE_MESSAGES = [
    {
        'id': 1,
        'sender': 'Emily Fowler',
        'avatar': 'img/undraw_profile_1.svg',
        'status': 'online',
        'message': "Hi there! I am wondering if you can help me with a problem I've been having.",
        'time': '58m'
    },
    {
        'id': 2,
        'sender': 'Jae Chun',
        'avatar': 'img/undraw_profile_2.svg',
        'status': 'offline',
        'message': 'I have the photos that you ordered last month, how would you like them sent to you?',
        'time': '1d'
    },
    {
        'id': 3,
        'sender': 'Morgan Alvarez',
        'avatar': 'img/undraw_profile_3.svg',
        'status': 'warning',
        'message': "Last month's report looks great, I am very happy with the progress so far, keep up the good work!",
        'time': '2d'
    }
]

SAMPLE_TABLE_DATA = [
    {'id': 1, 'name': 'Tiger Nixon', 'position': 'System Architect', 'office': 'Edinburgh', 'age': 61, 'start_date': '2011/04/25', 'salary': '$320,800'},
    {'id': 2, 'name': 'Garrett Winters', 'position': 'Accountant', 'office': 'Tokyo', 'age': 63, 'start_date': '2011/07/25', 'salary': '$170,750'},
    {'id': 3, 'name': 'Ashton Cox', 'position': 'Junior Technical Author', 'office': 'San Francisco', 'age': 66, 'start_date': '2009/01/12', 'salary': '$86,000'},
    {'id': 4, 'name': 'Cedric Kelly', 'position': 'Senior Javascript Developer', 'office': 'Edinburgh', 'age': 22, 'start_date': '2012/03/29', 'salary': '$433,060'},
    {'id': 5, 'name': 'Airi Satou', 'position': 'Accountant', 'office': 'Tokyo', 'age': 33, 'start_date': '2008/11/28', 'salary': '$162,700'},
    {'id': 6, 'name': 'Brielle Williamson', 'position': 'Integration Specialist', 'office': 'New York', 'age': 61, 'start_date': '2012/12/02', 'salary': '$372,000'},
    {'id': 7, 'name': 'Herrod Chandler', 'position': 'Sales Assistant', 'office': 'San Francisco', 'age': 59, 'start_date': '2012/08/06', 'salary': '$137,500'},
    {'id': 8, 'name': 'Rhona Davidson', 'position': 'Integration Specialist', 'office': 'Tokyo', 'age': 55, 'start_date': '2010/10/14', 'salary': '$327,900'},
    {'id': 9, 'name': 'Colleen Hurst', 'position': 'Javascript Developer', 'office': 'San Francisco', 'age': 39, 'start_date': '2009/09/15', 'salary': '$205,500'},
    {'id': 10, 'name': 'Sonya Frost', 'position': 'Software Engineer', 'office': 'Edinburgh', 'age': 23, 'start_date': '2008/12/13', 'salary': '$103,600'}
]

# Forms
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Account')

class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

# Helper functions
def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if is_logged_in():
        user = get_user_by_id(session['user_id'])
        if user:
            return {
                'email': user.email,
                'first_name': user.display_name.split(' ')[0] if ' ' in user.display_name else user.display_name,
                'last_name': user.display_name.split(' ')[1] if ' ' in user.display_name else '',
                'role': user.role
            }
    return None

# Routes
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            # If the authenticated user is an admin, land them on /admin first
            if user.role == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = get_user_by_email(form.email.data)
        if existing_user:
            flash('Email already registered', 'error')
        else:
            display_name = f"{form.first_name.data} {form.last_name.data}"
            create_user(
                email=form.email.data,
                password=form.password.data,
                display_name=display_name,
                role='user'
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if is_logged_in():
        return redirect(url_for('index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('login'))
    
    return render_template('forgot-password.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('index'))

@app.route('/tables')
def tables():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('tables.html', user=get_current_user(), table_data=SAMPLE_TABLE_DATA)

@app.route('/charts')
def charts():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('charts.html', user=get_current_user())


@app.route('/admin')
def admin():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('admin.html', user=get_current_user())

# === START: intentionally insecure demo routes (for lab) ===

# ANNOUNCEMENTS (stored XSS demo)
ANNOUNCEMENTS = []
# seed demonstration announcement (stored XSS)
ANNOUNCEMENTS.append({
  'id': 1,
  'title': 'Welcome',
  'body': '<script>alert("Stored XSS: admin view")</script>',
  'author': 'seed'
})

@app.route('/announce', methods=['GET', 'POST'])
def announce():
    if not is_logged_in():
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form.get('title', '')
        body = request.form.get('body', '')
        ANNOUNCEMENTS.append({
            'id': len(ANNOUNCEMENTS) + 1,
            'title': title,
            'body': body,
            'author': get_current_user()['email'] if get_current_user() else 'anonymous'
        })
        flash('Announcement posted (stored).', 'success')
        return redirect(url_for('announce'))
    return render_template('announce.html', user=get_current_user(), announcements=ANNOUNCEMENTS)


# PEOPLE SEARCH (SQLi demo)
@app.route('/people-search', methods=['GET', 'POST'])
def people_search():
    if not is_logged_in():
        return redirect(url_for('login'))

    results = []
    query_str = ''
    if request.method == 'POST':
        name_query = request.form.get('name', '')
        # INSECURE: string concatenation -> SQL injection
        query_str = f"SELECT id, email, display_name FROM users WHERE display_name LIKE '%{name_query}%'"
        try:
            res = db.session.execute(text(query_str))
            results = [dict(row) for row in res.mappings()]
        except Exception as e:
            flash(f"Query error: {e}", "error")

    return render_template('people_search.html', user=get_current_user(), results=results, query=query_str)


# UPLOAD (unrestricted file upload demo)
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    # INTENTIONALLY insecure: allow everything
    return True

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not is_logged_in():
        return redirect(url_for('login'))
    uploaded_url = None
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        f = request.files['file']
        if f.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(save_path)
            uploaded_url = url_for('static', filename=f'uploads/{filename}')
            flash('File uploaded (no validation).', 'success')
            return redirect(url_for('upload'))

    # list uploaded files
    files = []
    for p in pathlib.Path(app.config['UPLOAD_FOLDER']).iterdir():
        if p.is_file():
            files.append(p.name)
    return render_template('upload.html', user=get_current_user(), files=files, uploaded_url=uploaded_url)
# === END insecure demo routes ===

@app.route('/blank')
def blank():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('blank.html', user=get_current_user())

@app.route('/404')
def error_404():
    return render_template('404.html')

# API endpoints for dynamic content
@app.route('/api/alerts')
def api_alerts():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(SAMPLE_ALERTS)

@app.route('/api/messages')
def api_messages():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(SAMPLE_MESSAGES)

@app.route('/api/table-data')
def api_table_data():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(SAMPLE_TABLE_DATA)

@app.route('/api/chart-data')
def api_chart_data():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Sample chart data
    chart_data = {
        'area_chart': {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'data': [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 25000, 40000]
        },
        'pie_chart': {
            'labels': ['Direct', 'Social', 'Referral'],
            'data': [55, 30, 15]
        }
    }
    return jsonify(chart_data)

@app.route('/sql-console', methods=['POST'])
def sql_console():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    query = request.form.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        # Wrap query in text() and use .mappings() to get dict-like rows
        result = db.session.execute(text(query))
        rows = [dict(row) for row in result.mappings()]  # <- important

        return jsonify({'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 40

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)



