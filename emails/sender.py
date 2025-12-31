from flask_mail import Message
from flask import current_app
from . import templates  # Import the email templates

def send_email(subject, recipients, html_body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html_body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    current_app.extensions['mail'].send(msg)


def send_welcome_email(email, username, password):
    html_body = templates.welcome_email_template(username, password)
    send_email("Welcome to Plateau Estate Portal", [email], html_body)


def send_payment_confirmation_email(user, amount, payment_type, payment_date, months_str, origin_bank):
    html_body = templates.payment_confirmation_email_template(user, amount, payment_type, payment_date, months_str, origin_bank)
    send_email("Payment Confirmation", [user.email], html_body)


def send_password_reset_email(email, username, reset_url):
    html_body = templates.password_reset_email_template(username, reset_url)
    send_email("Password Reset Request", [email], html_body)