from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import (
    Patient, Doctor, Receptionist, Admin, Hospital, Appointment, Token,
    Medicine, Prescription, Billing, Transaction, BloodBank, BloodStock,
    BloodRequest, Donor, BloodReport, BloodTransaction
)
from app.services.id_generator import (
    next_doctor_id, next_receptionist_id, next_hospital_id, next_blood_bank_id,
    next_donor_id, next_blood_transaction_id, next_blood_report_id
)
from app.utils import login_required, BLOOD_GROUPS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _current_admin():
    return Admin.query.get(session['user_id'])


@admin_bp.route('/dashboard')
@login_required('admin')
def dashboard():
    admin = _current_admin()
    stats = {
        'patients': Patient.query.count(),
        'doctors': Doctor.query.count(),
        'receptionists': Receptionist.query.count(),
        'hospitals': Hospital.query.count(),
        'appointments': Appointment.query.count(),
        'medicines': Medicine.query.count(),
        'prescriptions': Prescription.query.count(),
        'blood_requests': BloodRequest.query.filter_by(status='Pending').count(),
        'pending_bills': Billing.query.filter(Billing.payment_status != 'Paid').count(),
    }
    return render_template('admin/dashboard.html', admin=admin, stats=stats)


@admin_bp.route('/patients')
@login_required('admin')
def patients():
    items = Patient.query.order_by(Patient.id.desc()).all()
    return render_template('admin/patients.html', admin=_current_admin(), patients=items)


@admin_bp.route('/patients/delete/<int:pid>', methods=['POST'])
@login_required('admin')
def delete_patient(pid):
    p = Patient.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('Patient deleted.', 'success')
    return redirect(url_for('admin.patients'))


@admin_bp.route('/doctors', methods=['GET', 'POST'])
@login_required('admin')
def doctors():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            d = Doctor(
                doctor_id=next_doctor_id(),
                name=(request.form.get('name') or '').strip(),
                email=(request.form.get('email') or '').strip(),
                phone=(request.form.get('phone') or '').strip(),
                specialization=(request.form.get('specialization') or '').strip(),
                qualification=(request.form.get('qualification') or '').strip(),
                experience=int(request.form.get('experience') or 0),
                hospital=(request.form.get('hospital') or '').strip(),
                availability='Available',
            )
            d.set_password(request.form.get('password') or 'Doctor@123')
            db.session.add(d)
            db.session.commit()
            flash(f'Doctor {d.doctor_id} created.', 'success')
        elif action == 'update':
            d = Doctor.query.get(request.form.get('id'))
            if d:
                d.name = request.form.get('name') or d.name
                d.email = request.form.get('email')
                d.phone = request.form.get('phone')
                d.specialization = request.form.get('specialization') or d.specialization
                d.qualification = request.form.get('qualification')
                d.experience = int(request.form.get('experience') or d.experience)
                d.hospital = request.form.get('hospital')
                d.availability = request.form.get('availability') or d.availability
                d.status = request.form.get('status') or d.status
                db.session.commit()
                flash('Doctor updated.', 'success')
        elif action == 'delete':
            d = Doctor.query.get(request.form.get('id'))
            if d:
                db.session.delete(d)
                db.session.commit()
                flash('Doctor deleted.', 'success')
        return redirect(url_for('admin.doctors'))
    items = Doctor.query.order_by(Doctor.id.desc()).all()
    return render_template('admin/doctors.html', admin=_current_admin(), doctors=items)


@admin_bp.route('/receptionists', methods=['GET', 'POST'])
@login_required('admin')
def receptionists():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            r = Receptionist(
                receptionist_id=next_receptionist_id(),
                name=(request.form.get('name') or '').strip(),
                email=(request.form.get('email') or '').strip(),
                phone=(request.form.get('phone') or '').strip(),
                hospital=(request.form.get('hospital') or '').strip(),
            )
            r.set_password(request.form.get('password') or 'Reception@123')
            db.session.add(r)
            db.session.commit()
            flash(f'Receptionist {r.receptionist_id} created.', 'success')
        elif action == 'delete':
            r = Receptionist.query.get(request.form.get('id'))
            if r:
                db.session.delete(r)
                db.session.commit()
                flash('Receptionist deleted.', 'success')
        return redirect(url_for('admin.receptionists'))
    items = Receptionist.query.order_by(Receptionist.id.desc()).all()
    return render_template('admin/receptionists.html', admin=_current_admin(), receptionists=items)


