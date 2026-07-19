# HDMS --- Historical Market Data Management System

## Setup Guide

This guide explains how to set up the HDMS project on a new Windows
system.

------------------------------------------------------------------------

# 1. Project Architecture

The project consists of two main parts:

``` text
HDMS
│
├── Django REST API
│   │
│   ├── PostgreSQL
│   │
│   ├── Celery
│   │
│   └── Redis / Memurai
│
└── PyQt6 Client
    │
    ├── Uploader
    │
    └── Downloader
```

## Upload Flow

``` text
PyQt6 Uploader
       ↓
Django REST API
       ↓
Temporary CSV File
       ↓
Celery Background Task
       ↓
Polars CSV Processing
       ↓
PostgreSQL COPY
       ↓
futstk_table
```

## Download Flow

``` text
PyQt6 Downloader
       ↓
Django REST API
       ↓
PostgreSQL
       ↓
Streaming CSV Response
       ↓
CSV File Saved on Client
```

------------------------------------------------------------------------

# 2. Requirements

Install the following software:

-   Python 3.12 or newer
-   PostgreSQL
-   Redis-compatible message broker
-   Memurai (recommended for Windows)
-   Git (optional)

Python packages used by the project include:

``` text
Django
Django REST Framework
psycopg
Celery
Polars
PyQt6
Requests
```

The exact packages are listed in:

``` text
requirements.txt
```

------------------------------------------------------------------------

# 3. Clone or Copy the Project

Copy the project to the new system.

Example:

``` text
D:\Projects\Real_Projects\hdms
```

Project structure:

``` text
hdms/
│
├── config/
│
├── downloader/
│
├── uploader/
│
├── manage.py
│
├── requirements.txt
│
└── venv/
```

Do not copy the old virtual environment if possible.

Create a new one on the new machine.

------------------------------------------------------------------------

# 4. Create a Virtual Environment

Open PowerShell inside the project directory:

``` powershell
python -m venv venv
```

Activate it:

``` powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run PowerShell as Administrator and
execute:

``` powershell
Set-ExecutionPolicy RemoteSigned
```

Then activate again:

``` powershell
.\venv\Scripts\Activate.ps1
```

You should see:

``` text
(venv) PS D:\Projects\Real_Projects\hdms>
```

------------------------------------------------------------------------

# 5. Install Python Dependencies

With the virtual environment activated:

``` powershell
pip install -r requirements.txt
```

Verify Django:

``` powershell
python -m django --version
```

Verify Polars:

``` powershell
python -c "import polars; print(polars.__version__)"
```

Verify Celery:

``` powershell
celery --version
```

------------------------------------------------------------------------

# 6. Install PostgreSQL

Install PostgreSQL on the new system.

During installation, remember:

``` text
Username: postgres
Password: YOUR_PASSWORD
Port: 5432
```

The PostgreSQL service must be running.

You can verify it from:

``` text
Windows Services
```

Look for a PostgreSQL service.

------------------------------------------------------------------------

# 7. Create the Database

Open PostgreSQL using `psql` or pgAdmin.

Create the database:

``` sql
CREATE DATABASE hdms_db;
```

Connect to it:

``` sql
\c hdms_db
```

The database name used by this project is:

``` text
hdms_db
```

------------------------------------------------------------------------

# 8. Configure Django Database

Open:

``` text
config/settings.py
```

Configure PostgreSQL:

``` python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "hdms_db",
        "USER": "postgres",
        "PASSWORD": "YOUR_POSTGRES_PASSWORD",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
