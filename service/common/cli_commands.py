# service/common/cli_commands.py
from flask import current_app as app
import click

# expose db so tests can patch service.common.cli_commands.db
from service.models import db  # noqa: F401


@app.cli.command("db-create")
def db_create() -> None:
    """Create all database tables."""
    with app.app_context():
        db.create_all()
    click.echo("Database tables created")