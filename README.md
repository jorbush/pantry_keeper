# Pantry Keeper

Automated backup system for [Jorbites](https://jorbites.com) database (MongoDB) to a local file which can be restored to a new database.

![logo](./docs/assets/pantry_keeper_logo_no_bg.png)

You can find the documentation [here](./docs/README.md).

## Requirements

- Python 3.10+
- MongoDB tools: `mongodump` and `mongorestore` (`sudo apt-get install mongodb-database-tools` on Ubuntu/Debian, `brew install mongodb/brew/mongodb-database-tools` on macOS)
- Setup a `.env` file in the root directory with the following variables:
    - `DATABASE_URL`: The URI of the MongoDB database (e.g. `mongodb://localhost:27017/jorbites` or `mongodb+srv://jorbites:jorbites@jorbites.mongodb.net/jorbites`)
    - Email configuration (optional, for error notifications):
        - `EMAIL_USER`: Your email address
        - `EMAIL_PASSWORD`: Your email password or app password
        - `EMAIL_TO`: Email address to receive notifications

## Features

- ✅ Backup the database to a local file which can be restored to a new database
- ✅ Do this weekly and keep the backups for 1 month
- ✅ Log when the backup is successful or fails
- ✅ Send an email if the backup fails

## Installation

1. Create a virtual environment:
    ```bash
    python -m venv venv
    ```

2. Activate the virtual environment:
    ```bash
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Install MongoDB tools (if not already installed):
    ```bash
    # On Ubuntu/Debian
    sudo apt-get install mongodb-database-tools

    # On macOS
    brew install mongodb/brew/mongodb-database-tools
    ```

5. Create a `.env` file with your database URL and email configuration:
    ```bash
    # Database configuration
    echo "DATABASE_URL=mongodb://localhost:27017/jorbites" > .env

    # Email configuration (optional)
    echo "EMAIL_USER=your-email@gmail.com" >> .env
    echo "EMAIL_PASSWORD=your-app-password" >> .env
    echo "EMAIL_TO=admin@yourdomain.com" >> .env
    ```

## Usage

### Manual Backup
```bash
python backup.py
```

### Run Weekly Scheduler
```bash
python scheduler.py
```

## Running as a System Service

To run the backup scheduler automatically as a system service:

1. Copy the service file:
    ```bash
    sudo cp pantry-keeper.service /etc/systemd/system/
    ```

2. Enable and start the service:
    ```bash
    sudo systemctl enable pantry-keeper
    sudo systemctl start pantry-keeper
    ```

3. Check service status:
    ```bash
    sudo systemctl status pantry-keeper
    ```
