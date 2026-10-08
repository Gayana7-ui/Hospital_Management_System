from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import (
    Patient, Doctor, Appointment, Token, Prescription, Billing,
    MedicineQuestion, BloodRequest, Hospital
)
from app.services.id_generator import next_appointment_id, next_blood_request_id
from app.utils import login_required, BLOOD_GROUPS, specialization_for_disease

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


def _current_patient():
    return Patient.query.get(session['user_id'])


@patient_bp.route('/dashboard')
@login_required('patient')
def dashboard():
    patient = _current_patient()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(['Pending', 'Confirmed']),
        Appointment.appointment_date >= date.today()
    ).order_by(Appointment.appointment_date).first()
    current_token = Token.query.filter(
        Token.patient_id == patient.id,
        Token.status.in_(['Waiting', 'In Consultation'])
    ).order_by(Token.id.desc()).first()
    rx_count = Prescription.query.filter_by(patient_id=patient.id).count()
    pending_bill = Billing.query.filter(
        Billing.patient_id == patient.id,
        Billing.payment_status.in_(['Pending', 'Partially Paid'])
    ).order_by(Billing.id.desc()).first()
    blood_req = BloodRequest.query.filter_by(patient_id=patient.id).order_by(BloodRequest.id.desc()).first()
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        upcoming=upcoming,
        current_token=current_token,
        rx_count=rx_count,
        pending_bill=pending_bill,
        blood_req=blood_req,
    )


@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required('patient')
def profile():
    patient = _current_patient()
    if request.method == 'POST':
        patient.name = (request.form.get('name') or patient.name).strip()
        try:
            patient.age = int(request.form.get('age') or patient.age)
        except ValueError:
            flash('Please enter a valid age.', 'error')
            return redirect(url_for('patient.profile'))
        patient.gender = request.form.get('gender') or patient.gender
        patient.phone = (request.form.get('phone') or patient.phone).strip()
        patient.email = (request.form.get('email') or '').strip()
        patient.address = (request.form.get('address') or '').strip()
        bg = request.form.get('blood_group')
        if bg in BLOOD_GROUPS:
            patient.blood_group = bg
        patient.disease = (request.form.get('disease') or '').strip()
        patient.insurance_provider = (request.form.get('insurance_provider') or '').strip()
        patient.policy_number = (request.form.get('policy_number') or '').strip()
        try:
            patient.coverage_amount = float(request.form.get('coverage_amount') or 0)
        except ValueError:
            patient.coverage_amount = 0
        db.session.commit()
        session['name'] = patient.name
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('patient.profile'))
    return render_template('patient/profile.html', patient=patient, blood_groups=BLOOD_GROUPS)


@patient_bp.route('/book-appointment', methods=['GET', 'POST'])
@login_required('patient')
def book_appointment():
    patient = _current_patient()
    doctors = Doctor.query.filter_by(status='Active').all()
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        appt_date = request.form.get('appointment_date')
        appt_time = request.form.get('appointment_time')
        reason = (request.form.get('reason') or '').strip()
        doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
        if not doctor:
            flash('Doctor not found.', 'error')
            return redirect(url_for('patient.book_appointment'))
        if doctor.availability in ('Not Available', 'On Leave'):
            alts = Doctor.query.filter(
                Doctor.specialization == doctor.specialization,
                Doctor.availability == 'Available',
                Doctor.status == 'Active',
                Doctor.id != doctor.id
            ).all()
            flash('Doctor not available. Please select an alternative doctor.', 'error')
            return render_template(
                'patient/book_appointment.html',
                patient=patient, doctors=doctors, alternatives=alts, selected=doctor
            )
        try:
            parsed_date = datetime.strptime(appt_date, '%Y-%m-%d').date()
        except (TypeError, ValueError):
            flash('Please enter a valid appointment date.', 'error')
            return redirect(url_for('patient.book_appointment'))
        appt = Appointment(
            appointment_id=next_appointment_id(),
            patient_id=patient.id,
            doctor_id=doctor.id,
            department=doctor.specialization,
            appointment_date=parsed_date,
            appointment_time=appt_time,
            reason=reason or patient.disease,
            status='Pending',
        )
        db.session.add(appt)
        db.session.commit()
        flash(f'Appointment {appt.appointment_id} requested successfully.', 'success')
        return redirect(url_for('patient.appointments'))
    return render_template('patient/book_appointment.html', patient=patient, doctors=doctors, alternatives=None)


@patient_bp.route('/appointments')
@login_required('patient')
def appointments():
    patient = _current_patient()
    items = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.id.desc()).all()
    return render_template('patient/appointments.html', patient=patient, appointments=items)


@patient_bp.route('/token')
@login_required('patient')
def token():
    patient = _current_patient()
    tokens = Token.query.filter_by(patient_id=patient.id).order_by(Token.id.desc()).all()
    return render_template('patient/token.html', patient=patient, tokens=tokens)


