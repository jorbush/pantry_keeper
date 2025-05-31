#!/usr/bin/env python3
"""
Pantry Keeper Scheduler - Runs weekly backups
"""

import schedule
import time
from backup import PantryKeeper
from constants import *
from utils import setup_logging

logger = setup_logging(SCHEDULER_LOG_FILE)

def run_weekly_backup():
    """Run the weekly backup job."""
    try:
        keeper = PantryKeeper()
        keeper.run_backup_job()
    except Exception as e:
        logger.error(f"Scheduled backup failed: {str(e)}")

def main():
    """Main scheduler loop."""
    logger.info("Pantry Keeper Scheduler started")

    # Schedule weekly backup
    getattr(schedule.every(), BACKUP_DAY).at(BACKUP_TIME).do(run_weekly_backup)

    logger.info(f"Scheduled weekly backup for {BACKUP_DAY.title()}s at {BACKUP_TIME}")

    while True:
        schedule.run_pending()
        time.sleep(SCHEDULER_CHECK_INTERVAL)

if __name__ == '__main__':
    main()
