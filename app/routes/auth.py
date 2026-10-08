from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Patient, Doctor, Receptionist, Admin
from app.services.id_generator import next_patient_id
from app.utils import BLOOD_GROUPS

auth_bp = Blueprint('auth', __name__)


def _login_user(role, user, display_id):
    session.clear()
    session['user_id'] = user.id
    session['role'] = role
    session['display_id'] = display_id
    session['name'] = user.name
    session.permanent = True


@auth_bp.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        patient_id = (request.form.get('patient_id') or '').strip().upper()
        password = request.form.get('password') or ''
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if patient and patient.check_password(password):
            _login_user('patient', patient, patient.patient_id)
            flash(f'Welcome back, {patient.name}!', 'success')
            return redirect(url_for('patient.dashboard'))
        flash('Invalid Patient ID or password.', 'error')
    return render_template('auth/patient_login.html')


@auth_bp.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        phone = (request.form.get('phone') or '').strip()
        email = (request.form.get('email') or '').strip()
        address = (request.form.get('address') or '').strip()
        blood_group = request.form.get('blood_group')
        disease = (request.form.get('disease') or '').strip()
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm_password') or ''

        errors = []
        if not name:
            errors.append('Name is required.')
        try:
            age = int(age)
            if age < 0 or age > 150:
                errors.append('Please enter a valid age.')
        except (TypeError, ValueError):
            errors.append('Please enter a valid age.')
        if not gender:
            errors.append('Gender is required.')
        if not phone:
            errors.append('Phone number is required.')
        if blood_group not in BLOOD_GROUPS:
            errors.append('Please select a valid blood group.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'error')
            return render_template('auth/patient_register.html', blood_groups=BLOOD_GROUPS)

        patient_id = next_patient_id()
        patient = Patient(
            patient_id=patient_id,
            name=name,
            age=age,
            gender=gender,
            phone=phone,
            email=email,
            address=address,
            blood_group=blood_group,
            disease=disease,
        )
        patient.set_password(password)
        db.session.add(patient)
        db.session.commit()

        flash(f'Registration successful! Your Patient ID is {patient_id}. Please login with this ID.', 'success')
        return redirect(url_for('auth.patient_login', registered=patient_id))

    return render_template('auth/patient_register.html', blood_groups=BLOOD_GROUPS)


@auth_bp.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        doctor_id = (request.form.get('doctor_id') or '').strip().upper()
        password = request.form.get('password') or ''
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if doctor and doctor.check_password(password):
            _login_user('doctor', doctor, doctor.doctor_id)
            flash(f'Welcome Dr. {doctor.name}!', 'success')
            return redirect(url_for('doctor.dashboard'))
        flash('Invalid Doctor ID or password.', 'error')
    return render_template('auth/doctor_login.html')


@auth_bp.route('/receptionist/login', methods=['GET', 'POST'])
def receptionist_login():
    if request.method == 'POST':
        receptionist_id = (request.form.get('receptionist_id') or '').strip().upper()
        password = request.form.get('password') or ''
        receptionist = Receptionist.query.filter_by(receptionist_id=receptionist_id).first()
        if receptionist and receptionist.check_password(password):
            _login_user('receptionist', receptionist, receptionist.receptionist_id)
            flash(f'Welcome, {receptionist.name}!', 'success')
            return redirect(url_for('receptionist.dashboard'))
        flash('Invalid Receptionist ID or password.', 'error')
    return render_template('auth/receptionist_login.html')


@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = (request.form.get('admin_id') or '').strip().upper()
        password = request.form.get('password') or ''
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if admin and admin.check_password(password):
            _login_user('admin', admin, admin.admin_id)
            flash(f'Welcome, {admin.name}!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid Admin ID or password.', 'error')
    return render_template('auth/admin_login.html')


@auth_bp.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash('You have been logged out.', 'success')
    if role == 'patient':
        return redirect(url_for('auth.patient_login'))
    if role == 'doctor':
        return redirect(url_for('auth.doctor_login'))
    if role == 'receptionist':
        return redirect(url_for('auth.receptionist_login'))
    if role == 'admin':
        return redirect(url_for('auth.admin_login'))
    return redirect(url_for('main.index'))
