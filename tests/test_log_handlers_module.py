# tests/test_log_handlers_module.py
from flask import Flask
from service.common.log_handlers import init_logging

def test_init_logging_attaches_handlers():
    app = Flask(__name__)
    # Use a common production logger name like gunicorn.error
    init_logging(app, "gunicorn.error")

    # After init_logging, app.logger should have at least one handler
    assert hasattr(app.logger, "handlers")
    assert len(app.logger.handlers) >= 1
