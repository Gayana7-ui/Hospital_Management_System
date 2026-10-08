from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    role = session.get('role')
    if role == 'patient':
        return redirect(url_for('patient.dashboard'))
    if role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    if role == 'receptionist':
        return redirect(url_for('receptionist.dashboard'))
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('index.html')


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500
