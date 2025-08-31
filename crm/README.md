# CRM Celery Setup and Documentation

This document provides instructions for setting up and running the Celery-based CRM reporting system.

## Overview

The CRM application uses Celery with Redis as a message broker to run background tasks, including:

- **Weekly CRM Reports**: Automatically generated every Monday at 6:00 AM UTC
- **GraphQL Integration**: Uses GraphQL queries to fetch CRM data
- **Logging**: All reports are logged to `/tmp/crm_report_log.txt`

## Prerequisites

- Python 3.8+
- Django 5.2.4
- Redis server
- Required Python packages (see requirements.txt)

## Installation and Setup

### 1. Install Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

#### Windows:
- Download Redis from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis:alpine`

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations

```bash
python manage.py migrate
```

This will create the necessary tables for django-celery-beat to store periodic task schedules.

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

This allows you to access the Django admin interface to manage Celery Beat schedules.

## Running the System

### 1. Start Redis Server

Make sure Redis is running on `localhost:6379`:

```bash
redis-server
```

You can test Redis connectivity:
```bash
redis-cli ping
# Should return: PONG
```

### 2. Start Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at: http://localhost:8000/graphql/

### 3. Start Celery Worker

Open a new terminal and run:

```bash
celery -A crm worker -l info
```

This starts the Celery worker that will execute the background tasks.

### 4. Start Celery Beat Scheduler

Open another terminal and run:

```bash
celery -A crm beat -l info
```

This starts the Celery Beat scheduler that will trigger the weekly CRM report task.

## Verifying the Setup

### 1. Check Celery Worker Status

The worker terminal should show:
```
[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] mingle: searching for available nodes...
[INFO/MainProcess] mingle: all alone
[INFO/MainProcess] pidbox: enabled
[INFO/MainProcess] celery@hostname ready.
```

### 2. Check Celery Beat Status

The beat terminal should show:
```
[INFO/MainProcess] beat: Starting...
[INFO/MainProcess] Scheduler: Sending due task generate-crm-report (crm.tasks.generate_crm_report)
```

### 3. Test Manual Task Execution

You can manually trigger the CRM report task:

```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report, test_celery_task

# Test basic Celery functionality
result = test_celery_task.delay()
print(result.get())

# Test CRM report generation
result = generate_crm_report.delay()
print(result.get())
```

### 4. Check Log Files

Verify that reports are being logged:

```bash
# On Linux/macOS
tail -f /tmp/crm_report_log.txt

# On Windows
type C:\temp\crm_report_log.txt
```

Expected log format:
```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
YYYY-MM-DD HH:MM:SS GraphQL endpoint responsive: Hello, GraphQL!
YYYY-MM-DD HH:MM:SS CRM report generated successfully via GraphQL
```

## Task Schedule

The CRM report task is scheduled to run:
- **Day**: Every Monday
- **Time**: 6:00 AM UTC
- **Cron Expression**: `0 6 * * 1`

## Task Details

### generate_crm_report Task

This task performs the following operations:

1. **Endpoint Check**: Queries the GraphQL `hello` field to verify connectivity
2. **Data Fetching**: Uses GraphQL queries to fetch:
   - Total number of customers
   - Total number of orders  
   - Total revenue (sum of order amounts)
3. **Fallback**: If GraphQL fails, uses direct database queries
4. **Logging**: Writes detailed report to log file with timestamp

### GraphQL Queries Used

```graphql
# Endpoint health check
query {
    hello
}

# CRM data query
query {
    customers {
        id
        name
        email
    }
    orders {
        id
        totalAmount
        orderDate
        customer {
            id
            name
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```
   Error: No such file or directory: redis-server
   ```
   - Solution: Install and start Redis server

2. **Import Error for Celery**
   ```
   ImportError: No module named 'celery'
   ```
   - Solution: `pip install celery django-celery-beat redis`

3. **Task Not Executing**
   - Check that both worker and beat are running
   - Verify Redis is accessible
   - Check the Django admin for periodic tasks

4. **GraphQL Endpoint Not Responding**
   - Ensure Django server is running
   - Check GraphQL endpoint at http://localhost:8000/graphql/
   - Task will fallback to database queries

### Debug Commands

```bash
# Check Redis connectivity
redis-cli ping

# List Celery workers
celery -A crm inspect active

# Check scheduled tasks
celery -A crm inspect scheduled

# Monitor task execution
celery -A crm events

# View task history in Django admin
python manage.py runserver
# Go to: http://localhost:8000/admin/django_celery_beat/
```

## Configuration

### Celery Settings

Key settings in `crm/settings.py`:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

### Modifying the Schedule

To change when the report runs, modify the `crontab` parameters:

```python
# Daily at 8 AM
'schedule': crontab(hour=8, minute=0),

# Every Friday at 5 PM
'schedule': crontab(day_of_week='fri', hour=17, minute=0),

# Every 6 hours
'schedule': crontab(minute=0, hour='*/6'),
```

## Production Considerations

1. **Use a Process Manager**: Use Supervisor or systemd to manage Celery processes
2. **Monitoring**: Set up monitoring for Celery workers and Redis
3. **Logging**: Configure proper log rotation for the report log files
4. **Redis Persistence**: Configure Redis persistence for task result storage
5. **Multiple Workers**: Run multiple Celery workers for better performance

## File Structure

```
crm/
├── __init__.py          # Loads Celery app
├── celery.py           # Celery configuration
├── tasks.py            # Celery tasks
├── settings.py         # CRM-specific settings
├── models.py           # Django models
├── schema.py           # GraphQL schema
├── cron.py             # Crontab functions
└── README.md           # This file
```

## Support

For issues or questions:
1. Check the log files for error messages
2. Verify all services (Redis, Django, Celery) are running
3. Review the Django admin for Celery Beat configuration
4. Check the GraphQL endpoint manually
