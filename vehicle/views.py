from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

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

# ------------------------------------------------------------
# 🧩 1. AUTHENTICATION VIEWS
# ------------------------------------------------------------

def home(request):
    """Landing Page"""
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
    """Login for all users with role-based redirection"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "login.html")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(user)
            login(request, user)
            messages.success(request, f"Welcome, {user.username}!")

            # 🔹 Redirect based on user role
            if hasattr(user, "customer"):
                return redirect("customer_dashboard")
            elif hasattr(user, "servicecenter"):
                return redirect("servicecenter_dashboard")
            else:
                # fallback if neither role (e.g., admin)
                return redirect("login")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")
    

@login_required
def logout_view(request):
    """Logout the current user"""
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("login")


# ------------------------------------------------------------
# 🏠 2. DASHBOARD
# ------------------------------------------------------------

@login_required
def customer_dashboard(request):
    """Dashboard for Customers"""
    customer = request.user.customer  # linked via OneToOneField

    # ✅ Use 'booking_date' instead of 'date'
    bookings = ServiceBooking.objects.filter(customer=customer).order_by('-booking_date')

    context = {
        "customer": customer,
        "bookings": bookings,
    }
    return render(request, "customer_dashboard.html", context)



@login_required
def servicecenter_dashboard(request):
    """Dashboard for Service Centers"""
    try:
        service_center = request.user.servicecenter
    except ServiceCenter.DoesNotExist:
        messages.error(request, "Service Center profile not found.")
        return redirect("dashboard")

    bookings = ServiceBooking.objects.filter(service_center=service_center).order_by('-booking_date')

    context = {
        "service_center": service_center,
        "bookings": bookings,
    }
    return render(request, "servicecenter_dashboard.html", context)



# ------------------------------------------------------------
# 🚗 3. VEHICLE MANAGEMENT (Customer)
# ------------------------------------------------------------

@login_required
def add_vehicle(request):
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
    """List all vehicles of the logged-in customer"""
    vehicles = Vehicle.objects.filter(customer=request.user.customer)
    return render(request, "vehicle_list.html", {"vehicles": vehicles})


# ------------------------------------------------------------
# 🧰 4. SERVICE BOOKING (Customer)
# ------------------------------------------------------------

@login_required
def booking_service(request):
    if request.method == "POST":
        form = ServiceBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user.customer
            booking.status = "Pending"
            booking.save()
            messages.success(request, "Service booked successfully.")
            return redirect("view_bookings")
    else:
        form = ServiceBookingForm()
    return render(request, "booking_service.html", {"form": form})


@login_required
def view_bookings(request):
    """Customer or Service Center can view their bookings"""
    if hasattr(request.user, "customer"):
        bookings = ServiceBooking.objects.filter(customer=request.user.customer)
    elif hasattr(request.user, "servicecenter"):
        bookings = ServiceBooking.objects.filter(service_center=request.user.servicecenter)
    else:
        bookings = []
    return render(request, "booking_list.html", {"bookings": bookings})


# ------------------------------------------------------------
# 🧑‍🔧 5. SERVICE CENTER OPERATIONS
# ------------------------------------------------------------

@login_required
def assign_job(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    if request.method == "POST":
        form = JobAssignmentForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.booking = booking
            job.save()
            messages.success(request, "Job assigned successfully.")
            return redirect("view_bookings")
    else:
        form = JobAssignmentForm(initial={"booking": booking})
    return render(request, "assign_job.html", {"form": form})


@login_required
def update_booking_status(request, pk):
    booking = get_object_or_404(ServiceBooking, id=pk)
    if request.method == "POST":
        form = ServiceStatusForm(request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.booking = booking
            status.save()
            booking.status = status.current_status
            booking.save()
            messages.success(request, "Service status updated successfully.")
            return redirect("view_bookings")
    else:
        form = ServiceStatusForm()
    return render(request, "update_status.html", {"form": form})


# ------------------------------------------------------------
# 💰 6. INVOICE AND HISTORY
# ------------------------------------------------------------

@login_required
def generate_invoice(request, booking_id):
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.booking = booking
            invoice.service_center = booking.service_center
            invoice.save()
            messages.success(request, "Invoice generated successfully.")
            return redirect("view_bookings")
    else:
        form = InvoiceForm(initial={"booking": booking})
    return render(request, "invoice.html", {"form": form})


@login_required
def view_history(request):
    """View service history for customers"""
    if hasattr(request.user, "customer"):
        histories = ServiceHistory.objects.filter(customer=request.user.customer)
        return render(request, "history_list.html", {"histories": histories})
    else:
        messages.error(request, "Access denied.")
        return redirect("dashboard")


# ------------------------------------------------------------
# 📩 7. REMINDERS & OFFERS
# ------------------------------------------------------------

@login_required
def reminder_offer(request):
    """Service center sends reminder or offer"""
    if hasattr(request.user, "servicecenter"):
        if request.method == "POST":
            form = ReminderOfferForm(request.POST)
            if form.is_valid():
                reminder = form.save(commit=False)
                reminder.service_center = request.user.servicecenter
                reminder.save()
                messages.success(request, "Reminder/Offer sent successfully.")
                return redirect("view_bookings")
        else:
            form = ReminderOfferForm()
        return render(request, "reminder_offer.html", {"form": form})
    else:
        messages.error(request, "Access denied.")
        return redirect("dashboard")


@login_required
def record_history(request):
    """Record service history after completion"""
    if request.method == "POST":
        form = ServiceHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            # Automatically assign customer and service center if available
            if hasattr(request.user, "customer"):
                history.customer = request.user.customer
            elif hasattr(request.user, "servicecenter"):
                history.service_center = request.user.servicecenter
            history.save()
            messages.success(request, "Service history recorded successfully.")
            return redirect("view_history")
    else:
        form = ServiceHistoryForm()
    return render(request, "record_history.html", {"form": form})
