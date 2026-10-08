from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request


def login_required(role=None):
    """Require login. Optionally restrict to a specific role string or list."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session or 'role' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'success': False, 'message': 'Session expired. Please login again.'}), 401
                flash('Session expired. Please login again.', 'error')
                return redirect(url_for('main.index'))
            if role:
                allowed = role if isinstance(role, (list, tuple)) else [role]
                if session.get('role') not in allowed:
                    if request.path.startswith('/api/'):
                        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403
                    flash('Unauthorized access.', 'error')
                    return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


def current_user_info():
    return {
        'user_id': session.get('user_id'),
        'role': session.get('role'),
        'display_id': session.get('display_id'),
        'name': session.get('name'),
    }


def haversine_km(lat1, lon1, lat2, lon2):
    """Approximate distance in km between two lat/lon points."""
    from math import radians, sin, cos, sqrt, atan2
    if None in (lat1, lon1, lat2, lon2):
        return None
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(r * c, 2)


BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

DISEASE_SPECIALIZATION_MAP = {
    'fever': 'General Medicine',
    'cold': 'General Medicine',
    'cough': 'General Medicine',
    'flu': 'General Medicine',
    'diabetes': 'Endocrinology',
    'thyroid': 'Endocrinology',
    'heart': 'Cardiology',
    'chest pain': 'Cardiology',
    'hypertension': 'Cardiology',
    'blood pressure': 'Cardiology',
    'skin': 'Dermatology',
    'rash': 'Dermatology',
    'allergy': 'Dermatology',
    'bone': 'Orthopedics',
    'fracture': 'Orthopedics',
    'joint': 'Orthopedics',
    'pregnancy': 'Gynecology',
    'gynecology': 'Gynecology',
    'eye': 'Ophthalmology',
    'vision': 'Ophthalmology',
    'child': 'Pediatrics',
    'pediatric': 'Pediatrics',
    'stomach': 'Gastroenterology',
    'gastric': 'Gastroenterology',
    'kidney': 'Nephrology',
    'urine': 'Nephrology',
    'mental': 'Psychiatry',
    'anxiety': 'Psychiatry',
    'depression': 'Psychiatry',
    'ear': 'ENT',
    'nose': 'ENT',
    'throat': 'ENT',
    'neuro': 'Neurology',
    'migraine': 'Neurology',
    'headache': 'Neurology',
}


def specialization_for_disease(disease):
    if not disease:
        return None
    text = disease.lower()
    for keyword, spec in DISEASE_SPECIALIZATION_MAP.items():
        if keyword in text:
            return spec
    return 'General Medicine'
