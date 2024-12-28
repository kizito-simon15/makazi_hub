# owners/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import PropertyOwner

class House(models.Model):
    # Basic Details
    owner = models.ForeignKey(
        PropertyOwner,
        on_delete=models.CASCADE,
        related_name="houses",
        verbose_name=_("Property Owner"),
    )
    profile_picture = models.ImageField(
        upload_to="owner_profiles/",
        blank=True,
        null=True,
        verbose_name=_("Owner's Profile Picture"),
    )

    region = models.ForeignKey(
        "settings.Region",
        on_delete=models.CASCADE,
        related_name='houses',
        verbose_name=_("Region")
    )
    district = models.ForeignKey(
        "settings.District",
        on_delete=models.CASCADE,
        related_name='houses',
        verbose_name=_("District")
    )
    ward = models.ForeignKey(
        "settings.Ward",
        on_delete=models.CASCADE,
        related_name='houses',
        verbose_name=_("Ward")
    )
    street = models.ForeignKey(
        "settings.Street",
        on_delete=models.CASCADE,
        related_name='houses',
        verbose_name=_("Street")
    )

    house_number = models.CharField(max_length=50, verbose_name=_("House Number"))
    house_name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("House Name"),
    )
    number_of_rooms = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Number of Rooms"),
    )

    # Existing Additional Details
    furnishing_status = models.CharField(
        max_length=20,
        choices=[
            ("Furnished", "Furnished"),
            ("Semi-Furnished", "Semi-Furnished"),
            ("Unfurnished", "Unfurnished"),
        ],
        default="Unfurnished",
        verbose_name=_("Furnishing Status"),
    )
    amenities = models.TextField(
        blank=True,
        verbose_name=_("Amenities (e.g., Parking, Garden, Security)"),
    )
    utilities_included = models.TextField(
        blank=True,
        verbose_name=_("Utilities Included in Rent"),
    )
    house_type = models.CharField(
        max_length=50,
        choices=[
            ("Apartment", "Apartment"),
            ("Bungalow", "Bungalow"),
            ("Duplex", "Duplex"),
            ("Single-Family", "Single-Family"),
        ],
        default="Single-Family",
        verbose_name=_("House Type"),
    )
    flooring_and_finishing = models.TextField(
        blank=True, 
        verbose_name=_("Flooring and Finishing")
    )
    land_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Land Size (sq. m)"),
    )
    proximity_information = models.TextField(
        blank=True,
        verbose_name=_("Proximity Information (e.g., Schools, Hospitals)"),
    )
    rules_and_restrictions = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Rules and Restrictions")
    )
    contact_information = models.TextField(
        verbose_name=_("Contact Information")
    )
    insurance_details = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Insurance Details")
    )

    # New Boolean Fields
    is_furnished = models.BooleanField(default=False, verbose_name=_("Is the house furnished?"))
    has_swimming_pool = models.BooleanField(default=False, verbose_name=_("Has Swimming Pool?"))
    has_wifi = models.BooleanField(default=False, verbose_name=_("Has WiFi?"))
    has_backup_generator = models.BooleanField(default=False, verbose_name=_("Has Backup Generator?"))
    has_water_services = models.BooleanField(default=False, verbose_name=_("Has Water Services?"))
    is_smart_home = models.BooleanField(default=False, verbose_name=_("Is Smart Home?"))
    has_playground = models.BooleanField(default=False, verbose_name=_("Has Playground?"))
    has_parking = models.BooleanField(default=False, verbose_name=_("Has Parking?"))
    has_fence = models.BooleanField(default=False, verbose_name=_("Has Fence?"))
    has_cctv_cameras = models.BooleanField(default=False, verbose_name=_("Has CCTV Cameras?"))
    has_security_guard = models.BooleanField(default=False, verbose_name=_("Has Security Guard?"))
    has_grill_doors_and_windows = models.BooleanField(default=False, verbose_name=_("Has Grill Doors/Windows?"))
    is_modern_design = models.BooleanField(default=False, verbose_name=_("Is Modern Design?"))
    has_floors = models.BooleanField(default=False, verbose_name=_("Has Multiple Floors?"))
    has_outdoor_seating_area = models.BooleanField(default=False, verbose_name=_("Has Outdoor Seating Area?"))
    has_garden = models.BooleanField(default=False, verbose_name=_("Has Garden?"))
    has_entertaining_area = models.BooleanField(default=False, verbose_name=_("Has Entertaining Area?"))
    has_rooftop_for_resting = models.BooleanField(default=False, verbose_name=_("Has Rooftop for Resting?"))
    is_disability_friendly = models.BooleanField(default=False, verbose_name=_("Is Disability Friendly?"))
    is_near_pollution_sites = models.BooleanField(default=False, verbose_name=_("Is Near Pollution Sites?"))
    has_elevator = models.BooleanField(default=False, verbose_name=_("Has Elevator?"))
    is_near_schools = models.BooleanField(default=False, verbose_name=_("Is Near Schools?"))
    is_near_hospital = models.BooleanField(default=False, verbose_name=_("Is Near Hospital?"))
    is_near_ocean_river_lake = models.BooleanField(default=False, verbose_name=_("Is Near Ocean/River/Lake?"))
    is_in_quiet_area = models.BooleanField(default=False, verbose_name=_("Is in Quiet Area?"))
    is_near_commercial_center = models.BooleanField(default=False, verbose_name=_("Is Near Commercial Center?"))
    is_family_friendly = models.BooleanField(default=False, verbose_name=_("Is family friendly?"))
    is_new = models.BooleanField(default=False, verbose_name=_("Is the house new?"))
    is_pet_friendly = models.BooleanField(default=False, verbose_name=_("Is the house pet friendly?"))

    has_historical_significance = models.BooleanField(default=False, verbose_name=_("Has Historical Significance?"))
    was_stayed_by_celebrity = models.BooleanField(default=False, verbose_name=_("Was Stayed by Celebrity?"))
    allows_installment_payment = models.BooleanField(default=False, verbose_name=_("Allows Installment Payment?"))
    rent_includes_other_services = models.BooleanField(default=False, verbose_name=_("Rent Includes Other Services?"))
    is_short_term = models.BooleanField(default=False, verbose_name=_("Allows short term payments?"))

    # Trending Field
    is_trending = models.BooleanField(default=False, verbose_name=_("Is Trending?"))

    is_luxury = models.BooleanField(default=False, verbose_name=_("Is Luxury?"))

    has_discount = models.BooleanField(default=False, verbose_name=_("Has discount?"))

    has_scenic_view = models.BooleanField(default=False, verbose_name=_("Has scenic view?"))



    # NEW FIELDS
    is_rented_as_whole = models.BooleanField(
        default=False,
        verbose_name=_("Is your house rented as a whole?")
    )
    rent_for_whole_house = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Rent for the Whole House"),
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.house_name or ''} - {self.house_number}, {self.street}, {self.ward}, {self.district} - {self.region}"

