from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PropertyOwner, Client

class PropertyOwnerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        }),
        label="First Name",
    )
    middle_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Middle Name',
        }),
        label="Middle Name",
    )
    surname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Surname',
        }),
        label="Surname",
    )
    email = forms.EmailField(
        initial="@gmail.com",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        }),
        label="Email",
    )
    phone_number1 = forms.CharField(
        max_length=13,
        initial="+255",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+255XXXXXXXXX',
        }),
        label="Phone Number 1",
    )
    phone_number2 = forms.CharField(
        max_length=13,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+255XXXXXXXXX (Optional)',
        }),
        label="Phone Number 2",
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        }),
        label="Username",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        }),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'surname', 'email', 'phone_number1', 'phone_number2', 'username', 'password1', 'password2']

class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
        }),
        label="First Name",
    )
    middle_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Middle Name',
        }),
        label="Middle Name",
    )
    surname = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Surname',
        }),
        label="Surname",
    )
    email = forms.EmailField(
        initial="@gmail.com",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
        }),
        label="Email",
    )
    phone_number = forms.CharField(
        max_length=13,
        initial="+255",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+255XXXXXXXXX',
        }),
        label="Phone Number",
    )
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
        }),
        label="Username",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
        }),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
        }),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ['first_name', 'middle_name', 'surname', 'email', 'phone_number', 'username', 'password1', 'password2']


from django import forms
from .models import PropertyOwner, Client

class PropertyOwnerProfilePictureForm(forms.ModelForm):
    class Meta:
        model = PropertyOwner
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ClientProfilePictureForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

from django import forms
from .models import Client

class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'first_name',
            'middle_name',
            'surname',
            'email',
            'phone_number',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter middle name'}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter surname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
        }
