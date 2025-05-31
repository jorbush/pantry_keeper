#!/usr/bin/env python3
"""
Pantry Keeper - Configuration Constants
"""

# Backup configuration
BACKUP_DIR = 'backups'
RETENTION_DAYS = 30  # Keep backups for 1 month
DEFAULT_DATABASE_NAME = 'jorbites'

# Logging configuration
LOGS_DIR = 'logs'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
BACKUP_LOG_FILE = 'logs/backup.log'
SCHEDULER_LOG_FILE = 'logs/scheduler.log'

# Scheduler configuration
BACKUP_DAY = 'sunday'  # Day of the week for weekly backups
BACKUP_TIME = '02:00'  # Time for weekly backups (24-hour format)
SCHEDULER_CHECK_INTERVAL = 60  # Check every minute for scheduled tasks

# Backup file naming
BACKUP_PREFIX = 'jorbites_backup'
TIMESTAMP_FORMAT = '%Y%m%d_%H%M%S'

# Email configuration
EMAIL_ENABLED = True  # Set to False to disable email notifications
SMTP_SERVER = 'smtp.gmail.com'  # Default to Gmail, can be overridden via env vars
SMTP_PORT = 587
EMAIL_SUBJECT = 'Pantry Keeper - Backup Failed'
