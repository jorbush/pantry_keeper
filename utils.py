#!/usr/bin/env python3
"""
Pantry Keeper - Utility Functions
Helper functions for backup operations and file management.
"""

import os
import logging
import smtplib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from constants import *


class _ServiceFilter(logging.Filter):
    """Inject a 'service' field into every log record."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = self.service_name
        return True

def setup_logging(log_file):
    """Setup logging configuration with optional Axiom integration."""
    load_dotenv()
    # Ensure logs directory exists
    ensure_directory_exists(LOGS_DIR)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    service_filter = _ServiceFilter("pantry_keeper")

    # Stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    stdout_handler.addFilter(service_filter)

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    file_handler.addFilter(service_filter)

    handlers = [stdout_handler, file_handler]

    # Optional Axiom handler — only when env vars are present
    axiom_token = os.getenv("AXIOM_TOKEN")
    axiom_dataset = os.getenv("AXIOM_DATASET")
    if axiom_token and axiom_dataset:
        try:
            from axiom import Client
            from axiom.logging import AxiomHandler

            axiom_client = Client(axiom_token)
            axiom_handler = AxiomHandler(axiom_client, axiom_dataset)
            axiom_handler.setLevel(logging.INFO)
            axiom_handler.addFilter(service_filter)
            handlers.append(axiom_handler)
        except Exception as e:
            # Don't crash if axiom-py is unavailable or misconfigured
            print(f"[pantry_keeper] Axiom logging unavailable: {e}")

    for handler in handlers:
        root_logger.addHandler(handler)

    return logging.getLogger(__name__)


def generate_backup_name():
    """Generate a backup filename with current timestamp."""
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    return f"{BACKUP_PREFIX}_{timestamp}"


def parse_backup_filename(filename):
    """
    Parse backup filename to extract timestamp.

    Args:
        filename (str): Backup filename (e.g., 'jorbites_backup_20250531_134108.tar.gz')

    Returns:
        datetime or None: Parsed datetime object, or None if parsing fails
    """
    try:
        # Remove .tar.gz extension completely
        filename_without_ext = filename.replace('.tar.gz', '')
        filename_parts = filename_without_ext.split('_')

        # The timestamp should be the last two parts: date and time
        if len(filename_parts) >= 3:
            date_part = filename_parts[-2]  # 20250531
            time_part = filename_parts[-1]  # 134108
            timestamp_str = f"{date_part}_{time_part}"
            return datetime.strptime(timestamp_str, TIMESTAMP_FORMAT)
        else:
            return None

    except (ValueError, IndexError):
        return None


def parse_mongo_url(database_url):
    """
    Parse MongoDB URL to extract connection details.

    Args:
        database_url (str): MongoDB connection string

    Returns:
        dict: Connection details including host, port, database, etc.
    """
    parsed = urlparse(database_url)

    # Extract database name from path
    db_name = parsed.path.lstrip('/')
    if not db_name:
        db_name = DEFAULT_DATABASE_NAME

    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 27017,
        'username': parsed.username,
        'password': parsed.password,
        'database': db_name,
        'uri': database_url
    }


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create it if it doesn't.

    Args:
        directory_path (Path or str): Path to the directory

    Returns:
        Path: Path object of the directory
    """
    path = Path(directory_path)
    path.mkdir(exist_ok=True)
    return path


def get_backup_files(backup_dir):
    """
    Get list of backup files in the backup directory.

    Args:
        backup_dir (Path): Path to backup directory

    Returns:
        list: List of backup file paths
    """
    return list(backup_dir.glob(f'{BACKUP_PREFIX}_*.tar.gz'))


def send_error_email(error_message, backup_name=None):
    """
    Send email notification when backup fails.

    Args:
        error_message (str): The error message to include in the email
        backup_name (str, optional): Name of the failed backup
    """
    if not EMAIL_ENABLED:
        return

    try:
        # Get email configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', SMTP_SERVER)
        smtp_port = int(os.getenv('SMTP_PORT', SMTP_PORT))
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        email_to = os.getenv('EMAIL_TO')

        # Check if email configuration is complete
        if not all([email_user, email_password, email_to]):
            print("Email configuration incomplete. Skipping email notification.")
            return

        # Create email message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_to
        msg['Subject'] = EMAIL_SUBJECT

        # Email body
        body = f"""
Pantry Keeper Backup Failed

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Backup Name: {backup_name or 'Unknown'}
Error: {error_message}

Please check the backup logs for more details.

Server: {os.uname().nodename}
"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, email_to, text)
        server.quit()

        print(f"Error notification email sent to {email_to}")

    except Exception as e:
        print(f"Failed to send error notification email: {str(e)}")


def get_email_config_status():
    """
    Check if email configuration is properly set up.

    Returns:
        dict: Status of email configuration
    """
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_to = os.getenv('EMAIL_TO')

    return {
        'enabled': EMAIL_ENABLED,
        'configured': all([email_user, email_password, email_to]),
        'missing_vars': [
            var for var, val in [
                ('EMAIL_USER', email_user),
                ('EMAIL_PASSWORD', email_password),
                ('EMAIL_TO', email_to)
            ] if not val
        ]
    }
