from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from accounts.models import Client
from owners.models import Room, BookingRule
from settings.models import Payment

class Booking(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="bookings_from_booking_app",  # Unique related_name
        verbose_name=_("Client"),
        help_text=_("The client who made this booking."),
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings_from_booking_app",
        verbose_name=_("Room"),
        help_text=_("The room being booked."),
    )
    booking_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("Booking Date"),
        help_text=_("The date on which the booking is created."),
    )
    payment_method = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
        verbose_name=_("Payment Method"),
        help_text=_("The payment method selected for this booking."),
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Total Amount"),
        help_text=_("The total amount to be paid for this booking."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this booking was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when this booking was last updated."),
    )

    def clean(self):
        house = self.room.house
        rule = BookingRule.objects.filter(house=house).first()
        if rule and self.payment_method and self.payment_method not in rule.payment_methods.all():
            raise ValidationError(_("Selected payment method is not allowed by the booking rules."))

    def __str__(self):
        return f"Booking by {self.client.user.username} for Room {self.room} on {self.booking_date}"

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")
        ordering = ["-created_at"]

from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import PropertyOwner
from owners.models import House

class Bill(models.Model):
    # Reference to the Property Owner
    property_owner = models.ForeignKey(
        PropertyOwner,
        on_delete=models.CASCADE,
        related_name="bills",
        verbose_name=_("Property Owner"),
        help_text=_("The property owner creating this bill."),
    )

    # Reference to the House
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="bills",
        verbose_name=_("House"),
        help_text=_("The house this bill is associated with."),
    )

    # Bill Details
    title = models.CharField(
        max_length=255,
        verbose_name=_("Bill Title"),
        help_text=_("Title of the bill (e.g., Water Bill, Maintenance Fee, etc.)."),
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Details or description of the bill."),
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Amount to be paid for this bill."),
    )
    reference_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Reference Number"),
        help_text=_("Optional payment number for the bill (e.g., account or invoice number)."),
    )
    validity_period = models.CharField(
        max_length=50,
        verbose_name=_("Validity Period"),
        help_text=_("The time this bill will be valid (e.g., 'One Month', 'Three Months')."),
    )

    # Audit Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this bill was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when this bill was last updated."),
    )

    def __str__(self):
        return f"{self.title} - {self.house.house_name} ({self.amount} TZS)"

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")
        ordering = ["-created_at"]


from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import Client
from owners.models import House

class HouseLike(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="liked_houses",
        verbose_name=_("Client"),
        help_text=_("The client who liked or disliked the house."),
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name=_("House"),
        help_text=_("The house that is liked or disliked."),
    )
    is_liked = models.BooleanField(
        default=False,
        verbose_name=_("Is Liked"),
        help_text=_("Indicates if the client liked this house."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this record was created."),
    )

    def __str__(self):
        status = "Liked" if self.is_liked else "Disliked"
        return f"{self.client.user.username} {status} {self.house.house_name}"

    class Meta:
        verbose_name = _("House Like")
        verbose_name_plural = _("House Likes")
        unique_together = ("client", "house")

# models.py (in the same app where House is defined, e.g. owners/models.py)
from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import Client
from owners.models import House

class HouseComment(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="house_comments",
        verbose_name=_("Client"),
        help_text=_("The client who made the comment."),
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("House"),
        help_text=_("The house this comment belongs to."),
    )
    comment_text = models.TextField(
        verbose_name=_("Comment Text"),
        help_text=_("The text of the comment."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The date and time when this comment was created."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
        help_text=_("The date and time when this comment was last updated."),
    )

    def __str__(self):
        snippet = self.comment_text[:50] + "..." if len(self.comment_text) > 50 else self.comment_text
        return f"{self.client.user.username} on {self.house.house_name}: {snippet}"

    class Meta:
        verbose_name = _("House Comment")
        verbose_name_plural = _("House Comments")
        ordering = ["-created_at"]


# After defining the model:
# python manage.py makemigrations
# python manage.py migrate
