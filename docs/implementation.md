# Pantry Keeper Implementation Documentation

## Overview

Pantry Keeper is a MongoDB backup system designed for Raspberry Pi servers, providing automated weekly backups with retention management, email notifications, and comprehensive logging. The system is built with simplicity and reliability in mind, using Python and standard MongoDB tools.

## System Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   scheduler.py  │    │    backup.py    │    │    utils.py     │
│                 │    │                 │    │                 │
│ - Weekly cron   │───▶│ - Backup logic  │───▶│ - Helper funcs  │
│ - Service mgmt  │    │ - Error handling│    │ - Email alerts  │
│ - Logging       │    │ - Retention     │    │ - File parsing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  constants.py   │    │ MongoDB Tools   │    │ File System     │
│                 │    │                 │    │                 │
│ - Configuration │    │ - mongodump     │    │ - backups/      │
│ - Settings      │    │ - compression   │    │ - logs/         │
│ - Defaults      │    │ - validation    │    │ - .env          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Scheduler Initialization**: `scheduler.py` starts and sets up weekly backup schedule
2. **Backup Trigger**: Every Sunday at 2:00 AM, backup job is triggered
3. **Backup Execution**: `backup.py` creates MongoDB dump using `mongodump`
4. **Compression**: Raw backup is compressed to `.tar.gz` format
5. **Retention Management**: Old backups (>30 days) are automatically removed
6. **Logging**: All operations are logged to `logs/backup.log` and `logs/scheduler.log`
7. **Error Handling**: Failed backups trigger email notifications

## Design Decisions

### 1. Modular Architecture

**Decision**: Split functionality across multiple files (`backup.py`, `scheduler.py`, `utils.py`, `constants.py`)

**Rationale**:
- **Separation of Concerns**: Each file has a single responsibility
- **Maintainability**: Easier to modify individual components
- **Testability**: Functions can be tested in isolation
- **Reusability**: Utility functions can be shared across modules

### 2. Configuration Management

**Decision**: Centralized configuration in `constants.py` with environment variable overrides

**Rationale**:
- **Single Source of Truth**: All settings in one place
- **Environment Flexibility**: Production vs development configurations
- **Security**: Sensitive data (passwords) in environment variables
- **Easy Deployment**: Configuration changes don't require code changes

### 3. Error Handling Strategy

**Decision**: Multi-layered error handling with email notifications

**Rationale**:
- **Reliability**: System continues running even if individual backups fail
- **Visibility**: Administrators are immediately notified of failures
- **Debugging**: Comprehensive logging for troubleshooting
- **Graceful Degradation**: Email failures don't stop backup operations

### 4. File Naming Convention

**Decision**: Timestamp-based naming: `jorbites_backup_YYYYMMDD_HHMMSS.tar.gz`

**Rationale**:
- **Chronological Sorting**: Files naturally sort by creation time
- **Uniqueness**: Timestamp ensures no naming conflicts
- **Parseability**: Structured format allows automated date extraction
- **Human Readable**: Easy to identify backup dates manually

## Technical Implementation Details

### Backup Process

```python
def create_backup(self):
    """Create a MongoDB backup using mongodump."""
    backup_name = generate_backup_name()  # jorbites_backup_20250531_134108
    backup_path = self.backup_dir / backup_name

    # 1. Parse MongoDB connection
    mongo_config = parse_mongo_url(self.database_url)

    # 2. Execute mongodump
    cmd = ['mongodump', '--uri', uri, '--out', str(backup_path)]
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    # 3. Compress and cleanup
    shutil.make_archive(str(backup_path), 'gztar', str(backup_path))
    shutil.rmtree(backup_path)
```

### Retention Management

```python
def cleanup_old_backups(self):
    """Remove backups older than retention period."""
    cutoff_date = datetime.now() - timedelta(days=self.retention_days)

    for backup_file in get_backup_files(self.backup_dir):
        backup_date = parse_backup_filename(backup_file.name)
        if backup_date and backup_date < cutoff_date:
            backup_file.unlink()
```

### Email Notifications

```python
def send_error_email(error_message, backup_name=None):
    """Send email notification when backup fails."""
    # SMTP configuration from environment
    # MIMEText message construction
    # Gmail/custom SMTP server support
    # Graceful failure handling
```

## File Structure and Responsibilities

```
pantry_keeper/
├── backup.py           # Main backup orchestration
│   ├── PantryKeeper class
│   ├── create_backup()
│   ├── cleanup_old_backups()
│   └── run_backup_job()
│
├── scheduler.py        # Weekly scheduling
│   ├── schedule library integration
│   ├── systemd service compatibility
│   └── continuous monitoring
│
├── utils.py           # Shared utilities
│   ├── setup_logging()
│   ├── parse_backup_filename()
│   ├── send_error_email()
│   ├── ensure_directory_exists()
│   └── get_email_config_status()
│
├── constants.py       # Configuration
│   ├── Backup settings
│   ├── Logging configuration
│   ├── Email settings
│   └── File naming patterns
│
├── backups/          # Backup storage (auto-created)
├── logs/             # Log files (auto-created)
├── .env              # Environment variables
└── requirements.txt  # Python dependencies
```

## Dependencies and External Tools

### Python Libraries

- **`pymongo`**: MongoDB connection and validation
- **`python-dotenv`**: Environment variable management
- **`schedule`**: Cron-like job scheduling
- **Standard Library**: `subprocess`, `shutil`, `smtplib`, `pathlib`, `datetime`

### System Dependencies

- **`mongodump`**: MongoDB backup utility (mongodb-database-tools package)
- **`tar`**: Archive compression (system utility)
- **`systemd`**: Service management (Linux systems)

### Installation Considerations

**Raspberry Pi ARM64 Support**:
```bash
# Add MongoDB repository for ARM64
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install mongodb-database-tools
```
