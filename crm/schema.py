import graphene
from graphene_django import DjangoObjectType
from django import forms
from crm.models import Customer, Product, Order
from crm.models import Product


# ------------------------
# GraphQL Types
# ------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ------------------------
# Django Forms for Validation
# ------------------------
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "phone"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price"]

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be positive")
        return price


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer", "products", "total_amount"]

    def clean_total_amount(self):
        amount = self.cleaned_data["total_amount"]
        if amount < 0:
            raise forms.ValidationError("Total amount cannot be negative")
        return amount


# ------------------------
# Mutations
# ------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, phone=None):
        form = CustomerForm(data={"name": name, "email": email, "phone": phone})
        if form.is_valid():
            customer = form.save()
            return CreateCustomer(customer=customer, errors=None)
        return CreateCustomer(customer=None, errors=[str(e) for e in form.errors.values()])


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, price):
        form = ProductForm(data={"name": name, "price": price})
        if form.is_valid():
            product = form.save()
            return CreateProduct(product=product, errors=None)
        return CreateProduct(product=None, errors=[str(e) for e in form.errors.values()])


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        total_amount = graphene.Float()

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customer_id, product_ids, total_amount=None):
        try:
            customer = Customer.objects.get(id=customer_id)
            products = Product.objects.filter(id__in=product_ids)
            
            if not products.exists():
                return CreateOrder(order=None, errors=["No valid products found"])
            
            # Calculate total amount if not provided
            if total_amount is None:
                total_amount = sum(product.price for product in products)
            
            form_data = {
                "customer": customer_id,
                "total_amount": total_amount,
            }
            
            form = OrderForm(data=form_data)
            if form.is_valid():
                order = form.save()
                order.products.set(products)
                return CreateOrder(order=order, errors=None)
            return CreateOrder(order=None, errors=[str(e) for e in form.errors.values()])
        except Customer.DoesNotExist:
            return CreateOrder(order=None, errors=["Customer not found"])
        except Exception as e:
            return CreateOrder(order=None, errors=[str(e)])


class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        pass

    updated_products = graphene.List(ProductType)
    success_message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info):
        try:
            # Query products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            if not low_stock_products.exists():
                return UpdateLowStockProducts(
                    updated_products=[],
                    success_message="No low-stock products found.",
                    errors=None
                )
            
            updated_products = []
            for product in low_stock_products:
                # Increment stock by 10 (simulating restocking)
                product.stock += 10
                product.save()
                updated_products.append(product)
            
            success_message = f"Successfully updated {len(updated_products)} low-stock products."
            
            return UpdateLowStockProducts(
                updated_products=updated_products,
                success_message=success_message,
                errors=None
            )
        except Exception as e:
            return UpdateLowStockProducts(
                updated_products=[],
                success_message=None,
                errors=[str(e)]
            )


# ------------------------
# Query + Mutation Root
# ------------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    hello = graphene.String(default_value="Hello, GraphQL!")

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
