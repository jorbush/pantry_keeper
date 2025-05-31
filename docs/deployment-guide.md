# Deployment Guide

This guide covers the complete deployment process for Pantry Keeper on a Raspberry Pi server, including installation, configuration, and troubleshooting.

## Prerequisites

### Hardware Requirements

- **Raspberry Pi 4** (recommended) or Raspberry Pi 3B+
- **8GB+ SD Card** (Class 10 or better)
- **Stable Internet Connection** for MongoDB Atlas or local network for local MongoDB
- **Sufficient Storage** for backups (estimate 10-30% of database size per backup)

### Software Requirements

- **Raspberry Pi OS** (64-bit recommended)
- **Python 3.10+** (usually pre-installed)
- **MongoDB Tools** (mongodb-database-tools package)
- **Git** (for cloning repository)

## Installation Steps

### 1. System Preparation

Update your Raspberry Pi system:

```bash
sudo apt update && sudo apt upgrade -y
```

Install required system packages:

```bash
sudo apt install -y python3-pip python3-venv git curl wget
```

### 2. MongoDB Tools Installation

The MongoDB tools are required for backup operations. On Raspberry Pi (ARM64), you need to add the MongoDB repository:

```bash
# Import MongoDB GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository for ARM64
echo "deb [ arch=arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt-get update

# Install MongoDB database tools
sudo apt-get install -y mongodb-database-tools
```

Verify installation:

```bash
mongodump --version
# Should output: mongodump version: 100.12.1
```

### 3. Project Setup

Clone the repository:

```bash
cd /opt
sudo git clone https://github.com/jorbush/pantry_keeper.git
sudo chown -R $USER:$USER pantry_keeper
cd pantry_keeper
```

Create and activate virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configuration

Create environment file from template:

```bash
cp env_example.txt .env
```

Edit the `.env` file with your configuration:

```bash
nano .env
```

**Required Configuration:**

```bash
# MongoDB Database URL
DATABASE_URL=mongodb://localhost:27017/jorbites
# OR for MongoDB Atlas:
# DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/jorbites
```

**Optional Email Configuration:**

```bash
# Email notifications (optional but recommended)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=admin@yourdomain.com
```

Set proper file permissions:

```bash
chmod 600 .env
```

### 5. Directory Structure

The system will automatically create required directories, but you can create them manually:

```bash
mkdir -p backups logs
```

## Testing the Installation

### Manual Backup Test

Test the backup functionality:

```bash
source venv/bin/activate
python backup.py
```

Expected output:
```
2025-05-31 13:41:08,123 - INFO - Email notifications: ENABLED and CONFIGURED
2025-05-31 13:41:08,124 - INFO - === Starting Pantry Keeper Backup Job ===
2025-05-31 13:41:08,124 - INFO - Starting backup: jorbites_backup_20250531_134108
2025-05-31 13:41:15,789 - INFO - Backup completed successfully: /opt/pantry_keeper/backups/jorbites_backup_20250531_134108.tar.gz
2025-05-31 13:41:15,790 - INFO - No old backups to remove
2025-05-31 13:41:15,790 - INFO - === Backup Job Completed Successfully ===
```

### Verify Backup Files

Check that backup was created:

```bash
ls -la backups/
# Should show: jorbites_backup_YYYYMMDD_HHMMSS.tar.gz
```

### Test Email Notifications

Test email functionality by temporarily breaking the database URL:

```bash
# Backup current .env
cp .env .env.backup

# Set invalid database URL
echo "DATABASE_URL=mongodb://invalid:27017/test" > .env

# Run backup (should fail and send email)
python backup.py

# Restore original .env
mv .env.backup .env
```

## System Service Setup

### 1. Configure Service File

Edit the systemd service file to match your installation path:

```bash
sudo nano pantry-keeper.service
```

Update paths if necessary:

```ini
[Unit]
Description=Pantry Keeper - MongoDB Backup Scheduler
After=network.target

[Service]
Type=simple
User={your-username}
WorkingDirectory=/opt/pantry_keeper
Environment=PATH=/opt/pantry_keeper/venv/bin
ExecStart=/opt/pantry_keeper/venv/bin/python scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Install and Enable Service

Copy service file:

```bash
sudo cp pantry-keeper.service /etc/systemd/system/
```

Reload systemd and enable service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pantry-keeper
sudo systemctl start pantry-keeper
```

### 3. Verify Service Status

Check service status:

```bash
sudo systemctl status pantry-keeper
```

Expected output:
```
● pantry-keeper.service - Pantry Keeper - MongoDB Backup Scheduler
   Loaded: loaded (/etc/systemd/system/pantry-keeper.service; enabled; vendor preset: enabled)
   Active: active (running) since Fri 2025-05-31 13:45:00 UTC; 5min ago
 Main PID: 1234 (python)
   CGroup: /system.slice/pantry-keeper.service
           └─1234 /opt/pantry_keeper/venv/bin/python scheduler.py
```

View service logs:

```bash
sudo journalctl -u pantry-keeper -f
```

## Monitoring and Maintenance

### Log Files

Monitor system logs:

```bash
# Backup logs
tail -f logs/backup.log

# Scheduler logs
tail -f logs/scheduler.log

# System service logs
sudo journalctl -u pantry-keeper -f
```

