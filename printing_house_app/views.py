from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from .models import Employees, Delivery, Order, Review, Contacts, Service, Premises, DeliveryStatus
from .serializers import EmployeesSerializer, DeliverySerializer, OrderSerializer, ReviewSerializer
from django import forms

def has_role(user, role):
    if user.is_superuser:
        return role in ['owner', 'manager']  # Superuser has owner/manager access

    if role == 'client':
        return hasattr(user, 'contact')
    elif role == 'courier' or role == 'manager':
        if hasattr(user, 'employee'):
            position = user.employee.position.lower()
            if role == 'manager' and 'manager' in position:
                return True
            elif role == 'courier' and 'courier' in position:
                return True
    elif role == 'owner':
        return user.is_superuser

    return False

class AverageSalaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (has_role(request.user, 'manager') or has_role(request.user, 'owner')):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        avg_salary = Employees.objects.aggregate(avg_salary=Avg('salary'))['avg_salary']
        return Response({'average_salary': avg_salary})

class DeliveredDeliveriesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliverySerializer

    def get_queryset(self):
        if has_role(self.request.user, 'courier'):
            return Delivery.objects.filter(status__status='Delivered', employee__user=self.request.user)
        elif has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner'):
            return Delivery.objects.filter(status__status='Delivered')
        return Delivery.objects.none()

class OrdersByServiceView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if not (has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner')):
            return Order.objects.none()
        service_id = self.kwargs['service_id']
        return Order.objects.filter(service_id=service_id)

class DeliveriesByCourierView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliverySerializer

    def get_queryset(self):
        employee_id = self.kwargs['employee_id']
        if has_role(self.request.user, 'courier'):
            # Only their own
            try:
                user_employee = self.request.user.employee
                if user_employee.id == employee_id:
                    return Delivery.objects.filter(employee_id=employee_id)
            except:
                return Delivery.objects.none()
        elif has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner'):
            return Delivery.objects.filter(employee_id=employee_id)
        return Delivery.objects.none()

class ReviewCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        if has_role(self.request.user, 'client'):
            # Only for their own orders
            order = serializer.validated_data['order']
            if order.client.user != self.request.user:
                raise serializers.ValidationError("Can only review your own orders")
        elif not (has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner')):
            raise serializers.ValidationError("Permission denied")
        serializer.save()

class CompletedOrdersView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if not (has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner')):
            return Order.objects.none()
        return Order.objects.filter(delivery__status__status='Delivered')

class ReviewsReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not (has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner')):
            return Review.objects.none()
        return Review.objects.select_related('order').all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for review in queryset:
            data.append({
                'review_id': review.id,
                'order_id': review.order.id,
                'review_text': review.review_text,
                'client_name': review.order.client_name,
                'order_date': review.order.order_date
            })
        return Response(data)

class DeliveriesReportView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not (has_role(self.request.user, 'manager') or has_role(self.request.user, 'owner')):
            return Delivery.objects.none()
        return Delivery.objects.select_related('order', 'employee', 'status').all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for delivery in queryset:
            data.append({
                'delivery_id': delivery.id,
                'order_id': delivery.order.id,
                'packaging_type': delivery.packaging_type,
                'volume': delivery.volume,
                'weight': delivery.weight,
                'address': delivery.address,
                'status': delivery.status.status,
                'employee_name': delivery.employee.user.get_full_name() if delivery.employee else None
            })
        return Response(data)

# UI Views

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'printing_house_app/dashboard.html')

@login_required
def my_orders(request):
    if has_role(request.user, 'client'):
        orders = Order.objects.filter(client__user=request.user)
    else:
        orders = Order.objects.none()
    return render(request, 'printing_house_app/orders.html', {'orders': orders, 'title': 'My Orders'})

@login_required
def all_orders(request):
    if has_role(request.user, 'manager') or has_role(request.user, 'owner'):
        orders = Order.objects.all()
    else:
        orders = Order.objects.none()
    return render(request, 'printing_house_app/orders.html', {'orders': orders, 'title': 'All Orders'})

@login_required
def my_deliveries(request):
    if has_role(request.user, 'courier'):
        deliveries = Delivery.objects.filter(employee__user=request.user)
    else:
        deliveries = Delivery.objects.none()
    return render(request, 'printing_house_app/deliveries.html', {'deliveries': deliveries, 'title': 'My Deliveries'})

@login_required
def average_salary_view(request):
    if has_role(request.user, 'manager') or has_role(request.user, 'owner'):
        avg_salary = Employees.objects.aggregate(avg_salary=Avg('salary'))['avg_salary'] or 0
        return render(request, 'printing_house_app/average_salary.html', {'average_salary': avg_salary})
    else:
        messages.error(request, 'Permission denied')
        return redirect('dashboard')

@login_required
def completed_orders_view(request):
    if has_role(request.user, 'manager') or has_role(request.user, 'owner'):
        orders = Order.objects.filter(delivery__status__status='Delivered')
        return render(request, 'printing_house_app/orders.html', {'orders': orders, 'title': 'Completed Orders'})
    else:
        messages.error(request, 'Permission denied')
        return redirect('dashboard')

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client_name', 'order_date', 'print_date', 'service_package', 'quantity', 'amount', 'address', 'client', 'service', 'premises']

@login_required
def create_order(request):
    if not (has_role(request.user, 'manager') or has_role(request.user, 'owner')):
        messages.error(request, 'Permission denied')
        return redirect('dashboard')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            # Create delivery
            delivery_status = DeliveryStatus.objects.filter(status='Pending').first()
            if not delivery_status:
                delivery_status = DeliveryStatus.objects.create(status='Pending', count=0)
            Delivery.objects.create(
                order=order,
                packaging_type='Standard',
                volume=1.0,
                weight=1.0,
                address=order.address,
                status=delivery_status
            )
            messages.success(request, 'Order created successfully')
            return redirect('all_orders')
    else:
        form = OrderForm()
    return render(request, 'printing_house_app/create_order.html', {'form': form})

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']

@login_required
def create_review(request):
    if not has_role(request.user, 'client'):
        messages.error(request, 'Only clients can leave reviews')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        order_id = request.POST.get('order')
        order = get_object_or_404(Order, id=order_id, client__user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.save()
            messages.success(request, 'Review submitted successfully')
            return redirect('my_orders')
    else:
        form = ReviewForm()
        orders = Order.objects.filter(client__user=request.user, review__isnull=True)
    return render(request, 'printing_house_app/create_review.html', {'form': form, 'orders': orders})

@login_required
def reviews_report(request):
    if not (has_role(request.user, 'manager') or has_role(request.user, 'owner')):
        messages.error(request, 'Permission denied')
        return redirect('dashboard')
    reviews = Review.objects.select_related('order').all()
    return render(request, 'printing_house_app/reviews_report.html', {'reviews': reviews})

@login_required
def deliveries_report(request):
    if not (has_role(request.user, 'manager') or has_role(request.user, 'owner')):
        messages.error(request, 'Permission denied')
        return redirect('dashboard')
    deliveries = Delivery.objects.select_related('order', 'employee', 'status').all()
    return render(request, 'printing_house_app/deliveries_report.html', {'deliveries': deliveries})