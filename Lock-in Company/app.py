from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Sample data for demonstration
SAMPLE_USERS = {
    'admin@example.com': {
        'password': generate_password_hash('admin123'),
        'first_name': 'Douglas',
        'last_name': 'McGee',
        'role': 'admin'
    }
}

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
        return SAMPLE_USERS.get(session['user_id'])
    return None

# Routes
@app.route('/')
def index():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('index.html', user=get_current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = SAMPLE_USERS.get(form.email.data)
        if user and check_password_hash(user['password'], form.password.data):
            session['user_id'] = form.email.data
            flash('Login successful!', 'success')
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
        if form.email.data in SAMPLE_USERS:
            flash('Email already registered', 'error')
        else:
            SAMPLE_USERS[form.email.data] = {
                'password': generate_password_hash(form.password.data),
                'first_name': form.first_name.data,
                'last_name': form.last_name.data,
                'role': 'user'
            }
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
