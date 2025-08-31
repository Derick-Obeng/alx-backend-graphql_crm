"""
CRM app specific settings for django-crontab.

This file contains the CRM-specific cron job configurations.
It should be imported or included in the main Django settings.
"""

from django.conf import settings
from celery.schedules import crontab

# Ensure django_crontab is in INSTALLED_APPS
if 'django_crontab' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ['django_crontab']

# Ensure django_celery_beat is in INSTALLED_APPS
if 'django_celery_beat' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ['django_celery_beat']

# CRM-specific cron jobs
CRM_CRONJOBS = [
    # Update low-stock products every 12 hours
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
    
    # Log CRM heartbeat every 5 minutes
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    
    # Clean inactive customers weekly on Sunday at 2 AM
    ('0 2 * * 0', 'crm.cron.clean_inactive_customers'),
    
    # Send order reminders daily at 8 AM
    ('0 8 * * *', 'crm.cron.send_order_reminders'),
]

# Add CRM cron jobs to the main CRONJOBS setting
if hasattr(settings, 'CRONJOBS'):
    # Merge with existing cron jobs, avoiding duplicates
    existing_jobs = [job[1] for job in settings.CRONJOBS]
    for job in CRM_CRONJOBS:
        if job[1] not in existing_jobs:
            settings.CRONJOBS.append(job)
else:
    settings.CRONJOBS = CRM_CRONJOBS

# Django-crontab settings
CRONTAB_LOCK_JOBS = True
CRONTAB_COMMAND_PREFIX = ''
CRONTAB_COMMAND_SUFFIX = ''

# Log file paths for CRM cron jobs
CRM_LOG_PATHS = {
    'low_stock_updates': '/tmp/low_stock_updates_log.txt',
    'heartbeat': '/tmp/crm_heartbeat_log.txt',
    'customer_cleanup': '/tmp/customer_cleanup_log.txt',
    'order_reminders': '/tmp/order_reminders_log.txt',
}

# GraphQL endpoint for CRM cron jobs
CRM_GRAPHQL_ENDPOINT = 'http://localhost:8000/graphql/'

# CRM cron job configurations
CRM_CRON_CONFIG = {
    'low_stock_threshold': 10,
    'restock_amount': 10,
    'inactive_customer_days': 365,
    'order_reminder_days': 7,
}

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Configuration
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
