from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sheets_api import append_row, find_by_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        grade = request.form['grade']

        if find_by_email(email):
            flash("Email already exists.", "error")
            return redirect('/register')

        hashed_pw = generate_password_hash(password)
        append_row('users', [name, email, hashed_pw, grade, 'student'])
        send_registration_email(email, name)
        flash("Registration successful. Please log in.", "success")
        return redirect('/login')
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = find_by_email(email)

        if not user or not check_password_hash(user['password'], password):
            flash("Invalid credentials.", "error")
            return redirect('/login')

        session['user'] = {
            'name': user['name'],
            'email': user['email'],
            'role': user.get('role', 'student')
        }
        flash("Welcome back!", "success")
        return redirect('/admin-dashboard' if session['user']['role'] == 'admin' else '/student-dashboard')
    return render_template('login.html')


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash('Please log in first.', 'error')
                return redirect('/login')
            if role and user.get('role') != role:
                flash('Unauthorized access.', 'error')
                return redirect('/')
            return f(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "success")
    return redirect('/')



from utils import send_email

def send_registration_email(email, name):
    subject = "Welcome to the Service Tracker"
    message = f"Hi {name},\n\nThank you for registering. You can now log your hours and view your progress anytime.\n\n- Tracker Team"
    try:
        send_email(to=email, subject=subject, body=message)
    except Exception as e:
        print("Email sending failed:", e)


@auth_bp.route('/request-reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form['email']
        user = find_by_email(email)
        if user:
            from utils import generate_reset_token, send_reset_email
            token = generate_reset_token(email)
            send_reset_email(email, token)
            flash("Reset email sent. Please check your inbox.", "success")
        else:
            flash("No account found with that email.", "error")
        return redirect('/request-reset')
    return render_template('request_reset.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    from utils import get_email_by_token
    email = get_email_by_token(token)
    if not email:
        flash("Invalid or expired reset link.", "error")
        return redirect('/login')

    if request.method == 'POST':
        password = request.form['password']
        from werkzeug.security import generate_password_hash
        hashed_pw = generate_password_hash(password)

        # Update user in sheet
        ws = get_or_create_tab("users")
        records = ws.get_all_records()
        headers = ws.row_values(1)
        password_col = headers.index("password") + 1 if "password" in headers else len(headers) + 1
        if "password" not in headers:
            ws.update_cell(1, password_col, "password")
        for i, r in enumerate(records):
            if r.get("email") == email:
                ws.update_cell(i + 2, password_col, hashed_pw)
                flash("Password updated successfully.", "success")
                return redirect("/login")
        flash("Error updating password.", "error")
        return redirect("/login")

    return render_template('reset_password.html')
