# Real-Time Hospital and Blood Bank Management System

A complete full-stack academic project connecting patients, doctors, receptionists, and administrators. Data is stored in SQLite via Flask-SQLAlchemy. Prescriptions, appointments, tokens, billing, and blood stock are database-backed (not hardcoded mockups).

## Features

- Role-based login for Patient, Doctor, Receptionist, and Admin
- Patient registration with automatic Patient IDs (`PAT001`, `PAT002`, …)
- Appointments, tokens, and live queue updates (AJAX polling)
- Doctor availability and disease-based doctor search
- Online prescriptions with medicines from the database
- Medicine intake as a single string (`1-0-1` = morning-afternoon-night counts)
- Medicine reminders derived from intake patterns
- Patient questions about medicines and doctor answers
- Billing, insurance fields, and payment status
- Emergency hospital search (browser Geolocation + manual search)
- Blood banks, stock, requests, donors, reports, and transactions
- Admin CRUD for core entities

## Technology stack

- **Frontend:** HTML5, CSS3, vanilla JavaScript, Fetch API
- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask sessions, Werkzeug hashing
- **Database:** SQLite (SQLAlchemy ORM; URI can be switched toward MySQL later)
- **Other:** Browser Geolocation API, optional SMTP via `.env`

## Project structure

```
PROJECT/
├── app.py                 # Entry point (python app.py)
├── init_db.py             # Create tables + seed demo data
├── config.py
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py        # Flask factory
│   ├── extensions.py
│   ├── models.py
│   ├── utils.py
│   ├── routes/            # Blueprints + REST APIs
│   └── services/          # IDs, email
├── templates/             # Jinja templates by role
├── static/css|js
└── instance/              # SQLite file after init
```

## Installation (Windows / VS Code)

```powershell
cd path\to\PROJECT
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY`. Do not commit real SMTP passwords.

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Database initialization

```powershell
python init_db.py
```

This is **idempotent**: running it again does not duplicate demo accounts. Tables are also created automatically on first `python app.py` if the SQLite file is missing.

## Run

```powershell
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

Alternatively: `flask --app app run` (after `set FLASK_APP=app.py`).

## Demo login credentials

| Role | ID | Password |
|------|-----|----------|
| Patient | `PAT001` | `Patient@123` |
| Doctor | `DOC001` | `Doctor@123` |
| Receptionist | `REC001` | `Reception@123` |
| Admin | `ADMIN001` | `Admin@123` |

Patients log in with **Patient ID + password**, not phone number. After registration, the unique Patient ID is shown immediately.

## Prescription test flow

1. Doctor login (`DOC001` / `Doctor@123`)
2. Add Prescription → search `PAT001` → Open Prescription
3. Click **+** on medicines from the database
4. Set intake (e.g. `1-0-1`), dosage, days, quantity, instructions
5. Save Prescription
6. Patient login → My Prescriptions and Medicine Reminders

## Blood bank test flow

1. Patient → Blood Requirement
2. Search **O+**, quantity **2**, location **Hospital A**
3. If stock is insufficient, the API returns **alternative blood banks**
4. Admin can update stock; refresh/search again to see new availability

Demo seed: Hospital A (`BB002`) has only **1 unit of O+**, so a request for 2 units shows alternatives (City Blood Bank / Hospital C).

## API (AJAX / JSON)

Authenticated session cookies plus `X-CSRFToken` for JSON POSTs (`csrf.exempt` is used on selected JSON APIs). Examples:

- `GET /api/patients/search?q=PAT001`
- `GET /api/patients/PAT001`
- `GET /api/doctors?disease=fever`
- `POST /api/appointments/<id>/status`
- `GET /api/tokens/queue`
- `POST /api/tokens/<id>/status`
- `GET /api/medicines`
- `POST /api/prescriptions`
- `GET /api/hospitals/emergency?lat=&lon=`
- `GET /api/blood/search?blood_group=O+&quantity=2&location=Hospital%20A`

## Troubleshooting

- **Module not found:** activate the venv and `pip install -r requirements.txt`
- **Database locked / missing:** run `python init_db.py`
- **Invalid login:** use IDs from the table above; passwords are hashed (not stored in plaintext)
- **Port 5000 in use:** stop the other process or change the port in `app.py`
- **CSRF / session expired:** log in again; keep a valid `.env` `SECRET_KEY`

## Deployment notes

- Set a long random `SECRET_KEY` and disable debug
- Point `DATABASE_URL` at a production database (e.g. MySQL) with the same SQLAlchemy models
- Configure SMTP env vars if you want email
- Serve behind a reverse proxy (nginx) with HTTPS in production
- Do not expose `.env` or the SQLite file publicly

## Download / export source

Copy the entire project folder (exclude `venv/` and `instance/*.db` if you want a clean tree). Zip it from File Explorer or:

```powershell
Compress-Archive -Path app.py,app,templates,static,config.py,init_db.py,requirements.txt,README.md,.env.example,.gitignore -DestinationPath HospitalHMS.zip
```
