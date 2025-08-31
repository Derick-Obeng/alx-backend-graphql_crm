#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def main():
    """Send order reminders by querying GraphQL endpoint and logging to file"""
    
    # GraphQL endpoint configuration
    graphql_url = 'http://localhost:8000/graphql/'
    
    # Create GraphQL client
    transport = RequestsHTTPTransport(url=graphql_url)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # GraphQL query to get recent orders
    query = gql("""
        query {
            orders {
                id
                customer {
                    name
                    email
                }
                totalAmount
                orderDate
            }
        }
    """)
    
    try:
        # Execute the query
        result = client.execute(query)
        orders = result['orders']
        
        # Filter orders from the last 7 days (since GraphQL doesn't have date filtering in this schema)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_orders = []
        
        for order in orders:
            order_date = datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00'))
            if order_date >= seven_days_ago:
                recent_orders.append(order)
        
        # Log the order reminders
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_path = '/tmp/order_reminders_log.txt'
        
        with open(log_path, 'a') as log_file:
            log_file.write(f"[{timestamp}] Order reminders processing started\n")
            
            if recent_orders:
                log_file.write(f"[{timestamp}] Found {len(recent_orders)} recent orders\n")
                
                for order in recent_orders:
                    customer_name = order['customer']['name']
                    customer_email = order['customer']['email']
                    order_id = order['id']
                    total_amount = order['totalAmount']
                    order_date = order['orderDate']
                    
                    log_entry = (
                        f"[{timestamp}] Order Reminder - "
                        f"Order ID: {order_id}, "
                        f"Customer: {customer_name} ({customer_email}), "
                        f"Amount: ${total_amount}, "
                        f"Date: {order_date}\n"
                    )
                    log_file.write(log_entry)
            else:
                log_file.write(f"[{timestamp}] No recent orders found for reminders\n")
            
            log_file.write(f"[{timestamp}] Order reminders processing completed\n\n")
        
        print(f"Order reminders processed! Found {len(recent_orders)} recent orders.")
        
    except Exception as e:
        # Log errors
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = f"[{timestamp}] Error processing order reminders: {str(e)}\n"
        
        try:
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                log_file.write(error_msg)
        except:
            # If we can't write to the log file, at least print the error
            print(error_msg)
        
        # Also use fallback direct database approach if GraphQL fails
        fallback_database_approach(timestamp)

def fallback_database_approach(timestamp):
    """Fallback method using direct database access if GraphQL fails"""
    try:
        import django
        from django.utils import timezone
        
        # Setup Django
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
        django.setup()
        
        from crm.models import Order
        
        # Get orders from the last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        pending_orders = Order.objects.filter(order_date__gte=seven_days_ago)
        
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] [FALLBACK] Using direct database access\n")
            log_file.write(f"[{timestamp}] [FALLBACK] Found {pending_orders.count()} recent orders\n")
            
            for order in pending_orders:
                log_entry = (
                    f"[{timestamp}] [FALLBACK] Order Reminder - "
                    f"Order ID: {order.id}, "
                    f"Customer: {order.customer.name} ({order.customer.email}), "
                    f"Amount: ${order.total_amount}, "
                    f"Date: {order.order_date}\n"
                )
                log_file.write(log_entry)
            
            log_file.write(f"[{timestamp}] [FALLBACK] Order reminders processing completed\n\n")
        
        print(f"[FALLBACK] Order reminders processed via database! Found {pending_orders.count()} recent orders.")
        
    except Exception as e:
        error_msg = f"[{timestamp}] [FALLBACK] Database approach also failed: {str(e)}\n"
        try:
            with open('/tmp/order_reminders_log.txt', 'a') as log_file:
                log_file.write(error_msg)
        except:
            print(error_msg)

if __name__ == "__main__":
    main()
