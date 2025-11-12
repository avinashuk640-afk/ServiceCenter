from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.db import transaction
from functools import wraps

from .models import (
    ServiceCenter, Customer, Vehicle, Staff,
    ServiceBooking, JobAssignment, ServiceStatus,
    Invoice, ServiceHistory, ReminderOffer
)
from .forms import (
    UserRegisterForm, CustomerForm, ServiceCenterForm,
    VehicleForm, StaffForm, ServiceBookingForm,
    JobAssignmentForm, ServiceStatusForm, InvoiceForm,
    ServiceHistoryForm, ReminderOfferForm
)


# ---------------------------
# Helper decorator: require servicecenter user
# ---------------------------
def require_servicecenter(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, 'servicecenter'):
            messages.error(request, "Access denied.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ------------------------------------------------------------
# 1. AUTHENTICATION VIEWS
# ------------------------------------------------------------
def home(request):
    return render(request, "home.html")


def register_customer(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            messages.success(request, "Customer account created successfully.")
            return redirect("login")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserRegisterForm()
        customer_form = CustomerForm()

    return render(request, "register_customer.html", {
        "user_form": user_form,
        "customer_form": customer_form,
    })


def register_servicecenter(request):
    if request.method == "POST":
        user_form = UserRegisterForm(request.POST)
        servicecenter_form = ServiceCenterForm(request.POST)
        if user_form.is_valid() and servicecenter_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data["password"])
            user.save()

            servicecenter = servicecenter_form.save(commit=False)
            servicecenter.user = user
            servicecenter.save()

            messages.success(request, "Service Center account created successfully.")
            return redirect("login")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserRegisterForm()
        servicecenter_form = ServiceCenterForm()

    return render(request, "register_servicecenter.html", {
        "user_form": user_form,
        "servicecenter_form": servicecenter_form,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")

            if hasattr(user, "customer"):
                return redirect("customer_dashboard")
            elif hasattr(user, "servicecenter"):
                return redirect("servicecenter_dashboard")
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")


# ------------------------------------------------------------
# 2. DASHBOARDS
# ------------------------------------------------------------
@login_required
def customer_dashboard(request):
    if not hasattr(request.user, "customer"):
        messages.error(request, "Access denied.")
        return redirect("home")

    customer = request.user.customer
    bookings = ServiceBooking.objects.filter(customer=customer).order_by('-booking_date')
    vehicles = Vehicle.objects.filter(customer=customer)

    context = {"customer": customer, "bookings": bookings, "vehicles": vehicles}
    return render(request, "customer_dashboard.html", context)


@login_required
@require_servicecenter
def servicecenter_dashboard(request):
    service_center = request.user.servicecenter
    bookings = ServiceBooking.objects.filter(service_center=service_center).order_by('-booking_date')
    staff = Staff.objects.filter(service_center=service_center)
    context = {"service_center": service_center, "bookings": bookings, "staff": staff}
    return render(request, "servicecenter_dashboard.html", context)


# ------------------------------------------------------------
# 3. VEHICLE MANAGEMENT (Customer)
# ------------------------------------------------------------
@login_required
def add_vehicle(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, "Only customers can add vehicles.")
        return redirect('home')

    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.customer = request.user.customer
            vehicle.save()
            messages.success(request, "Vehicle added successfully.")
            return redirect("view_vehicle")
    else:
        form = VehicleForm()
    return render(request, "vehicle_form.html", {"form": form})


@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, customer=request.user.customer)
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully.")
            return redirect("view_vehicle")
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, "vehicle_form.html", {"form": form})


@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, customer=request.user.customer)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully.")
    return redirect("view_vehicle")


@login_required
def view_vehicle(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, "Access denied.")
        return redirect('home')
    vehicles = Vehicle.objects.filter(customer=request.user.customer)
    return render(request, "vehicle_list.html", {"vehicles": vehicles})


# ------------------------------------------------------------
# 4. SERVICE BOOKING (Customer)
# ------------------------------------------------------------
@login_required
def booking_service(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, "Only customers can book services.")
        return redirect('home')

    if request.method == "POST":
        form = ServiceBookingForm(request.POST, user=request.user)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user.customer
            booking.status = "Pending"
            booking.save()
            messages.success(request, "Service booked successfully.")
            return redirect("view_bookings")
    else:
        form = ServiceBookingForm(user=request.user)
    return render(request, "booking_service.html", {"form": form})