class Room(models.Model):
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name=_("House"),
    )
    room_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_("Room Number"),
    )
    description = models.TextField(blank=True, verbose_name=_("Room Description"))
    rental_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Rental Price (Monthly/Yearly)"),
    )
    availability_status = models.CharField(
        max_length=20,
        choices=[("Available", "Available"), ("Occupied", "Occupied")],
        default="Available",
        verbose_name=_("Availability Status"),
    )

    # Removed room_video, photo_1...photo_5 fields

    def __str__(self):
        return f"Room {self.room_number} - {self.house}"


class HouseMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', _("Photo")),
        ('video', _("Video")),
    ]

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='medias',
        verbose_name=_("House")
    )
    media_type = models.CharField(
        max_length=5,
        choices=MEDIA_TYPE_CHOICES,
        default='photo',
        verbose_name=_("Media Type")
    )
    media_file = models.FileField(
        upload_to='house_medias/',
        verbose_name=_("House Media File")
    )

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.house.house_name or self.house.house_number}"


class RoomMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('photo', _("Photo")),
        ('video', _("Video")),
    ]

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='medias',
        verbose_name=_("Room")
    )
    media_type = models.CharField(
        max_length=5,
        choices=MEDIA_TYPE_CHOICES,
        default='photo',
        verbose_name=_("Media Type")
    )
    media_file = models.FileField(
        upload_to='room_medias/',
        verbose_name=_("Room Media File")
    )

    def __str__(self):
        return f"{self.get_media_type_display()} for Room {self.room.room_number} in {self.room.house}"