```

Replace:

``` text
YOUR_POSTGRES_PASSWORD
```

with the actual PostgreSQL password.

------------------------------------------------------------------------

# 9. Configure Allowed Hosts

If the Django API must be accessed from other computers on the same
network:

``` python
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "YOUR_SYSTEM_IP",
]
```

Example:

``` python
ALLOWED_HOSTS = [
    "10.203.6.124",
    "localhost",
    "127.0.0.1",
]
```

To find the system IP:

``` powershell
ipconfig
```

Look for:

``` text
IPv4 Address
```

For example:

``` text
10.203.6.124
```

Use the current IP address of the machine running Django.

------------------------------------------------------------------------

# 10. Run Database Migrations

From the project root:

``` powershell
python manage.py migrate
```

Check the project:

``` powershell
python manage.py check
```

Expected result:

``` text
System check identified no issues
```

------------------------------------------------------------------------

# 11. Verify the Database Table

After migrations, verify:

``` sql
\d+ futstk_table
```

The table structure should be:

``` text
id       bigint
symbol   varchar(50)
fut      varchar(10)
date     date
time     integer
open     numeric(15,4)
high     numeric(15,4)
low      numeric(15,4)
close    numeric(15,4)
volume   bigint
oi       bigint
```

The source CSV structure is:

``` text
Symbol,Date,Time,open,high,low,close,volume,OI
```

Example:

``` text
ADANIENSOL-I,2015-07-31,95000,26.3,26.3,26.3,26.3,0,0
```

The importer transforms:

``` text
ADANIENSOL-I
```

into:

``` text
symbol = ADANIENSOL
fut = I
```

------------------------------------------------------------------------

# 12. Create the Important Database Index

The downloader uses:

``` sql
WHERE symbol = ?
AND fut = ?
AND date BETWEEN ? AND ?
ORDER BY date, time
```

Therefore create:

``` sql
CREATE INDEX CONCURRENTLY idx_futstk_symbol_fut_date_time
ON futstk_table (symbol, fut, date, time);
```

Verify:

``` sql
\d+ futstk_table
```

You should see:

``` text
idx_futstk_symbol_fut_date_time
```

This index is very important for downloader performance.

------------------------------------------------------------------------

# 13. Install and Start Memurai

On Windows, Memurai is used as the Redis-compatible broker for Celery.

After installation, start the Memurai service.

Verify:

``` powershell
memurai-cli
```

Then run:

``` text
ping
```

Expected:

``` text
PONG
```

Exit:

``` text
exit
```

The Celery broker is typically configured as:

``` text
redis://127.0.0.1:6379/0
```

------------------------------------------------------------------------

# 14. Start Django

Open PowerShell:

``` powershell
.\venv\Scripts\Activate.ps1
```

Run:

``` powershell
python manage.py runserver 0.0.0.0:8000
```

The API will be available at:

``` text
http://127.0.0.1:8000/
```

From another computer on the same network:

``` text
http://YOUR_SYSTEM_IP:8000/
```

Example:

``` text
http://10.203.6.124:8000/
```

------------------------------------------------------------------------

# 15. Start Celery Worker

Open a second PowerShell window.

Go to the project directory:

``` powershell
cd D:\Projects\Real_Projects\hdms
```

Activate the environment:

``` powershell
.\venv\Scripts\Activate.ps1
```

Start Celery:

``` powershell
celery -A config worker --loglevel=info --pool=solo
```

On Windows, use:

``` text
--pool=solo
```

The worker should display something similar to:

``` text
celery@COMPUTER-NAME ready.
```

The system now has:

``` text
Django API
     +
Celery Worker
     +
Memurai
     +
PostgreSQL
```

------------------------------------------------------------------------

# 16. Start the PyQt6 Uploader

The uploader client contains:

``` text
worker.py
ui.py
main.py
```

Start it with:

``` powershell
python main.py
```

The uploader workflow is:

``` text
Select CSV
       ↓
Upload to Django
       ↓
Create ImportJob
       ↓
Celery Task
       ↓
Read CSV with Polars
       ↓
Transform Symbol
       ↓
PostgreSQL COPY
       ↓
