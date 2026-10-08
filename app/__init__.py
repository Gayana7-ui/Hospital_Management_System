from datetime import timedelta
from flask import Flask
from config import Config
from app.extensions import db, csrf


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
        instance_relative_config=True,
    )
    app.config.from_object(config_class)
    app.permanent_session_lifetime = timedelta(hours=8)

    db.init_app(app)
    csrf.init_app(app)

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.patient import patient_bp
    from app.routes.doctor import doctor_bp
    from app.routes.receptionist import receptionist_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(receptionist_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        from flask import session
        from flask_wtf.csrf import generate_csrf
        return {
            'current_role': session.get('role'),
            'current_name': session.get('name'),
            'current_display_id': session.get('display_id'),
            'csrf_token': generate_csrf,
        }

    return app
