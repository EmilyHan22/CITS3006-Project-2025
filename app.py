from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from sqlalchemy import text
from models import db, User, Client, AreaDataPoint, BarDataPoint, PieSlice
import os
import json
from datetime import datetime
import subprocess


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "app.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database using the shared instance from models.py
db.init_app(app)

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# User model and helpers are defined in models.py

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

SAMPLE_TABLE_DATA = None

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
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
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
    clients = Client.query.all()
    return render_template('tables.html', user=get_current_user(), table_data=clients)

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

# ANNOUNCEMENTS (stored XSS demo)
ANNOUNCEMENTS = []
# seed demonstration announcement (stored XSS)
ANNOUNCEMENTS.append({
  'id': 1,
  'title': 'Welcome',
  'body': 'Welcome to the announcements demo. Post an announcement to test stored XSS.',
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
    rows = [e.to_dict() for e in Client.query.all()]
    return jsonify(rows)

@app.route('/api/chart-data')
def api_chart_data():
    if not is_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401

    area_pairs = [p.to_pair() for p in AreaDataPoint.query.order_by(AreaDataPoint.id.asc()).all()]
    bar_pairs = [p.to_pair() for p in BarDataPoint.query.order_by(BarDataPoint.id.asc()).all()]
    pie_pairs = [p.to_pair() for p in PieSlice.query.order_by(PieSlice.id.asc()).all()]

    chart_data = {
        'area_chart': {
            'labels': [l for l, _ in area_pairs],
            'data': [v for _, v in area_pairs]
        },
        'bar_chart': {
            'labels': [l for l, _ in bar_pairs],
            'data': [v for _, v in bar_pairs]
        },
        'pie_chart': {
            'labels': [l for l, _ in pie_pairs],
            'data': [v for _, v in pie_pairs]
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
        result = db.session.execute(text(query))
        rows = [dict(row) for row in result.mappings()]

        return jsonify({'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def handle_404(error):
    return render_template('404.html'), 404

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    output = None
    uploaded_filename = None
    file_type = None
    
    if request.method == 'POST':
        file = request.files['file']
        if not file or file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        uploaded_filename = file.filename
        
        # Process documents and scripts
        try:
            ext = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
            
            # Execute Python scripts - VULNERABLE!
            if ext == 'py':
                file_type = 'Python Script'
                result = subprocess.run(
                    ['python', filepath],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    cwd=os.path.dirname(filepath)
                )
                output = result.stdout if result.stdout else result.stderr
                flash(f'Script executed successfully.', 'success')
                
            # Execute Bash/Batch scripts - VULNERABLE!
            elif ext in ['bat', 'cmd', 'sh']:
                file_type = 'Shell Script'
                if ext == 'sh':
                    result = subprocess.run(
                        ['bash', filepath],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                else:
                    result = subprocess.run(
                        [filepath],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                output = result.stdout if result.stdout else result.stderr
                flash(f'Script executed successfully.', 'success')
                
            # Display text documents
            elif ext in ['txt', 'md', 'log', 'csv', 'json', 'xml']:
                file_type = f'{ext.upper()} Document'
                with open(filepath, 'r', encoding='utf-8') as f:
                    output = f.read()
                flash(f'Document loaded successfully.', 'success')
                    
            # Display binary documents (PDF, DOCX, etc.) as hex/info
            elif ext in ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'odt', 'rtf']:
                file_type = f'{ext.upper()} Document'
                file_size = os.path.getsize(filepath)
                with open(filepath, 'rb') as f:
                    preview_bytes = f.read(2048)
                    hex_preview = ' '.join(f'{b:02x}' for b in preview_bytes[:512])
                    
                output = f"Document Type: {ext.upper()}\n"
                output += f"File Size: {file_size:,} bytes\n"
                output += f"Location: {filepath}\n\n"
                output += f"--- Hex Preview (first 512 bytes) ---\n{hex_preview}\n\n"
                output += f"--- ASCII Preview ---\n"
                try:
                    ascii_preview = preview_bytes.decode('utf-8', errors='ignore')
                    output += ascii_preview
                except:
                    output += "Binary content"
                    
                flash(f'Document metadata loaded successfully.', 'success')
            else:
                file_type = 'Unknown File'
                flash(f'Unsupported file type.', 'warning')
                output = f"File '{file.filename}' uploaded but format not recognized.\nSupported: PDF, DOCX, TXT, PY, SH, BAT"
                        
        except subprocess.TimeoutExpired:
            flash('Script execution timed out (10 second limit)', 'warning')
            output = "Execution timed out after 10 seconds"
        except Exception as e:
            flash(f'Error processing file: {e}', 'error')
            output = f"Error: {str(e)}"

    return render_template('upload.html', user=get_current_user(), output=output, filename=uploaded_filename, file_type=file_type)

@app.route('/search')
def search():
    if not is_logged_in():
        return redirect(url_for('login'))

    # Vulnerable search function for pentesting practice
    # WARNING: This is intentionally vulnerable to SQL injection!
    q = request.args.get('q') or request.args.get('query') or ''
    
    # Using string concatenation instead of parameterized queries - VULNERABLE!
    # Simpler structure that's easier to exploit
    sql_query = f"SELECT name, position, salary FROM clients WHERE name LIKE '%{q}%' ORDER BY name"

    rows = []
    error = None
    try:
        result = db.session.execute(text(sql_query))
        rows = [dict(r) for r in result.mappings()]
    except Exception as e:
        error = str(e)

    return render_template('search.html', user=get_current_user(), query=q, results=rows, error=error)

if __name__ == '__main__':
    # Ensure tables exist and seed initial data
    try:
        from database import init_db
        init_db(app, reset=False)
    except Exception as e:
        print(f"Database init error: {e}")
    app.run(host='0.0.0.0', debug=True)