# owners/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings  # Import settings
from accounts.models import PropertyOwner
from .models import House

class Agent(models.Model):
    # Linking to User using settings.AUTH_USER_MODEL
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Updated line
        on_delete=models.CASCADE,
        related_name="agent_profile",
        verbose_name=_("User Account"),
    )

    # Linking to Property Owner
    property_owner = models.ForeignKey(
        PropertyOwner,
        on_delete=models.CASCADE,
        related_name="agents",
        verbose_name=_("Property Owner"),
    )

    # Personal Details
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name"),
    )
    last_name = models.CharField(
        max_length=30,
        verbose_name=_("Last Name"),
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        unique=True,
        help_text=_("Email address for the agent."),
    )
    phone_number = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r'^\+255\d{9}$',
                message=_("Phone number must be in the format +255XXXXXXXXX."),
            )
        ],
        verbose_name=_("Phone Number"),
        unique=True,
    )
    profile_picture = models.ImageField(
        upload_to="agent_profiles/",
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
    )

    # Assignment and Management
    assigned_houses = models.ManyToManyField(
        House,
        related_name="agents",
        verbose_name=_("Assigned Houses"),
        blank=True,
        help_text=_("Houses managed by this agent."),
    )

    # Agent Status
    class StatusChoices(models.TextChoices):
        ACTIVE = "Active", _("Active")
        INACTIVE = "Inactive", _("Inactive")
        SUSPENDED = "Suspended", _("Suspended")

    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        verbose_name=_("Status"),
    )

    # Financials
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Commission Rate"),
        help_text=_("Commission rate in percentage (e.g., 10.00 for 10%)."),
    )

    # Audit Fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    # Verification
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Is Verified"),
        help_text=_("Indicates whether the agent's identity has been verified."),
    )

    # String Representation
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"

    class Meta:
        verbose_name = _("Agent")
        verbose_name_plural = _("Agents")
        ordering = ["-created_at"]

from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import PropertyOwner
from .models import House
from settings.models import Payment  # Adjust the import path based on your project structure

