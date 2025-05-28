from routes.auth import login_required


from flask import Blueprint, render_template, session, redirect, url_for
from flask import session, render_template
import logs_api

student_bp = Blueprint("student", __name__, url_prefix="/student")


from sheets_api import get_all_records
@student_bp.route("/dashboard")
@login_required(role='student')
def dashboard():
    expire_old_logs()
    user = session.get("user")
    if not user or user.get("is_admin"):
        return redirect(url_for("auth.login"))
    
from flask import request
from logs_api import log_start, log_stop
from utils import get_client_ip, get_device_info

@student_bp.route("/start-log", methods=["POST"])
@login_required(role='student')
def start_log():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    activity = request.form["activity"]
    ip = get_client_ip()
    device = get_device_info()
    location = request.form.get("location", "unknown")

    start_time = log_start(user["email"], activity, ip, location, str(device))
    session["start_time"] = start_time
    session["activity"] = activity
    return redirect(url_for("student.dashboard"))

@student_bp.route("/stop-log", methods=["POST"])
@login_required(role='student')
def stop_log():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    activity = session.get("activity")
    start_time = session.get("start_time")
    ip = get_client_ip()
    device = get_device_info()
    location = request.form.get("location", "unknown")

    from logs_api import get_registered_device, is_suspicious
    registered_device, registered_location = get_registered_device(user["email"])
    status, reason = is_suspicious(str(device), location, registered_device, registered_location)
    end_time, duration = log_stop(user["email"], activity, start_time, ip, location, str(device))

    session.pop("start_time", None)
    session.pop("activity", None)
    return redirect(url_for("student.dashboard"))


    
    logs = get_all_records("smart_logs")
    student_logs = [log for log in logs if log.get("student_id") == user["email"]]

    flagged_logs = [log for log in student_logs if log.get("status") == "flagged"]
    expired_logs = [log for log in student_logs if log.get("status") == "expired"]

    alert_message = None
    if flagged_logs:
        alert_message = f"You have {len(flagged_logs)} flagged log(s) that may need review."
    elif expired_logs:
        alert_message = f"You have {len(expired_logs)} expired log(s) — make sure to stop future logs in time."

    return render_template("student_dashboard.html", user=user, alert_message=alert_message)


from sheets_api import get_all_records

@student_bp.route("/my-logs")
@login_required(role='student')
def my_logs():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    logs = get_all_records("smart_logs")
    my_logs = [log for log in logs if log.get("student_id") == user["email"]]
    return render_template("my_logs.html", logs=my_logs)


@student_bp.route("/calendar")
@login_required(role='student')
def calendar():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login"))

    logs = get_all_records("smart_logs")
    my_logs = [log for log in logs if log.get("student_id") == user["email"]]

    events = []
    for log in my_logs:
        if log.get("start"):
            events.append({
                "title": log.get("activity", "Logged"),
                "start": log.get("start").split("T")[0]
            })

    return render_template("student_calendar.html", events=events)

@student.route('/my-activity')
@login_required('student')
def my_activity():
    if 'email' not in session or session.get('user_type') != 'student':
        return "Access denied", 403

    logs = logs_api.get_all_logs()
    user_logs = [log for log in logs if log['email'] == session['email']]
    user_logs.sort(key=lambda x: x.get('date', ''), reverse=True)  # Assuming 'date' field exists
    return render_template('my_activity.html', logs=user_logs)

@student.route('/student-dashboard')
@login_required('student')
def student_dashboard():
    from sheets_api import get_student_badges, get_all_logs
    email = session['user']['email']
    name = session['user']['name']

    # Fetch total hours
    logs = get_all_logs()
    user_logs = [log for log in logs if log.get('email') == email]
    total_hours = sum(float(log.get('hours', 0)) for log in user_logs)

    # Fetch badge data
    badges = get_student_badges(email)

    return render_template('student_dashboard.html', name=name, total_hours=total_hours, badges=badges)

@student.route('/calendar')
@login_required('student')
def student_calendar():
    from logs_api import get_all_logs
    email = session['user']['email']
    logs = get_all_logs()
    user_logs = [log for log in logs if log.get('email') == email]
    return render_template('student_calendar.html', logs=user_logs)


@student.route('/log-hours', methods=['GET', 'POST'])
@login_required('student')
def log_hours():
    from logs_api import log_hours_entry
    if request.method == 'POST':
        activity = request.form['activity']
        hours = request.form['hours']
        email = session['user']['email']
        log_hours_entry(email=email, activity=activity, hours=hours)
        flash("Log entry added.", "success")
        return redirect('/my-activity')
    return render_template('my_logs.html')
