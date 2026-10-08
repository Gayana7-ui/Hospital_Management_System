from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Patient(db.Model, TimestampMixin):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    blood_group = db.Column(db.String(5), nullable=False)
    disease = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    insurance_provider = db.Column(db.String(120), nullable=True)
    policy_number = db.Column(db.String(80), nullable=True)
    coverage_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='Active')

    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)
    bills = db.relationship('Billing', backref='patient', lazy=True)
    tokens = db.relationship('Token', backref='patient', lazy=True)
    blood_requests = db.relationship('BloodRequest', backref='patient', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'blood_group': self.blood_group,
            'disease': self.disease,
            'insurance_provider': self.insurance_provider,
            'policy_number': self.policy_number,
            'coverage_amount': self.coverage_amount,
            'status': self.status,
        }


class Doctor(db.Model, TimestampMixin):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=True)
    experience = db.Column(db.Integer, default=0)
    hospital = db.Column(db.String(120), nullable=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    availability = db.Column(db.String(40), default='Available')
    available_from = db.Column(db.String(50), nullable=True)
    available_to = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Active')

    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.doctor_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'specialization': self.specialization,
            'qualification': self.qualification,
            'experience': self.experience,
            'hospital': self.hospital,
            'availability': self.availability,
            'available_from': self.available_from,
            'available_to': self.available_to,
            'status': self.status,
        }


class Receptionist(db.Model, TimestampMixin):
    __tablename__ = 'receptionists'

    id = db.Column(db.Integer, primary_key=True)
    receptionist_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    hospital = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='Active')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'receptionist_id': self.receptionist_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'hospital': self.hospital,
            'status': self.status,
        }


class Admin(db.Model, TimestampMixin):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='Active')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'name': self.name,
            'email': self.email,
            'status': self.status,
        }


class Hospital(db.Model, TimestampMixin):
    __tablename__ = 'hospitals'

    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(80), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    emergency_available = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    services = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')

    blood_banks = db.relationship('BloodBank', backref='hospital', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'hospital_id': self.hospital_id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'phone': self.phone,
            'emergency_available': self.emergency_available,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'services': self.services,
            'status': self.status,
        }


class Appointment(db.Model, TimestampMixin):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    department = db.Column(db.String(120), nullable=True)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')

    token = db.relationship('Token', backref='appointment', uselist=False, lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor.doctor_id if self.doctor else None,
            'doctor_name': self.doctor.name if self.doctor else None,
            'department': self.department,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time,
            'reason': self.reason,
            'status': self.status,
        }


class Token(db.Model, TimestampMixin):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    token_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    appointment_time = db.Column(db.String(20), nullable=True)
    queue_position = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='Waiting')
    entry_fee = db.Column(db.Float, default=0.0)

    doctor = db.relationship('Doctor', backref='tokens')

    def to_dict(self):
        return {
            'id': self.id,
            'token_number': self.token_number,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor.doctor_id if self.doctor else None,
            'doctor_name': self.doctor.name if self.doctor else None,
            'appointment_time': self.appointment_time,
            'queue_position': self.queue_position,
            'status': self.status,
            'entry_fee': self.entry_fee,
        }