@admin_bp.route('/hospitals', methods=['GET', 'POST'])
@login_required('admin')
def hospitals():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            h = Hospital(
                hospital_id=next_hospital_id(),
                name=(request.form.get('name') or '').strip(),
                address=(request.form.get('address') or '').strip(),
                city=(request.form.get('city') or '').strip(),
                phone=(request.form.get('phone') or '').strip(),
                emergency_available=request.form.get('emergency_available') == '1',
                latitude=float(request.form.get('latitude') or 0) or None,
                longitude=float(request.form.get('longitude') or 0) or None,
                services=(request.form.get('services') or '').strip(),
            )
            db.session.add(h)
            db.session.commit()
            flash(f'Hospital {h.hospital_id} created.', 'success')
        elif action == 'update':
            h = Hospital.query.get(request.form.get('id'))
            if h:
                h.name = request.form.get('name') or h.name
                h.address = request.form.get('address')
                h.city = request.form.get('city')
                h.phone = request.form.get('phone')
                h.emergency_available = request.form.get('emergency_available') == '1'
                h.status = request.form.get('status') or h.status
                try:
                    h.latitude = float(request.form.get('latitude')) if request.form.get('latitude') else h.latitude
                    h.longitude = float(request.form.get('longitude')) if request.form.get('longitude') else h.longitude
                except ValueError:
                    pass
                h.services = request.form.get('services')
                db.session.commit()
                flash('Hospital updated.', 'success')
        elif action == 'delete':
            h = Hospital.query.get(request.form.get('id'))
            if h:
                db.session.delete(h)
                db.session.commit()
                flash('Hospital deleted.', 'success')
        return redirect(url_for('admin.hospitals'))
    items = Hospital.query.order_by(Hospital.id.desc()).all()
    return render_template('admin/hospitals.html', admin=_current_admin(), hospitals=items)


@admin_bp.route('/appointments')
@login_required('admin')
def appointments():
    items = Appointment.query.order_by(Appointment.id.desc()).all()
    return render_template('admin/appointments.html', admin=_current_admin(), appointments=items)


@admin_bp.route('/tokens')
@login_required('admin')
def tokens():
    items = Token.query.order_by(Token.id.desc()).all()
    return render_template('admin/tokens.html', admin=_current_admin(), tokens=items)


@admin_bp.route('/medicines', methods=['GET', 'POST'])
@login_required('admin')
def medicines():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            m = Medicine(
                medicine_name=(request.form.get('medicine_name') or '').strip(),
                medicine_type=(request.form.get('medicine_type') or '').strip(),
                strength=(request.form.get('strength') or '').strip(),
                description=(request.form.get('description') or '').strip(),
                status='Active',
            )
            db.session.add(m)
            db.session.commit()
            flash('Medicine added.', 'success')
        elif action == 'update':
            m = Medicine.query.get(request.form.get('id'))
            if m:
                m.medicine_name = request.form.get('medicine_name') or m.medicine_name
                m.medicine_type = request.form.get('medicine_type')
                m.strength = request.form.get('strength')
                m.description = request.form.get('description')
                m.status = request.form.get('status') or m.status
                db.session.commit()
                flash('Medicine updated.', 'success')
        elif action == 'delete':
            m = Medicine.query.get(request.form.get('id'))
            if m:
                db.session.delete(m)
                db.session.commit()
                flash('Medicine deleted.', 'success')
        return redirect(url_for('admin.medicines'))
    items = Medicine.query.order_by(Medicine.medicine_name).all()
    return render_template('admin/medicines.html', admin=_current_admin(), medicines=items)


@admin_bp.route('/prescriptions')
@login_required('admin')
def prescriptions():
    items = Prescription.query.order_by(Prescription.id.desc()).all()
    return render_template('admin/prescriptions.html', admin=_current_admin(), prescriptions=items)