### Backup Verification

Regularly check backup files:

```bash
# List recent backups
ls -la backups/ | head -10

# Check backup file sizes
du -h backups/*.tar.gz | tail -5

# Verify backup integrity (extract test)
cd /tmp
tar -tzf /opt/pantry_keeper/backups/latest_backup.tar.gz > /dev/null && echo "Backup integrity OK"
```

### Disk Space Monitoring

Monitor disk usage:

```bash
# Check overall disk usage
df -h

# Check backup directory size
du -sh /opt/pantry_keeper/backups/

# Check logs directory size
du -sh /opt/pantry_keeper/logs/
```

## Troubleshooting

### Common Issues

#### 1. MongoDB Tools Not Found

**Error:** `mongodump: command not found`

**Solution:**
```bash
# Verify installation
which mongodump

# If not found, reinstall
sudo apt-get install --reinstall mongodb-database-tools
```

#### 2. Permission Denied Errors

**Error:** `Permission denied: '/opt/pantry_keeper/backups'`

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/pantry_keeper

# Fix permissions
chmod 755 /opt/pantry_keeper
chmod 755 /opt/pantry_keeper/backups
chmod 755 /opt/pantry_keeper/logs
```

#### 3. Database Connection Failed

**Error:** `Failed to connect to MongoDB`

**Solutions:**
- Verify `DATABASE_URL` in `.env` file
- Test connection manually:
  ```bash
  mongodump --uri="$DATABASE_URL" --dryRun
  ```
- Check network connectivity
- Verify MongoDB server is running

#### 4. Email Sending Failed

**Error:** `Failed to send error notification email`

**Solutions:**
- Verify email configuration in `.env`
- Test SMTP connection:
  ```bash
  python3 -c "
  import smtplib
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login('your-email@gmail.com', 'your-app-password')
  print('SMTP connection successful')
  server.quit()
  "
  ```
- Check firewall settings
- Verify app password (not account password)

#### 5. Service Won't Start

**Error:** Service fails to start or immediately stops

**Solutions:**
```bash
# Check service status
sudo systemctl status pantry-keeper

# View detailed logs
sudo journalctl -u pantry-keeper -n 50

# Check Python path and virtual environment
/opt/pantry_keeper/venv/bin/python --version

# Test scheduler manually
cd /opt/pantry_keeper
source venv/bin/activate
python scheduler.py
```

#### 6. Backup Files Not Being Cleaned Up

**Issue:** Old backup files accumulating

**Solutions:**
- Check retention settings in `constants.py`
- Verify filename parsing:
  ```bash
  python3 -c "
  from utils import parse_backup_filename
  import os
  for f in os.listdir('backups'):
      if f.endswith('.tar.gz'):
          print(f, parse_backup_filename(f))
  "
  ```
- Run cleanup manually:
  ```bash
  python3 -c "
  from backup import PantryKeeper
  keeper = PantryKeeper()
  keeper.cleanup_old_backups()
  "
  ```

### Log Analysis

#### Backup Success Indicators

Look for these log entries:
```
INFO - === Starting Pantry Keeper Backup Job ===
INFO - Starting backup: jorbites_backup_YYYYMMDD_HHMMSS
INFO - Backup completed successfully: /path/to/backup.tar.gz
INFO - === Backup Job Completed Successfully ===
```

#### Error Indicators

Watch for these error patterns:
```
ERROR - mongodump failed: [error details]
ERROR - Backup failed with error: [error details]
ERROR - === Backup Job Failed ===
WARNING - Email notifications: ENABLED but missing variables: [variables]
```

### Performance Optimization

#### Backup Performance

- **Compression Level**: Modify compression in `utils.py` if needed
- **Parallel Processing**: Consider `mongodump --numParallelCollections`
- **Network Optimization**: Use local MongoDB when possible

#### Storage Optimization

- **Retention Period**: Adjust `RETENTION_DAYS` in `constants.py`
- **Compression**: Backups are already compressed with gzip
- **External Storage**: Consider moving old backups to external storage

## Security Considerations

### File Permissions

Ensure proper permissions:

```bash
# Application directory
chmod 755 /opt/pantry_keeper

# Environment file (contains secrets)
chmod 600 /opt/pantry_keeper/.env

# Log files
chmod 644 /opt/pantry_keeper/logs/*.log

# Backup files
chmod 644 /opt/pantry_keeper/backups/*.tar.gz
```

## Backup and Recovery

### System Backup

Backup the entire Pantry Keeper installation:

```bash
# Create system backup
sudo tar -czf pantry_keeper_system_backup.tar.gz \
  /opt/pantry_keeper \
  /etc/systemd/system/pantry-keeper.service

# Restore system backup
sudo tar -xzf pantry_keeper_system_backup.tar.gz -C /
sudo systemctl daemon-reload
sudo systemctl enable pantry-keeper
```

### Database Restore

To restore from a backup:

```bash
# Extract backup
cd /tmp
tar -xzf /opt/pantry_keeper/backups/jorbites_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore to MongoDB
mongorestore --uri="mongodb://localhost:27017" --drop jorbites_backup_YYYYMMDD_HHMMSS/
```
