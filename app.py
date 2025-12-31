from functools import wraps  # Add this import at the top of the file
from flask_login import login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import func
from flask_mail import Mail, Message
import secrets
import string
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from sqlalchemy.exc import IntegrityError  # Import IntegrityError
from wtforms import DecimalField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from wtforms import DecimalField, SelectField, SubmitField, DateField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms import StringField, FloatField, SelectField, SubmitField
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import current_user
from flask_login import LoginManager
from flask_login import UserMixin
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import login_user
from flask import Flask, session, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from itsdangerous import URLSafeTimedSerializer
from flask import jsonify
from flask import Flask, render_template
# from email_templates import get_reminder_email_template
# from payment_calculations import calculate_user_balance
import logging
import psycopg2
from sqlalchemy import desc
from flask import jsonify, make_response
from datetime import date


app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///estate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://estateportal_user:8JEKVkfA20xJ0r22d3TNyldmSfKsWpZ9@dpg-cutm5i8gph6c73b47gn0-a.oregon-postgres.render.com/estateportal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# ... other imports
db = SQLAlchemy(app)
migrate = Migrate(app, db) # Initialize Migrate


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'plateaucluster@gmail.com')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'wdok rsnf zxar hyft')  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME','plateauclustern@gmail.com')


mail = Mail(app)

app.jinja_env.globals['datetime'] = datetime

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)  # Bind the LoginManager to your Flask app

# Define the user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define the AddUserForm class
class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    house_number = StringField('House Number', validators=[DataRequired(), Length(max=20)])
    family_name = StringField('Family Name', validators=[DataRequired(), Length(max=50)])
    opening_balance = DecimalField('Opening Balance', default=0.0)  # New field
    submit = SubmitField('Add User')

# Define the PaymentForm class
class PaymentForm(FlaskForm):
    amount = DecimalField('Payment Amount', validators=[DataRequired()])
    payment_type = SelectField('Payment Method', choices=[
        ('M-PESA Transfer', 'M-PESA Transfer'),
        ('Bank Deposit', 'Bank Deposit'),
        ('Bank Transfer', 'Bank Transfer')
    ], validators=[DataRequired()])
    payment_date = DateField('Payment Date', format='%Y-%m-%d', validators=[DataRequired()])
    months = SelectMultipleField('Select Payment Month(s)', choices=[
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'), ('September', 'September'),
        ('October', 'October'), ('November', 'November'), ('December', 'December')
    ])
    submit = SubmitField('Add Payment')

class BankTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    narration = db.Column(db.String(255), nullable=False)  # Description of expense
    amount = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(50), nullable=False)  # Cash, Bank Transfer, etc.
    payee = db.Column(db.String(100), nullable=False)  # Who was paid


class BankTransactionForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), Length(max=255)])
    amount = FloatField('Amount', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Cash', 'Cash')
    ], validators=[DataRequired()])
    payee = StringField('Payee', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Add Transaction')
# ---------------------------
# Database Models
# ---------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), default='member')
    house_number = db.Column(db.String(20), nullable=False)
    family_name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    opening_balance = db.Column(db.Float, default=0.0)  # New column for opening balance
    payments = db.relationship('Payment', backref='user')

    # Flask-Login required methods
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(50))
    origin_bank = db.Column(db.String(50), nullable=True)
    months = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, default=lambda: datetime.now().year)  # ADD THIS LINE

   # Define the relationship to the User model
   # user = db.relationship('User', backref=db.backref('payments', lazy=True)) 

# ===== EMERGENCY DATABASE FIX =====

@app.before_request
def ensure_database_schema():
    if not hasattr(app, 'schema_checked'):
        from sqlalchemy import inspect, text
        
        inspector = inspect(db.engine)
        
        # Check if payment table exists
        if 'payment' in inspector.get_table_names():
            # Check columns
            columns = [col['name'] for col in inspector.get_columns('payment')]
            
            # Add year column if missing
            if 'year' not in columns:
                db.session.execute(text("ALTER TABLE payment ADD COLUMN IF NOT EXISTS year INTEGER"))
                db.session.commit()
                print("✅ Added year column to payment table")
                
                # Set default values for existing payments
                db.session.execute(text("UPDATE payment SET year = EXTRACT(YEAR FROM date) WHERE year IS NULL"))
                db.session.commit()
                print("✅ Updated existing payments with year values")
            else:
                print("✅ Year column already exists")
        
        app.schema_checked = True