@admin_bp.route('/billing')
@login_required('admin')
def billing():
    items = Billing.query.order_by(Billing.id.desc()).all()
    return render_template('admin/billing.html', admin=_current_admin(), bills=items)


@admin_bp.route('/blood-banks', methods=['GET', 'POST'])
@login_required('admin')
def blood_banks():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            bb = BloodBank(
                blood_bank_id=next_blood_bank_id(),
                name=(request.form.get('name') or '').strip(),
                hospital_id=int(request.form.get('hospital_id')) if request.form.get('hospital_id') else None,
                location=(request.form.get('location') or '').strip(),
                phone=(request.form.get('phone') or '').strip(),
            )
            db.session.add(bb)
            db.session.commit()
            flash(f'Blood bank {bb.blood_bank_id} created.', 'success')
        elif action == 'delete':
            bb = BloodBank.query.get(request.form.get('id'))
            if bb:
                db.session.delete(bb)
                db.session.commit()
                flash('Blood bank deleted.', 'success')
        return redirect(url_for('admin.blood_banks'))
    items = BloodBank.query.order_by(BloodBank.id.desc()).all()
    hospitals = Hospital.query.filter_by(status='Active').all()
    return render_template(
        'admin/blood_banks.html',
        admin=_current_admin(), blood_banks=items, hospitals=hospitals
    )


@admin_bp.route('/blood-stock', methods=['GET', 'POST'])
@login_required('admin')
def blood_stock():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            stock = BloodStock(
                blood_bank_id=int(request.form.get('blood_bank_id')),
                blood_group=request.form.get('blood_group'),
                available_quantity=float(request.form.get('available_quantity') or 0),
                unit=request.form.get('unit') or 'Units',
                status='Available' if float(request.form.get('available_quantity') or 0) > 0 else 'Unavailable',
            )
            db.session.add(stock)
            db.session.commit()
            flash('Blood stock added.', 'success')
        elif action == 'update':
            stock = BloodStock.query.get(request.form.get('id'))
            if stock:
                stock.available_quantity = float(request.form.get('available_quantity') or 0)
                stock.status = 'Available' if stock.available_quantity > 0 else 'Unavailable'
                stock.last_updated = datetime.utcnow()
                db.session.commit()
                flash('Blood stock updated.', 'success')
        elif action == 'delete':
            stock = BloodStock.query.get(request.form.get('id'))
            if stock:
                db.session.delete(stock)
                db.session.commit()
                flash('Blood stock deleted.', 'success')
        return redirect(url_for('admin.blood_stock'))
    stocks = BloodStock.query.order_by(BloodStock.id.desc()).all()
    banks = BloodBank.query.filter_by(status='Active').all()
    return render_template(
        'admin/blood_stock.html',
        admin=_current_admin(), stocks=stocks, banks=banks, blood_groups=BLOOD_GROUPS
    )


@admin_bp.route('/blood-requests', methods=['GET', 'POST'])
@login_required('admin')
def blood_requests():
    if request.method == 'POST':
        req = BloodRequest.query.get(request.form.get('id'))
        if req:
            req.status = request.form.get('status') or req.status
            db.session.commit()
            flash('Blood request updated.', 'success')
        return redirect(url_for('admin.blood_requests'))
    items = BloodRequest.query.order_by(BloodRequest.id.desc()).all()
    return render_template('admin/blood_requests.html', admin=_current_admin(), requests=items)


@admin_bp.route('/donors', methods=['GET', 'POST'])
@login_required('admin')
def donors():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            last_date = request.form.get('last_donation_date')
            parsed = None
            if last_date:
                try:
                    parsed = datetime.strptime(last_date, '%Y-%m-%d').date()
                except ValueError:
                    pass
            d = Donor(
                donor_id=next_donor_id(),
                name=(request.form.get('name') or '').strip(),
                age=int(request.form.get('age') or 0),
                phone=(request.form.get('phone') or '').strip(),
                blood_group=request.form.get('blood_group'),
                address=(request.form.get('address') or '').strip(),
                last_donation_date=parsed,
                eligibility_status=request.form.get('eligibility_status') or 'Eligible',
            )
            db.session.add(d)
            db.session.commit()
            flash(f'Donor {d.donor_id} created.', 'success')
        elif action == 'delete':
            d = Donor.query.get(request.form.get('id'))
            if d:
                db.session.delete(d)
                db.session.commit()
                flash('Donor deleted.', 'success')
        return redirect(url_for('admin.donors'))
    items = Donor.query.order_by(Donor.id.desc()).all()
    return render_template('admin/donors.html', admin=_current_admin(), donors=items, blood_groups=BLOOD_GROUPS)


