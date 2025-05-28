
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_path = os.getenv("GOOGLE_CREDS_JSON", "credentials.json")
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(spreadsheet_id)

def get_or_create_tab(name, rows=100, cols=20):
    try:
        return sheet.worksheet(name)
    except:
        return sheet.add_worksheet(title=name, rows=str(rows), cols=str(cols))

def append_row(tab_name, row_data):
    ws = get_or_create_tab(tab_name)
    ws.append_row(row_data)

def get_all_records(tab_name):
    ws = get_or_create_tab(tab_name)
    return ws.get_all_records()

def find_by_email(tab_name, email):
    records = get_all_records(tab_name)
    for r in records:
        if r.get("email") == email:
            return r
    return None


def get_user_goal(email):
    users = get_all_records("users")
    for u in users:
        if u.get("email") == email:
            return float(u.get("goal", 0))
    return 0

def update_user_goal(email, goal):
    ws = get_or_create_tab("users")
    records = ws.get_all_records()
    for i, r in enumerate(records):
        if r.get("email") == email:
            row_index = i + 2
            col_headers = ws.row_values(1)
            if "goal" not in col_headers:
                ws.update_cell(1, len(col_headers) + 1, "goal")
                goal_col = len(col_headers) + 1
            else:
                goal_col = col_headers.index("goal") + 1
            ws.update_cell(row_index, goal_col, goal)
            return True
    return False

def update_student_password(email, new_password_hash):
    worksheet = sh.worksheet("students")
    students = worksheet.get_all_records()
    for i, student in enumerate(students, start=2):  # start=2 to skip header
        if student['email'] == email:
            worksheet.update_cell(i, student.keys().index('password') + 1, new_password_hash)
            return True
    return False

def log_admin_action(admin_email, action_type, description):
    worksheet = sh.worksheet("audit_log")
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([now, admin_email, action_type, description])


def get_student_badges(email):
    logs = get_all_records("logs")
    user_logs = [log for log in logs if log.get("email") == email]
    total_hours = sum(float(log.get("hours", 0)) for log in user_logs)

    badges = []
    if total_hours >= 10:
        badges.append("10 Hour Badge")
    if total_hours >= 25:
        badges.append("25 Hour Star")
    if total_hours >= 50:
        badges.append("50 Hour Champion")
    if total_hours >= 100:
        badges.append("Century Hero")

    return badges