class Medicine(db.Model, TimestampMixin):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(120), nullable=False, index=True)
    medicine_type = db.Column(db.String(60), nullable=True)
    strength = db.Column(db.String(60), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')

    def to_dict(self):
        return {
            'id': self.id,
            'medicine_name': self.medicine_name,
            'medicine_type': self.medicine_type,
            'strength': self.strength,
            'description': self.description,
            'status': self.status,
        }


class Prescription(db.Model, TimestampMixin):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    prescription_date = db.Column(db.Date, default=date.today, nullable=False)
    diagnosis = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    medicines = db.relationship('PrescriptionMedicine', backref='prescription', lazy=True, cascade='all, delete-orphan')
    questions = db.relationship('MedicineQuestion', backref='prescription', lazy=True)

    def to_dict(self, include_medicines=True):
        data = {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor.doctor_id if self.doctor else None,
            'doctor_name': self.doctor.name if self.doctor else None,
            'prescription_date': self.prescription_date.isoformat() if self.prescription_date else None,
            'diagnosis': self.diagnosis,
            'notes': self.notes,
        }
        if include_medicines:
            data['medicines'] = [m.to_dict() for m in self.medicines]
        return data


class PrescriptionMedicine(db.Model):
    __tablename__ = 'prescription_medicines'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=True)
    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(80), nullable=True)
    medicine_intake = db.Column(db.String(20), nullable=False, default='1-0-1')
    number_of_days = db.Column(db.Integer, default=1)
    quantity = db.Column(db.Integer, default=1)
    instructions = db.Column(db.Text, nullable=True)

    medicine = db.relationship('Medicine')

    def to_dict(self):
        parts = (self.medicine_intake or '0-0-0').split('-')
        morning = parts[0] if len(parts) > 0 else '0'
        afternoon = parts[1] if len(parts) > 1 else '0'
        night = parts[2] if len(parts) > 2 else '0'
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine_name,
            'dosage': self.dosage,
            'medicine_intake': self.medicine_intake,
            'morning': morning,
            'afternoon': afternoon,
            'night': night,
            'number_of_days': self.number_of_days,
            'quantity': self.quantity,
            'instructions': self.instructions,
        }


class MedicineQuestion(db.Model, TimestampMixin):
    __tablename__ = 'medicine_questions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=True)
    medicine_name = db.Column(db.String(120), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_date = db.Column(db.DateTime, default=datetime.utcnow)
    doctor_answer = db.Column(db.Text, nullable=True)
    answer_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Pending')

    patient = db.relationship('Patient', backref='medicine_questions')
    doctor = db.relationship('Doctor', backref='medicine_questions')

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient.name if self.patient else None,
            'doctor_id': self.doctor.doctor_id if self.doctor else None,
            'prescription_id': self.prescription.prescription_id if self.prescription else None,
            'medicine_name': self.medicine_name,
            'question': self.question,
            'question_date': self.question_date.isoformat() if self.question_date else None,
            'doctor_answer': self.doctor_answer,
            'answer_date': self.answer_date.isoformat() if self.answer_date else None,
            'status': self.status,
        }


class Billing(db.Model, TimestampMixin):
    __tablename__ = 'billings'

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    hospital = db.Column(db.String(120), nullable=True)
    consultation_fee = db.Column(db.Float, default=0.0)
    entry_fee = db.Column(db.Float, default=0.0)
    medicine_charges = db.Column(db.Float, default=0.0)
    other_charges = db.Column(db.Float, default=0.0)
    insurance = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)
    balance = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(30), default='Pending')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    claim_amount = db.Column(db.Float, default=0.0)
    claim_status = db.Column(db.String(30), default='None')

    def to_dict(self):
        return {
            'id': self.id,
            'bill_id': self.bill_id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient.name if self.patient else None,
            'hospital': self.hospital,
            'consultation_fee': self.consultation_fee,
            'entry_fee': self.entry_fee,
            'medicine_charges': self.medicine_charges,
            'other_charges': self.other_charges,
            'insurance': self.insurance,
            'total_amount': self.total_amount,
            'amount_paid': self.amount_paid,
            'balance': self.balance,
            'payment_status': self.payment_status,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'claim_amount': self.claim_amount,
            'claim_status': self.claim_status,
        }


