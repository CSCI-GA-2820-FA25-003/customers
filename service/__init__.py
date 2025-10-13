import os
from flask import Flask
from service.common.log_handlers import init_logging
from service.models import db

def create_app():
    app = Flask(__name__)

    # Basic config
    app.config["TESTING"] = os.getenv("TESTING", "").lower() in ("1", "true", "yes")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URI",
        "postgresql+psycopg://postgres:postgres@localhost:5432/testdb",
    )

    init_logging(app, "gunicorn.error")
    db.init_app(app)

    # Import routes & CLI only after app/db are ready
    with app.app_context():
        from service import routes                # noqa: F401
        from service.common import cli_commands   # noqa: F401
        db.create_all()

    return app

