# API Reference

This document provides detailed information about all classes, functions, and their parameters in the Pantry Keeper system.

## backup.py

### PantryKeeper Class

Main class that orchestrates MongoDB backup operations.

#### `__init__(self)`

Initialize the PantryKeeper instance.

**Raises:**
- `ValueError`: If `DATABASE_URL` environment variable is not set

**Attributes:**
- `database_url` (str): MongoDB connection string from environment
- `backup_dir` (Path): Directory for storing backups
- `retention_days` (int): Number of days to keep backups
- `logger` (Logger): Configured logger instance

#### `create_backup(self) -> bool`

Create a MongoDB backup using mongodump.

**Returns:**
- `bool`: True if backup successful, False otherwise

**Process:**
1. Generate timestamped backup name
2. Parse MongoDB connection details
3. Execute mongodump command
4. Compress backup to .tar.gz format
5. Clean up temporary files

**Error Handling:**
- Logs all errors
- Sends email notification on failure
- Returns False on any error

#### `cleanup_old_backups(self)`

Remove backups older than the retention period.

**Process:**
1. Calculate cutoff date based on retention period
2. Scan backup directory for old files
3. Parse timestamps from filenames
4. Remove files older than cutoff date
5. Log removal operations

#### `run_backup_job(self)`

Execute complete backup job including cleanup.

**Process:**
1. Log job start
2. Create new backup
3. Clean up old backups (if backup successful)
4. Log job completion status

#### `_run_mongodump(self, uri: str, backup_path: Path) -> bool`

Execute mongodump command with error handling.

**Parameters:**
- `uri` (str): MongoDB connection URI
- `backup_path` (Path): Directory path for backup output

**Returns:**
- `bool`: True if mongodump successful, False otherwise

#### `_create_archive(self, backup_path: Path) -> str`

Create compressed archive and remove uncompressed directory.

**Parameters:**
- `backup_path` (Path): Path to backup directory

**Returns:**
- `str`: Path to created archive file

#### `_log_email_status(self)`

Log current email configuration status at startup.

#### `_log_cleanup_result(self, removed_count: int)`

Log the result of cleanup operation.

**Parameters:**
- `removed_count` (int): Number of files removed

### Functions

#### `main() -> int`

Main entry point for the backup script.

**Returns:**
- `int`: Exit code (0 for success, 1 for failure)

## scheduler.py

### Functions

#### `main()`

Main scheduler function that runs continuously.

**Process:**
1. Setup logging
2. Schedule weekly backup job
3. Run continuous loop checking for scheduled tasks
4. Handle interruption signals gracefully

**Schedule:**
- Day: Sunday (configurable via `BACKUP_DAY`)
- Time: 02:00 (configurable via `BACKUP_TIME`)
- Check interval: 60 seconds (configurable via `SCHEDULER_CHECK_INTERVAL`)

## utils.py

### Logging Functions

#### `setup_logging(log_file: str) -> logging.Logger`

Setup logging configuration with file and console output.

**Parameters:**
- `log_file` (str): Path to log file

**Returns:**
- `logging.Logger`: Configured logger instance

**Features:**
- Creates logs directory if it doesn't exist
- Dual output: file and console
- Standardized format with timestamps

### File Management Functions

#### `generate_backup_name() -> str`

Generate a backup filename with current timestamp.

**Returns:**
- `str`: Backup name in format `{BACKUP_PREFIX}_{YYYYMMDD}_{HHMMSS}`

**Example:**
```python
# Returns: "jorbites_backup_20250531_134108"
backup_name = generate_backup_name()
```

#### `parse_backup_filename(filename: str) -> datetime | None`

Parse backup filename to extract timestamp.

**Parameters:**
- `filename` (str): Backup filename (e.g., 'jorbites_backup_20250531_134108.tar.gz')

**Returns:**
- `datetime | None`: Parsed datetime object, or None if parsing fails

**Example:**
```python
# Returns: datetime(2025, 5, 31, 13, 41, 8)
dt = parse_backup_filename("jorbites_backup_20250531_134108.tar.gz")
```

#### `ensure_directory_exists(directory_path: Path | str) -> Path`

Ensure a directory exists, create it if it doesn't.

**Parameters:**
- `directory_path` (Path | str): Path to the directory

**Returns:**
- `Path`: Path object of the directory

#### `get_backup_files(backup_dir: Path) -> list[Path]`

Get list of backup files in the backup directory.

**Parameters:**
- `backup_dir` (Path): Path to backup directory

**Returns:**
- `list[Path]`: List of backup file paths matching the naming pattern

### Database Functions

#### `parse_mongo_url(database_url: str) -> dict`

Parse MongoDB URL to extract connection details.

**Parameters:**
- `database_url` (str): MongoDB connection string

**Returns:**
- `dict`: Connection details with keys:
  - `host` (str): Hostname or IP address
  - `port` (int): Port number
  - `username` (str | None): Username if provided
  - `password` (str | None): Password if provided
  - `database` (str): Database name
  - `uri` (str): Original URI

