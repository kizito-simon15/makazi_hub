from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Base User Model
class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        default="@gmail.com",
        verbose_name=_("Email Address"),
    )
    phone_number1 = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r'^\+255\d{9}$',
                message="Phone number must be in the format +255XXXXXXXXX.",
            )
        ],
        verbose_name=_("Phone Number 1"),
    )
    phone_number2 = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+255\d{9}$',
                message="Phone number must be in the format +255XXXXXXXXX.",
            )
        ],
        verbose_name=_("Phone Number 2 (Optional)"),
    )
    middle_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Middle Name"),
    )

    def __str__(self):
        return self.username



# Property Owner Profile
class PropertyOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='property_owner')
    first_name = models.CharField(max_length=30, verbose_name=_("First Name"))
    middle_name = models.CharField(max_length=30, blank=True, verbose_name=_("Middle Name"))
    surname = models.CharField(max_length=30, verbose_name=_("Surname"))
    profile_picture = models.ImageField(
        upload_to="property_owner_profiles/",
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
    )
    is_allowed = models.BooleanField(default=False, verbose_name=_("Is Allowed"))

    def __str__(self):
        return f"{self.first_name} {self.surname}"

# Client Profile
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    first_name = models.CharField(max_length=30, verbose_name=_("First Name"))
    middle_name = models.CharField(max_length=30, blank=True, verbose_name=_("Middle Name"))
    surname = models.CharField(max_length=30, verbose_name=_("Surname"))
    profile_picture = models.ImageField(
        upload_to="client_profiles/",
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
    )
    email = models.EmailField(
        verbose_name=_("Email"),
        validators=[
            RegexValidator(
                regex=r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                message="Enter a valid email address.",
            )
        ],
    )
    phone_number = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                regex=r'^\+255\d{9}$',
                message="Phone number must be in the format +255XXXXXXXXX.",
            )
        ],
        verbose_name=_("Phone Number"),
    )
    is_allowed = models.BooleanField(default=False, verbose_name=_("Is Allowed"))

    def __str__(self):
        return self.user.username