Import Complete
```

Example transformation:

``` text
ADANIPORTS-I
```

becomes:

``` text
symbol = ADANIPORTS
fut = I
```

------------------------------------------------------------------------

# 17. Upload Processing

The API creates an import job.

Example response:

``` json
{
    "message": "File uploaded successfully",
    "job_id": 7,
    "filename": "ADANIPORTS-I.csv",
    "status": "QUEUED"
}
```

Celery then processes the job:

``` text
QUEUED
   ↓
PROCESSING
   ↓
COMPLETED
```

If an error occurs:

``` text
FAILED
```

The import job stores:

``` text
status
total_rows
processed_rows
error_message
started_at
completed_at
```

------------------------------------------------------------------------

# 18. Downloader API

The downloader currently provides these APIs.

## Get Symbols

``` text
GET /api/downloader/futstk/symbols/
```

Example:

``` text
http://YOUR_IP:8000/api/downloader/futstk/symbols/
```

Response:

``` json
{
    "symbols": [
        "ABB",
        "ADANIENSOL",
        "ADANIPORTS"
    ]
}
```

------------------------------------------------------------------------

## Get Futures

``` text
GET /api/downloader/futstk/futures/?symbol=ADANIENSOL
```

Response:

``` json
{
    "symbol": "ADANIENSOL",
    "futures": [
        "I"
    ]
}
```

------------------------------------------------------------------------

## Get Date Range

``` text
GET /api/downloader/futstk/date-range/?symbol=ADANIENSOL&fut=I
```

Response:

``` json
{
    "symbol": "ADANIENSOL",
    "fut": "I",
    "min_date": "2015-07-31",
    "max_date": "2026-07-17"
}
```

------------------------------------------------------------------------

## Get Metadata

``` text
GET /api/downloader/futstk/metadata/
```

Example:

``` text
/api/downloader/futstk/metadata/?symbol=ADANIENSOL&fut=I&start_date=2015-07-31&end_date=2015-08-31
```

Response:

``` json
{
    "symbol": "ADANIENSOL",
    "fut": "I",
    "start_date": "2015-07-31",
    "end_date": "2015-08-31",
    "total_rows": 8212
}
```

------------------------------------------------------------------------

## Download CSV

``` text
GET /api/downloader/futstk/download/
```

Example:

``` text
/api/downloader/futstk/download/?symbol=ADANIENSOL&fut=I&start_date=2015-07-31&end_date=2015-08-31
```

The API streams the CSV directly to the client.

------------------------------------------------------------------------

# 19. Start the PyQt6 Downloader

The downloader client contains:

``` text
worker.py
ui.py
main.py
```

Before starting it, update:

``` python
self.base_url = "http://YOUR_SERVER_IP:8000"
```

Example:

``` python
self.base_url = "http://10.203.6.124:8000"
```

Then run:

``` powershell
python main.py
```

The downloader workflow is:

``` text
Load Symbols
     ↓
Select Symbol
     ↓
Load Futures
     ↓
Select Future
     ↓
Load Date Range
     ↓
Load Row Count
     ↓
Select Date Range
     ↓
Download CSV
```

------------------------------------------------------------------------

# 20. Running the Complete System

The complete system requires three services.

## Terminal 1 --- Django

``` powershell
python manage.py runserver 0.0.0.0:8000
```

## Terminal 2 --- Celery

``` powershell
celery -A config worker --loglevel=info --pool=solo
```

## Memurai

Memurai must be running:

``` text
127.0.0.1:6379
```

Then:

``` text
PyQt6 Client
```

can connect to the Django API.

------------------------------------------------------------------------

# 21. Troubleshooting

## Django cannot connect to PostgreSQL

Check:

``` text
PostgreSQL service is running
```

Verify:

``` text
Database name
Username
Password
Port
```

Default PostgreSQL port:

``` text
5432
```

------------------------------------------------------------------------

## Celery worker does not start

Check Memurai:

``` powershell
memurai-cli
```

Then:

``` text
ping
```

Expected:

``` text
PONG
```

Also verify the Celery broker configuration.

------------------------------------------------------------------------

## PyQt6 cannot connect to Django

Check:

``` text
1. Django is running
2. Correct IP address is used
3. Port 8000 is open
4. ALLOWED_HOSTS contains the server IP
5. Windows Firewall allows port 8000
```

Test from another system:

``` text
http://SERVER_IP:8000/
```

------------------------------------------------------------------------

## API returns connection error

Check:

``` text
Django server
```

and the URL configured in the PyQt6 client:

``` python
self.base_url = "http://SERVER_IP:8000"
```

------------------------------------------------------------------------

## Celery task remains QUEUED

Check that:

``` text
Memurai is running
```

and:

``` text
Celery worker is running
```

The worker should show:

``` text
Task received
```

------------------------------------------------------------------------

# 22. Recommended Startup Order

Always start the system in this order:

``` text
1. PostgreSQL
       ↓
