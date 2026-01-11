import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Configure structured logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "cirujano.log")

    # Root logger
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Console handler with JSON formatter
    console_handler = logging.StreamHandler()
    json_formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    console_handler.setFormatter(json_formatter)
    root.addHandler(console_handler)

    # Rotating file handler (structured logs as JSON)
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(json_formatter)
    root.addHandler(file_handler)

    # Create an 'audit' logger for audit events
    audit_logger = logging.getLogger("audit")
    audit_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    audit_logger.propagate = True

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    root.info("Logging configured (structured JSON)")
