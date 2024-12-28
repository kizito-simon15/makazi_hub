# locations/forms.py
from django import forms
from settings.models import House, Region, District, Ward, Street

class HouseStep1Form(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    ward = forms.ModelChoiceField(
        queryset=Ward.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    street = forms.ModelChoiceField(
        queryset=Street.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = House
        fields = [
            "profile_picture",
            "region",
            "district",
            "ward",
            "street",
            "house_number",
            "house_name",
            "number_of_rooms",
        ]
        widgets = {
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "house_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter house number"}),
            "house_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter house name"}),
            "number_of_rooms": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

# owners/forms.py (or the appropriate forms file for step2)
from django import forms
from owners.models import House

class HouseStep2Form(forms.ModelForm):
    class Meta:
        model = House
        fields = [
            "furnishing_status",
            "amenities",
            "utilities_included",
            "house_type",
            "flooring_and_finishing",
            "land_size",
            "proximity_information",
            "rules_and_restrictions",
            "contact_information",
            "insurance_details",  # Added field
        ]
        widgets = {
            "furnishing_status": forms.Select(attrs={"class": "form-control"}),
            "amenities": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter amenities"}),
            "utilities_included": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter utilities"}),
            "house_type": forms.Select(attrs={"class": "form-control"}),
            "flooring_and_finishing": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter flooring and finishing details"}),
            "land_size": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01", "placeholder": "Enter land size in sq. m"}),
            "proximity_information": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter proximity information"}),
            "rules_and_restrictions": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter rules and restrictions"}),
            "contact_information": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter contact information"}),
            "insurance_details": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter insurance details"}),  # Added widget
        }

from django import forms
from .models import HouseMedia

class HouseMediaForm(forms.Form):
    MEDIA_TYPE_CHOICES = [
        ('audio', "Audio"),
        ('video', "Video"),
    ]

    media_type = forms.ChoiceField(
        choices=MEDIA_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='audio'
    )
    media_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        required=True
    )

from django import forms
from django.forms import formset_factory
from .models import Room

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'description', 'rental_price', 'availability_status']
        widgets = {
            'room_number': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1',
                    'placeholder': 'Enter room number (e.g., 101)'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter a brief description of the room (e.g., large, window facing garden)'
                }
            ),
            'rental_price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Enter rental price (e.g., 500.00)'
                }
            ),
            'availability_status': forms.Select(
                attrs={
                    'class': 'form-select',
                    'placeholder': 'Select availability status'
                }
            ),
        }

RoomFormSet = formset_factory(RoomForm, extra=0)  # 'extra' will be set in the view

# locations/forms.py
from django import forms
from .models import RoomMedia

class RoomMediaForm(forms.Form):
    MEDIA_TYPE_CHOICES = [
        ('audio', "Audio"),
        ('video', "Video"),
    ]

    media_type = forms.ChoiceField(choices=MEDIA_TYPE_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}), initial='audio')
    media_file = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}), required=True)

from django import forms
from .models import House

class HouseFilterForm(forms.Form):
    region = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    district = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    ward = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    street = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    house_number = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    furnishing_status = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    amenities = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    utilities_included = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    house_type = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    flooring_and_finishing = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    proximity_information = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    rules_and_restrictions = forms.ChoiceField(choices=[('', 'All')], required=False, widget=forms.Select(attrs={'class': 'form-select'}))

# owners/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Agent, House

User = get_user_model()  # Dynamically get the user model

class AgentRegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'aria-describedby': 'usernameHelp',
            'id': 'id_username'  # Explicit ID
        })
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'aria-describedby': 'passwordHelp',
            'id': 'id_password1'  # Explicit ID
        }),
        help_text='Your password must contain at least 8 characters and not be entirely numeric.'
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'aria-describedby': 'password2Help',
            'id': 'id_password2'  # Explicit ID
        }),
        help_text='Enter the same password as before, for verification.'
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        })
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address',
            'value': '@gmail.com'
        })
    )
    phone_number = forms.CharField(
        max_length=13,
        required=True,
        help_text='Required. Format: +255XXXXXXXXX.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+255XXXXXXXXX',
            'value': '+255'
        })
    )
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )
    assigned_houses = forms.ModelMultipleChoiceField(
        queryset=House.objects.none(),  # Will be set in the view
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        help_text='Select houses managed by this agent.'
    )
    status = forms.ChoiceField(
        choices=Agent.StatusChoices.choices,
        initial=Agent.StatusChoices.ACTIVE,
        required=True,
        help_text='Select the status of the agent.',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    commission_rate = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        help_text='Enter commission rate in percentage (e.g., 10.00 for 10%).',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter commission rate (optional)'
        })
    )
    is_verified = forms.BooleanField(
        required=False,
        initial=False,
        help_text='Check if the agent is verified.',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    class Meta:
        model = User
        fields = (
            'username',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'profile_picture',
            'assigned_houses',
            'status',
            'commission_rate',
            'is_verified',
        )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        property_owner = kwargs.pop('property_owner', None)
        super(AgentRegistrationForm, self).__init__(*args, **kwargs)
        if property_owner:
            self.fields['assigned_houses'].queryset = property_owner.houses.all()
        else:
            self.fields['assigned_houses'].queryset = House.objects.none()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Agent.objects.filter(email=email)
        if self.current_user:
            qs = qs.exclude(user=self.current_user)
        if qs.exists():
            raise forms.ValidationError("An agent with this email already exists.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        qs = Agent.objects.filter(phone_number=phone_number)
        if self.current_user:
            qs = qs.exclude(user=self.current_user)
        if qs.exists():
            raise forms.ValidationError("An agent with this phone number already exists.")
        return phone_number

from django import forms
from .models import BookingRule
from settings.models import Payment  # Adjust this import according to your project structure
from owners.models import House      # Ensure this is imported if not already

class BookingRuleForm(forms.ModelForm):
    payment_methods = forms.ModelMultipleChoiceField(
        queryset=Payment.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Payment Methods",
        help_text="Select the payment methods that will be available for booking."
    )

    class Meta:
        model = BookingRule
        fields = ['house', 'minimum_months_to_pay', 'payment_terms', 'payment_methods']
        widgets = {
            'house': forms.Select(attrs={'class': 'form-control'}),
            'minimum_months_to_pay': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter minimum months to pay'
            }),
            'payment_terms': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter payment terms and conditions'
            }),
        }

    def __init__(self, *args, **kwargs):
        property_owner = kwargs.pop('property_owner', None)
        super().__init__(*args, **kwargs)
        if property_owner:
            # Limit the house and payment methods to those owned by the logged-in property owner
            self.fields['house'].queryset = House.objects.filter(owner=property_owner)
            self.fields['payment_methods'].queryset = Payment.objects.filter(property_owner=property_owner)

# forms.py (in the same app)
from django import forms
from booking.models import HouseComment

class HouseCommentForm(forms.ModelForm):
    class Meta:
        model = HouseComment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your comment...'})
        }
        labels = {
            'comment_text': ""
        }


from django import forms
from .models import ClientMessage

class ClientMessageForm(forms.ModelForm):
    class Meta:
        model = ClientMessage
        fields = ['message_text', 'audio', 'image']
        widgets = {
            'message_text': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Type your message...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['audio'].required = False
        self.fields['image'].required = False
        self.fields['message_text'].required = False


from django import forms
from .models import AgentReply

class AgentReplyForm(forms.ModelForm):
    class Meta:
        model = AgentReply
        fields = ['reply_text', 'image', 'audio']
        widgets = {
            'reply_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your reply...'
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'audio': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'audio/*'}),
        }


from django import forms
from owners.models import Agent, House, Room
from .models import HousePromotion, PromotionMedia

from django import forms
from owners.models import Agent, House, Room

class PromotionStep1Form(forms.Form):
    house = forms.ModelChoiceField(
        queryset=House.objects.none(),
        widget=forms.RadioSelect,
        required=True,
        label="Select House to Promote"
    )
    promote_choice = forms.ChoiceField(
        choices=[('house', 'Promote Whole House'), ('room', 'Promote Specific Room')],
        widget=forms.RadioSelect,
        required=True,
        label="Promotion Target"
    )
    description_whole_house = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter promotion description for the whole house...'}),
        required=False,
        label="Whole House Description"
    )

    def __init__(self, *args, **kwargs):
        agent = kwargs.pop('agent', None)
        super().__init__(*args, **kwargs)
        if agent:
            self.fields['house'].queryset = House.objects.filter(agents=agent)

    def clean(self):
        cleaned_data = super().clean()
        promote_choice = cleaned_data.get('promote_choice')
        house = cleaned_data.get('house')

        if promote_choice == 'house':
            # Must provide a description for whole house
            if not cleaned_data.get('description_whole_house'):
                self.add_error('description_whole_house', "Description is required for promoting the whole house.")
        # If 'room' is chosen, we don't validate rooms here because we handle them after re-rendering
        return cleaned_data

class PromotionMediaForm(forms.ModelForm):
    media_type = forms.ChoiceField(
        choices=PromotionMedia.PROMOTION_MEDIA_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label="Media Type"
    )

    class Meta:
        model = PromotionMedia
        fields = ['media_type', 'file', 'caption']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'accept': 'image/*,video/*'}),
            'caption': forms.TextInput(attrs={'placeholder': 'Optional caption...'})
        }

from django.forms import formset_factory

PromotionMediaFormSet = formset_factory(PromotionMediaForm, extra=1, can_delete=False)

# owners/forms.py

from django import forms
from .models import House