@patient_bp.route('/prescriptions')
@login_required('patient')
def prescriptions():
    patient = _current_patient()
    items = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.id.desc()).all()
    return render_template('patient/prescriptions.html', patient=patient, prescriptions=items)


@patient_bp.route('/reminders')
@login_required('patient')
def reminders():
    patient = _current_patient()
    items = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.id.desc()).all()
    reminders_list = []
    for rx in items:
        for med in rx.medicines:
            parts = (med.medicine_intake or '0-0-0').split('-')
            reminders_list.append({
                'prescription_id': rx.prescription_id,
                'medicine_name': med.medicine_name,
                'medicine_intake': med.medicine_intake,
                'morning': parts[0] if len(parts) > 0 else '0',
                'afternoon': parts[1] if len(parts) > 1 else '0',
                'night': parts[2] if len(parts) > 2 else '0',
                'number_of_days': med.number_of_days,
                'instructions': med.instructions,
                'dosage': med.dosage,
                'status': 'Active',
            })
    return render_template('patient/reminders.html', patient=patient, reminders=reminders_list)


@patient_bp.route('/ask-doctor', methods=['GET', 'POST'])
@login_required('patient')
def ask_doctor():
    patient = _current_patient()
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
    if request.method == 'POST':
        rx_id = request.form.get('prescription_id')
        medicine = (request.form.get('medicine_name') or '').strip()
        question = (request.form.get('question') or '').strip()
        rx = Prescription.query.filter_by(prescription_id=rx_id, patient_id=patient.id).first()
        if not rx or not medicine or not question:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('patient.ask_doctor'))
        q = MedicineQuestion(
            patient_id=patient.id,
            doctor_id=rx.doctor_id,
            prescription_id=rx.id,
            medicine_name=medicine,
            question=question,
            status='Pending',
        )
        db.session.add(q)
        db.session.commit()
        flash('Question submitted successfully.', 'success')
        return redirect(url_for('patient.ask_doctor'))
    questions = MedicineQuestion.query.filter_by(patient_id=patient.id).order_by(MedicineQuestion.id.desc()).all()
    return render_template('patient/ask_doctor.html', patient=patient, prescriptions=prescriptions, questions=questions)


@patient_bp.route('/billing')
@login_required('patient')
def billing():
    patient = _current_patient()
    bills = Billing.query.filter_by(patient_id=patient.id).order_by(Billing.id.desc()).all()
    return render_template('patient/billing.html', patient=patient, bills=bills)


@patient_bp.route('/blood-requirement', methods=['GET', 'POST'])
@login_required('patient')
def blood_requirement():
    patient = _current_patient()
    hospitals = Hospital.query.filter_by(status='Active').all()
    if request.method == 'POST':
        try:
            qty = float(request.form.get('quantity_required') or 0)
            if qty <= 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid blood quantity.', 'error')
            return redirect(url_for('patient.blood_requirement'))
        req_date = request.form.get('required_date')
        parsed = None
        if req_date:
            try:
                parsed = datetime.strptime(req_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Please enter a valid required date.', 'error')
                return redirect(url_for('patient.blood_requirement'))
        req = BloodRequest(
            request_id=next_blood_request_id(),
            patient_id=patient.id,
            patient_name=patient.name,
            hospital=request.form.get('hospital'),
            blood_group_required=request.form.get('blood_group_required') or patient.blood_group,
            quantity_required=qty,
            required_date=parsed,
            disease_reason=(request.form.get('disease_reason') or patient.disease or '').strip(),
            contact_number=request.form.get('contact_number') or patient.phone,
            location=request.form.get('location'),
            status='Pending',
        )
        db.session.add(req)
        db.session.commit()
        flash(f'Blood requirement {req.request_id} submitted.', 'success')
        return redirect(url_for('patient.blood_requirement'))
    requests_list = BloodRequest.query.filter_by(patient_id=patient.id).order_by(BloodRequest.id.desc()).all()
    return render_template(
        'patient/blood_requirement.html',
        patient=patient, hospitals=hospitals, requests=requests_list, blood_groups=BLOOD_GROUPS
    )


@patient_bp.route('/emergency-hospitals')
@login_required('patient')
def emergency_hospitals():
    patient = _current_patient()
    hospitals = Hospital.query.filter_by(status='Active').all()
    return render_template('patient/emergency_hospitals.html', patient=patient, hospitals=hospitals)


@patient_bp.route('/search-doctors')
@login_required('patient')
def search_doctors():
    patient = _current_patient()
    disease = request.args.get('disease', '')
    doctors = []
    if disease:
        spec = specialization_for_disease(disease)
        doctors = Doctor.query.filter(
            Doctor.status == 'Active',
            Doctor.specialization.ilike(f'%{spec}%')
        ).all()
        if not doctors:
            doctors = Doctor.query.filter_by(status='Active', availability='Available').all()
    return render_template('patient/search_doctors.html', patient=patient, doctors=doctors, disease=disease)
