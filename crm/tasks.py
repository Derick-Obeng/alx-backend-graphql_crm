"""
Celery tasks for the CRM application.

This module contains background tasks that can be executed asynchronously
using Celery workers.
"""

import os
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with GraphQL queries.
    
    This task:
    1. Queries the GraphQL endpoint for CRM data
    2. Calculates total customers, orders, and revenue
    3. Logs the report to /tmp/crm_report_log.txt
    
    Returns:
        dict: Report data with timestamp and statistics
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # GraphQL endpoint configuration
        graphql_url = 'http://localhost:8000/graphql/'
        
        # Create GraphQL client
        transport = RequestsHTTPTransport(url=graphql_url, timeout=30)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # First, verify endpoint is responsive
        hello_query = gql("""
            query {
                hello
            }
        """)
        
        try:
            hello_result = client.execute(hello_query)
            hello_message = hello_result.get('hello', 'No response')
            _log_message(f"{timestamp} GraphQL endpoint responsive: {hello_message}")
        except Exception as e:
            _log_message(f"{timestamp} GraphQL endpoint check failed: {str(e)}")
            return _fallback_database_report(timestamp)
        
        # Query for CRM data
        crm_query = gql("""
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
        """)
        
        # Execute the query
        result = client.execute(crm_query)
        
        # Calculate statistics
        customers = result.get('customers', [])
        orders = result.get('orders', [])
        
        total_customers = len(customers)
        total_orders = len(orders)
        
        # Calculate total revenue
        total_revenue = 0
        for order in orders:
            try:
                amount = float(order.get('totalAmount', 0))
                total_revenue += amount
            except (ValueError, TypeError):
                continue
        
        # Format revenue to 2 decimal places
        total_revenue = round(total_revenue, 2)
        
        # Create report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue} revenue"
        
        # Log the report
        _log_message(report_message)
        _log_message(f"{timestamp} CRM report generated successfully via GraphQL")
        
        # Additional detailed logging
        if total_customers > 0:
            _log_message(f"{timestamp} Customer details: {total_customers} total customers")
        if total_orders > 0:
            _log_message(f"{timestamp} Order details: {total_orders} total orders")
            average_order_value = total_revenue / total_orders if total_orders > 0 else 0
            _log_message(f"{timestamp} Average order value: ${round(average_order_value, 2)}")
        
        _log_message("")  # Add blank line for readability
        
        return {
            'success': True,
            'timestamp': timestamp,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'method': 'graphql'
        }
        
    except Exception as e:
        error_message = f"{timestamp} GraphQL report generation failed: {str(e)}"
        _log_message(error_message)
        
        # Fallback to database approach
        return _fallback_database_report(timestamp)


def _fallback_database_report(timestamp):
    """
    Fallback method using direct database access if GraphQL fails.
    
    Args:
        timestamp (str): Current timestamp string
        
    Returns:
        dict: Report data using database fallback
    """
    try:
        import django
        from django.db.models import Sum
        import sys
        import os
        
        # Setup Django
        sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
        django.setup()
        
        from crm.models import Customer, Order
        
        # Get statistics from database
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        
        # Calculate total revenue
        revenue_sum = Order.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        total_revenue = float(revenue_sum)
        
        # Create report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue} revenue"
        
        # Log the report
        _log_message(f"{timestamp} [FALLBACK] Using direct database access")
        _log_message(report_message)
        _log_message(f"{timestamp} [FALLBACK] CRM report generated successfully via database")
        
        # Additional detailed logging
        if total_customers > 0:
            _log_message(f"{timestamp} [FALLBACK] Customer details: {total_customers} total customers")
        if total_orders > 0:
            _log_message(f"{timestamp} [FALLBACK] Order details: {total_orders} total orders")
            average_order_value = total_revenue / total_orders if total_orders > 0 else 0
            _log_message(f"{timestamp} [FALLBACK] Average order value: ${round(average_order_value, 2)}")
        
        _log_message("")  # Add blank line for readability
        
        return {
            'success': True,
            'timestamp': timestamp,
            'total_customers': total_customers,
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'method': 'database_fallback'
        }
        
    except Exception as e:
        error_message = f"{timestamp} [FALLBACK] Database report generation also failed: {str(e)}"
        _log_message(error_message)
        
        return {
            'success': False,
            'timestamp': timestamp,
            'error': str(e),
            'method': 'failed'
        }


def _log_message(message):
    """
    Log a message to the CRM report log file.
    
    Args:
        message (str): Message to log
    """
    log_path = '/tmp/crm_report_log.txt'
    
    try:
        with open(log_path, 'a') as log_file:
            log_file.write(f"{message}\n")
    except Exception as e:
        # If we can't write to /tmp, try a fallback location
        fallback_path = 'C:\\temp\\crm_report_log.txt' if os.name != 'posix' else '/var/log/crm_report_log.txt'
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, 'a') as log_file:
                log_file.write(f"{message}\n")
                log_file.write(f"Note: Using fallback log location {fallback_path}\n")
        except Exception:
            # If all else fails, at least try to print to console
            print(f"Failed to write log: {message}")


@shared_task
def test_celery_task():
    """
    Simple test task to verify Celery is working.
    
    Returns:
        dict: Test result with timestamp
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{timestamp} Celery test task executed successfully"
    
    _log_message(message)
    
    return {
        'success': True,
        'timestamp': timestamp,
        'message': 'Celery test task completed'
    }