@admin_bp.route('/blood-reports')
@login_required('admin')
def blood_reports():
    items = BloodReport.query.order_by(BloodReport.id.desc()).all()
    return render_template('admin/blood_reports.html', admin=_current_admin(), reports=items)


@admin_bp.route('/transactions', methods=['GET', 'POST'])
@login_required('admin')
def transactions():
    if request.method == 'POST':
        bb_id = request.form.get('blood_bank_id')
        patient = Patient.query.filter_by(patient_id=(request.form.get('patient_id') or '').upper()).first()
        donor = Donor.query.filter_by(donor_id=(request.form.get('donor_id') or '').upper()).first()
        qty = float(request.form.get('quantity') or 0)
        bg = request.form.get('blood_group')
        ttype = request.form.get('transaction_type')
        bt = BloodTransaction(
            transaction_id=next_blood_transaction_id(),
            blood_bank_id=int(bb_id) if bb_id else None,
            patient_id=patient.id if patient else None,
            donor_id=donor.id if donor else None,
            blood_group=bg,
            quantity=qty,
            transaction_type=ttype,
            status='Completed',
        )
        db.session.add(bt)
        # Update stock for Issue/Donation
        if bb_id and bg:
            stock = BloodStock.query.filter_by(blood_bank_id=int(bb_id), blood_group=bg).first()
            if stock:
                if ttype == 'Issue':
                    stock.available_quantity = max(0, stock.available_quantity - qty)
                elif ttype == 'Donation':
                    stock.available_quantity += qty
                elif ttype == 'Return':
                    stock.available_quantity += qty
                stock.status = 'Available' if stock.available_quantity > 0 else 'Unavailable'
                stock.last_updated = datetime.utcnow()
        if patient and ttype == 'Issue':
            report = BloodReport(
                report_id=next_blood_report_id(),
                patient_id=patient.id,
                blood_group=bg,
                disease=patient.disease,
                quantity=qty,
                hospital=request.form.get('hospital'),
                blood_bank=BloodBank.query.get(int(bb_id)).name if bb_id else None,
                transaction_id=bt.transaction_id,
                status='Completed',
            )
            db.session.add(report)
        db.session.commit()
        flash(f'Transaction {bt.transaction_id} recorded.', 'success')
        return redirect(url_for('admin.transactions'))
    items = BloodTransaction.query.order_by(BloodTransaction.id.desc()).all()
    banks = BloodBank.query.filter_by(status='Active').all()
    return render_template(
        'admin/transactions.html',
        admin=_current_admin(), transactions=items, banks=banks, blood_groups=BLOOD_GROUPS
    )


@admin_bp.route('/reports')
@login_required('admin')
def reports():
    admin = _current_admin()
    data = {
        'patients': Patient.query.count(),
        'doctors': Doctor.query.count(),
        'appointments': Appointment.query.count(),
        'completed_appts': Appointment.query.filter_by(status='Completed').count(),
        'prescriptions': Prescription.query.count(),
        'bills_pending': Billing.query.filter(Billing.payment_status != 'Paid').count(),
        'blood_stock_total': db.session.query(db.func.sum(BloodStock.available_quantity)).scalar() or 0,
        'donors': Donor.query.count(),
        'blood_requests_pending': BloodRequest.query.filter_by(status='Pending').count(),
    }
    return render_template('admin/reports.html', admin=admin, data=data)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required('admin')
def settings():
    admin = _current_admin()
    if request.method == 'POST':
        admin.name = request.form.get('name') or admin.name
        admin.email = request.form.get('email')
        new_pw = request.form.get('password')
        if new_pw:
            admin.set_password(new_pw)
        db.session.commit()
        session['name'] = admin.name
        flash('Settings updated.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', admin=admin)
