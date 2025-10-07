from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Contacts(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contact')
    full_name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    age = models.IntegerField(validators=[MinValueValidator(1)])
    home_address = models.TextField()

    def __str__(self):
        return self.full_name

class Premises(models.Model):
    area = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    machines_count = models.IntegerField(validators=[MinValueValidator(0)])
    type = models.CharField(max_length=100)

    def __str__(self):
        return f"Premises {self.id} - {self.type}"

class Employees(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    premises = models.ForeignKey(Premises, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return f"{self.position} - {self.id}"

class Access(models.Model):
    access_level = models.CharField(max_length=50)
    employee_position = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    employee = models.OneToOneField(Employees, on_delete=models.CASCADE, related_name='access')

    def __str__(self):
        return f"Access for {self.employee}"

class Service(models.Model):
    package = models.CharField(max_length=255)
    material = models.CharField(max_length=100)
    premises = models.ForeignKey(Premises, on_delete=models.CASCADE, related_name='services')
    type = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.package

class DeliveryStatus(models.Model):
    status = models.CharField(max_length=50)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.status

class Order(models.Model):
    client_name = models.CharField(max_length=255)
    order_date = models.DateField()
    print_date = models.DateField()
    service_package = models.CharField(max_length=255)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.TextField()
    client = models.ForeignKey(Contacts, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='orders')
    premises = models.ForeignKey(Premises, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f"Order {self.id} by {self.client_name}"

class Delivery(models.Model):
    packaging_type = models.CharField(max_length=50)
    volume = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    weight = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    address = models.TextField()
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    employee = models.ForeignKey(Employees, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    status = models.ForeignKey(DeliveryStatus, on_delete=models.CASCADE, related_name='deliveries')

    def __str__(self):
        return f"Delivery for Order {self.order.id}"

class Review(models.Model):
    review_text = models.TextField()
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')

    def __str__(self):
        return f"Review for Order {self.order.id}"