2. Memurai
       ↓
3. Django
       ↓
4. Celery Worker
       ↓
5. PyQt6 Client
```

------------------------------------------------------------------------

# 23. Project Backup

For moving the project to another system, back up:

``` text
config/
downloader/
uploader/
manage.py
requirements.txt
```

Also export the database if the data must be moved:

``` powershell
pg_dump -U postgres -d hdms_db -F c -f hdms_backup.dump
```

Restore on another system:

``` powershell
pg_restore -U postgres -d hdms_db hdms_backup.dump
```

For very large datasets, PostgreSQL's native backup and restore tools
are recommended.

------------------------------------------------------------------------

# 24. Current Architecture

``` text
                         ┌──────────────────────┐
                         │      PyQt6 Client    │
                         │                      │
                         │  ┌───────────────┐   │
                         │  │    Uploader   │   │
                         │  └───────────────┘   │
                         │                      │
                         │  ┌───────────────┐   │
                         │  │   Downloader  │   │
                         │  └───────────────┘   │
                         └──────────┬───────────┘
                                    │
                                    │ HTTP / REST API
                                    │
                         ┌──────────▼───────────┐
                         │      Django API      │
                         └──────┬─────────┬─────┘
                                │         │
                                │         │
                       ┌────────▼───┐ ┌───▼────────┐
                       │ PostgreSQL │ │  Celery    │
                       │             │ │  Worker    │
                       └─────────────┘ └─────┬──────┘
                                             │
                                      ┌──────▼──────┐
                                      │   Memurai   │
                                      │ Redis Broker│
                                      └─────────────┘
```

------------------------------------------------------------------------

# 25. Important Performance Notes

The project is designed for large CSV files.

The upload pipeline uses:

``` text
Polars
     +
PostgreSQL COPY
```

The database uses:

``` text
Composite Index
```

for fast queries:

``` sql
(symbol, fut, date, time)
```

The current downloader query is optimized for:

``` sql
WHERE symbol = ?
AND fut = ?
AND date BETWEEN ? AND ?
ORDER BY date, time
```

For future datasets with hundreds of millions or billions of rows,
consider:

``` text
TimescaleDB
Partitioning
Additional indexes
Download job management
Compressed storage
```

------------------------------------------------------------------------

# 26. Quick Start Summary

On a new system:

``` powershell
git clone PROJECT
cd PROJECT

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate

python manage.py check
```

Then start:

``` powershell
# Terminal 1
python manage.py runserver 0.0.0.0:8000
```

``` powershell
# Terminal 2
celery -A config worker --loglevel=info --pool=solo
```

Make sure:

``` text
PostgreSQL is running
Memurai is running
```

Finally start the PyQt6 client:

``` powershell
python main.py
```

------------------------------------------------------------------------

# End

The current HDMS system supports:

-   CSV upload from PyQt6
-   Background processing using Celery
-   Fast CSV processing using Polars
-   PostgreSQL bulk insertion using COPY
-   Symbol and futures discovery
-   Date-range discovery
-   Row-count metadata
-   Streaming CSV downloads
-   Threaded PyQt6 operations
-   Progress and cancellation support