@login_required
def view_bookings(request):
    if hasattr(request.user, "customer"):
        bookings = ServiceBooking.objects.filter(customer=request.user.customer)
    elif hasattr(request.user, "servicecenter"):
        bookings = ServiceBooking.objects.filter(service_center=request.user.servicecenter)
    else:
        bookings = []
    return render(request, "booking_list.html", {"bookings": bookings})


# ------------------------------------------------------------
# 5. SERVICE CENTER OPERATIONS
# ------------------------------------------------------------
@login_required
@require_servicecenter
def add_staff(request):
    if request.method == "POST":
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.service_center = request.user.servicecenter
            staff.save()
            messages.success(request, "Staff added successfully.")
            return redirect("servicecenter_dashboard")
    else:
        form = StaffForm()
    return render(request, "staff_form.html", {"form": form})


@login_required
@require_servicecenter
def assign_job(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    if booking.service_center != request.user.servicecenter:
        return HttpResponseForbidden("Not your booking.")
    if request.method == "POST":
        form = JobAssignmentForm(request.POST, booking=booking)
        if form.is_valid():
            job = form.save(commit=False)
            job.booking = booking
            job.save()
            messages.success(request, "Job assigned successfully.")
            return redirect("view_bookings")
    else:
        form = JobAssignmentForm(booking=booking)
    return render(request, "assign_job.html", {"form": form, "booking": booking})


@login_required
@require_servicecenter
def update_booking_status(request, pk):
    booking = get_object_or_404(ServiceBooking, id=pk)
    if booking.service_center != request.user.servicecenter:
        return HttpResponseForbidden("Not your booking.")
    if request.method == "POST":
        form = ServiceStatusForm(request.POST)
        if form.is_valid():
            status_obj = form.save(commit=False)
            status_obj.booking = booking
            status_obj.save()
            booking.status = status_obj.current_status
            booking.save()
            messages.success(request, "Service status updated successfully.")
            return redirect("view_bookings")
    else:
        form = ServiceStatusForm()
    return render(request, "update_status.html", {"form": form, "booking": booking})


# ------------------------------------------------------------
# 6. INVOICE AND HISTORY
# ------------------------------------------------------------
@login_required
@require_servicecenter
def generate_invoice(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    if booking.service_center != request.user.servicecenter:
        return HttpResponseForbidden("Not your booking.")

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.booking = booking
                invoice.service_center = request.user.servicecenter
                invoice.save()
                booking.status = 'Completed'
                booking.save()
            messages.success(request, "Invoice generated successfully.")
            return redirect("view_bookings")
    else:
        form = InvoiceForm()
    return render(request, "invoice.html", {"form": form, "booking": booking})


@login_required
def view_history(request):
    if hasattr(request.user, "customer"):
        histories = ServiceHistory.objects.filter(customer=request.user.customer).order_by('-service_date')
        return render(request, "history_list.html", {"histories": histories})
    else:
        messages.error(request, "Access denied.")
        return redirect("home")


@login_required
def record_history(request, booking_id=None):
    """
    Record service history after completion.
    booking_id optional — if present, ensure the booking belongs to the user or service center.
    """
    if request.method == "POST":
        form = ServiceHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            # assign customer/service_center based on current user or booking
            if hasattr(request.user, 'customer'):
                history.customer = request.user.customer
                # if booking provided ensure it matches
                if history.booking and history.booking.customer != request.user.customer:
                    messages.error(request, "Booking mismatch.")
                    return redirect("view_history")
            elif hasattr(request.user, 'servicecenter'):
                history.service_center = request.user.servicecenter
                if history.booking and history.booking.service_center != request.user.servicecenter:
                    messages.error(request, "Booking mismatch.")
                    return redirect("servicecenter_dashboard")
            history.save()
            messages.success(request, "Service history recorded successfully.")
            return redirect("view_history")
    else:
        form = ServiceHistoryForm()
    return render(request, "record_history.html", {"form": form})
