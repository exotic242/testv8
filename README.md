
# Community Service Hours Tracker — Flask + Google Sheets App

## 🔧 Project Overview
This web application allows students to log their community service hours, view badges, track their activity history, and check the leaderboard. Admins can export logs, view analytics, and audit actions. All data is synced in real-time with Google Sheets.

---

## 👤 User Features
- **Register/Login**: Students register with email and grade, login with hashed credentials.
- **Edit Profile**: Change name or email; session and sheet are updated.
- **Smart Logging**: Start/stop a session; logs activity with location, device, and IP.
- **View Logs**: Access full activity history.
- **Badges**: Automatically awarded at 10, 25, 50, 100 hours.
- **Leaderboard**: Displays ranked student hours, live-refreshed.
- **Password Reset**: Request reset link by email and securely set a new password.

---

## 🔐 Admin Features
- **Dashboard**: See total hours and student log summary.
- **Export Logs**: Generate CSV from log data.
- **Audit Log**: Tracks admin actions.
- **Role Protection**: All admin/student routes are secured with decorators.

---

## 🌐 Tech Stack
- **Flask** (with Blueprints)
- **Google Sheets API (gspread)**
- **Bootstrap CSS**
- **Flask-Mail** (for reset emails)
- **Werkzeug** (for password hashing)

---

## 📁 Project Structure
- `/routes/` – Route logic for auth, student, admin, and public
- `/templates/` – HTML templates with Jinja2
- `sheets_api.py` – Google Sheets integration
- `logs_api.py` – Smart log handling
- `utils.py` – Session protection, tokens, helper logic

---

## 📌 Setup Notes
- Fill in `.env` with your Google Sheet ID and mail config
- Install dependencies with `pip install -r requirements.txt`
- Start the server: `python app.py`

---

## ✅ Final Status
All core features are complete and fully functional.
