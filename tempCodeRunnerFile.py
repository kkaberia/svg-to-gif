from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import or_
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


app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db) # Initialize Migrate
# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///estate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ... other imports



# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'njorogeken@gmail.com')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'shwa fkem fnhi garn')  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME','njorogeken@gmail.com')


mail = Mail(app)

app.jinja_env.globals['datetime'] = datetime

# Define the AddUserForm class
class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=50)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    house_number = StringField('House Number', validators=[DataRequired(), Length(max=20)])
    family_name = StringField('Family Name', validators=[DataRequired(), Length(max=50)])
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

class User(db.Model):
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
    payments = db.relationship('Payment', backref='user')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(50))
    origin_bank = db.Column(db.String(50), nullable=True)
    months = db.Column(db.String(100), nullable=True)

# ---------------------------
# Utility Functions
# ---------------------------

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_password_email(email, username, password):
    msg = Message('Your Plateau Estate Portal Password', sender='no-reply@estateportal.com', recipients=[email])
    msg.body = f'''
    Hello {username},

    Your account has been created successfully. Here are your login details:
    Username: {username}
    Password: {password}

    Please log in and change your password as soon as possible.

    Regards,
    Plateau Estate Portal Team
    '''
    mail.send(msg)

# ---------------------------
# Routes
# ---------------------------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
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
    current_year = datetime.now().year
    payments = Payment.query.filter_by(user_id=user_id).filter(
        Payment.date.between(datetime(current_year, 1, 1), datetime(current_year, 12, 31))
    ).all()

    total_paid = sum(p.amount for p in payments)
    monthly_due = 3850
    current_month = datetime.now().month
    expected_so_far = current_month * monthly_due
    paid_segment = (total_paid *1)
    arrears_segment = max(expected_so_far - total_paid, 0)
    not_due_segment = (12 - current_month) * monthly_due
    pending = max(46200 - total_paid, 0)
    arrears =max(expected_so_far-total_paid,0)

    return render_template('dashboard.html', 
                           payments=payments, 
                           total_paid=total_paid,
                           pending=pending,
                           arrears=arrears,
                           paid_segment=paid_segment,
                           arrears_segment=arrears_segment,
                           not_due_segment=not_due_segment)


@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    form = PaymentForm()
    if form.validate_on_submit():
        amount = form.amount.data
        payment_type = form.payment_type.data
        payment_date = form.payment_date.data
        months_list = request.form.getlist('months')  # Get selected months from form
        months_str = ','.join(months_list) if months_list else None
        origin_bank = request.form.get('origin_bank') if payment_type == "Bank Transfer" else None

        user_id = session.get('user_id')  # Ensure user is logged in
        if not user_id:
            flash("You must be logged in to add a payment", "error")
            return redirect(url_for('login'))

        new_payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_type=payment_type,
            date=payment_date,
            origin_bank=origin_bank,
            months=months_str
        )

        db.session.add(new_payment)
        db.session.commit()
        
        flash("Payment added successfully!", "success")
        return redirect(url_for('dashboard'))  # Redirect to dashboard

    return render_template('add_payment.html', form=form)


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

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        return "Access Denied: Only admins can view this page."

    current_year = datetime.now().year
    current_month = datetime.now().month

    all_payments = Payment.query.filter(
        Payment.date.between(datetime(current_year, 1, 1), datetime(current_year, 12, 31))
    ).all()
    total_received = sum(p.amount for p in all_payments)
    expected_so_far = current_month * 20 * 3850  # Assuming 20 members and 3850 due per member
    arrears = max(expected_so_far - total_received, 0)
    not_due = (12 - current_month) * 20 * 3850

    # Get total debits from BankTransaction
    total_debits = sum(t.amount for t in BankTransaction.query.all())

    opening_bank_balance = 10000.0  # Initial balance
    closing_bank_balance = opening_bank_balance + total_received - total_debits  # Subtract expenses

    transactions = BankTransaction.query.order_by(BankTransaction.date.desc()).all()
    payments = Payment.query.order_by(Payment.date).all()
    users = User.query.all()

    return render_template('admin_dashboard.html',
                           payments=payments,
                           total_received=total_received,
                           arrears=arrears,
                           not_due=not_due,
                           opening_bank_balance=opening_bank_balance,
                           closing_bank_balance=closing_bank_balance,
                           transactions=transactions,
                           users=users)



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
            family_name=family_name
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
            token = secrets.token_urlsafe(32)  # Generate a secure token
            reset_url = url_for('confirm_reset', token=token, _external=True)

            # Create the email message
            msg = Message(
                "Password Reset Request",
                sender=app.config['MAIL_DEFAULT_SENDER'],  # Use default sender, username does not have to be hardcoded here** Check
                recipients=[email]
            )
            msg.body = f"Hello {user.username},\n\nClick the link below to reset your password:\n{reset_url}\n\nIf you didn't request this, ignore this email."

            try:
                mail.send(msg)
                flash("A password reset link has been sent to your email.", "success")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "danger")

        else:
            flash("Email not found. Please check and try again.", "error")

        return redirect(url_for('reset_password'))

    return render_template('reset_password.html')


@app.route('/confirm_reset/<token>', methods=['GET', 'POST'])
def confirm_reset(token):  # Ensure this function is properly defined
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        user = User.query.filter_by(email=session.get('reset_email')).first()
        if user:
            user.password = hashed_password
            db.session.commit()
            flash("Password reset successful! You can now log in.", "success")
            return redirect(url_for('login'))

    return render_template('confirm_reset.html', token=token)  # Ensure this line is inside the function

@app.route('/fund_utilization', methods=['GET', 'POST'])
def fund_utilization():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'admin':
        flash("Access denied. Only admins can manage funds.", "danger")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
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

        new_transaction = BankTransaction(
            date=date,
            narration=narration,
            amount=float(amount),
            payment_mode=payment_mode,
            payee=payee
        )

        db.session.add(new_transaction)
        db.session.commit()
        flash("Transaction added successfully!", "success")
        return redirect(url_for('fund_utilization'))

    transactions = BankTransaction.query.order_by(BankTransaction.date.desc()).all()
    return render_template('fund_utilization.html', transactions=transactions)


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

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


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
    app.run(debug=True)