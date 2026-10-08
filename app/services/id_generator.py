from app.models import (
    Patient, Doctor, Receptionist, Admin, Hospital, Appointment,
    Token, Prescription, Billing, Transaction, BloodBank, BloodRequest,
    Donor, BloodTransaction, BloodReport
)


def _next_seq(model, field_name, prefix):
    last = model.query.order_by(model.id.desc()).first()
    if not last:
        return f"{prefix}001"
    current = getattr(last, field_name)
    try:
        num = int(current.replace(prefix, ''))
    except (ValueError, AttributeError):
        num = model.query.count()
    return f"{prefix}{num + 1:03d}"


def next_patient_id():
    return _next_seq(Patient, 'patient_id', 'PAT')


def next_doctor_id():
    return _next_seq(Doctor, 'doctor_id', 'DOC')


def next_receptionist_id():
    return _next_seq(Receptionist, 'receptionist_id', 'REC')


def next_admin_id():
    return _next_seq(Admin, 'admin_id', 'ADMIN')


def next_hospital_id():
    return _next_seq(Hospital, 'hospital_id', 'HOS')


def next_appointment_id():
    return _next_seq(Appointment, 'appointment_id', 'APT')


def next_token_number():
    last = Token.query.order_by(Token.id.desc()).first()
    if not last:
        return 'A001'
    try:
        num = int(last.token_number[1:])
    except (ValueError, AttributeError):
        num = Token.query.count()
    return f"A{num + 1:03d}"


def next_prescription_id():
    return _next_seq(Prescription, 'prescription_id', 'RX')


def next_bill_id():
    return _next_seq(Billing, 'bill_id', 'BILL')


def next_transaction_id():
    return _next_seq(Transaction, 'transaction_id', 'TXN')


def next_blood_bank_id():
    return _next_seq(BloodBank, 'blood_bank_id', 'BB')


def next_blood_request_id():
    return _next_seq(BloodRequest, 'request_id', 'BR')


def next_donor_id():
    return _next_seq(Donor, 'donor_id', 'DON')


def next_blood_transaction_id():
    return _next_seq(BloodTransaction, 'transaction_id', 'BTX')


def next_blood_report_id():
    return _next_seq(BloodReport, 'report_id', 'BRP')
