from django import forms
from .models import Payment, House

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'house',
            'method_name',
            'provider',
            'account_details',
            'number',
            'recipient_name',
            'instructions',
            'status',
            'currency'
        ]
        widgets = {
            'house': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select House'}),
            'method_name': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Payment Method'}),
            'provider': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Provider'}),
            'account_details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter account details'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +255123456789 for mobile or 83767628727354829463 for banks'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipient name'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter additional instructions'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency (e.g., TZS)'}),
        }

    def __init__(self, *args, **kwargs):
        property_owner = kwargs.pop('property_owner', None)
        super().__init__(*args, **kwargs)
        if property_owner:
            self.fields['house'].queryset = House.objects.filter(owner=property_owner)


class PaymentUpdateForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'house',
            'method_name',
            'provider',
            'account_details',
            'number',
            'recipient_name',
            'instructions',
            'status',
            'currency'
        ]
        widgets = {
            'house': forms.Select(attrs={'class': 'form-control'}),
            'method_name': forms.Select(attrs={'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-control'}),
            'account_details': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter account details'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +255123456789'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter recipient name'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter additional instructions'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter currency (e.g., TZS)'}),
        }

    def __init__(self, *args, **kwargs):
        property_owner = kwargs.pop('property_owner', None)
        super().__init__(*args, **kwargs)
        if property_owner:
            self.fields['house'].queryset = House.objects.filter(owner=property_owner)

# locations/forms.py
from django import forms
from .models import Region

class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter region name...',
                'style': 'font-size: 1.2rem; border-radius:10px;'
            }),
        }

# locations/forms.py
from django import forms
from .models import District

class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter district name...',
                'style': 'font-size: 1.2rem; border-radius:10px;'
            }),
        }

# locations/forms.py
from django import forms
from .models import Ward

class WardForm(forms.ModelForm):
    class Meta:
        model = Ward
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter ward name...',
                'style': 'font-size: 1.2rem; border-radius:10px;',
            }),
        }

# locations/forms.py
from django import forms
from .models import Street

class StreetForm(forms.ModelForm):
    class Meta:
        model = Street
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter street name...',
                'style': 'font-size: 1.2rem; border-radius:10px;',
            }),
        }


from django import forms
from .models import HouseLocation

class HouseLocationForm(forms.ModelForm):
    class Meta:
        model = HouseLocation
        fields = ['latitude', 'longitude']  # Only latitude and longitude
        widgets = {
            'latitude': forms.TextInput(attrs={'readonly': 'readonly', 'size': '50', 'style': 'width:300px;'}),
            'longitude': forms.TextInput(attrs={'readonly': 'readonly', 'size': '50', 'style': 'width:300px;'}),
        }
