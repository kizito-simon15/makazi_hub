from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from django.contrib import messages
from owners.models import Room, BookingRule
from settings.models import Payment
from accounts.models import Client
from .models import Booking
from django import forms

class CreateBookingForm(forms.Form):
    payment_method = forms.ModelChoiceField(
        queryset=Payment.objects.none(),
        label="Select Payment Method",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        payment_methods = kwargs.pop('payment_methods', Payment.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].queryset = payment_methods


from django import forms
from .models import Bill
from owners.models import House

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ["title", "description", "amount", "validity_period", "reference_number"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter bill title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Enter description"}),
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount"}),
            "validity_period": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter validity period"}),
            "reference_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter reference number (if applicable)"}),
        }

class SelectHouseForm(forms.Form):
    house = forms.ModelChoiceField(
        queryset=House.objects.none(),
        widget=forms.RadioSelect(),
        label="Select a House",
    )

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["house"].queryset = House.objects.filter(owner=owner)


