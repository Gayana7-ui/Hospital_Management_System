from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import (
    Patient, Doctor, Appointment, Token, Billing, Hospital
)
from app.services.id_generator import (
    next_patient_id, next_appointment_id, next_token_number, next_bill_id
)
from app.utils import login_required, BLOOD_GROUPS, specialization_for_disease

receptionist_bp = Blueprint('receptionist', __name__, url_prefix='/receptionist')


def _current_receptionist():
    from app.models import Receptionist
    return Receptionist.query.get(session['user_id'])


@receptionist_bp.route('/dashboard')
@login_required('receptionist')
def dashboard():
    receptionist = _current_receptionist()
    stats = {
        'patients': Patient.query.count(),
        'appointments_today': Appointment.query.filter_by(appointment_date=date.today()).count(),
        'waiting': Token.query.filter_by(status='Waiting').count(),
        'pending_bills': Billing.query.filter(Billing.payment_status.in_(['Pending', 'Partially Paid'])).count(),
    }
    return render_template('receptionist/dashboard.html', receptionist=receptionist, stats=stats)


@receptionist_bp.route('/register-patient', methods=['GET', 'POST'])
@login_required('receptionist')
def register_patient():
    receptionist = _current_receptionist()
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        phone = (request.form.get('phone') or '').strip()
        password = request.form.get('password') or 'Patient@123'
        try:
            age = int(request.form.get('age') or 0)
        except ValueError:
            flash('Please enter a valid age.', 'error')
            return redirect(url_for('receptionist.register_patient'))
        if not name or not phone:
            flash('Name and phone are required.', 'error')
            return redirect(url_for('receptionist.register_patient'))
        patient = Patient(
            patient_id=next_patient_id(),
            name=name,
            age=age,
            gender=request.form.get('gender') or 'Other',
            phone=phone,
            email=(request.form.get('email') or '').strip(),
            address=(request.form.get('address') or '').strip(),
            blood_group=request.form.get('blood_group') or 'O+',
            disease=(request.form.get('disease') or '').strip(),
        )
        patient.set_password(password)
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient registered. Patient ID: {patient.patient_id}', 'success')
        return redirect(url_for('receptionist.search_patient', q=patient.patient_id))
    return render_template('receptionist/register_patient.html', receptionist=receptionist, blood_groups=BLOOD_GROUPS)


@receptionist_bp.route('/search-patient')
@login_required('receptionist')
def search_patient():
    receptionist = _current_receptionist()
    q = (request.args.get('q') or '').strip()
    patients = []
    if q:
        like = f'%{q}%'
        patients = Patient.query.filter(
            db.or_(
                Patient.patient_id.ilike(like),
                Patient.name.ilike(like),
                Patient.phone.ilike(like),
            )
        ).all()
    return render_template('receptionist/search_patient.html', receptionist=receptionist, patients=patients, q=q)


@receptionist_bp.route('/appointments', methods=['GET', 'POST'])
@login_required('receptionist')
def appointments():
    receptionist = _current_receptionist()
    doctors = Doctor.query.filter_by(status='Active').all()
    if request.method == 'POST':
        patient = Patient.query.filter_by(patient_id=(request.form.get('patient_id') or '').upper()).first()
        doctor = Doctor.query.filter_by(doctor_id=request.form.get('doctor_id')).first()
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('receptionist.appointments'))
        if not doctor:
            flash('Doctor not found.', 'error')
            return redirect(url_for('receptionist.appointments'))
        if doctor.availability in ('Not Available', 'On Leave'):
            flash('Doctor not available.', 'error')
            return redirect(url_for('receptionist.appointments'))
        try:
            appt_date = datetime.strptime(request.form.get('appointment_date'), '%Y-%m-%d').date()
        except (TypeError, ValueError):
            flash('Please enter a valid date.', 'error')
            return redirect(url_for('receptionist.appointments'))
        disease = (request.form.get('disease') or patient.disease or '').strip()
        if disease:
            patient.disease = disease
        appt = Appointment(
            appointment_id=next_appointment_id(),
            patient_id=patient.id,
            doctor_id=doctor.id,
            department=doctor.specialization,
            appointment_date=appt_date,
            appointment_time=request.form.get('appointment_time') or '09:00',
            reason=request.form.get('reason') or disease,
            status='Confirmed',
        )
        db.session.add(appt)
        db.session.flush()
        waiting_count = Token.query.filter_by(doctor_id=doctor.id, status='Waiting').count()
        token = Token(
            token_number=next_token_number(),
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_id=appt.id,
            appointment_time=appt.appointment_time,
            queue_position=waiting_count + 1,
            status='Waiting',
            entry_fee=float(request.form.get('entry_fee') or 0),
        )
        db.session.add(token)
        db.session.commit()
        flash(f'Appointment created. Token: {token.token_number}', 'success')
        return redirect(url_for('receptionist.tokens'))
    items = Appointment.query.order_by(Appointment.id.desc()).limit(50).all()
    return render_template(
        'receptionist/appointments.html',
        receptionist=receptionist, appointments=items, doctors=doctors
    )


