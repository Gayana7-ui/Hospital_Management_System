"""Initialize database tables and seed demo data (idempotent)."""
from datetime import date, timedelta
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import (
    Patient, Doctor, Receptionist, Admin, Hospital, Appointment, Token,
    Medicine, Prescription, PrescriptionMedicine, Billing, BloodBank,
    BloodStock, Donor, BloodRequest
)


def initialize_database(app=None):
    close_app = False
    if app is None:
        app = create_app()
        close_app = True

    with app.app_context():
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        db.create_all()
        _seed_demo_data()
        db.session.commit()
        print('Tables created and demo data seeded (idempotent).')

    if close_app:
        pass


def _seed_demo_data():
    # Admin
    if not Admin.query.filter_by(admin_id='ADMIN001').first():
        admin = Admin(admin_id='ADMIN001', name='System Admin', email='admin@hospital.local')
        admin.set_password('Admin@123')
        db.session.add(admin)

    # Receptionist
    if not Receptionist.query.filter_by(receptionist_id='REC001').first():
        rec = Receptionist(
            receptionist_id='REC001',
            name='Rita Reception',
            email='reception@hospital.local',
            phone='9876500001',
            hospital='City General Hospital',
        )
        rec.set_password('Reception@123')
        db.session.add(rec)

    # Hospitals
    hospitals_data = [
        ('HOS001', 'City General Hospital', '100 MG Road', 'Bengaluru', '0801234567', True, 12.9716, 77.5946, 'Emergency, ICU, Blood Bank, Cardiology'),
        ('HOS002', 'Hospital A', '22 Lake View', 'Bengaluru', '0802223344', True, 12.9352, 77.6245, 'Emergency, Blood Bank, Orthopedics'),
        ('HOS003', 'Hospital C', '55 Ring Road', 'Mysuru', '0821222333', True, 12.2958, 76.6394, 'Emergency, Pediatrics'),
        ('HOS004', 'Green Valley Medical', '8 Park Avenue', 'Bengaluru', '0809988776', True, 13.0358, 77.5970, 'Emergency, Neurology'),
    ]
    for hid, name, addr, city, phone, emerg, lat, lon, services in hospitals_data:
        if not Hospital.query.filter_by(hospital_id=hid).first():
            db.session.add(Hospital(
                hospital_id=hid, name=name, address=addr, city=city, phone=phone,
                emergency_available=emerg, latitude=lat, longitude=lon, services=services, status='Active'
            ))
    db.session.flush()

    # Doctors
    doctors_data = [
        ('DOC001', 'Dr. Anil Sharma', 'anil@hospital.local', '9876501001', 'General Medicine', 'MBBS, MD', 12, 'City General Hospital', 'Available'),
        ('DOC002', 'Dr. Priya Nair', 'priya@hospital.local', '9876501002', 'Cardiology', 'MBBS, DM', 15, 'City General Hospital', 'Available'),
        ('DOC003', 'Dr. Rahul Mehta', 'rahul@hospital.local', '9876501003', 'Orthopedics', 'MBBS, MS', 10, 'Hospital A', 'Available'),
        ('DOC004', 'Dr. Sneha Reddy', 'sneha@hospital.local', '9876501004', 'Dermatology', 'MBBS, MD', 8, 'City General Hospital', 'On Leave'),
        ('DOC005', 'Dr. Vikram Das', 'vikram@hospital.local', '9876501005', 'Pediatrics', 'MBBS, DCH', 9, 'Hospital C', 'Available'),
        ('DOC006', 'Dr. Meera Iyer', 'meera@hospital.local', '9876501006', 'Neurology', 'MBBS, DM', 14, 'Green Valley Medical', 'Emergency Only'),
    ]
    for did, name, email, phone, spec, qual, exp, hospital, avail in doctors_data:
        if not Doctor.query.filter_by(doctor_id=did).first():
            d = Doctor(
                doctor_id=did, name=name, email=email, phone=phone,
                specialization=spec, qualification=qual, experience=exp,
                hospital=hospital, availability=avail, status='Active',
                available_from='09:00', available_to='17:00',
            )
            d.set_password('Doctor@123')
            db.session.add(d)

    # Patient PAT001
    if not Patient.query.filter_by(patient_id='PAT001').first():
        p = Patient(
            patient_id='PAT001',
            name='John Patient',
            age=32,
            gender='Male',
            phone='9876543210',
            email='patient@example.com',
            address='12 Residency Road, Bengaluru',
            blood_group='O+',
            disease='Fever',
            insurance_provider='HealthPlus',
            policy_number='HP-10021',
            coverage_amount=50000,
        )
        p.set_password('Patient@123')
        db.session.add(p)

    if not Patient.query.filter_by(patient_id='PAT002').first():
        p2 = Patient(
            patient_id='PAT002',
            name='Anita Kumar',
            age=28,
            gender='Female',
            phone='9876543211',
            email='anita@example.com',
            address='45 Indiranagar, Bengaluru',
            blood_group='A+',
            disease='Skin rash',
        )
        p2.set_password('Patient@123')
        db.session.add(p2)

    db.session.flush()

    # Medicines
    medicines = [
        ('Paracetamol', 'Tablet', '500mg', 'Pain and fever relief'),
        ('Amoxicillin', 'Capsule', '500mg', 'Antibiotic'),
        ('Cetirizine', 'Tablet', '10mg', 'Antihistamine'),
        ('Azithromycin', 'Tablet', '500mg', 'Antibiotic'),
        ('Ibuprofen', 'Tablet', '400mg', 'Anti-inflammatory'),
        ('Pantoprazole', 'Tablet', '40mg', 'Acid reducer'),
        ('ORS', 'Powder', '21g', 'Oral rehydration salts'),
        ('Vitamin D3', 'Tablet', '60000 IU', 'Vitamin supplement'),
        ('Calcium', 'Tablet', '500mg', 'Calcium supplement'),
        ('Iron Supplement', 'Tablet', '100mg', 'Iron deficiency'),
    ]
    for name, mtype, strength, desc in medicines:
        if not Medicine.query.filter_by(medicine_name=name).first():
            db.session.add(Medicine(
                medicine_name=name, medicine_type=mtype,
                strength=strength, description=desc, status='Active'
            ))

    # Blood banks
    hos_a = Hospital.query.filter_by(hospital_id='HOS002').first()
    hos_c = Hospital.query.filter_by(hospital_id='HOS003').first()
    hos_city = Hospital.query.filter_by(hospital_id='HOS001').first()

    banks = [
        ('BB001', 'City Blood Bank', hos_city.id if hos_city else None, 'City General Hospital', '0801111222'),
        ('BB002', 'Blood Bank B', hos_a.id if hos_a else None, 'Hospital A', '0803333444'),
        ('BB003', 'Mysuru Blood Center', hos_c.id if hos_c else None, 'Hospital C', '0821555666'),
    ]
    for bid, name, hid, loc, phone in banks:
        if not BloodBank.query.filter_by(blood_bank_id=bid).first():
            db.session.add(BloodBank(
                blood_bank_id=bid, name=name, hospital_id=hid,
                location=loc, phone=phone, status='Active'
            ))
    db.session.flush()

    # Blood stock - intentionally low O+ at Hospital A for alternative demo
    stock_data = [
        ('BB001', 'O+', 15), ('BB001', 'A+', 10), ('BB001', 'B+', 8), ('BB001', 'AB+', 4),
        ('BB001', 'O-', 5), ('BB001', 'A-', 3),
        ('BB002', 'O+', 1), ('BB002', 'A+', 6), ('BB002', 'B+', 4),  # low O+ at Hospital A
        ('BB003', 'O+', 12), ('BB003', 'A+', 7), ('BB003', 'B-', 3), ('BB003', 'AB-', 2),
    ]
    for bank_code, bg, qty in stock_data:
        bank = BloodBank.query.filter_by(blood_bank_id=bank_code).first()
        if not bank:
            continue
        existing = BloodStock.query.filter_by(blood_bank_id=bank.id, blood_group=bg).first()
        if not existing:
            db.session.add(BloodStock(
                blood_bank_id=bank.id,
                blood_group=bg,
                available_quantity=qty,
                unit='Units',
                status='Available' if qty > 0 else 'Unavailable',
            ))

    # Donors
    donors = [
        ('DON001', 'Ravi Donor', 30, '9876502001', 'O+', 'Bengaluru'),
        ('DON002', 'Lakshmi Donor', 26, '9876502002', 'A+', 'Mysuru'),
        ('DON003', 'Arjun Donor', 35, '9876502003', 'B+', 'Bengaluru'),
    ]
    for did, name, age, phone, bg, addr in donors:
        if not Donor.query.filter_by(donor_id=did).first():
            db.session.add(Donor(
                donor_id=did, name=name, age=age, phone=phone,
                blood_group=bg, address=addr,
                last_donation_date=date.today() - timedelta(days=90),
                eligibility_status='Eligible',
            ))

    # Sample appointment + token for PAT001
    patient = Patient.query.filter_by(patient_id='PAT001').first()
    doctor = Doctor.query.filter_by(doctor_id='DOC001').first()
    if patient and doctor and not Appointment.query.filter_by(appointment_id='APT001').first():
        appt = Appointment(
            appointment_id='APT001',
            patient_id=patient.id,
            doctor_id=doctor.id,
            department=doctor.specialization,
            appointment_date=date.today() + timedelta(days=1),
            appointment_time='10:30',
            reason='Fever consultation',
            status='Confirmed',
        )
        db.session.add(appt)
        db.session.flush()
        if not Token.query.filter_by(token_number='A001').first():
            db.session.add(Token(
                token_number='A001',
                patient_id=patient.id,
                doctor_id=doctor.id,
                appointment_id=appt.id,
                appointment_time='10:30',
                queue_position=1,
                status='Waiting',
                entry_fee=50,
            ))

    # Sample bill
    if patient and not Billing.query.filter_by(bill_id='BILL001').first():
        db.session.add(Billing(
            bill_id='BILL001',
            patient_id=patient.id,
            hospital='City General Hospital',
            consultation_fee=300,
            entry_fee=50,
            medicine_charges=120,
            other_charges=0,
            insurance=100,
            total_amount=370,
            amount_paid=0,
            balance=370,
            payment_status='Pending',
            claim_amount=100,
            claim_status='Applied',
        ))

    # Sample blood request
    if patient and not BloodRequest.query.filter_by(request_id='BR001').first():
        db.session.add(BloodRequest(
            request_id='BR001',
            patient_id=patient.id,
            patient_name=patient.name,
            hospital='Hospital A',
            blood_group_required='O+',
            quantity_required=2,
            required_date=date.today() + timedelta(days=2),
            disease_reason='Surgery preparation',
            contact_number=patient.phone,
            location='Hospital A',
            status='Pending',
        ))


if __name__ == '__main__':
    initialize_database()
