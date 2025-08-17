# ALX Backend GraphQL CRM

A Customer Relationship Management (CRM) system built with Django and GraphQL as part of the ALX Backend Specialization program. This project demonstrates the implementation of a modern GraphQL API for managing customers, products, and orders.

## 🚀 Features

- **GraphQL API**: Full GraphQL implementation with queries and mutations
- **Customer Management**: Create and manage customer profiles with contact information
- **Product Management**: Add and manage products with pricing and stock information
- **Order Management**: Create orders linking customers to products
- **Data Validation**: Comprehensive form validation using Django forms
- **Database Seeding**: Pre-built script to populate the database with sample data

## 🛠️ Technology Stack

- **Backend Framework**: Django 5.2.4
- **GraphQL**: Graphene Django
- **Database**: SQLite (default)
- **Filtering**: Django Filters
- **Python Version**: 3.x

## 📋 API Schema

### Models

#### Customer
- `id`: Unique identifier
- `name`: Customer name (max 100 characters)
- `email`: Unique email address
- `phone`: Optional phone number

#### Product
- `id`: Unique identifier
- `name`: Product name (max 100 characters)
- `price`: Product price (decimal)
- `stock`: Available stock quantity

#### Order
- `id`: Unique identifier
- `customer`: Foreign key to Customer
- `products`: Many-to-many relationship with Products
- `total_amount`: Automatically calculated total
- `order_date`: Timestamp of order creation

### GraphQL Operations

#### Queries
```graphql
query {
  customers {
    id
    name
    email
    phone
  }
  
  products {
    id
    name
    price
  }
  
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
```

#### Mutations
```graphql
# Create Customer
mutation {
  createCustomer(name: "John Doe", email: "john@example.com", phone: "+1234567890") {
    customer {
      id
      name
      email
    }
    errors
  }
}

# Create Product
mutation {
  createProduct(name: "Laptop", price: 999.99) {
    product {
      id
      name
      price
    }
    errors
  }
}

# Create Order
mutation {
  createOrder(customerId: 1, productId: 1, quantity: 2) {
    order {
      id
      customer {
        name
      }
    }
    errors
  }
}
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Derick-Obeng/alx-backend-graphql_crm.git
   cd alx-backend-graphql_crm
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django graphene-django django-filter
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed the database with sample data**
   ```bash
   python seed_db.py
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000/`

### GraphQL Playground

Access the GraphQL interface at `http://localhost:8000/graphql/` to interact with the API using the built-in GraphiQL explorer.

## 📁 Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/     # Main Django project directory
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL configuration
│   ├── schema.py                # Main GraphQL schema
│   └── wsgi.py                  # WSGI configuration
├── crm/                         # CRM application
│   ├── models.py                # Database models
│   ├── schema.py                # GraphQL schema definitions
│   ├── admin.py                 # Django admin configuration
│   └── filters.py               # Django filters
├── manage.py                    # Django management script
├── seed_db.py                   # Database seeding script
├── db.sqlite3                   # SQLite database
└── README.md                    # Project documentation
```

## 🧪 Testing

To run the tests:

```bash
python manage.py test
```

## 📚 Learning Objectives

This project was developed as part of the ALX Backend Specialization program to demonstrate:

- Understanding of GraphQL concepts and implementation
- Django framework proficiency
- Database modeling and relationships
- API design and validation
- Modern backend development practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Derick Obeng**
- GitHub: [@Derick-Obeng](https://github.com/Derick-Obeng)

## 🙏 Acknowledgments

- ALX Africa for the comprehensive backend specialization program
- The Django and GraphQL communities for excellent documentation and tools