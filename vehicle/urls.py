from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/servicecenter/", views.register_servicecenter, name="register_servicecenter"),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Vehicle management
    path('vehicle/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicle/edit/<int:pk>/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicle/delete/<int:pk>/', views.delete_vehicle, name='delete_vehicle'),
    path('vehicle/view/', views.view_vehicle, name='view_vehicle'),

    # Booking management
    path('booking/service/', views.booking_service, name='booking_service'),
    path('bookings/view/', views.view_bookings, name='view_bookings'),
    path('booking/update/<int:pk>/', views.update_booking_status, name='update_booking_status'),

    # Service Center operations
    path('assign-job/<int:booking_id>/', views.assign_job, name='assign_job'),
    path('record-history/', views.record_history, name='record_history'),
    path('view-history/', views.view_history, name='view_history'),
    path('reminder-offer/', views.reminder_offer, name='reminder_offer'),

    # Invoice
    path('generate-invoice/<int:booking_id>/', views.generate_invoice, name='generate_invoice'),

    # Home page or dashboard
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/servicecenter/', views.servicecenter_dashboard, name='servicecenter_dashboard'),
]
