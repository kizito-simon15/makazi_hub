from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import PropertyOwner
from owners.models import House

class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = "Active", _("Active")
        INACTIVE = "Inactive", _("Inactive")
    
    class MethodChoices(models.TextChoices):
        BANK_TRANSFER = "Bank Transfer", _("Bank Transfer")
        MOBILE_MONEY = "Mobile Money", _("Mobile Money")
        CREDIT_CARD = "Credit Card", _("Credit Card")
        PAYPAL = "PayPal", _("PayPal")
        OTHER = "Other", _("Other")
    
    class ProviderChoices(models.TextChoices):
        MPESA = "M-Pesa", _("M-Pesa")
        YAS = "Yas", _("Yas")  # Updated from Tigo Pesa
        HALOPESA = "Halopesa", _("Halopesa")
        AIRTEL_MONEY = "Airtel Money", _("Airtel Money")
        AZAM_PESA = "Azam Pesa", _("Azam Pesa")
        CRDB_BANK = "CRDB Bank", _("CRDB Bank")
        NMB_BANK = "NMB Bank", _("NMB Bank")
        EXIM_BANK = "Exim Bank", _("Exim Bank")
        PAYPAL = "PayPal", _("PayPal")
        STRIPE = "Stripe", _("Stripe")
        OTHER = "Other", _("Other")

    property_owner = models.ForeignKey(
        PropertyOwner,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("Property Owner"),
        help_text=_("The property owner associated with this payment method."),
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("House"),
        null=True,
        blank=True,
        help_text=_("The house this payment method is specific to. Leave blank if it's for all houses."),
    )
    method_name = models.CharField(
        max_length=50,
        choices=MethodChoices.choices,
        verbose_name=_("Payment Method"),
        help_text=_("Select the type of payment method (e.g., Bank Transfer, Mobile Money)."),
    )
    provider = models.CharField(
        max_length=50,
        choices=ProviderChoices.choices,
        verbose_name=_("Payment Provider"),
        help_text=_("Select the payment provider (e.g., M-Pesa, Yas, CRDB Bank)."),
    )
    account_details = models.TextField(
        verbose_name=_("Account Details"),
        help_text=_("Provide account details for this payment method (e.g., account number, phone number)."),
    )

    # New fields
    number = models.CharField(
        max_length=20,
        verbose_name=_("Recipient Number"),
        help_text=_("Enter a valid mobile number that will receive the payment.")
    )
    recipient_name = models.CharField(
        max_length=100,
        verbose_name=_("Recipient Name"),
        help_text=_("The name that will be displayed during payments to the above number.")
    )

    instructions = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Instructions"),
        help_text=_("Additional instructions for using this payment method."),
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name=_("Status"),
        help_text=_("Set the status of this payment method (Active or Inactive)."),
    )
    currency = models.CharField(
        max_length=10,
        default="TZS",
        verbose_name=_("Currency"),
        help_text=_("The currency supported by this payment method (e.g., TZS, USD)."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this payment method was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when this payment method was last updated."),
    )

    def __str__(self):
        return f"{self.method_name} - {self.provider} ({self.property_owner})"

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from accounts.models import Client
from owners.models import Room

class Booking(models.Model):
    # Linking to Client and Room
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Client"),
        help_text=_("The client making the booking."),
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name=_("Room"),
        help_text=_("The room being booked."),
    )

    # Booking Details
    booking_date = models.DateTimeField(
        default=now,
        verbose_name=_("Booking Date"),
        help_text=_("The date and time when the booking was made."),
    )
    check_in_date = models.DateField(
        verbose_name=_("Check-In Date"),
        help_text=_("The date when the client plans to check in."),
    )
    check_out_date = models.DateField(
        verbose_name=_("Check-Out Date"),
        help_text=_("The date when the client plans to check out."),
    )
    payment_status = models.CharField(
        max_length=15,
        choices=[
            ("Pending", _("Pending")),
            ("Paid", _("Paid")),
            ("Failed", _("Failed")),
        ],
        default="Pending",
        verbose_name=_("Payment Status"),
        help_text=_("The status of the payment for this booking."),
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Total Cost"),
        help_text=_("The total cost for the booking."),
    )
    special_requests = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Special Requests"),
        help_text=_("Any special requests or instructions from the client."),
    )

    # Booking Status
    class BookingStatus(models.TextChoices):
        CONFIRMED = "Confirmed", _("Confirmed")
        CANCELLED = "Cancelled", _("Cancelled")
        PENDING = "Pending", _("Pending")

    status = models.CharField(
        max_length=10,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
        verbose_name=_("Booking Status"),
        help_text=_("The current status of the booking."),
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    def __str__(self):
        return f"Booking #{self.id} - {self.client} ({self.status})"

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-created_at"]

from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if another region with the same name exists (exclude this one if updating)
        if Region.objects.filter(name=self.name).exclude(pk=self.pk).exists():
            # Duplicate found, do not save
            return
        super().save(*args, **kwargs)

from django.db import models

class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.region.name})"

    def save(self, *args, **kwargs):
        # Check for another district with the same name in the same region
        if District.objects.filter(region=self.region, name=self.name).exclude(pk=self.pk).exists():
            # Duplicate found, do not save
            return
        super().save(*args, **kwargs)

from django.db import models
from .models import District

class Ward(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.district.name}, {self.district.region.name})"

    def save(self, *args, **kwargs):
        # Check for another ward with the same name in the same district
        if Ward.objects.filter(district=self.district, name=self.name).exclude(pk=self.pk).exists():
            # Duplicate found, do not save
            return
        super().save(*args, **kwargs)

from django.db import models
from .models import Ward

class Street(models.Model):
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name='streets')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.ward.name}, {self.ward.district.name}, {self.ward.district.region.name})"

    def save(self, *args, **kwargs):
        # Check for another street with the same name in the same ward
        if Street.objects.filter(ward=self.ward, name=self.name).exclude(pk=self.pk).exists():
            # Duplicate found, do not save
            return
        super().save(*args, **kwargs)


from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from owners.models import House
import requests

class HouseLocation(models.Model):
    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name='location',
        verbose_name="Related House"
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
        null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
        null=True, blank=True
    )
    altitude = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True, null=True,
        help_text="Altitude in meters."
    )

    def __str__(self):
        return f"Location of {self.house}"

    def save(self, *args, **kwargs):
        # If latitude and longitude are set and altitude not defined, fetch from Open-Elevation
        if self.latitude is not None and self.longitude is not None and self.altitude is None:
            self.altitude = self.get_altitude_from_open_elevation(float(self.latitude), float(self.longitude))
        super().save(*args, **kwargs)

    def get_altitude_from_open_elevation(self, lat, lng):
        """Fetch altitude from Open-Elevation API."""
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            # Expecting data['results'][0]['elevation']
            if 'results' in data and len(data['results']) > 0:
                elevation = data['results'][0]['elevation']
                return round(elevation, 2)
            return None
        except (requests.RequestException, KeyError, ValueError):
            # If there's an error or unexpected response, return None or handle it as needed
            return None
