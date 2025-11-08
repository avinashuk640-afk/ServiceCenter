from django import forms
from django.contrib.auth.models import User
from .models import (
    ServiceCenter,
    Customer,
    Vehicle,
    Staff,
    ServiceBooking,
    JobAssignment,
    ServiceStatus,
    Invoice,
    ServiceHistory,
    ReminderOffer
)


# ---------------------------
# 1. User Registration Forms
# ---------------------------

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "address", "phone", "email"]
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}


class ServiceCenterForm(forms.ModelForm):
    class Meta:
        model = ServiceCenter
        fields = ["name", "address", "phone", "email"]
        widgets = {"address": forms.Textarea(attrs={"rows": 2})}

# ---------------------------
# 2. Vehicle Form
# ---------------------------

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'customer', 'vehicle_number', 'model',
            'manufacturer', 'year', 'fuel_type'
        ]


# ---------------------------
# 3. Staff Form
# ---------------------------

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['service_center', 'name', 'role', 'phone', 'email']


# ---------------------------
# 4. Service Booking Form
# ---------------------------

class ServiceBookingForm(forms.ModelForm):
    class Meta:
        model = ServiceBooking
        fields = [
            'customer', 'vehicle', 'service_center',
            'scheduled_date', 'description', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
        }


# ---------------------------
# 5. Job Assignment Form
# ---------------------------

class JobAssignmentForm(forms.ModelForm):
    class Meta:
        model = JobAssignment
        fields = ['booking', 'staff', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


# ---------------------------
# 6. Service Status Form
# ---------------------------

class ServiceStatusForm(forms.ModelForm):
    class Meta:
        model = ServiceStatus
        fields = ['booking', 'current_status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
        }


# ---------------------------
# 7. Invoice Form
# ---------------------------

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['booking', 'service_center', 'total_amount', 'payment_status']


# ---------------------------
# 8. Service History Form
# ---------------------------

class ServiceHistoryForm(forms.ModelForm):
    class Meta:
        model = ServiceHistory
        fields = ['customer', 'vehicle', 'booking', 'service_date', 'details', 'cost']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 3}),
        }


# ---------------------------
# 9. Reminder / Offer Form
# ---------------------------

class ReminderOfferForm(forms.ModelForm):
    class Meta:
        model = ReminderOffer
        fields = ['service_center', 'customer', 'title', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }
