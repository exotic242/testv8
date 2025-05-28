
import datetime
from sheets_api import append_row

def log_start(student_id, activity, ip, location, device):
    timestamp = datetime.datetime.now().isoformat()
    append_row("smart_logs", [
        student_id, activity, timestamp, "", ip, location, device, "", "", "started"
    ])
    return timestamp

def log_stop(student_id, activity, start_time, ip, location, device):
    end_time = datetime.datetime.now().isoformat()
    start_dt = datetime.datetime.fromisoformat(start_time)
    end_dt = datetime.datetime.fromisoformat(end_time)
    duration_hours = round((end_dt - start_dt).total_seconds() / 3600, 2)

    append_row("smart_logs", [
        student_id, activity, start_time, end_time, ip, location, device,
        duration_hours, "verified", "completed"
    ])
    return end_time, duration_hours


from sheets_api import get_all_records

def get_registered_device(email):
    users = get_all_records("users")
    for u in users:
        if u.get("email") == email:
            return u.get("device_info", ""), u.get("location", "")
    return "", ""

def is_suspicious(current_device, current_location, registered_device, registered_location):
    reasons = []
    if registered_device and current_device != registered_device:
        reasons.append("Device mismatch")
    if registered_location and current_location != registered_location:
        reasons.append("Location mismatch")
    if reasons:
        return "flagged", "; ".join(reasons)
    return "verified", ""


def expire_old_logs():
    logs = get_all_records("smart_logs")
    now = datetime.datetime.now()
    expired_count = 0

    for log in logs:
        if log.get("status") == "started":
            try:
                start_time = datetime.datetime.fromisoformat(log.get("start"))
                elapsed = (now - start_time).total_seconds() / 3600
                if elapsed > 12:
                    append_row("smart_logs", [
                        log.get("student_id"), log.get("activity"), log.get("start"), "", 
                        log.get("ip"), log.get("location"), log.get("device"),
                        "", "expired", "Auto-expired after timeout"
                    ])
                    expired_count += 1
            except Exception:
                continue
    return expired_count
