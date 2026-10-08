import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-me-in-production')
    _db_url = os.getenv('DATABASE_URL', '').strip()
    if not _db_url:
        _db_url = f"sqlite:///{(BASE_DIR / 'instance' / 'hospital.db').as_posix()}"
    elif _db_url.startswith('sqlite:///') and not _db_url.startswith('sqlite:////'):
        rel = _db_url.replace('sqlite:///', '', 1)
        if rel and not Path(rel).is_absolute():
            _db_url = f"sqlite:///{(BASE_DIR / rel).as_posix()}"
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    MAIL_FROM = os.getenv('MAIL_FROM', 'Hospital System <noreply@hospital.local>')
