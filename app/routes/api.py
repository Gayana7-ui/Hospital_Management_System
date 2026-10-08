from datetime import datetime, date
from flask import Blueprint, request, jsonify, session
from app.extensions import db, csrf
from app.models import (
    Patient, Doctor, Appointment, Token, Medicine, Prescription,
    PrescriptionMedicine, MedicineQuestion, Billing, Hospital,
    BloodBank, BloodStock, BloodRequest, Donor
)
from app.services.id_generator import next_prescription_id, next_appointment_id, next_token_number
from app.utils import login_required, haversine_km, specialization_for_disease, BLOOD_GROUPS

api_bp = Blueprint('api', __name__, url_prefix='/api')


def _ok(data=None, message='OK', status=200):
    payload = {'success': True, 'message': message}
    if data is not None:
        payload['data'] = data
    return jsonify(payload), status


def _err(message, status=400):
    return jsonify({'success': False, 'message': message}), status


@api_bp.route('/csrf-token')
def csrf_token():
    from flask_wtf.csrf import generate_csrf
    return _ok({'csrf_token': generate_csrf()})


# ---------- Patients ----------
@api_bp.route('/patients/search')
@login_required(['doctor', 'receptionist', 'admin'])
def search_patients():
    q = (request.args.get('q') or '').strip()
    if not q:
        return _ok([])
    like = f'%{q}%'
    patients = Patient.query.filter(
        db.or_(
            Patient.patient_id.ilike(like),
            Patient.name.ilike(like),
            Patient.phone.ilike(like),
        )
    ).limit(20).all()
    return _ok([p.to_dict() for p in patients])


@api_bp.route('/patients/<patient_code>')
@login_required(['doctor', 'receptionist', 'admin', 'patient'])
def get_patient(patient_code):
    patient = Patient.query.filter_by(patient_id=patient_code.upper()).first()
    if not patient:
        return _err('Patient not found.', 404)
    if session.get('role') == 'patient' and session.get('user_id') != patient.id:
        return _err('Unauthorized access.', 403)
    return _ok(patient.to_dict())


# ---------- Doctors ----------
@api_bp.route('/doctors')
@login_required(['patient', 'doctor', 'receptionist', 'admin'])
def list_doctors():
    disease = request.args.get('disease')
    specialization = request.args.get('specialization')
    q = Doctor.query.filter_by(status='Active')
    if disease:
        spec = specialization_for_disease(disease)
        q = q.filter(Doctor.specialization.ilike(f'%{spec}%'))
    if specialization:
        q = q.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    doctors = q.all()
    return _ok([d.to_dict() for d in doctors])


@api_bp.route('/doctors/search')
@login_required(['patient', 'receptionist', 'admin'])
def search_doctors():
    q = (request.args.get('q') or '').strip()
    like = f'%{q}%'
    doctors = Doctor.query.filter(
        Doctor.status == 'Active',
        db.or_(
            Doctor.doctor_id.ilike(like),
            Doctor.name.ilike(like),
            Doctor.specialization.ilike(like),
        )
    ).limit(20).all()
    return _ok([d.to_dict() for d in doctors])


@api_bp.route('/doctors/<doctor_code>/availability', methods=['POST'])
@csrf.exempt
@login_required('doctor')
def update_doctor_availability(doctor_code):
    doctor = Doctor.query.filter_by(doctor_id=doctor_code.upper()).first()
    if not doctor or doctor.id != session.get('user_id'):
        return _err('Unauthorized access.', 403)
    data = request.get_json(silent=True) or {}
    doctor.availability = data.get('availability') or doctor.availability
    doctor.available_from = data.get('available_from', doctor.available_from)
    doctor.available_to = data.get('available_to', doctor.available_to)
    db.session.commit()
    return _ok(doctor.to_dict(), 'Availability updated.')


