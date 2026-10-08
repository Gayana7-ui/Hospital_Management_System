import os
from pathlib import Path
from app import create_app
from app.extensions import db

app = create_app()

# Ensure instance folder exists for SQLite
Path(app.instance_path).mkdir(parents=True, exist_ok=True)


@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with tables and demo data."""
    from init_db import initialize_database
    initialize_database(app)
    print('Database initialized successfully.')


if __name__ == '__main__':
    # Auto-create tables on first run if DB missing
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri.replace('sqlite:///', '')
            if not os.path.isabs(db_path):
                db_path = os.path.join(os.path.dirname(__file__), db_path)
            if not os.path.exists(db_path):
                from init_db import initialize_database
                initialize_database(app)
                print('First-run: database created with demo data.')
    app.run(host='127.0.0.1', port=5000, debug=True)
