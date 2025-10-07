from django.contrib import admin
from .models import Contacts, Premises, Employees, Access, Service, DeliveryStatus, Order, Delivery, Review

admin.site.register(Contacts)
admin.site.register(Premises)
admin.site.register(Employees)
admin.site.register(Access)
admin.site.register(Service)
admin.site.register(DeliveryStatus)
admin.site.register(Order)
admin.site.register(Delivery)
admin.site.register(Review)