# ===== TEMPORARY FIX ROUTE =====
@app.route('/fix_year_column')
@login_required      # ADD THIS LINE
@admin_required
def fix_year_column():
    """One-time fix for year column"""
    try:
        from sqlalchemy import text
        
        # Add column
        db.session.execute(text("ALTER TABLE payment ADD COLUMN IF NOT EXISTS year INTEGER"))
        
        # Update existing payments
        db.session.execute(text("UPDATE payment SET year = EXTRACT(YEAR FROM date) WHERE year IS NULL"))
        
        db.session.commit()
        
        # Count updated
        result = db.session.execute(text("SELECT COUNT(*) FROM payment WHERE year IS NOT NULL"))
        count = result.fetchone()[0]
        
        flash(f'Year column fixed! {count} payments updated.', 'success')
        return redirect(url_for('admin_dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))
# ---------------------------
# Utility Functions
# ---------------------------

def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits #+ string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_reminder_email_html(user, arrears, current_month, total_outstanding):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; background: #2c3e50; color: white; padding: 20px; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 5px; }}
            .highlight {{ background: #e74c3c; color: white; padding: 15px; text-align: center; }}
            .footer {{ text-align: center; margin-top: 20px; color: #777; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🏡 Plateau Cluster</h2>
                <p>Monthly Security Contribution Reminder</p>
            </div>
            
            <div class="content">
                <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
                <p>Requesting you to pay the security arrears as per the details below:</p>
                <div class="highlight">
                    <h3>Overdue Arrears Balance: Ksh {arrears:,.2f}</h3>
                    <p>For House {user.house_number}</p>
                </div>
                
                <p><strong>Payment Details:</strong></p>
                <p>• Monthly Payment Amount: Ksh 3,850</p>
                <p>• Total Annual Outstanding Amount: <strong>Ksh {total_outstanding:,.2f}</strong></p>
                
                <p><strong>Payment Methods:</strong></p>
                <p>• KCB BANK, Account No: <strong>1298976472</strong></p>
                <p>• M-PESA: Paybill <strong>522522</strong></p>
                <p>• If paying via Bank Transfer Please include Month and House number as reference</p>
                <p>• Kindly ignore the notification if already paid</p>

            </div>
            
            <div class="footer">
                <p>Thank you for your prompt payment!</p>
                <p>Treasurer, Plateau Cluster Management</p>
            </div>
        </div>
    </body>
    </html>
    """

def generate_payment_statement_html(user, payments, current_year, custom_message=""):
    """Generate HTML for payment statement email - Bank Statement Style"""
    # Calculate totals
    total_paid = sum(p.amount for p in payments)
    monthly_due = 3850
    current_month = datetime.now().month
    expected_so_far = current_month * monthly_due
    
    # Calculate arrears
    arrears_raw = expected_so_far - total_paid
    if user.opening_balance < 0:
        arrears_raw += abs(user.opening_balance)
    arrears = max(arrears_raw, 0)
    
    # Calculate remaining balance for the year
    remaining_balance = max(46200 - total_paid, 0)
    if user.opening_balance < 0:
        remaining_balance += abs(user.opening_balance)
    
    # Generate payment details HTML table
    payment_details_html = ""
    if payments:
        payment_details_html = """
        <div style="margin: 20px 0; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
            <table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;">
                <thead>
                    <tr style="background-color: #2c3e50; color: white;">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Date</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Description</th>
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Payment Method</th>
                        <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">Amount (KES)</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for payment in payments:
            # Create description based on payment type
            description = f"Security Contribution"
            if payment.months:
                description += f" - {payment.months}"
            
                        
            payment_details_html += f"""
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px; color: #333;">{payment.date.strftime('%d-%b-%Y')}</td>
                        <td style="padding: 10px; color: #333;">{description}</td>
                        <td style="padding: 10px; color: #333;">{payment.payment_type}</td>
                        <td style="padding: 10px; text-align: right; color: #333; font-weight: 500;">{payment.amount:,.2f}</td>
                    </tr>
            """
        
        # Add TOTAL row
        payment_details_html += f"""
                    <tr style="background-color: #f8f9fa; font-weight: bold; border-top: 2px solid #ddd;">
                        <td style="padding: 12px; text-align: right; color: #2c3e50;" colspan="3">TOTAL PAID IN {current_year}:</td>
                        <td style="padding: 12px; text-align: right; color: #27ae60; font-size: 1.1em;">{total_paid:,.2f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    else:
        payment_details_html = """
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
            <p style="color: #666; margin: 0;">No payments recorded for the current year.</p>
        </div>
        """
    
    # Generate the full HTML email - Bank Statement Style
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f9f9f9;
                margin: 0;
                padding: 0;
            }}
            .statement-container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            .statement-header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .statement-body {{
                padding: 30px;
            }}
            .account-summary {{
                background-color: #f8f9fa;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 25px;
                border-left: 4px solid #3498db;
            }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }}
            .summary-item {{
                padding: 10px;
            }}
            .summary-label {{
                font-size: 0.9em;
                color: #666;
                margin-bottom: 5px;
            }}
            .summary-value {{
                font-size: 1.2em;
                font-weight: 600;
                color: #2c3e50;
            }}
            .summary-value.positive {{
                color: #27ae60;
            }}
            .summary-value.negative {{
                color: #e74c3c;
            }}
            .section-title {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
                margin-top: 30px;
                margin-bottom: 20px;
            }}
            .statement-footer {{
                background-color: #f8f9fa;
                padding: 25px;
                margin-top: 30px;
                border-top: 1px solid #ddd;
                color: #666;
            }}
            .important-note {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="statement-container">
            <!-- Statement Header -->
            <div class="statement-header">
                <h1 style="margin: 0; font-size: 28px;">🏡 Plateau Cluster</h1>
                <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">SECURITY PAYMENT STATEMENT - {current_year}</p>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.8;">Statement Date: {datetime.now().strftime('%d %B %Y')}</p>
            </div>
            
            <!-- Statement Body -->
            <div class="statement-body">
                <!-- Account Holder Info -->
                <div style="margin-bottom: 25px;">
                    <h3 style="margin: 0 0 10px 0; color: #2c3e50;">Account Holder Information</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                        <div>
                            <p style="margin: 5px 0; color: #666;"><strong>Name:</strong> {user.first_name} {user.last_name}</p>
                            <p style="margin: 5px 0; color: #666;"><strong>Account:</strong> {user.username}</p>
                        </div>
                        <div>
                            <p style="margin: 5px 0; color: #666;"><strong>House Number:</strong> {user.house_number}</p>
                    </div>
                    </div>
                </div>
                
                <!-- Financial Summary -->
                <div class="account-summary">
                    <h3 style="margin: 0 0 15px 0; color: #2c3e50;">Financial Summary</h3>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <div class="summary-label">Opening Balance</div>
                            <div class="summary-value">{user.opening_balance:,.2f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">Total Paid ({current_year})</div>
                            <div class="summary-value positive">{total_paid:,.2f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">Current Arrears</div>
                            <div class="summary-value {'negative' if arrears > 0 else ''}">{arrears:,.2f}</div>
                        </div>
                        <div class="summary-item">
                            <div class="summary-label">Annual Balance</div>
                            <div class="summary-value">{remaining_balance:,.2f}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Payment Details -->
                <h3 class="section-title">Transaction Details</h3>
                {payment_details_html}
                
                <!-- Custom Message -->
                {f'<div class="important-note"><strong>Message from Treasurer:</strong><br>{custom_message}</div>' if custom_message else ''}
                
                <!-- Important Notes -->
                <div class="important-note">
                    <strong>IMPORTANT NOTICE:</strong>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Monthly Contribution: KES 3,850</li>
                        <li>Annual Total: KES 46,200</li>
                        <li>Current Month: {datetime.now().strftime('%B')}</li>
                        <li>Months Due: {current_month} of 12</li>
                    </ul>
                </div>
            </div>
            
            <!-- Statement Footer -->
            <div class="statement-footer">
                <h4 style="margin: 0 0 15px 0; color: #2c3e50;">Payment Instructions</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                    <div>
                        <p style="margin: 5px 0; font-weight: 500;">Bank Transfer:</p>
                        <p style="margin: 5px 0;">KCB BANK<br>Account: <strong>1298976472</strong><br>Name: Plateau Residents Association</p>
                    </div>
                    <div>
                        <p style="margin: 5px 0; font-weight: 500;">M-PESA:</p>
                        <p style="margin: 5px 0;">Paybill: <strong>522522</strong><br>Account No: 1298976472</p>
                    </div>
                </div>
                <p style="margin: 20px 0 0 0; font-size: 0.9em; text-align: center;">
                    <strong>Reference:</strong> Please include Month and House Number ({user.house_number})<br>
                    For inquiries: plateaucluster@gmail.com | +254721658182
                </p>
                <p style="margin: 20px 0 0 0; font-size: 0.8em; text-align: center; color: #999;">
                    This is an automated statement from Plateau Cluster Management System.<br>
                    Generated on {datetime.now().strftime('%d %B %Y at %H:%M')}
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def send_password_email(email, username, password):
    msg = Message(
        subject='Your Plateau Estate Portal Password',
        sender='no-reply@estateportal.com',
        recipients=[email]
    )
    
    # HTML content for the email
    msg.html = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    background-color: #fff;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    font-size: 24px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                p {{
                    margin: 10px 0;
                    font-size: 16px;
                }}
                .details {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .details p {{
                    margin: 5px 0;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #777;
                    text-align: center;
                }}
                .button {{
                    display: inline-block;
                    margin: 20px 0;
                    padding: 12px 24px;
                    background-color: #3498db;
                    color: #fff;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 16px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to Plateau Estate Portal</h1>
                <p>Hello {username},</p>
                <p>Your account has been created successfully. Here are your login details:</p>
                
                <div class="details">
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Password:</strong> {password}</p>
                </div>

                <p>Please log in and change your password as soon as possible.</p>
                <a href="https://estate-portal.onrender.com/login" class="button">Log In Now</a>

                <div class="footer">
                    <p>Best regards,</p>
                    <p><strong>Plateau Estate Portal Team</strong></p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Send the email
    mail.send(msg)

    # Monthly reminder function
def send_monthly_reminders():
    with app.app_context():
        users = User.query.all()
        for user in users:
            msg = Message('Monthly Security Payment Reminder', recipients=[user.email])
            msg.body = f"Hello {user.first_name},\n\nThis is a reminder to pay your monthly security fee via M-PESA Paybill 522522 Account No 7102430033.\n\nThank you,\nPlateau Estate Management."
            mail.send(msg)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('home'))  # Redirect to home or login page
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Routes
# ---------------------------
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
     app.logger.debug('Rendering index.html')
     return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').lower()  # Convert input to lowercase
        password = request.form.get('password')
        
        # Convert database username to lowercase for case-insensitive comparison
        user = User.query.filter(func.lower(User.username) == username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            session['user_id'] = user.id
            session['user_role'] = user.role  # Store the user's role in the session
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        if User.query.filter(or_(User.username == username, User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))
        plain_password = generate_random_password()
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        send_password_email(email, username, plain_password)
        flash('Account created successfully! Check your email for the password.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Use selected year from session, default to current year
    selected_year = session.get('selected_year', datetime.now().year)
    
    # Get payments for selected year
    payments = Payment.query.filter_by(user_id=user_id, year=selected_year).all()

    # Calculate totals
    total_paid = sum(p.amount for p in payments)
    if user.opening_balance > 0:
        total_paid += user.opening_balance

    # Monthly due and expected payments
    monthly_due = 3850
    
    # If viewing current year, calculate based on current month
    if selected_year == datetime.now().year:
        current_month = datetime.now().month
        expected_so_far = current_month * monthly_due
    else:
        # For past years, expect full year's payment
        expected_so_far = 12 * monthly_due
        current_month = 12

    # Calculate arrears
    arrears_raw = expected_so_far - total_paid
    if user.opening_balance < 0:
        arrears_raw += abs(user.opening_balance)
    arrears = max(arrears_raw, 0)

    # Calculate pending amount
    pending = max(46200 - total_paid, 0)
    if user.opening_balance < 0:
        pending += abs(user.opening_balance)

    # Calculate segments for visualization
    paid_segment = total_paid
    arrears_segment = max(expected_so_far - total_paid, 0)
    not_due_segment = (12 - current_month) * monthly_due

    return render_template('dashboard.html', 
                           payments=payments, 
                           total_paid=total_paid,
                           pending=pending,
                           arrears=arrears,
                           paid_segment=paid_segment,
                           arrears_segment=arrears_segment,
                           not_due_segment=not_due_segment,
                           opening_balance=user.opening_balance,
                           selected_year=selected_year)

@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        # Get form data
        amount = form.amount.data
        payment_type = form.payment_type.data
        payment_date = form.payment_date.data
        months_list = request.form.getlist('months')
        months_str = ','.join(months_list) if months_list else None
        origin_bank = request.form.get('origin_bank') if payment_type == "Bank Transfer" else None
        
        # Get year from payment date
        payment_year = payment_date.year

        # Get the selected user_id
        user_id = request.form.get('user_id')
        if not user_id:
            user_id = session.get('user_id')
            if not user_id:
                flash("You must be logged in to add a payment", "error")
                return redirect(url_for('login'))

        user = User.query.get(user_id)
        if not user:
            flash("Invalid user selected.", "error")
            return redirect(url_for('add_payment'))

        # Create new payment with year
        new_payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_type=payment_type,
            date=payment_date,
            origin_bank=origin_bank,
            months=months_str,
            year=payment_year  # ADD THIS
        )

        db.session.add(new_payment)
        db.session.commit()

        flash("Payment added successfully!", "success")
        return redirect(url_for('dashboard'))

    users = User.query.all()
    return render_template('add_payment.html', form=form, users=users)

# Add this to your app.py
@app.template_filter('format_currency')
def format_currency(value):
    return "{:,.2f}".format(value)

@app.route('/update_payment', methods=['GET', 'POST'])
def update_payment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        payment_id = request.form.get('payment_id')
        new_amount = request.form.get('new_amount')
        new_payment_type = request.form.get('payment_type')
        origin_bank = request.form.get('origin_bank') if new_payment_type == "Bank Transfer" else None
        months_list = request.form.getlist('months')
        months_str = ','.join(months_list) if months_list else None
        payment_date_str = request.form.get('payment_date')
        try:
            payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d") if payment_date_str else datetime.now()
        except Exception:
            payment_date = datetime.now()
        payment = Payment.query.get(payment_id)
        if payment:
            payment.amount = float(new_amount)
            payment.payment_type = new_payment_type
            payment.origin_bank = origin_bank
            payment.months = months_str
            payment.date = payment_date
            db.session.commit()
            flash('Payment updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after update
        else:
            flash('Payment not found.', 'error')  # Handle the case where payment isn't found
            return redirect(url_for('admin_dashboard'))

    else:
        payment = None
        payment_id = request.args.get('payment_id')
        if payment_id:
            payment = Payment.query.get(payment_id)
        return render_template('update_payment.html', payment=payment)
    
    # Route to delete a payment record
@app.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)  # Fetch the payment record
    db.session.delete(payment)  # Delete the record
    db.session.commit()  # Commit the changes
    flash('Payment record deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard

    
    
@app.route('/admin_add_payment', methods=['GET', 'POST'])
@admin_required  # Ensure only admins can access this route
def admin_add_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        # Get form data
        amount = form.amount.data
        payment_type = form.payment_type.data
        payment_date = form.payment_date.data
        months_list = request.form.getlist('months')  # Get selected months from form
        months_str = ','.join(months_list) if months_list else None
        origin_bank = request.form.get('origin_bank') if payment_type == "Bank Transfer" else None

        # Get the selected user_id from the form
        user_id = request.form.get('user_id')

        # Validate the selected user
        user = User.query.get(user_id)
        if not user:
            flash("Invalid user selected.", "error")
            return redirect(url_for('admin_add_payment'))

        # Create a new payment record
        new_payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_type=payment_type,
            date=payment_date,
            origin_bank=origin_bank,
            months=months_str
        )

        # Save to database
        db.session.add(new_payment)
        db.session.commit()

        # Generate a transaction ID
        transaction_id = f"PC-{payment_date.strftime('%Y')}-{new_payment.id:04d}"

        # Format the payment date for display
        formatted_date = payment_date.strftime('%B %d, %Y')

        # Send email to the user with enhanced template
        try:
            msg = Message(
                subject="Payment Confirmation - Plateau Cluster",
                recipients=[user.email],  # Send to the user's email
                html=f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Payment Confirmation - Plateau Cluster</title>
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        }}
                        body {{
                            background-color: #f5f7fa;
                            padding: 20px;
                            color: #333;
                        }}
                        .email-container {{
                            max-width: 650px;
                            margin: 0 auto;
                            background: #ffffff;
                            border-radius: 12px;
                            overflow: hidden;
                            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                        }}
                        .email-header {{
                            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                            padding: 30px;
                            text-align: center;
                            color: white;
                        }}
                        .logo {{
                            font-size: 28px;
                            font-weight: bold;
                            margin-bottom: 15px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            gap: 10px;
                        }}
                        .logo-icon {{
                            width: 40px;
                            height: 40px;
                            background: white;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            color: #3498db;
                            font-size: 20px;
                        }}
                        .email-title {{
                            font-size: 24px;
                            margin: 10px 0;
                        }}
                        .email-body {{
                            padding: 35px;
                        }}
                        .greeting {{
                            font-size: 20px;
                            margin-bottom: 25px;
                            color: #2c3e50;
                        }}
                        .message {{
                            line-height: 1.6;
                            margin-bottom: 30px;
                            color: #555;
                        }}
                        .payment-details {{
                            background: #f8f9fa;
                            border-radius: 10px;
                            padding: 25px;
                            margin-bottom: 30px;
                            border-left: 4px solid #3498db;
                        }}
                        .detail-row {{
                            display: flex;
                            margin-bottom: 15px;
                            padding-bottom: 15px;
                            border-bottom: 1px solid #eee;
                        }}
                        .detail-row:last-child {{
                            margin-bottom: 0;
                            padding-bottom: 0;
                            border-bottom: none;
                        }}
                        .detail-label {{
                            flex: 1;
                            font-weight: 600;
                            color: #2c3e50;
                        }}
                        .detail-value {{
                            flex: 2;
                            color: #555;
                        }}
                        .amount-highlight {{
                            font-size: 22px;
                            font-weight: bold;
                            color: #27ae60;
                        }}
                        .footer {{
                            text-align: center;
                            padding: 25px;
                            background: #f8f9fa;
                            color: #777;
                            font-size: 14px;
                        }}
                        .signature {{
                            margin-top: 25px;
                            color: #2c3e50;
                        }}
                        .signature p {{
                            margin: 5px 0;
                        }}
                        .contact-info {{
                            margin-top: 20px;
                            padding-top: 20px;
                            border-top: 1px solid #ddd;
                            font-size: 13px;
                        }}
                        .badge {{
                            display: inline-block;
                            background: #27ae60;
                            color: white;
                            padding: 5px 10px;
                            border-radius: 20px;
                            font-size: 12px;
                            margin-left: 10px;
                        }}
                        .button {{
                            display: inline-block;
                            background: #3498db;
                            color: white;
                            padding: 12px 25px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin-top: 15px;
                            font-weight: 600;
                        }}
                        .divider {{
                            height: 1px;
                            background: linear-gradient(to right, transparent, #ddd, transparent);
                            margin: 25px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="email-header">
                            <div class="logo">
                                <div class="logo-icon">P</div>
                                <span>Plateau Cluster</span>
                            </div>
                            <h1 class="email-title">Payment Confirmation</h1>
                        </div>
                        
                        <div class="email-body">
                            <h2 class="greeting">Hello {user.first_name},</h2>
                            
                            <p class="message">
                                Thank you for your payment to Plateau Cluster Account. We've received your transaction and updated your account details accordingly.
                            </p>
                            
                            <div class="payment-details">
                                <h3 style="margin-bottom: 20px; color: #2c3e50;">Payment Details</h3>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Amount</div>
                                    <div class="detail-value"><span class="amount-highlight">KSH {amount}</span></div>
                                </div>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Payment Type</div>
                                    <div class="detail-value">{payment_type} <span class="badge">Completed</span></div>
                                </div>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Payment Date</div>
                                    <div class="detail-value"> { formatted_date}<br></div>
                                </div>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Months Covered</div>
                                    <div class="detail-value"> { months_str if months_str else "N/A"}<br></div>
                                </div>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Originating Bank</div>
                                    <div class="detail-value"> { origin_bank if origin_bank else "N/A"}<br></div>
                                </div>
                                
                                <div class="detail-row">
                                    <div class="detail-label">Transaction ID</div>
                                    <div class="detail-value"> { transaction_id}<br></div>
                                </div>
                            </div>
                            
                            <div class="divider"></div>
                            
                            <p class="message">
                                Your continued support helps us grow and improve our cluster community. If you have any questions about this payment, please don't hesitate to contact us.
                            </p>
                            
                            <div style="text-align: center;">
                                <a href="#" class="button">View Payment History</a>
                            </div>
                        </div>
                        
                        <div class="footer">
                            <p>Best regards,</p>
                            <div class="signature">
                                <p><strong>Treasurer</strong></p>
                                <p><strong>Plateau Cluster</strong></p>
                            </div>
                            
                            <div class="contact-info">
                                <p>Email: plateaucluster@gmail.com | Phone: +254721658182</p>
                                <p>© 2024 Plateau Cluster. All rights reserved.</p>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            mail.send(msg)  # Send the email
            flash("Payment added successfully and email sent!", "success")
        except Exception as e:
            flash(f"Payment added, but email could not be sent: {str(e)}", "warning")

        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard

    # For GET requests, fetch the list of users (for admin dropdown)
    users = User.query.all()
    return render_template('admin_add_payment.html', form=form, users=users)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_obj = User.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.role != 'admin':
        return "Access Denied: Only admins can view this page."

    # Use selected year from session
    selected_year = session.get('selected_year', datetime.now().year)
    
    # Fetch payments for selected year
    payments = db.session.query(Payment, User)\
        .join(User, Payment.user_id == User.id)\
        .filter(Payment.year == selected_year)\
        .order_by(desc(Payment.date)).all()
    
    # Calculate totals for selected year
    all_payments = Payment.query.filter_by(year=selected_year).all()
    total_received = sum(p.amount for p in all_payments)
    
    users = User.query.all()
    total_members = len(users)
    
    # Calculate expected amount based on selected year
    if selected_year == datetime.now().year:
        current_month = datetime.now().month
        expected_so_far = current_month * total_members * 3850
    else:
        # For past years, expect full year
        expected_so_far = 12 * total_members * 3850
        current_month = 12
    
    # Calculate financials for selected year
    total_arrears = 0
    user_financials = []
    
    for usr in users:
        user_payments = Payment.query.filter_by(user_id=usr.id, year=selected_year).all()
        user_total_paid = sum(p.amount for p in user_payments)
        
        # Only apply opening balance for current year
        if selected_year == datetime.now().year:
            if usr.opening_balance > 0:
                user_total_paid += usr.opening_balance
        
        user_expected = current_month * 3850
        
        # Calculate arrears
        arrears_raw = user_expected - user_total_paid
        if selected_year == datetime.now().year and usr.opening_balance < 0:
            arrears_raw += abs(usr.opening_balance)
        user_arrears = max(arrears_raw, 0)
        
        total_arrears += user_arrears
        
        user_pending = max(46200 - user_total_paid, 0)
        if selected_year == datetime.now().year and usr.opening_balance < 0:
            user_pending += abs(usr.opening_balance)

        user_financials.append({
            'username': usr.username,
            'first_name': usr.first_name,
            'last_name': usr.last_name,
            'opening_balance': usr.opening_balance,
            'total_paid': user_total_paid,
            'arrears': user_arrears,
            'pending': user_pending,
            'user_id': usr.id
        })
    
    # Calculate "Not Due"
    not_due = (12 - current_month) * total_members * 3850
    
    # Bank transactions (these are not year-specific in your current model)
    total_debits = sum(t.amount for t in BankTransaction.query.all())
    opening_bank_balance = 1336315.0
    closing_bank_balance = opening_bank_balance + total_received - total_debits

    transactions = BankTransaction.query.order_by(BankTransaction.date.desc()).all()

    return render_template('admin_dashboard.html',
                           payments=payments,
                           total_received=total_received,
                           arrears=total_arrears,
                           not_due=not_due,
                           total_debits=total_debits,
                           opening_bank_balance=opening_bank_balance,
                           closing_bank_balance=closing_bank_balance,
                           transactions=transactions,
                           users=users,
                           user_financials=user_financials,
                           current_user=current_user_obj,
                           selected_year=selected_year)

@app.route('/members_summary')
@admin_required
def members_summary():
    """Separate page for detailed members financial summary"""
    selected_year = session.get('selected_year', datetime.now().year)
    
    if selected_year == datetime.now().year:
        current_month = datetime.now().month
    else:
        current_month = 12
    
    users = User.query.all()
    user_financials = []
    
    for usr in users:
        # Get user payments for selected year
        user_payments = Payment.query.filter_by(user_id=usr.id, year=selected_year).all()
        
        total_paid = sum(p.amount for p in user_payments)
        
        # Only apply opening balance for current year
        if selected_year == datetime.now().year and usr.opening_balance > 0:
            total_paid += usr.opening_balance
        
        # Calculate arrears
        expected_so_far = current_month * 3850
        arrears_raw = expected_so_far - total_paid
        
        if selected_year == datetime.now().year and usr.opening_balance < 0:
            arrears_raw += abs(usr.opening_balance)
        
        user_arrears = max(arrears_raw, 0)
        
        # Calculate pending
        user_pending = max(46200 - total_paid, 0)
        if selected_year == datetime.now().year and usr.opening_balance < 0:
            user_pending += abs(usr.opening_balance)

        user_financials.append({
            'username': usr.username,
            'first_name': usr.first_name,
            'last_name': usr.last_name,
            'opening_balance': usr.opening_balance,
            'total_paid': total_paid,
            'arrears': user_arrears,
            'pending': user_pending,
            'user_id': usr.id,
            'email': usr.email,
            'house_number': usr.house_number
        })
    
    # Calculate summary totals
    summary_totals = {
        'total_opening': sum(uf['opening_balance'] for uf in user_financials),
        'total_paid': sum(uf['total_paid'] for uf in user_financials),
        'total_arrears': sum(uf['arrears'] for uf in user_financials),
        'total_pending': sum(uf['pending'] for uf in user_financials),
        'member_count': len(user_financials)
    }
    
    return render_template('members_summary.html',
                         user_financials=user_financials,
                         summary_totals=summary_totals,
                         selected_year=selected_year,
                         current_month=current_month)


@app.route('/payment_records')
@login_required
def payment_records():
    # Check if user is admin
    current_user_obj = User.query.get(session['user_id'])
    if not current_user_obj or current_user_obj.role != 'admin':  # Changed 'Admin' to 'admin'
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all payments with user information
    payments = Payment.query.join(User).order_by(Payment.id.desc()).all()
    
    # Calculate statistics
    total_amount = sum(payment.amount for payment in payments)
    average_payment = total_amount / len(payments) if payments else 0
    
    return render_template(
        'payment_records.html',
        payments=payments,
        total_amount=total_amount,
        average_payment=average_payment
    )
# Update the navigation in other pages to include the new link

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        house_number = form.house_number.data
        family_name = form.family_name.data
        opening_balance = form.opening_balance.data  # Get opening balance

        if User.query.filter(or_(User.username == username, User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('add_user'))

        plain_password = generate_random_password()
        hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')

        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            house_number=house_number,
            family_name=family_name,
            opening_balance=opening_balance  # Set opening balance
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            send_password_email(email, username, plain_password)
            flash('User added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except IntegrityError:
            db.session.rollback()  # Rollback the transaction
            flash('Username or email already exists.', 'error')  # More specific message
            return redirect(url_for('add_user'))  # Redirect back to the form
        except Exception as e:  # Catch other potential errors
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')  # Generic error message
            return redirect(url_for('add_user'))  # Redirect back to the form

    return render_template('add_user.html', form=form)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.house_number = request.form.get('house_number')
        user.family_name = request.form.get('family_name')
        user.opening_balance = float(request.form.get('opening_balance', 0.0))  # Update opening balance
        user.role = request.form['role']  # Update the role
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate a secure token and create the reset URL
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('confirm_reset', token=token, _external=True)

            # Create the email message with HTML format
            msg = Message(
                subject="Password Reset Request",
                sender=app.config['MAIL_DEFAULT_SENDER'],  # Use default sender
                recipients=[email]
            )
            msg.html = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            margin: 0;
                            padding: 0;
                            background-color: #f9f9f9;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 20px auto;
                            padding: 20px;
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            background-color: #fff;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        }}
                        h1 {{
                            color: #2c3e50;
                            font-size: 24px;
                            margin-bottom: 20px;
                            text-align: center;
                        }}
                        p {{
                            margin: 10px 0;
                            font-size: 16px;
                        }}
                        .button {{
                            display: inline-block;
                            margin: 20px 0;
                            padding: 12px 24px;
                            background-color: #3498db;
                            color: #fff;
                            text-decoration: none;
                            border-radius: 5px;
                            font-size: 16px;
                            text-align: center;
                        }}
                        .footer {{
                            margin-top: 20px;
                            font-size: 14px;
                            color: #777;
                            text-align: center;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Password Reset Request</h1>
                        <p>Hello {user.username},</p>
                        <p>We received a request to reset your password. Click the button below to reset it:</p>
                        <a href="{reset_url}" class="button">Reset Password</a>
                        <p>If you didn't request this, please ignore this email. Your password will remain unchanged.</p>
                        <div class="footer">
                            <p>Best regards,</p>
                            <p><strong>Plateau Cluster System Admin</strong></p>
                        </div>
                    </div>
                </body>
            </html>
            """

            try:
                mail.send(msg)  # Send the email
                flash("A password reset link has been sent to your email.", "success")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "danger")

        else:
            flash("Email not found. Please check and try again.", "error")

        return redirect(url_for('reset_password'))

    # Render the reset password form for GET requests
    return render_template('reset_password.html')


@app.route('/confirm_reset/<token>', methods=['GET', 'POST'])
def confirm_reset(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour validity
    except SignatureExpired:
        flash('The reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('reset_password'))
    except BadSignature:
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('reset_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('confirm_reset', token=token))
        
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
            db.session.commit()
            flash("Password reset successful! You can now log in.", "success")
            return redirect(url_for('login'))
    
    return render_template('confirm_reset.html', token=token)

@app.route('/fund_utilization', methods=['GET', 'POST'])
def fund_utilization():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        flash("Access denied. Only admins can manage funds.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        date_str = request.form.get('date')
        narration = request.form.get('narration')
        amount = request.form.get('amount')
        payment_mode = request.form.get('payment_mode')
        payee = request.form.get('payee')

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format.", "danger")
            return redirect(url_for('fund_utilization'))

        if transaction_id:  # Editing an existing transaction
            transaction = BankTransaction.query.get(transaction_id)
            transaction.date = date
            transaction.narration = narration
            transaction.amount = float(amount)
            transaction.payment_mode = payment_mode
            transaction.payee = payee
            flash("Transaction updated successfully!", "success")
        else:  # Adding a new transaction
            new_transaction = BankTransaction(
                date=date,
                narration=narration,
                amount=float(amount),
                payment_mode=payment_mode,
                payee=payee
            )
            db.session.add(new_transaction)
            flash("Transaction added successfully!", "success")

        db.session.commit()
        return redirect(url_for('fund_utilization'))

    # Calculate summaries
    transactions = BankTransaction.query.order_by(BankTransaction.date.desc()).all()
    total_debits = sum(t.amount for t in transactions)
    total_expenses = total_debits

    return render_template('fund_utilization.html',
                           transactions=transactions,
                           total_debits=total_debits,
                           total_expenses=total_expenses)


@app.route('/get_transaction/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    transaction = BankTransaction.query.get_or_404(transaction_id)
    return jsonify({
        'id': transaction.id,
        'date': transaction.date.strftime('%Y-%m-%d'),
        'narration': transaction.narration,
        'amount': transaction.amount,
        'payment_mode': transaction.payment_mode,
        'payee': transaction.payee
    })

@app.route('/edit_transaction/<int:transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        flash("Access denied. Only admins can manage funds.", "danger")
        return redirect(url_for('dashboard'))

    transaction = BankTransaction.query.get_or_404(transaction_id)

    # Update transaction data
    transaction.date = datetime.strptime(request.form.get('date'), "%Y-%m-%d")
    transaction.narration = request.form.get('narration')
    transaction.amount = float(request.form.get('amount'))
    transaction.payment_mode = request.form.get('payment_mode')
    transaction.payee = request.form.get('payee')

    db.session.commit()
    flash("Transaction updated successfully!", "success")
    return redirect(url_for('fund_utilization'))

@app.route('/fund_utilization_view')
def fund_utilization_view():
    # Fetch all bank transactions from the database
    transactions = BankTransaction.query.order_by(BankTransaction.date.desc()).all()
    total_debits = sum(t.amount for t in transactions)
    
    # Calculate vendor summaries
    vendor_totals = {}
    for transaction in transactions:
        payee = transaction.payee.strip()
        if payee in vendor_totals:
            vendor_totals[payee]['total_amount'] += transaction.amount
            vendor_totals[payee]['transaction_count'] += 1
        else:
            vendor_totals[payee] = {
                'total_amount': transaction.amount,
                'transaction_count': 1
            }
    
    # Convert to list and sort by total amount (descending)
    vendor_summary = []
    for payee, data in vendor_totals.items():
        percentage = (data['total_amount'] / total_debits * 100) if total_debits > 0 else 0
        vendor_summary.append({
            'payee': payee,
            'total_amount': data['total_amount'],
            'transaction_count': data['transaction_count'],
            'percentage': percentage
        })
    
    # Sort by total amount descending
    vendor_summary.sort(key=lambda x: x['total_amount'], reverse=True)
    
    # Get top vendor total
    top_vendor_total = vendor_summary[0]['total_amount'] if vendor_summary else 0
    
    # Calculate average transaction
    average_transaction = total_debits / len(transactions) if transactions else 0

    return render_template('fund_utilization_view.html', 
                         transactions=transactions, 
                         total_debits=total_debits,
                         vendor_summary=vendor_summary,
                         top_vendor_total=top_vendor_total,
                         average_transaction=average_transaction)


@app.route('/add_bank_transaction', methods=['GET', 'POST'])
def add_bank_transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = BankTransactionForm()
    if form.validate_on_submit():
        new_transaction = BankTransaction(
            date=form.date.data,
            description=form.description.data,
            amount=form.amount.data,
            payment_method=form.payment_method.data,
            payee=form.payee.data
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Bank transaction added successfully!', 'success')
        return redirect(url_for('fund_utilization'))

    return render_template('add_bank_transaction.html', form=form)

# Flask route for sending reminder
@app.route('/send_reminder/<int:user_id>')
def send_reminder(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('admin_dashboard'))
    
    selected_year = session.get('selected_year', datetime.now().year)
    
    user_payments = Payment.query.filter_by(user_id=user_id, year=selected_year).all()
    
    total_paid = sum(p.amount for p in user_payments)
    if selected_year == datetime.now().year and user.opening_balance > 0:
        total_paid += user.opening_balance
    
    monthly_due = 3850
    
    if selected_year == datetime.now().year:
        current_month = datetime.now().month
    else:
        current_month = 12
    
    expected_so_far = current_month * monthly_due
    
    arrears = max(expected_so_far - total_paid, 0)
    if selected_year == datetime.now().year and user.opening_balance < 0:
        arrears += abs(user.opening_balance)
    
    remaining_months = 12 - current_month
    total_outstanding = arrears + (remaining_months * monthly_due)
    
    # Generate email HTML
    email_html = get_reminder_email_html(user, arrears, current_month, total_outstanding)
    
    try:
        msg = Message(
            subject=f'Monthly Security Contribution Reminder - Plateau Cluster ({selected_year})',
            recipients=[user.email],
            html=email_html
        )
        mail.send(msg)
        flash(f'Reminder sent to {user.first_name}!', 'success')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/user_payment_summary/<int:user_id>')
@login_required
@admin_required
def user_payment_summary(user_id):
    """Get user payment summary for the selected year"""
    user = User.query.get_or_404(user_id)
    selected_year = session.get('selected_year', datetime.now().year)
    
    # Get all payments for the selected year
    user_payments = Payment.query.filter_by(user_id=user_id, year=selected_year)\
        .order_by(Payment.date.desc()).all()
    
    # Calculate totals
    total_paid = sum(p.amount for p in user_payments)
    monthly_due = 3850
    
    if selected_year == datetime.now().year:
        current_month = datetime.now().month
    else:
        current_month = 12
    
    expected_so_far = current_month * monthly_due
    
    # Calculate arrears
    arrears_raw = expected_so_far - total_paid
    if selected_year == datetime.now().year and user.opening_balance < 0:
        arrears_raw += abs(user.opening_balance)
    arrears = max(arrears_raw, 0)
    
    # Calculate remaining balance for the year
    remaining_balance = max(46200 - total_paid, 0)
    if selected_year == datetime.now().year and user.opening_balance < 0:
        remaining_balance += abs(user.opening_balance)
    
    return render_template('user_payment_summary.html',
                         user=user,
                         user_payments=user_payments,
                         total_paid=total_paid,
                         arrears=arrears,
                         remaining_balance=remaining_balance,
                         opening_balance=user.opening_balance,
                         selected_year=selected_year)

@app.route('/update_existing_payments_years')
@admin_required
def update_existing_payments_years():
    """Temporary route to update existing payments with year from date"""
    try:
        # First ensure year column exists
        from sqlalchemy import text
        db.session.execute(text("ALTER TABLE payment ADD COLUMN IF NOT EXISTS year INTEGER"))
        db.session.commit()
        
        # Now update payments
        payments = Payment.query.all()
        updated_count = 0
        
        for payment in payments:
            # Safely check if year attribute exists
            current_year = getattr(payment, 'year', None)
            if current_year is None or current_year == 0:
                payment.year = payment.date.year
                updated_count += 1
        
        db.session.commit()
        
        flash(f'Updated {updated_count} payments with year information', 'success')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating payments: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/send_statement_email/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def send_statement_email(user_id):
    """Send payment statement email to user"""
    user = User.query.get_or_404(user_id)
    current_year = datetime.now().year
    
    # Get custom message from request
    data = request.get_json()
    custom_message = data.get('message', '')
    
    # Get user payments for the current year
    user_payments = Payment.query.filter_by(user_id=user_id).filter(
        Payment.date.between(datetime(current_year, 1, 1), datetime(current_year, 12, 31))
    ).order_by(Payment.date.desc()).all()
    
    try:
        # Generate email HTML using the helper function
        email_html = generate_payment_statement_html(user, user_payments, current_year, custom_message)
        
        # Create and send email
        msg = Message(
            subject=f"Plateau Cluster - Payment Statement for {current_year}",
            recipients=[user.email],
            html=email_html
        )
        
        mail.send(msg)
        return jsonify({
            'success': True,
            'message': f'Payment statement sent successfully to {user.email}!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending email: {str(e)}'
        })


@app.route('/logout')
def logout():
    logout_user()  # Log out the user
    session.pop('user_id', None)
    session.pop('user_role', None)  # Clear the user role from the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

    
@app.route('/change_password', methods=['GET', 'POST'])
@login_required  # Ensure only logged-in users can access this route
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Verify the current password
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('change_password'))

        # Check if the new password and confirmation match
        if new_password != confirm_password:
            flash('New password and confirmation do not match.', 'error')
            return redirect(url_for('change_password'))

        # Update the user's password
        current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()

        flash('Password updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required  # Only admins can delete users
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        # Delete all payments for this user first (if you want to cascade)
        Payment.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {e}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/user_management')
@admin_required  # Only admins can access
def user_management():
    users = User.query.all()
    return render_template('user_management.html', users=users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        existing_admin = User.query.filter_by(username="kkaberia").first()
        if existing_admin:
            if existing_admin.role != "admin":
                existing_admin.role = "admin"
                db.session.commit()
        else:
            admin_user = User(
                username="kkaberia",
                first_name="Admin",  # Add a first name
                last_name="User",  # Add a last name
                email="kkaberia@example.com",
                password=generate_password_hash("kkaberia", method='pbkdf2:sha256'),
                role="admin",
                house_number="1",  # Add a house number
                family_name="Admin Family"  # Add a family name
            )
            db.session.add(admin_user)
            db.session.commit()
    app.run(host='0.0.0.0', port=10000, debug=True)


