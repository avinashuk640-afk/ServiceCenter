from django.urls import path
from . import views

urlpatterns = [
    # Authentication
     path('', views.home, name='home'),

    # auth / registration
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/servicecenter/', views.register_servicecenter, name='register_servicecenter'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # dashboards
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/servicecenter/', views.servicecenter_dashboard, name='servicecenter_dashboard'),

    # vehicles
    path('vehicles/', views.view_vehicle, name='view_vehicle'),
    path('vehicles/add/', views.add_vehicle, name='add_vehicle'),
    path('vehicles/edit/<int:pk>/', views.edit_vehicle, name='edit_vehicle'),
    path('vehicles/delete/<int:pk>/', views.delete_vehicle, name='delete_vehicle'),

    # bookings
    path('bookings/new/', views.booking_service, name='booking_service'),
    path('bookings/', views.view_bookings, name='view_bookings'),

    # service center operations
    path('servicecenter/staff/add/', views.add_staff, name='add_staff'),
    path('servicecenter/assign/<int:booking_id>/', views.assign_job, name='assign_job'),
    path('servicecenter/status/<int:pk>/update/', views.update_booking_status, name='update_booking_status'),
    path('servicecenter/invoice/<int:booking_id>/generate/', views.generate_invoice, name='generate_invoice'),

    # history & reminders
    path('history/', views.view_history, name='view_history'),
    path('history/record/', views.record_history, name='record_history'),
    path('history/record/<int:booking_id>/', views.record_history, name='record_history_booking'),



]
