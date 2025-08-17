import graphene
from graphene_django import DjangoObjectType
from django import forms
from crm.models import Customer, Product, Order


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
        fields = ("id", "name", "price")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "product", "quantity", "created_at")


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
        fields = ["customer", "product", "quantity"]

    def clean_quantity(self):
        qty = self.cleaned_data["quantity"]
        if qty <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        return qty


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
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, customer_id, product_id, quantity):
        form = OrderForm(
            data={
                "customer": customer_id,
                "product": product_id,
                "quantity": quantity,
            }
        )
        if form.is_valid():
            order = form.save()
            return CreateOrder(order=order, errors=None)
        return CreateOrder(order=None, errors=[str(e) for e in form.errors.values()])


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


schema = graphene.Schema(query=Query, mutation=Mutation)
