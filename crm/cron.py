import os
import json
import requests
from datetime import datetime
from django.conf import settings


def log_crm_heartbeat():
    """Log CRM heartbeat message every 5 minutes"""
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"
    
    # Use appropriate temp directory for the platform
    log_path = '/tmp/crm_heartbeat_log.txt' if os.name == 'posix' else 'C:\\temp\\crm_heartbeat_log.txt'
    
    # Create directory if it doesn't exist (for Windows)
    if os.name != 'posix':
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, 'a') as log_file:
        log_file.write(message)


def update_low_stock():
    """Update low-stock products using GraphQL mutation and log the updates"""
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Try GraphQL approach first, then fallback to direct database approach
    success = _update_via_graphql(timestamp)
    
    if not success:
        _update_via_database(timestamp)


def _update_via_graphql(timestamp):
    """Try to update via GraphQL mutation"""
    # GraphQL mutation query
    mutation = """
    mutation {
        updateLowStockProducts {
            updatedProducts {
                id
                name
                stock
            }
            successMessage
            errors
        }
    }
    """
    
    try:
        # Execute GraphQL mutation via HTTP request
        # Assuming the GraphQL endpoint is available at /graphql/
        graphql_url = 'http://localhost:8000/graphql/'
        
        response = requests.post(
            graphql_url,
            json={'query': mutation},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'errors' in data:
                # GraphQL errors
                error_msg = f"{timestamp} GraphQL errors: {data['errors']}\n"
                _write_log(error_msg, timestamp)
                return False
            else:
                mutation_data = data['data']['updateLowStockProducts']
                
                if mutation_data['errors']:
                    # Mutation returned errors
                    error_msg = f"{timestamp} Mutation errors: {mutation_data['errors']}\n"
                    _write_log(error_msg, timestamp)
                    return False
                else:
                    # Success
                    updated_products = mutation_data['updatedProducts']
                    success_message = mutation_data['successMessage']
                    
                    log_message = f"{timestamp} {success_message}\n"
                    
                    if updated_products:
                        log_message += f"{timestamp} Updated products:\n"
                        for product in updated_products:
                            log_message += f"{timestamp}   - {product['name']} (ID: {product['id']}) - New stock: {product['stock']}\n"
                    
                    log_message += "\n"
                    _write_log(log_message, timestamp)
                    return True
        else:
            # HTTP error
            error_msg = f"{timestamp} HTTP error {response.status_code}: {response.text}\n"
            _write_log(error_msg, timestamp)
            return False
            
    except requests.exceptions.RequestException as e:
        # Request failed
        error_msg = f"{timestamp} Request failed: {str(e)}\n"
        _write_log(error_msg, timestamp)
        return False
    except Exception as e:
        # Other errors
        error_msg = f"{timestamp} GraphQL approach failed: {str(e)}\n"
        _write_log(error_msg, timestamp)
        return False


def _update_via_database(timestamp):
    """Fallback: Update directly via database"""
    try:
        from crm.models import Product
        
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        
        if not low_stock_products.exists():
            log_message = f"{timestamp} [Database Fallback] No low-stock products found.\n\n"
            _write_log(log_message, timestamp)
            return
        
        updated_products = []
        for product in low_stock_products:
            # Increment stock by 10 (simulating restocking)
            old_stock = product.stock
            product.stock += 10
            product.save()
            updated_products.append({
                'id': product.id,
                'name': product.name,
                'old_stock': old_stock,
                'new_stock': product.stock
            })
        
        log_message = f"{timestamp} [Database Fallback] Successfully updated {len(updated_products)} low-stock products.\n"
        
        if updated_products:
            log_message += f"{timestamp} [Database Fallback] Updated products:\n"
            for product in updated_products:
                log_message += f"{timestamp}   - {product['name']} (ID: {product['id']}) - Stock: {product['old_stock']} -> {product['new_stock']}\n"
        
        log_message += "\n"
        _write_log(log_message, timestamp)
        
    except Exception as e:
        error_msg = f"{timestamp} [Database Fallback] Failed: {str(e)}\n"
        _write_log(error_msg, timestamp)


def _write_log(message, timestamp):
    """Write message to log file with fallback locations"""
    log_path = '/tmp/low_stock_updates_log.txt'
    
    try:
        with open(log_path, 'a') as log_file:
            log_file.write(message)
    except Exception as e:
        # If we can't write to /tmp, try a fallback location
        fallback_path = 'C:\\temp\\low_stock_updates_log.txt' if os.name != 'posix' else '/var/log/low_stock_updates_log.txt'
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, 'a') as log_file:
                log_file.write(message)
                log_file.write(f"{timestamp} Note: Using fallback log location {fallback_path}\n")
        except Exception:
            # If all else fails, at least try to print to console
            print(f"Failed to write log: {message}")
