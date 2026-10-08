import smtplib
from email.mime.text import MIMEText
from flask import current_app


def send_email(to_address, subject, body):
    """Send email via SMTP if configured. Silently skips when SMTP is not set."""
    server = current_app.config.get('SMTP_SERVER')
    username = current_app.config.get('SMTP_USERNAME')
    password = current_app.config.get('SMTP_PASSWORD')
    mail_from = current_app.config.get('MAIL_FROM')
    port = current_app.config.get('SMTP_PORT', 587)

    if not server or not username or not password:
        current_app.logger.info('SMTP not configured; email skipped: %s', subject)
        return False

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = to_address

    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)
        return True
    except Exception as exc:
        current_app.logger.error('Email send failed: %s', exc)
        return False
