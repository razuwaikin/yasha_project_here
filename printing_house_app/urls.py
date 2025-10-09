from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # API endpoints
    path('api/employees/average-salary/', views.AverageSalaryView.as_view(), name='api-average-salary'),
    path('api/deliveries/delivered/', views.DeliveredDeliveriesView.as_view(), name='api-delivered-deliveries'),
    path('api/orders/by-service/<int:service_id>/', views.OrdersByServiceView.as_view(), name='api-orders-by-service'),
    path('api/deliveries/by-courier/<int:employee_id>/', views.DeliveriesByCourierView.as_view(), name='api-deliveries-by-courier'),
    path('api/reviews/', views.ReviewCreateView.as_view(), name='api-create-review'),
    path('api/orders/completed/', views.CompletedOrdersView.as_view(), name='api-completed-orders'),
    path('api/reports/reviews/', views.ReviewsReportView.as_view(), name='api-reviews-report'),
    path('api/reports/deliveries/', views.DeliveriesReportView.as_view(), name='api-deliveries-report'),

    # UI views
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/', views.all_orders, name='all_orders'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('deliveries/', views.my_deliveries, name='my_deliveries'),
    path('average-salary/', views.average_salary_view, name='average_salary'),
    path('completed-orders/', views.completed_orders_view, name='completed_orders'),
    path('create-order/', views.create_order, name='create_order'),
    path('create-review/', views.create_review, name='create_review'),
    path('reports/reviews/', views.reviews_report, name='reviews_report'),
    path('reports/deliveries/', views.deliveries_report, name='deliveries_report'),
]