class HouseAdditionalFeaturesStep1Form(forms.ModelForm):
    """
    Form for Step 1: Capturing the initial additional features
    about a house. This includes Boolean fields:
      - is_furnished
      - has_swimming_pool
      - has_wifi
      - has_backup_generator
      - has_water_services
      - is_smart_home
      - has_playground
      - has_parking
    """
    class Meta:
        model = House
        fields = [
            'is_furnished',
            'has_swimming_pool',
            'has_wifi',
            'has_backup_generator',
            'has_water_services',
            'is_smart_home',
            'has_playground',
            'has_parking',
        ]
        widgets = {
            'is_furnished': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_swimming_pool': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_wifi': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_backup_generator': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_water_services': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'is_smart_home': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_playground': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
            'has_parking': forms.CheckboxInput(attrs={
                'style': 'transform: scale(1.5); margin-right: 10px;',
            }),
        }


# owners/forms.py

from django import forms
from .models import House

class HouseAdditionalFeaturesStep2Form(forms.ModelForm):
    """
    Form for Step 2: Security, Design/Structure, Location, Historical Significance, etc.
    This includes:
      1) Security:
         - has_fence
         - has_cctv_cameras
         - has_security_guard
         - has_grill_doors_and_windows
      2) Design & Structure:
         - is_modern_design
         - has_floors
         - has_outdoor_seating_area
         - has_garden
         - has_entertaining_area
         - has_rooftop_for_resting
         - is_disability_friendly
         - has_elevator
      3) Location:
         - is_near_schools
         - is_near_hospital
         - is_near_ocean_river_lake
         - is_in_quiet_area
         - is_near_commercial_center
      4) Historical Significance:
         - has_historical_significance
         - was_stayed_by_celebrity
      5) Payment & Utilities:
         - allows_installment_payment
         - rent_includes_other_services
    """

    class Meta:
        model = House
        fields = [
            # Security
            'has_fence',
            'has_cctv_cameras',
            'has_security_guard',
            'has_grill_doors_and_windows',
            
            # Design & Structure
            'is_modern_design',
            'has_floors',
            'has_outdoor_seating_area',
            'has_garden',
            'has_entertaining_area',
            'has_rooftop_for_resting',
            'is_disability_friendly',
            'has_elevator',
            
            # Location
            'is_near_schools',
            'is_near_hospital',
            'is_near_ocean_river_lake',
            'is_in_quiet_area',
            'is_near_commercial_center',
            
            # Historical Significance
            'has_historical_significance',
            'was_stayed_by_celebrity',
            
            # Payment & Utilities
            'allows_installment_payment',
            'rent_includes_other_services',
            'is_family_friendly',
        ]
        widgets = {
            'has_fence': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_cctv_cameras': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_security_guard': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_grill_doors_and_windows': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_modern_design': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_floors': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_outdoor_seating_area': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_garden': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_entertaining_area': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_rooftop_for_resting': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_disability_friendly': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_elevator': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_near_schools': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_near_hospital': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_near_ocean_river_lake': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_in_quiet_area': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_near_commercial_center': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'has_historical_significance': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'was_stayed_by_celebrity': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'allows_installment_payment': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'rent_includes_other_services': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
            'is_family_friendly': forms.CheckboxInput(
                attrs={'style': 'transform: scale(1.5); margin-right: 10px;'}
            ),
        }

# owners/forms.py

from django import forms
from .models import House

class HouseRentAsWholeForm(forms.ModelForm):
    """
    Form for editing/creating the 'rented as whole' status
    and the total rent (if rented as a whole).
    """

    class Meta:
        model = House
        fields = [
            'is_rented_as_whole',
            'rent_for_whole_house',
        ]
        widgets = {
            'is_rented_as_whole': forms.CheckboxInput(
                attrs={
                    'style': 'transform: scale(1.3); margin-right: 10px;',
                    'class': 'form-check-input',  # or any custom class
                }
            ),
            'rent_for_whole_house': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter total rent (if applicable)',
                    'class': 'form-control form-control-lg rent-whole-input',  
                    'style': 'border-radius: 20px;'
                }
            ),
        }
        labels = {
            'is_rented_as_whole': 'Is your house rented as a whole?',
            'rent_for_whole_house': 'Rent for the Whole House',
        }


# owners/forms.py

from django import forms
from .models import HouseUpdate

class HouseUpdateForm(forms.ModelForm):
    """
    Form to create an update (photo/video) for a House.
    """
    class Meta:
        model = HouseUpdate
        fields = ['update_type', 'update_file', 'caption']
        widgets = {
            'update_type': forms.RadioSelect(
                attrs={
                    'style': 'transform: scale(1.3); margin-right: 10px;',
                }
            ),
            'update_file': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control form-control-lg',  # large input style
                    'style': 'transform: scale(1.2); margin-bottom: 1rem; border-radius: 10px;',
                }
            ),
            'caption': forms.Textarea(
                attrs={
                    'placeholder': 'Optional caption...',
                    'rows': 5,
                    'class': 'form-control form-control-lg',
                    'style': 'border-radius: 10px;',
                }
            ),
        }
        labels = {
            'update_type': 'Choose Update Type',
            'update_file': 'Upload Photo/Video',
            'caption': 'Caption (Optional)',
        }