**Example:**
```python
config = parse_mongo_url("mongodb://user:pass@localhost:27017/mydb")
# Returns: {
#     'host': 'localhost',
#     'port': 27017,
#     'username': 'user',
#     'password': 'pass',
#     'database': 'mydb',
#     'uri': 'mongodb://user:pass@localhost:27017/mydb'
# }
```

### Email Functions

#### `send_error_email(error_message: str, backup_name: str = None)`

Send email notification when backup fails.

**Parameters:**
- `error_message` (str): The error message to include in the email
- `backup_name` (str, optional): Name of the failed backup

**Environment Variables Required:**
- `EMAIL_USER`: Sender email address
- `EMAIL_PASSWORD`: Email password or app password
- `EMAIL_TO`: Recipient email address

**Optional Environment Variables:**
- `SMTP_SERVER`: SMTP server (defaults to Gmail)
- `SMTP_PORT`: SMTP port (defaults to 587)

**Features:**
- Uses STARTTLS for secure transmission
- Includes server hostname and timestamp
- Graceful failure handling
- Skips if email not configured

#### `get_email_config_status() -> dict`

Check if email configuration is properly set up.

**Returns:**
- `dict`: Status information with keys:
  - `enabled` (bool): Whether email notifications are enabled
  - `configured` (bool): Whether all required variables are set
  - `missing_vars` (list[str]): List of missing environment variables

**Example:**
```python
status = get_email_config_status()
# Returns: {
#     'enabled': True,
#     'configured': False,
#     'missing_vars': ['EMAIL_PASSWORD', 'EMAIL_TO']
# }
```

### Utility Functions

#### `format_file_size(size_bytes: int) -> str`

Format file size in human-readable format.

**Parameters:**
- `size_bytes` (int): File size in bytes

**Returns:**
- `str`: Formatted size string (e.g., "1.5 MB", "2.3 GB")

**Example:**
```python
# Returns: "1.5 MB"
size_str = format_file_size(1572864)
```

## constants.py

### Configuration Constants

#### Backup Configuration
- `BACKUP_DIR` (str): Directory for storing backups ('backups')
- `RETENTION_DAYS` (int): Number of days to keep backups (30)
- `DEFAULT_DATABASE_NAME` (str): Default database name ('jorbites')

#### Logging Configuration
- `LOGS_DIR` (str): Directory for log files ('logs')
- `LOG_FORMAT` (str): Log message format string
- `BACKUP_LOG_FILE` (str): Path to backup log file ('logs/backup.log')
- `SCHEDULER_LOG_FILE` (str): Path to scheduler log file ('logs/scheduler.log')

#### Scheduler Configuration
- `BACKUP_DAY` (str): Day of week for backups ('sunday')
- `BACKUP_TIME` (str): Time for backups in 24-hour format ('02:00')
- `SCHEDULER_CHECK_INTERVAL` (int): Seconds between schedule checks (60)

#### File Naming
- `BACKUP_PREFIX` (str): Prefix for backup files ('jorbites_backup')
- `TIMESTAMP_FORMAT` (str): Timestamp format string ('%Y%m%d_%H%M%S')

#### Email Configuration
- `EMAIL_ENABLED` (bool): Whether email notifications are enabled (True)
- `SMTP_SERVER` (str): Default SMTP server ('smtp.gmail.com')
- `SMTP_PORT` (int): Default SMTP port (587)
- `EMAIL_SUBJECT` (str): Subject line for error emails

## Environment Variables

### Required Variables

#### `DATABASE_URL`
MongoDB connection string.

**Examples:**
- Local: `mongodb://localhost:27017/jorbites`
- Authenticated: `mongodb://user:pass@localhost:27017/jorbites`
- Atlas: `mongodb+srv://user:pass@cluster.mongodb.net/jorbites`

### Optional Email Variables

#### `EMAIL_USER`
Email address for sending notifications.

#### `EMAIL_PASSWORD`
Email password or app-specific password.

#### `EMAIL_TO`
Recipient email address for notifications.

#### `SMTP_SERVER`
Custom SMTP server (overrides default Gmail).

#### `SMTP_PORT`
Custom SMTP port (overrides default 587).

## Error Handling

### Exception Types

#### `ValueError`
Raised when required environment variables are missing or invalid.

#### `subprocess.CalledProcessError`
Raised when mongodump command fails.

#### `FileNotFoundError`
Raised when backup files or directories are not found.

#### `smtplib.SMTPException`
Raised when email sending fails.

### Error Recovery

- **Backup Failures**: Logged and reported via email, scheduler continues
- **Email Failures**: Logged but don't stop backup operations
- **File System Errors**: Graceful handling with appropriate logging
- **Network Errors**: Retry logic for transient failures

## Return Codes

### Script Exit Codes

- `0`: Success
- `1`: General failure (configuration, backup, or system error)

### Function Return Values

- **Boolean Functions**: `True` for success, `False` for failure
- **Parsing Functions**: Parsed object or `None` for failure
- **File Operations**: Path object or raise exception