@receptionist_bp.route('/tokens')
@login_required('receptionist')
def tokens():
    receptionist = _current_receptionist()
    tokens_list = Token.query.order_by(Token.queue_position, Token.id).all()
    return render_template('receptionist/tokens.html', receptionist=receptionist, tokens=tokens_list)


@receptionist_bp.route('/queue')
@login_required('receptionist')
def queue():
    receptionist = _current_receptionist()
    tokens_list = Token.query.filter(Token.status.in_(['Waiting', 'In Consultation'])).order_by(
        Token.queue_position, Token.id
    ).all()
    return render_template('receptionist/queue.html', receptionist=receptionist, tokens=tokens_list)


@receptionist_bp.route('/patient-entry', methods=['GET', 'POST'])
@login_required('receptionist')
def patient_entry():
    receptionist = _current_receptionist()
    doctors = Doctor.query.filter(
        Doctor.status == 'Active',
        Doctor.availability.in_(['Available', 'Emergency Only'])
    ).all()
    if request.method == 'POST':
        patient = Patient.query.filter_by(patient_id=(request.form.get('patient_id') or '').upper()).first()
        doctor = Doctor.query.filter_by(doctor_id=request.form.get('doctor_id')).first()
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('receptionist.patient_entry'))
        entry_fee = float(request.form.get('entry_fee') or 50)
        disease = (request.form.get('disease') or '').strip()
        if disease:
            patient.disease = disease
        waiting_count = Token.query.filter_by(status='Waiting').count()
        token = Token(
            token_number=next_token_number(),
            patient_id=patient.id,
            doctor_id=doctor.id if doctor else None,
            appointment_time=datetime.now().strftime('%H:%M'),
            queue_position=waiting_count + 1,
            status='Waiting',
            entry_fee=entry_fee,
        )
        bill = Billing(
            bill_id=next_bill_id(),
            patient_id=patient.id,
            hospital=request.form.get('hospital') or 'City General Hospital',
            entry_fee=entry_fee,
            consultation_fee=float(request.form.get('consultation_fee') or 200),
            total_amount=0,
            amount_paid=0,
            balance=0,
            payment_status='Pending',
        )
        bill.total_amount = bill.entry_fee + bill.consultation_fee
        bill.balance = bill.total_amount
        db.session.add(token)
        db.session.add(bill)
        db.session.commit()
        flash(f'Patient entry recorded. Token: {token.token_number}, Bill: {bill.bill_id}', 'success')
        return redirect(url_for('receptionist.queue'))
    return render_template(
        'receptionist/patient_entry.html',
        receptionist=receptionist, doctors=doctors
    )


@receptionist_bp.route('/billing', methods=['GET', 'POST'])
@login_required('receptionist')
def billing():
    receptionist = _current_receptionist()
    if request.method == 'POST':
        patient = Patient.query.filter_by(patient_id=(request.form.get('patient_id') or '').upper()).first()
        if not patient:
            flash('Patient not found.', 'error')
            return redirect(url_for('receptionist.billing'))
        consultation = float(request.form.get('consultation_fee') or 0)
        entry = float(request.form.get('entry_fee') or 0)
        medicine = float(request.form.get('medicine_charges') or 0)
        other = float(request.form.get('other_charges') or 0)
        insurance = float(request.form.get('insurance') or 0)
        paid = float(request.form.get('amount_paid') or 0)
        total = consultation + entry + medicine + other - insurance
        balance = total - paid
        if balance <= 0:
            status = 'Paid'
            balance = 0
        elif paid > 0:
            status = 'Partially Paid'
        else:
            status = 'Pending'
        bill = Billing(
            bill_id=next_bill_id(),
            patient_id=patient.id,
            hospital=request.form.get('hospital') or 'City General Hospital',
            consultation_fee=consultation,
            entry_fee=entry,
            medicine_charges=medicine,
            other_charges=other,
            insurance=insurance,
            total_amount=total,
            amount_paid=paid,
            balance=balance,
            payment_status=status,
            claim_amount=insurance,
            claim_status='Applied' if insurance > 0 else 'None',
        )
        db.session.add(bill)
        db.session.commit()
        flash(f'Bill {bill.bill_id} created.', 'success')
        return redirect(url_for('receptionist.billing'))
    bills = Billing.query.order_by(Billing.id.desc()).limit(50).all()
    return render_template('receptionist/billing.html', receptionist=receptionist, bills=bills)


@receptionist_bp.route('/doctor-availability')
@login_required('receptionist')
def doctor_availability():
    receptionist = _current_receptionist()
    doctors = Doctor.query.filter_by(status='Active').all()
    disease = request.args.get('disease', '')
    filtered = doctors
    if disease:
        spec = specialization_for_disease(disease)
        filtered = [d for d in doctors if spec.lower() in (d.specialization or '').lower()]
    return render_template(
        'receptionist/doctor_availability.html',
        receptionist=receptionist, doctors=filtered, disease=disease
    )