class BookingRule(models.Model):
    owner = models.ForeignKey(
        PropertyOwner,
        on_delete=models.CASCADE,
        related_name="booking_rules",
        verbose_name=_("Property Owner"),
        help_text=_("The owner of the house these rules apply to."),
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="booking_rules",
        verbose_name=_("House"),
        help_text=_("The house these booking rules apply to."),
    )
    minimum_months_to_pay = models.PositiveIntegerField(
        verbose_name=_("Minimum Months to Pay"),
        help_text=_("The minimum number of months a client must pay for."),
        default=1,
    )
    payment_terms = models.TextField(
        verbose_name=_("Payment Terms"),
        help_text=_("Terms and conditions for payment."),
        blank=True,
        null=True,
    )
    payment_methods = models.ManyToManyField(
        Payment,
        blank=True,
        related_name="booking_rules",
        verbose_name=_("Payment Methods"),
        help_text=_("Select one or more payment methods that will be used during booking."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    def __str__(self):
        return f"Booking Rules for {self.house} (Owner: {self.owner})"

    class Meta:
        verbose_name = _("Booking Rule")
        verbose_name_plural = _("Booking Rules")
        ordering = ["-created_at"]


from django.db import models
from django.utils import timezone
from accounts.models import Client
from owners.models import Agent

class ClientMessage(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='messages_from_client',
        verbose_name="Client"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='messages_to_agent',
        verbose_name="Agent"
    )
    message_text = models.TextField(
        verbose_name="Message Text",
        help_text="The content of the client's message.",
        blank=True,
        null=True
    )
    audio = models.FileField(
        upload_to='messages/audio/',
        verbose_name="Audio Message",
        blank=True,
        null=True,
        help_text="Optional audio message file (e.g. .mp3, .wav)."
    )
    image = models.ImageField(
        upload_to='messages/images/',
        verbose_name="Image",
        blank=True,
        null=True,
        help_text="Optional image attachment."
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Is Read",
        help_text="Indicates whether the message has been read by the agent."
    )

    def __str__(self):
        client_name = f"{self.client.first_name} {self.client.last_name}".strip()
        agent_name = f"{self.agent.first_name} {self.agent.last_name}".strip()
        return f"Message from {client_name} to {agent_name}"

    class Meta:
        verbose_name = "Client Message"
        verbose_name_plural = "Client Messages"
        ordering = ["-created_at"]


class AgentReply(models.Model):
    client_message = models.ForeignKey(
        ClientMessage,
        on_delete=models.CASCADE,
        related_name='agent_replies',
        verbose_name="Client Message"
    )
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='replies_from_agent',
        verbose_name="Agent"
    )
    reply_text = models.TextField(
        verbose_name="Reply Text",
        help_text="The content of the agent's reply.",
        blank=True,
        null=True
    )
    audio = models.FileField(
        upload_to='replies/audio/',
        verbose_name="Reply Audio",
        blank=True,
        null=True,
        help_text="Optional audio reply (e.g. .mp3, .wav)."
    )
    image = models.ImageField(
        upload_to='replies/images/',
        verbose_name="Reply Image",
        blank=True,
        null=True,
        help_text="Optional image attachment."
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Is Read",
        help_text="Indicates whether the reply has been read by the client."
    )

    def __str__(self):
        agent_name = f"{self.agent.first_name} {self.agent.last_name}".strip()
        return f"Reply by {agent_name} to Message {self.client_message.id}"

    class Meta:
        verbose_name = "Agent Reply"
        verbose_name_plural = "Agent Replies"
        ordering = ["-created_at"]


from django.db import models
from django.utils import timezone
from owners.models import Agent, House
from owners.models import Room  # Assuming Room model is in owners.models

class HousePromotion(models.Model):
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='house_promotions',
        verbose_name="Agent",
        help_text="The agent who created this promotion."
    )
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='promotions',
        verbose_name="House",
        help_text="The house that is being promoted."
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        related_name='promotions',
        verbose_name="Room",
        blank=True,
        null=True,
        help_text="Optional: The specific room of the house being promoted. Leave blank to promote the entire house."
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Promotion Description",
        help_text="Words or a detailed description to promote the house or room."
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Created At",
        help_text="When this promotion was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
        help_text="When this promotion was last updated."
    )

    def __str__(self):
        target = f"House: {self.house.house_name}"
        if self.room:
            target += f", Room: {self.room.room_number}"
        return f"Promotion by {self.agent} for {target}"

    class Meta:
        verbose_name = "House Promotion"
        verbose_name_plural = "House Promotions"
        ordering = ["-created_at"]


class PromotionMedia(models.Model):
    PROMOTION_MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    promotion = models.ForeignKey(
        HousePromotion,
        on_delete=models.CASCADE,
        related_name='media_items',
        verbose_name="House Promotion",
        help_text="The promotion this media is associated with."
    )
    media_type = models.CharField(
        max_length=5,
        choices=PROMOTION_MEDIA_TYPE_CHOICES,
        default='image',
        verbose_name="Media Type",
        help_text="Type of media (image or video)."
    )
    file = models.FileField(
        upload_to='promotion_media/',
        verbose_name="Media File",
        help_text="Image or video file to promote the house/room."
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Caption",
        help_text="Optional caption or title for the media."
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Uploaded At",
        help_text="When this media was uploaded."
    )

    def __str__(self):
        return f"{self.get_media_type_display()} for {self.promotion}"

    class Meta:
        verbose_name = "Promotion Media"
        verbose_name_plural = "Promotion Media"
        ordering = ["-uploaded_at"]


# owners/models.py

from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from .models import House  # assuming House is in the same app; adjust import as needed

class HouseUpdate(models.Model):
    """
    Model to store updates (photo or video) for a given House.
    Think of this as a "status" or "story" post related to the house.
    """

    UPDATE_TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Video'),
    ]

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name="House",
    )
    update_type = models.CharField(
        max_length=10,
        choices=UPDATE_TYPE_CHOICES,
        default='photo',
        verbose_name="Update Type",
    )
    update_file = models.FileField(
        upload_to='house_updates/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'mp4', 'mov', 'avi'])],
        verbose_name="Update File (Photo/Video)",
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Caption (Optional)",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date/Time of Update",
    )

    def __str__(self):
        return f"{self.get_update_type_display()} update for {self.house} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
