#!/usr/bin/env python
"""
Test script for the low stock update functionality.
This script tests both the GraphQL mutation and the direct database approach.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Product
from crm.schema import schema


def create_test_products():
    """Create some test products with low stock"""
    print("Creating test products...")
    
    # Create products with low stock
    low_stock_products = [
        {'name': 'Test Product 1', 'price': 10.99, 'stock': 5},
        {'name': 'Test Product 2', 'price': 25.50, 'stock': 2},
        {'name': 'Test Product 3', 'price': 15.00, 'stock': 8},
    ]
    
    # Create products with normal stock
    normal_stock_products = [
        {'name': 'Normal Stock Product 1', 'price': 30.00, 'stock': 50},
        {'name': 'Normal Stock Product 2', 'price': 45.99, 'stock': 25},
    ]
    
    created_products = []
    
    for product_data in low_stock_products + normal_stock_products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            created_products.append(product)
            print(f"Created: {product.name} - Stock: {product.stock}")
        else:
            # Update existing product
            product.price = product_data['price']
            product.stock = product_data['stock']
            product.save()
            print(f"Updated: {product.name} - Stock: {product.stock}")
    
    return created_products


def test_graphql_mutation():
    """Test the GraphQL mutation directly"""
    print("\n" + "="*50)
    print("Testing GraphQL Mutation")
    print("="*50)
    
    query = """
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
        result = schema.execute(query)
        
        if result.errors:
            print("GraphQL Errors:")
            for error in result.errors:
                print(f"  - {error}")
            return False
        
        data = result.data['updateLowStockProducts']
        
        if data['errors']:
            print("Mutation Errors:")
            for error in data['errors']:
                print(f"  - {error}")
            return False
        
        print(f"Success: {data['successMessage']}")
        
        if data['updatedProducts']:
            print("Updated Products:")
            for product in data['updatedProducts']:
                print(f"  - {product['name']} (ID: {product['id']}) - New Stock: {product['stock']}")
        
        return True
        
    except Exception as e:
        print(f"Exception during GraphQL mutation: {e}")
        return False


def test_database_approach():
    """Test the direct database approach"""
    print("\n" + "="*50)
    print("Testing Database Approach")
    print("="*50)
    
    try:
        from crm.cron import _update_via_database
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        _update_via_database(timestamp)
        
        print("Database approach completed. Check the log file for details.")
        return True
        
    except Exception as e:
        print(f"Exception during database approach: {e}")
        return False


def show_current_products():
    """Display current products and their stock levels"""
    print("\n" + "="*50)
    print("Current Products in Database")
    print("="*50)
    
    products = Product.objects.all().order_by('stock', 'name')
    
    if not products.exists():
        print("No products found in database.")
        return
    
    low_stock_count = Product.objects.filter(stock__lt=10).count()
    
    print(f"Total Products: {products.count()}")
    print(f"Low Stock Products (< 10): {low_stock_count}")
    print()
    
    for product in products:
        stock_status = "LOW STOCK" if product.stock < 10 else "Normal"
        print(f"  - {product.name}: Stock={product.stock}, Price=${product.price} [{stock_status}]")


if __name__ == "__main__":
    print("Low Stock Update Test Script")
    print("="*50)
    
    # Show initial state
    show_current_products()
    
    # Create test products
    create_test_products()
    
    # Show state after creating test products
    show_current_products()
    
    # Test GraphQL mutation
    graphql_success = test_graphql_mutation()
    
    # Show state after GraphQL mutation
    show_current_products()
    
    # Create more low stock products for database test
    print("\nCreating more low stock products for database test...")
    Product.objects.filter(name__startswith="Test Product").update(stock=3)
    
    # Test database approach
    database_success = test_database_approach()
    
    # Show final state
    show_current_products()
    
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"GraphQL Mutation Test: {'PASSED' if graphql_success else 'FAILED'}")
    print(f"Database Approach Test: {'PASSED' if database_success else 'FAILED'}")
    
    if graphql_success and database_success:
        print("\nAll tests passed! The low stock update system is working correctly.")
    else:
        print("\nSome tests failed. Please check the error messages above.")