@api_bp.route('/doctors/alternatives')
@login_required(['patient', 'receptionist'])
def alternative_doctors():
    doctor_id = request.args.get('doctor_id')
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return _err('Doctor not found.', 404)
    alts = Doctor.query.filter(
        Doctor.specialization == doctor.specialization,
        Doctor.availability == 'Available',
        Doctor.status == 'Active',
        Doctor.id != doctor.id
    ).all()
    return _ok([d.to_dict() for d in alts])


# ---------- Appointments ----------
@api_bp.route('/appointments', methods=['GET'])
@login_required(['patient', 'doctor', 'receptionist', 'admin'])
def list_appointments():
    role = session.get('role')
    q = Appointment.query
    if role == 'patient':
        q = q.filter_by(patient_id=session['user_id'])
    elif role == 'doctor':
        q = q.filter_by(doctor_id=session['user_id'])
    items = q.order_by(Appointment.id.desc()).limit(100).all()
    return _ok([a.to_dict() for a in items])


@api_bp.route('/appointments/<int:appt_id>/status', methods=['POST'])
@csrf.exempt
@login_required(['doctor', 'receptionist', 'admin'])
def update_appointment_status(appt_id):
    appt = Appointment.query.get(appt_id)
    if not appt:
        return _err('Appointment not found.', 404)
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in ('Pending', 'Confirmed', 'Completed', 'Cancelled'):
        return _err('Invalid status.')
    appt.status = status
    if appt.token:
        if status == 'Completed':
            appt.token.status = 'Completed'
        elif status == 'Cancelled':
            appt.token.status = 'Cancelled'
    db.session.commit()
    return _ok(appt.to_dict(), 'Appointment status updated.')


# ---------- Tokens / Queue ----------
@api_bp.route('/tokens/queue')
@login_required(['patient', 'doctor', 'receptionist', 'admin'])
def queue_tokens():
    role = session.get('role')
    q = Token.query.filter(Token.status.in_(['Waiting', 'In Consultation']))
    if role == 'doctor':
        q = q.filter_by(doctor_id=session['user_id'])
    elif role == 'patient':
        q = q.filter_by(patient_id=session['user_id'])
    tokens = q.order_by(Token.queue_position, Token.id).all()
    return _ok([t.to_dict() for t in tokens])


@api_bp.route('/tokens/<int:token_id>/status', methods=['POST'])
@csrf.exempt
@login_required(['doctor', 'receptionist', 'admin'])
def update_token_status(token_id):
    token = Token.query.get(token_id)
    if not token:
        return _err('Token not found.', 404)
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in ('Waiting', 'In Consultation', 'Completed', 'Cancelled'):
        return _err('Invalid status.')
    token.status = status
    db.session.commit()
    return _ok(token.to_dict(), 'Token status updated.')


# ---------- Medicines ----------
@api_bp.route('/medicines')
@login_required(['doctor', 'admin', 'patient'])
def list_medicines():
    q = (request.args.get('q') or '').strip()
    query = Medicine.query.filter_by(status='Active')
    if q:
        query = query.filter(Medicine.medicine_name.ilike(f'%{q}%'))
    items = query.order_by(Medicine.medicine_name).all()
    return _ok([m.to_dict() for m in items])


# ---------- Prescriptions ----------
@api_bp.route('/prescriptions', methods=['POST'])
@csrf.exempt
@login_required('doctor')
def create_prescription():
    data = request.get_json(silent=True) or {}
    patient_code = (data.get('patient_id') or '').upper()
    patient = Patient.query.filter_by(patient_id=patient_code).first()
    if not patient:
        return _err('Patient not found.', 404)
    medicines = data.get('medicines') or []
    if not medicines:
        return _err('Please select at least one medicine.')
    doctor = Doctor.query.get(session['user_id'])
    rx = Prescription(
        prescription_id=next_prescription_id(),
        patient_id=patient.id,
        doctor_id=doctor.id,
        prescription_date=date.today(),
        diagnosis=(data.get('diagnosis') or '').strip(),
        notes=(data.get('notes') or '').strip(),
    )
    db.session.add(rx)
    db.session.flush()
    for med in medicines:
        intake = (med.get('medicine_intake') or '1-0-1').strip()
        parts = intake.split('-')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            db.session.rollback()
            return _err('Invalid medicine intake pattern. Use format like 1-0-1.')
        pm = PrescriptionMedicine(
            prescription_id=rx.id,
            medicine_id=med.get('medicine_id'),
            medicine_name=med.get('medicine_name'),
            dosage=med.get('dosage'),
            medicine_intake=intake,
            number_of_days=int(med.get('number_of_days') or 1),
            quantity=int(med.get('quantity') or 1),
            instructions=med.get('instructions'),
        )
        db.session.add(pm)
    db.session.commit()
    return _ok(rx.to_dict(), 'Prescription saved successfully.')


