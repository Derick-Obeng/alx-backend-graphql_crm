from crm.models import Customer, Product

Customer.objects.create(name="Test User", email="test@example.com", phone="+1234567890")
Product.objects.create(name="Phone", price=500, stock=5)
Product.objects.create(name="Tablet", price=800, stock=2)
