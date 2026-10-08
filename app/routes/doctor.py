from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import (
    Doctor, Patient, Appointment, Token, Prescription, PrescriptionMedicine,
    Medicine, MedicineQuestion
)
from app.utils import login_required

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')


def _current_doctor():
    return Doctor.query.get(session['user_id'])


@doctor_bp.route('/dashboard')
@login_required('doctor')
def dashboard():
    doctor = _current_doctor()
    today = date.today()
    today_appts = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today).count()
    waiting = Token.query.filter_by(doctor_id=doctor.id, status='Waiting').count()
    completed = Appointment.query.filter_by(doctor_id=doctor.id, status='Completed').count()
    rx_count = Prescription.query.filter_by(doctor_id=doctor.id).count()
    return render_template(
        'doctor/dashboard.html',
        doctor=doctor,
        today_appts=today_appts,
        waiting=waiting,
        completed=completed,
        rx_count=rx_count,
    )


@doctor_bp.route('/profile', methods=['GET', 'POST'])
@login_required('doctor')
def profile():
    doctor = _current_doctor()
    if request.method == 'POST':
        doctor.name = (request.form.get('name') or doctor.name).strip()
        doctor.email = (request.form.get('email') or '').strip()
        doctor.phone = (request.form.get('phone') or '').strip()
        doctor.qualification = (request.form.get('qualification') or '').strip()
        try:
            doctor.experience = int(request.form.get('experience') or doctor.experience)
        except ValueError:
            pass
        doctor.hospital = (request.form.get('hospital') or '').strip()
        db.session.commit()
        session['name'] = doctor.name
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('doctor.profile'))
    return render_template('doctor/profile.html', doctor=doctor)


@doctor_bp.route('/appointments')
@login_required('doctor')
def appointments():
    doctor = _current_doctor()
    items = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.id.desc()).all()
    return render_template('doctor/appointments.html', doctor=doctor, appointments=items)


@doctor_bp.route('/patients')
@login_required('doctor')
def patients():
    doctor = _current_doctor()
    appts = Appointment.query.filter_by(doctor_id=doctor.id).all()
    patient_ids = {a.patient_id for a in appts}
    patients_list = Patient.query.filter(Patient.id.in_(patient_ids)).all() if patient_ids else []
    return render_template('doctor/patients.html', doctor=doctor, patients=patients_list)


@doctor_bp.route('/add-prescription', methods=['GET', 'POST'])
@login_required('doctor')
def add_prescription():
    doctor = _current_doctor()
    patient = None
    patient_id_q = request.args.get('patient_id') or request.form.get('patient_id')
    if patient_id_q:
        patient = Patient.query.filter_by(patient_id=patient_id_q.strip().upper()).first()
        if not patient and request.method == 'POST':
            flash('Patient not found.', 'error')
    return render_template('doctor/add_prescription.html', doctor=doctor, patient=patient)


@doctor_bp.route('/prescription/<patient_code>', methods=['GET'])
@login_required('doctor')
def write_prescription(patient_code):
    doctor = _current_doctor()
    patient = Patient.query.filter_by(patient_id=patient_code.upper()).first()
    if not patient:
        flash('Patient not found.', 'error')
        return redirect(url_for('doctor.add_prescription'))
    medicines = Medicine.query.filter_by(status='Active').order_by(Medicine.medicine_name).all()
    return render_template(
        'doctor/prescription_form.html',
        doctor=doctor,
        patient=patient,
        medicines=medicines,
        today=date.today().isoformat(),
    )


@doctor_bp.route('/prescription-history')
@login_required('doctor')
def prescription_history():
    doctor = _current_doctor()
    items = Prescription.query.filter_by(doctor_id=doctor.id).order_by(Prescription.id.desc()).all()
    return render_template('doctor/prescription_history.html', doctor=doctor, prescriptions=items)


@doctor_bp.route('/medicines')
@login_required('doctor')
def medicines():
    doctor = _current_doctor()
    items = Medicine.query.filter_by(status='Active').order_by(Medicine.medicine_name).all()
    return render_template('doctor/medicines.html', doctor=doctor, medicines=items)


@doctor_bp.route('/availability', methods=['GET', 'POST'])
@login_required('doctor')
def availability():
    doctor = _current_doctor()
    if request.method == 'POST':
        doctor.availability = request.form.get('availability') or doctor.availability
        doctor.available_from = request.form.get('available_from')
        doctor.available_to = request.form.get('available_to')
        db.session.commit()
        flash('Availability updated.', 'success')
        return redirect(url_for('doctor.availability'))
    return render_template('doctor/availability.html', doctor=doctor)


@doctor_bp.route('/questions', methods=['GET', 'POST'])
@login_required('doctor')
def questions():
    doctor = _current_doctor()
    if request.method == 'POST':
        qid = request.form.get('question_id')
        answer = (request.form.get('doctor_answer') or '').strip()
        q = MedicineQuestion.query.filter_by(id=qid, doctor_id=doctor.id).first()
        if q and answer:
            q.doctor_answer = answer
            q.answer_date = datetime.utcnow()
            q.status = 'Answered'
            db.session.commit()
            flash('Answer submitted.', 'success')
        return redirect(url_for('doctor.questions'))
    items = MedicineQuestion.query.filter_by(doctor_id=doctor.id).order_by(MedicineQuestion.id.desc()).all()
    return render_template('doctor/questions.html', doctor=doctor, questions=items)