class Transaction(db.Model, TimestampMixin):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    bill_id = db.Column(db.Integer, db.ForeignKey('billings.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(40), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Completed')
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    bill = db.relationship('Billing', backref='transactions')
    patient = db.relationship('Patient', backref='transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'bill_id': self.bill.bill_id if self.bill else None,
            'patient_id': self.patient.patient_id if self.patient else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'description': self.description,
            'status': self.status,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
        }


class BloodBank(db.Model, TimestampMixin):
    __tablename__ = 'blood_banks'

    id = db.Column(db.Integer, primary_key=True)
    blood_bank_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.id'), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='Active')

    stocks = db.relationship('BloodStock', backref='blood_bank', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'blood_bank_id': self.blood_bank_id,
            'name': self.name,
            'hospital': self.hospital.name if self.hospital else None,
            'hospital_id': self.hospital_id,
            'location': self.location,
            'phone': self.phone,
            'status': self.status,
        }


class BloodStock(db.Model, TimestampMixin):
    __tablename__ = 'blood_stocks'

    id = db.Column(db.Integer, primary_key=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('blood_banks.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    available_quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default='Units')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.String(20), default='Available')

    def to_dict(self):
        return {
            'id': self.id,
            'blood_bank_id': self.blood_bank.blood_bank_id if self.blood_bank else None,
            'blood_bank_name': self.blood_bank.name if self.blood_bank else None,
            'location': self.blood_bank.location if self.blood_bank else None,
            'phone': self.blood_bank.phone if self.blood_bank else None,
            'hospital': self.blood_bank.hospital.name if self.blood_bank and self.blood_bank.hospital else None,
            'blood_group': self.blood_group,
            'available_quantity': self.available_quantity,
            'unit': self.unit,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'status': self.status,
        }


class BloodRequest(db.Model, TimestampMixin):
    __tablename__ = 'blood_requests'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    patient_name = db.Column(db.String(120), nullable=False)
    hospital = db.Column(db.String(120), nullable=True)
    blood_group_required = db.Column(db.String(5), nullable=False)
    quantity_required = db.Column(db.Float, nullable=False)
    required_date = db.Column(db.Date, nullable=True)
    disease_reason = db.Column(db.Text, nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(150), nullable=True)
    blood_group_taken = db.Column(db.String(5), nullable=True)
    status = db.Column(db.String(30), default='Pending')

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'patient_name': self.patient_name,
            'hospital': self.hospital,
            'blood_group_required': self.blood_group_required,
            'quantity_required': self.quantity_required,
            'required_date': self.required_date.isoformat() if self.required_date else None,
            'disease_reason': self.disease_reason,
            'contact_number': self.contact_number,
            'location': self.location,
            'blood_group_taken': self.blood_group_taken,
            'status': self.status,
        }


class Donor(db.Model, TimestampMixin):
    __tablename__ = 'donors'

    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(5), nullable=False)
    address = db.Column(db.Text, nullable=True)
    last_donation_date = db.Column(db.Date, nullable=True)
    eligibility_status = db.Column(db.String(30), default='Eligible')

    def to_dict(self):
        return {
            'id': self.id,
            'donor_id': self.donor_id,
            'name': self.name,
            'age': self.age,
            'phone': self.phone,
            'blood_group': self.blood_group,
            'address': self.address,
            'last_donation_date': self.last_donation_date.isoformat() if self.last_donation_date else None,
            'eligibility_status': self.eligibility_status,
        }


class BloodTransaction(db.Model, TimestampMixin):
    __tablename__ = 'blood_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('blood_banks.id'), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donors.id'), nullable=True)
    blood_group = db.Column(db.String(5), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(30), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Completed')

    blood_bank = db.relationship('BloodBank', backref='transactions')
    patient = db.relationship('Patient', backref='blood_transactions')
    donor = db.relationship('Donor', backref='blood_transactions')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'blood_bank': self.blood_bank.name if self.blood_bank else None,
            'patient_id': self.patient.patient_id if self.patient else None,
            'donor_id': self.donor.donor_id if self.donor else None,
            'blood_group': self.blood_group,
            'quantity': self.quantity,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'status': self.status,
        }


class BloodReport(db.Model, TimestampMixin):
    __tablename__ = 'blood_reports'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    disease = db.Column(db.String(255), nullable=True)
    quantity = db.Column(db.Float, default=0.0)
    hospital = db.Column(db.String(120), nullable=True)
    blood_bank = db.Column(db.String(120), nullable=True)
    transaction_id = db.Column(db.String(20), nullable=True)
    report_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.String(30), default='Completed')

    patient = db.relationship('Patient', backref='blood_reports')

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'patient_id': self.patient.patient_id if self.patient else None,
            'blood_group': self.blood_group,
            'disease': self.disease,
            'quantity': self.quantity,
            'hospital': self.hospital,
            'blood_bank': self.blood_bank,
            'transaction_id': self.transaction_id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'status': self.status,
        }