@api_bp.route('/prescriptions/<rx_id>')
@login_required(['patient', 'doctor', 'admin'])
def get_prescription(rx_id):
    rx = Prescription.query.filter_by(prescription_id=rx_id).first()
    if not rx:
        return _err('Prescription not found.', 404)
    if session.get('role') == 'patient' and rx.patient_id != session.get('user_id'):
        return _err('Unauthorized access.', 403)
    return _ok(rx.to_dict())


# ---------- Medicine Questions ----------
@api_bp.route('/questions/<int:qid>/answer', methods=['POST'])
@csrf.exempt
@login_required('doctor')
def answer_question(qid):
    q = MedicineQuestion.query.get(qid)
    if not q or q.doctor_id != session.get('user_id'):
        return _err('Question not found.', 404)
    data = request.get_json(silent=True) or {}
    answer = (data.get('doctor_answer') or '').strip()
    if not answer:
        return _err('Answer is required.')
    q.doctor_answer = answer
    q.answer_date = datetime.utcnow()
    q.status = 'Answered'
    db.session.commit()
    return _ok(q.to_dict(), 'Answer saved.')


# ---------- Billing ----------
@api_bp.route('/billing/<bill_id>/pay', methods=['POST'])
@csrf.exempt
@login_required(['receptionist', 'admin'])
def pay_bill(bill_id):
    bill = Billing.query.filter_by(bill_id=bill_id).first()
    if not bill:
        return _err('Bill not found.', 404)
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get('amount') or 0)
    except (TypeError, ValueError):
        return _err('Invalid payment amount.')
    if amount <= 0:
        return _err('Invalid payment amount.')
    bill.amount_paid += amount
    bill.balance = max(0, bill.total_amount - bill.amount_paid)
    if bill.balance <= 0:
        bill.payment_status = 'Paid'
        bill.balance = 0
    else:
        bill.payment_status = 'Partially Paid'
    db.session.commit()
    return _ok(bill.to_dict(), 'Payment recorded.')


# ---------- Hospitals / Emergency ----------
@api_bp.route('/hospitals')
@login_required(['patient', 'receptionist', 'admin'])
def list_hospitals():
    q = (request.args.get('q') or '').strip()
    city = request.args.get('city')
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    query = Hospital.query.filter_by(status='Active')
    if q:
        like = f'%{q}%'
        query = query.filter(db.or_(Hospital.name.ilike(like), Hospital.city.ilike(like), Hospital.address.ilike(like)))
    if city:
        query = query.filter(Hospital.city.ilike(f'%{city}%'))
    hospitals = query.all()
    result = []
    for h in hospitals:
        d = h.to_dict()
        if lat is not None and lon is not None:
            d['distance_km'] = haversine_km(lat, lon, h.latitude, h.longitude)
        result.append(d)
    if lat is not None and lon is not None:
        result.sort(key=lambda x: x.get('distance_km') if x.get('distance_km') is not None else 99999)
    return _ok(result)


