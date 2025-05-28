from flask import request
from user_agents import parse

def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def get_device_info():
    ua_string = request.headers.get("User-Agent", "")
    ua = parse(ua_string)
    return {
        "browser": ua.browser.family,
        "os": ua.os.family,
        "device": ua.device.family
    }


import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    sender = "noreply@trackerapp.com"
    password = "your-smtp-password"
    smtp_server = "smtp.your-email-provider.com"
    port = 587

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, [to], msg.as_string())


import secrets
from flask import url_for
from flask_mail import Message
from app import mail  # mail must be initialized in app.py

reset_tokens = {}

def generate_reset_token(email):
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    return token

def get_email_by_token(token):
    return reset_tokens.get(token)

def send_reset_email(email, token):
    reset_link = url_for('auth.reset_password_token', token=token, _external=True)
    msg = Message("Password Reset Request", recipients=[email])
    msg.body = f"Click the link to reset your password: {reset_link}"
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send reset email: {e}")


from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            user = session.get("user")
            if not user:
                flash("You must be logged in to access this page.", "error")
                return redirect(url_for("auth.login"))
            if role and user.get("role") != role:
                flash("Access denied: insufficient permissions.", "error")
                return redirect(url_for("auth.login"))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
