#!/usr/bin/env python3
"""
Pantry Keeper - MongoDB Backup System
Simple backup solution for MongoDB databases with retention management.
"""

import os
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from constants import *
from utils import (
    setup_logging,
    generate_backup_name,
    parse_backup_filename,
    parse_mongo_url,
    ensure_directory_exists,
    get_backup_files,
    send_error_email,
    get_email_config_status
)

# Load environment variables
load_dotenv()

class PantryKeeper:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.backup_dir = ensure_directory_exists(BACKUP_DIR)
        self.retention_days = RETENTION_DAYS
        self.logger = setup_logging(BACKUP_LOG_FILE)
        self._log_email_status()
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

    def _log_email_status(self):
        """Log the current email configuration status."""
        email_status = get_email_config_status()
        if email_status['enabled']:
            if email_status['configured']:
                self.logger.info("Email notifications: ENABLED and CONFIGURED")
            else:
                missing = ', '.join(email_status['missing_vars'])
                self.logger.warning(f"Email notifications: ENABLED but missing variables: {missing}")
        else:
            self.logger.info("Email notifications: DISABLED")

    def create_backup(self):
        """Create a MongoDB backup using mongodump."""
        backup_name = None
        try:
            backup_name = generate_backup_name()
            backup_path = self.backup_dir / backup_name
            self.logger.info(f"Starting backup: {backup_name}")

            mongo_config = parse_mongo_url(self.database_url)
            result = self._run_mongodump(mongo_config['uri'], backup_path)
            if not result:
                return False

            archive_path = self._create_archive(backup_path)
            self.logger.info(f"Backup completed successfully: {archive_path}")
            return True

        except Exception as e:
            error_msg = f"Backup failed with error: {str(e)}"
            self.logger.error(error_msg)
            send_error_email(str(e), backup_name)
            return False

    def _run_mongodump(self, uri, backup_path):
        """Execute mongodump command."""
        try:
            cmd = ['mongodump', '--uri', uri, '--out', str(backup_path)]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"mongodump failed: {e.stderr}"
            self.logger.error(error_msg)
            send_error_email(error_msg, backup_path.name if backup_path else None)
            return False

    def _create_archive(self, backup_path):
        """Create compressed archive and remove uncompressed directory."""
        archive_path = f"{backup_path}.tar.gz"
        shutil.make_archive(str(backup_path), 'gztar', str(backup_path))
        shutil.rmtree(backup_path)
        return archive_path

    def cleanup_old_backups(self):
        """Remove backups older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            removed_count = 0

            backup_files = get_backup_files(self.backup_dir)

            for backup_file in backup_files:
                backup_date = parse_backup_filename(backup_file.name)

                if backup_date is None:
                    self.logger.warning(f"Could not parse date from backup file: {backup_file.name}")
                    continue

                if backup_date < cutoff_date:
                    backup_file.unlink()
                    removed_count += 1
                    self.logger.info(f"Removed old backup: {backup_file.name}")

            self._log_cleanup_result(removed_count)

        except Exception as e:
            self.logger.error(f"Cleanup failed: {str(e)}")

    def _log_cleanup_result(self, removed_count):
        """Log the result of the cleanup operation."""
        if removed_count > 0:
            self.logger.info(f"Cleanup completed: {removed_count} old backups removed")
        else:
            self.logger.info("No old backups to remove")

    def run_backup_job(self):
        """Run the complete backup job with cleanup."""
        self.logger.info("=== Starting Pantry Keeper Backup Job ===")

        if self.create_backup():
            self.cleanup_old_backups()
            self.logger.info("=== Backup Job Completed Successfully ===")
        else:
            self.logger.error("=== Backup Job Failed ===")


def main():
    """Main entry point for the backup script."""
    try:
        keeper = PantryKeeper()
        keeper.run_backup_job()
    except Exception as e:
        error_msg = f"Script failed: {str(e)}"
        print(error_msg)
        send_error_email(str(e))
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
