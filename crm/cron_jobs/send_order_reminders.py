#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Order

def main():
    # Get orders from the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    pending_orders = Order.objects.filter(order_date__gte=seven_days_ago)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open('/tmp/order_reminders_log.txt', 'a') as log_file:
        for order in pending_orders:
            log_entry = f"[{timestamp}] Order ID: {order.id}, Customer Email: {order.customer.email}\n"
            log_file.write(log_entry)
    
    print("Order reminders processed!")

if __name__ == "__main__":
    main()