@api_bp.route('/hospitals/emergency')
@login_required(['patient', 'receptionist', 'admin'])
def emergency_hospitals():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    q = (request.args.get('q') or '').strip()
    query = Hospital.query.filter_by(status='Active', emergency_available=True)
    if q:
        like = f'%{q}%'
        query = query.filter(db.or_(Hospital.name.ilike(like), Hospital.city.ilike(like)))
    hospitals = query.all()
    result = []
    for h in hospitals:
        d = h.to_dict()
        if lat is not None and lon is not None:
            d['distance_km'] = haversine_km(lat, lon, h.latitude, h.longitude)
        result.append(d)
    if lat is not None:
        result.sort(key=lambda x: x.get('distance_km') if x.get('distance_km') is not None else 99999)
    return _ok(result)


# ---------- Blood ----------
@api_bp.route('/blood/search')
@login_required(['patient', 'receptionist', 'admin'])
def search_blood():
    blood_group = request.args.get('blood_group')
    try:
        quantity = float(request.args.get('quantity') or 0)
    except ValueError:
        return _err('Please enter a valid blood quantity.')
    location = (request.args.get('location') or '').strip()

    if blood_group not in BLOOD_GROUPS:
        return _err('Please select a valid blood group.')
    if quantity <= 0:
        return _err('Please enter a valid blood quantity.')

    stocks = BloodStock.query.filter(
        BloodStock.blood_group == blood_group,
        BloodStock.available_quantity > 0,
        BloodStock.status == 'Available'
    ).all()

    matching = []
    alternatives = []
    for s in stocks:
        item = s.to_dict()
        loc_match = True
        if location:
            loc_text = f"{item.get('location') or ''} {item.get('hospital') or ''} {item.get('blood_bank_name') or ''}".lower()
            loc_match = location.lower() in loc_text
        if loc_match and s.available_quantity >= quantity:
            matching.append(item)
        else:
            if s.available_quantity > 0:
                alternatives.append(item)

    if matching:
        return _ok({'available': True, 'results': matching, 'alternatives': []})

    msg = f'Blood not available at {location}.' if location else 'Blood not available at the selected location.'
    # If location filter found nothing matching, use all stocks of that group as alternatives
    if not alternatives:
        alternatives = [s.to_dict() for s in stocks]
    return _ok({
        'available': False,
        'message': msg,
        'results': [],
        'alternatives': alternatives,
    })


@api_bp.route('/blood/stock')
@login_required(['patient', 'receptionist', 'admin', 'doctor'])
def blood_stock():
    stocks = BloodStock.query.all()
    return _ok([s.to_dict() for s in stocks])


@api_bp.route('/blood/requests/<int:rid>/status', methods=['POST'])
@csrf.exempt
@login_required(['admin', 'receptionist'])
def update_blood_request(rid):
    req = BloodRequest.query.get(rid)
    if not req:
        return _err('Blood request not found.', 404)
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    if status not in ('Pending', 'Available', 'Partially Available', 'Not Available', 'Completed'):
        return _err('Invalid status.')
    req.status = status
    db.session.commit()
    return _ok(req.to_dict(), 'Blood request status updated.')


@api_bp.route('/dashboard/stats')
@login_required(['patient', 'doctor', 'receptionist', 'admin'])
def dashboard_stats():
    role = session.get('role')
    uid = session.get('user_id')
    if role == 'patient':
        return _ok({
            'upcoming': Appointment.query.filter(
                Appointment.patient_id == uid,
                Appointment.status.in_(['Pending', 'Confirmed'])
            ).count(),
            'tokens': Token.query.filter(
                Token.patient_id == uid,
                Token.status.in_(['Waiting', 'In Consultation'])
            ).count(),
            'prescriptions': Prescription.query.filter_by(patient_id=uid).count(),
        })
    if role == 'doctor':
        return _ok({
            'today': Appointment.query.filter_by(doctor_id=uid, appointment_date=date.today()).count(),
            'waiting': Token.query.filter_by(doctor_id=uid, status='Waiting').count(),
            'prescriptions': Prescription.query.filter_by(doctor_id=uid).count(),
        })
    return _ok({
        'patients': Patient.query.count(),
        'appointments': Appointment.query.filter_by(appointment_date=date.today()).count(),
        'waiting': Token.query.filter_by(status='Waiting').count(),
    })
