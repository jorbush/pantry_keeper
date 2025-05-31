# Pantry Keeper Documentation

Welcome to the Pantry Keeper documentation! This directory contains comprehensive documentation for the MongoDB backup system designed for Raspberry Pi servers.

## Documentation Overview

### 📋 [Implementation Documentation](implementation.md)
Detailed technical documentation covering:
- System architecture and design decisions
- Component responsibilities and data flow
- Technical implementation details

### 📚 [API Reference](api-reference.md)
Complete reference for all classes, functions, and their parameters:
- `PantryKeeper` class methods and attributes
- Utility functions in `utils.py`
- Configuration constants
- Environment variables
- Error handling and return codes

### 🚀 [Deployment Guide](deployment-guide.md)
Step-by-step deployment instructions:
- Prerequisites and system requirements
- Installation and configuration
- Email setup and testing
- System service configuration
- Monitoring and maintenance
- Troubleshooting common issues

## Quick Start

If you're new to Pantry Keeper, follow this sequence:

1. **Start with [Deployment Guide](deployment-guide.md)** - Get the system up and running
2. **Review [Implementation Documentation](implementation.md)** - Understand how it works
3. **Reference [API Documentation](api-reference.md)** - For detailed function information

## System Overview

Pantry Keeper is a MongoDB backup system with the following features:

- ✅ **Automated Weekly Backups** - Scheduled for Sundays at 2:00 AM
- ✅ **Retention Management** - Automatically removes backups older than 30 days
- ✅ **Email Notifications** - Alerts administrators when backups fail
- ✅ **Comprehensive Logging** - Detailed logs for monitoring and troubleshooting
- ✅ **Systemd Integration** - Runs as a background service
- ✅ **Raspberry Pi Optimized** - Designed specifically for ARM64 architecture

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   scheduler.py  │    │    backup.py    │    │    utils.py     │
│                 │    │                 │    │                 │
│ - Weekly cron   │───▶│ - Backup logic  │───▶│ - Helper funcs  │
│ - Service mgmt  │    │ - Error handling│    │ - Email alerts  │
│ - Logging       │    │ - Retention     │    │ - File parsing  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
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

## File Structure

```
pantry_keeper/
├── backup.py           # Main backup orchestration
├── scheduler.py        # Weekly backup scheduler
├── constants.py        # Configuration constants
├── utils.py           # Utility functions
├── requirements.txt   # Python dependencies
├── .env              # Environment variables
├── backups/          # Backup storage (auto-created)
├── logs/             # Log files (auto-created)
├── docs/             # Documentation
│   ├── README.md     # This file
│   ├── implementation.md
│   ├── api-reference.md
│   ├── deployment-guide.md
│   └── assets/       # Images and logos
└── pantry-keeper.service # Systemd service file
```

## Key Features Explained

### Automated Scheduling
- Uses Python `schedule` library for cron-like functionality
- Runs as systemd service for reliability
- Configurable schedule (default: Sunday 2:00 AM)

### Backup Process
1. Connects to MongoDB using provided URI
2. Creates timestamped backup using `mongodump`
3. Compresses backup to `.tar.gz` format
4. Stores in local `backups/` directory
5. Removes old backups based on retention policy

### Error Handling
- Multi-layered error handling with graceful degradation
- Email notifications for backup failures
- Comprehensive logging for troubleshooting
- Service continues running despite individual backup failures

### Email Notifications
- SMTP support with Gmail integration
- Configurable via environment variables
- Includes error details and server information
- Optional - can be disabled if not needed

## Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=mongodb://localhost:27017/jorbites

# Optional (for email notifications)
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=admin@yourdomain.com
```

### Constants (constants.py)
```python
BACKUP_DIR = 'backups'          # Backup storage directory
RETENTION_DAYS = 30             # Keep backups for 30 days
BACKUP_DAY = 'sunday'           # Weekly backup day
BACKUP_TIME = '02:00'           # Backup time (24-hour format)
EMAIL_ENABLED = True            # Enable/disable email notifications
```

## Monitoring

### Log Files
- `logs/backup.log` - Backup operation logs
- `logs/scheduler.log` - Scheduler logs
- System logs via `journalctl -u pantry-keeper`

### Health Checks
- Service status: `sudo systemctl status pantry-keeper`
- Recent backups: `ls -la backups/`
- Disk usage: `du -sh backups/`

## Support and Troubleshooting

### Common Issues
1. **MongoDB Tools Not Found** - See [Deployment Guide](deployment-guide.md#mongodb-tools-installation)
2. **Permission Errors** - Check file ownership and permissions
3. **Email Configuration** - Verify SMTP settings and app passwords
4. **Service Won't Start** - Check logs and Python virtual environment

### Getting Help
- Check the [Deployment Guide](deployment-guide.md) for troubleshooting steps
- Review log files for error details
- Verify configuration in `.env` and `constants.py`
- Test components individually (backup, email, etc.)


---

For detailed information on any topic, please refer to the specific documentation files linked above.
