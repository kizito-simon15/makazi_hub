from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import PaymentForm
from .models import Payment

@login_required
def create_payment_view(request):
    # Ensure only property owners can access this view
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")
    
    property_owner = request.user.property_owner

    # Create a formset for Payment
    PaymentFormSet = modelformset_factory(
        Payment,
        form=PaymentForm,
        extra=1,  # Number of empty forms to show by default
        can_delete=True  # Allow deletion of forms
    )

    if request.method == "POST":
        formset = PaymentFormSet(request.POST, queryset=Payment.objects.none())
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:  # Ensure the form is not empty
                    payment = form.save(commit=False)
                    payment.property_owner = property_owner
                    payment.save()
            return redirect('payments_list')  # Redirect to the payment list view
    else:
        formset = PaymentFormSet(queryset=Payment.objects.none())

    return render(request, 'settings/create_payment.html', {
        'formset': formset,
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House, Payment

@login_required
def payments_list_view(request):
    # Ensure that only property owners can access this view
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner

    # Retrieve all houses and their payments for the logged-in property owner
    houses_with_payments = []
    houses = House.objects.filter(owner=property_owner)

    for house in houses:
        payments = Payment.objects.filter(house=house)
        houses_with_payments.append({
            'house': house,
            'payments': payments
        })

    return render(request, 'settings/payments_list.html', {'houses_with_payments': houses_with_payments})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import PaymentUpdateForm
from .models import Payment

@login_required
def update_payment_view(request, payment_id):
    # Ensure the logged-in user is the property owner
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner
    payment = get_object_or_404(Payment, id=payment_id, property_owner=property_owner)

    if request.method == "POST":
        form = PaymentUpdateForm(request.POST, instance=payment, property_owner=property_owner)
        if form.is_valid():
            form.save()
            return redirect('payments_list')  # Redirect to the payment list page
    else:
        form = PaymentUpdateForm(instance=payment, property_owner=property_owner)

    return render(request, 'settings/update_payment.html', {'form': form, 'payment': payment})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Payment

@login_required
def delete_payment_view(request, payment_id):
    # Ensure the logged-in user is the property owner
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner
    payment = get_object_or_404(Payment, id=payment_id, property_owner=property_owner)

    if request.method == "POST":
        payment.delete()
        return redirect('payments_list')  # Redirect to the payment list after deletion

    return render(request, 'settings/confirm_delete_payment.html', {'payment': payment})

# locations/views.py
from django.shortcuts import render, redirect
from .forms import RegionForm
from .models import Region

def create_region_view(request):
    # Complete list of Tanzania's regions
    all_regions = [
        'Arusha', 'Dar es Salaam', 'Dodoma', 'Geita', 'Iringa', 'Kagera', 'Katavi', 'Kigoma', 
        'Kilimanjaro', 'Lindi', 'Manyara', 'Mara', 'Mbeya', 'Morogoro', 'Mtwara', 'Mwanza', 
        'Njombe', 'Pwani', 'Rukwa', 'Ruvuma', 'Shinyanga', 'Simiyu', 'Singida', 'Songwe', 'Tabora', 
        'Tanga', 'Mjini Magharibi (Urban West)', 'Kusini Unguja (South Unguja)', 'Kaskazini Unguja (North Unguja)', 
        'Kaskazini Pemba (North Pemba)', 'Kusini Pemba (South Pemba)'
    ]

    if request.method == 'POST':
        form = RegionForm(request.POST)
        if form.is_valid():
            # Save the user-created region
            user_region = form.save()

            # After saving the user's region, create all other regions automatically
            # get_or_create ensures we don't duplicate regions
            for region_name in all_regions:
                Region.objects.get_or_create(name=region_name)

            return redirect('region_list')
    else:
        form = RegionForm()

    return render(request, 'settings/create_region.html', {'form': form})

# locations/views.py
from django.shortcuts import render
from .models import Region

def region_list_view(request):
    # Prefetch all related districts, wards, and streets for efficiency
    regions = Region.objects.all().order_by('name') \
        .prefetch_related('districts__wards__streets')
    return render(request, 'settings/region_list.html', {'regions': regions})

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Region

def delete_region_view(request, pk):
    region = get_object_or_404(Region, pk=pk)
    if request.method == 'POST':
        # If POST, user confirmed deletion
        region.delete()
        return redirect('region_list')
    else:
        # If GET, show confirmation template
        return render(request, 'settings/delete_region.html', {'region': region})

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, District
from .forms import RegionForm, DistrictForm

# Updated list of regions and their districts including Arusha
TANZANIA_REGIONS_DISTRICTS = {
    'Arusha': [
        'Arusha City',
        'Arumeru',
        'Karatu',
        'Longido',
        'Monduli',
        'Ngorongoro',
    ],
    'Dar es Salaam': [
        'Ilala',
        'Kinondoni',
        'Temeke',
        'Ubungo',
    ],
    'Dodoma': [
        'Chamwino',
        'Chemba',
        'Dodoma Urban',
        'Dodoma Rural',
        'Kongwa',
        'Mpwapwa',
    ],
    'Geita': [
        'Chato',
        'Geita Urban',
        'Kagera Geita',
        'Mbogwe',
    ],
    'Iringa': [
        'Iringa Urban',
        'Iringa Rural',
        'Kilolo',
        'Mufindi',
    ],
    'Kagera': [
        'Biharamulo',
        'Bukoba Urban',
        'Kagera Urban',
        'Muleba',
        'Ngara Kagera',
    ],
    'Katavi': [
        'Mpanda Urban',
        'Mpanda Rural',
        'Katavi Urban',
        'Katavi Rural',
    ],
    'Kigoma': [
        'Buhigwe',
        'Kigoma Urban',
        'Kibondo',
        'Kakonko',
        'Kasulu',
        'Kasulu Rural',
        'Kigoma Rural',
        'Uvinza',
    ],
    'Kilimanjaro': [
        'Hai',
        'Moshi Urban',
        'Moshi Rural',
        'Siha',
        'Rombo',
        'Same',
    ],
    'Lindi': [
        'Kilwa Masoko',
        'Lindi Urban',
        'Lindi Rural',
        'Nachingwea',
        'Ruangwa',
        'Rufiji',
    ],
    'Manyara': [
        'Babati Urban',
        'Babati Rural',
        'Hanang',
        'Kiteto',
        'Mbulu',
        'Simanjiro',
    ],
    'Mara': [
        'Bunda',
        'Butiama',
        'Musoma Urban',
        'Musoma Rural',
        'Rorya',
    ],
    'Mbeya': [
        'Busokelo',
        'Mbarali',
        'Mbozi',
        'Rungwe',
        'Sumbawanga Urban',
        'Sumbawanga Rural',
        'Songwe Urban',
        'Songwe Rural',
        'Mbeya Urban',
        'Mbangala',
        'Kyela',
    ],
    'Morogoro': [
        'Kilombero',
        'Kilosa',
        'Morogoro Urban',
        'Morogoro Rural',
        'Mvomero',
    ],
    'Mtwara': [
        'Masasi',
        'Mtwara Urban',
        'Mtwara Rural',
        'Nanyumbu',
    ],
    'Mwanza': [
        'Bukombe',
        'Ilemela',
        'Kwimba',
        'Magu',
        'Misungwi',
        'Nyamagana',
        'Sengerema',
        'Serengeti',
        'Itilima',
        'Nyamagana',  # Nyamagana listed twice in original data, consider removing duplicate
        'Mwanza Urban',
    ],
    'Njombe': [
        'Njombe Urban',
        'Njombe Rural',
        'Makete',
        'Ludewa',
    ],
    'Pwani': [
        'Kibaha Urban',
        'Kibaha Rural',
        'Kisarawe',
        'Mkuranga',
    ],
    'Rukwa': [
        'Kalambo',
        'Kasulu',
        'Nkasi',
        'Sumbawanga',
    ],
    'Ruvuma': [
        'Nyasa',
        'Songea Urban',
        'Songea Rural',
        'Nguvumali',
    ],
    'Shinyanga': [
        'Kahama Urban',
        'Kahama Rural',
        'Kishapu',
        'Misingwi',
        'Nyangao',
        'Busega',
    ],
    'Simiyu': [
        'Itilima',
        'Maswa',
        'Simiyu Urban',
        'Busega',
    ],
    'Singida': [
        'Iramba',
        'Mkalama',
        'Singida Urban',
        'Singida Rural',
    ],
    'Songwe': [
        'Ludewa',
        'Mbeya Urban',
        'Momba',
        'Mpanda Urban',
        'Mpanda Rural',
        'Songwe Urban',
        'Songwe Rural',
    ],
    'Tabora': [
        'Igunga',
        'Kaliua',
        'Nzega Urban',
        'Nzega Rural',
        'Tabora Urban',
        'Tabora Rural',
    ],
    'Tanga': [
        'Bumbuli',
        'Handeni Urban',
        'Handeni Rural',
        'Kilindi',
        'Korogwe Urban',
        'Korogwe Rural',
        'Muheza',
        'Mkinga',
        'Pangani',
        'Tanga Urban',
        'Tanga Rural',
    ],
    'Mjini Magharibi (Urban West)': [
        'Stone Town',
    ],
    'Kusini Unguja (South Unguja)': [
        'Kinyasini',
        'Kitangaza',
    ],
    'Kaskazini Unguja (North Unguja)': [
        'Kaskazini A',
        'Kaskazini B',
    ],
    'Kaskazini Pemba (North Pemba)': [
        'Wete',
    ],
    'Kusini Pemba (South Pemba)': [
        'Chake Chake',
        'Ras Fumba',
    ],
}

def create_district_view(request, region_pk):
    region = get_object_or_404(Region, pk=region_pk)

    if request.method == 'POST':
        form = DistrictForm(request.POST)
        if form.is_valid():
            # Save the user-created district
            district = form.save(commit=False)
            district.region = region
            district.save()

            # Auto-create all districts for all regions, including Arusha now
            for reg_name, districts in TANZANIA_REGIONS_DISTRICTS.items():
                # get_or_create each region
                reg, created = Region.objects.get_or_create(name=reg_name)
                for dist_name in districts:
                    District.objects.get_or_create(region=reg, name=dist_name)

            return redirect('region_list')
    else:
        form = DistrictForm()

    return render(request, 'settings/create_district.html', {'form': form, 'region': region})

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, District, Ward
from .forms import WardForm

def create_ward_view(request, region_pk, district_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)

    if request.method == 'POST':
        form = WardForm(request.POST)
        if form.is_valid():
            ward = form.save(commit=False)
            ward.district = district
            ward.save()
            return redirect('region_list')
    else:
        form = WardForm()

    return render(request, 'settings/create_ward.html', {
        'form': form,
        'region': region,
        'district': district,
    })

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, District, Ward, Street
from .forms import StreetForm

def create_street_view(request, region_pk, district_pk, ward_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    ward = get_object_or_404(Ward, pk=ward_pk, district=district)

    if request.method == 'POST':
        form = StreetForm(request.POST)
        if form.is_valid():
            street = form.save(commit=False)
            street.ward = ward
            street.save()
            # Redirect to a list of streets in this ward
            return redirect('region_list')
    else:
        form = StreetForm()

    return render(request, 'settings/create_street.html', {
        'form': form,
        'region': region,
        'district': district,
        'ward': ward,
    })


# locations/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, District, Ward, Street
from .forms import RegionForm, DistrictForm, WardForm, StreetForm

def update_region_view(request, region_pk):
    region = get_object_or_404(Region, pk=region_pk)
    if request.method == 'POST':
        form = RegionForm(request.POST, instance=region)
        if form.is_valid():
            form.save()
            return redirect('region_list')
    else:
        form = RegionForm(instance=region)
    return render(request, 'settings/update_region.html', {'form': form, 'region': region})

def update_district_view(request, region_pk, district_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    if request.method == 'POST':
        form = DistrictForm(request.POST, instance=district)
        if form.is_valid():
            form.save()
            return redirect('region_list')  # Or redirect to a district list if you have one
    else:
        form = DistrictForm(instance=district)
    return render(request, 'settings/update_district.html', {'form': form, 'region': region, 'district': district})

def update_ward_view(request, region_pk, district_pk, ward_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    ward = get_object_or_404(Ward, pk=ward_pk, district=district)
    if request.method == 'POST':
        form = WardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            return redirect('region_list')  # Or a ward list page if it exists
    else:
        form = WardForm(instance=ward)
    return render(request, 'settings/update_ward.html', {'form': form, 'region': region, 'district': district, 'ward': ward})

def update_street_view(request, region_pk, district_pk, ward_pk, street_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    ward = get_object_or_404(Ward, pk=ward_pk, district=district)
    street = get_object_or_404(Street, pk=street_pk, ward=ward)
    if request.method == 'POST':
        form = StreetForm(request.POST, instance=street)
        if form.is_valid():
            form.save()
            return redirect('region_list')  # Or a street list page if it exists
    else:
        form = StreetForm(instance=street)
    return render(request, 'settings/update_street.html', {'form': form, 'region': region, 'district': district, 'ward': ward, 'street': street})

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Region, District, Ward, Street
from .forms import RegionForm, DistrictForm, WardForm, StreetForm

def delete_region_view(request, region_pk):
    region = get_object_or_404(Region, pk=region_pk)
    if request.method == 'POST':
        region.delete()
        return redirect('region_list')
    return render(request, 'settings/delete_region.html', {'region': region})

def delete_district_view(request, region_pk, district_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    if request.method == 'POST':
        district.delete()
        return redirect('region_list')  # or a district listing page if you have one
    return render(request, 'settings/delete_district.html', {'region': region, 'district': district})

def delete_ward_view(request, region_pk, district_pk, ward_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    ward = get_object_or_404(Ward, pk=ward_pk, district=district)
    if request.method == 'POST':
        ward.delete()
        return redirect('region_list')  # or a ward listing page if you have one
    return render(request, 'settings/delete_ward.html', {'region': region, 'district': district, 'ward': ward})

def delete_street_view(request, region_pk, district_pk, ward_pk, street_pk):
    region = get_object_or_404(Region, pk=region_pk)
    district = get_object_or_404(District, pk=district_pk, region=region)
    ward = get_object_or_404(Ward, pk=ward_pk, district=district)
    street = get_object_or_404(Street, pk=street_pk, ward=ward)
    if request.method == 'POST':
        street.delete()
        return redirect('region_list')  # or a street listing page if you have one
    return render(request, 'settings/delete_street.html', {'region': region, 'district': district, 'ward': ward, 'street': street})

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.core.exceptions import PermissionDenied
from owners.models import House
from .forms import HouseLocationForm
from .models import HouseLocation


class HouseLocationCreateView(View):
    template_name = "settings/location_form.html"

    def dispatch(self, request, house_id, *args, **kwargs):
        # Ensure user is authenticated and has a property_owner profile
        if not request.user.is_authenticated or not hasattr(request.user, 'property_owner'):
            raise PermissionDenied("Only property owners can access this view.")

        house = get_object_or_404(House, id=house_id)
        # Ensure that this house belongs to the current property owner
        if house.owner != request.user.property_owner:
            raise PermissionDenied("You do not have permission to access this house.")

        self.house = house  # Store the house for later use
        return super().dispatch(request, house_id, *args, **kwargs)

    def get(self, request, house_id):
        print("DEBUG: Entered GET method of HouseLocationCreateView")
        house = self.house
        print(f"DEBUG: Retrieved House with ID {house_id} -> {house}")

        if hasattr(house, 'location'):
            print("DEBUG: House already has a location, loading form with instance")
            form = HouseLocationForm(instance=house.location)
        else:
            print("DEBUG: House has no location yet, loading empty form")
            form = HouseLocationForm()

        return render(request, self.template_name, {"form": form, "house": house})

    def post(self, request, house_id):
        print("DEBUG: Entered POST method of HouseLocationCreateView")
        house = self.house
        print(f"DEBUG: Retrieved House with ID {house_id} -> {house}")

        if hasattr(house, 'location'):
            print("DEBUG: Editing existing location for this house")
            form = HouseLocationForm(request.POST, instance=house.location)
        else:
            print("DEBUG: Creating new location for this house")
            form = HouseLocationForm(request.POST)

        if form.is_valid():
            print("DEBUG: Form is valid, attempting to save location")
            location = form.save(commit=False)
            location.house = house
            location.save()
            print(f"DEBUG: Location saved successfully with ID {location.id} for house {house}")
            return redirect('house_location_detail', house_id=house.id)
        else:
            print("ERROR: Form is not valid")
            print("ERROR: Form errors:", form.errors)

        return render(request, self.template_name, {"form": form, "house": house})


class HouseLocationDetailView(View):
    template_name = "settings/location_detail.html"

    def dispatch(self, request, house_id, *args, **kwargs):
        # Ensure user is authenticated and has a property_owner profile
        if not request.user.is_authenticated or not hasattr(request.user, 'property_owner'):
            raise PermissionDenied("Only property owners can access this view.")

        house = get_object_or_404(House, id=house_id)
        # Ensure that this house belongs to the current property owner
        if house.owner != request.user.property_owner:
            raise PermissionDenied("You do not have permission to access this house.")

        self.house = house
        return super().dispatch(request, house_id, *args, **kwargs)

    def get(self, request, house_id):
        house = self.house
        location = getattr(house, 'location', None)  # May be None if no location yet

        context = {
            "house": house,
            "location": location,
        }
        return render(request, self.template_name, context)

from django.shortcuts import render
from django.urls import reverse
from owners.models import House

def houses_map_view(request):
    houses = House.objects.filter(location__isnull=False)

    houses_data = []
    for house in houses:
        loc = house.location
        detail_url = reverse('house_full_details', args=[house.id])  # Generate detail URL
        houses_data.append({
            'id': house.id,
            'name': house.house_name or "Unnamed House",
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude),
            'profile_picture': house.profile_picture.url if house.profile_picture else None,
            'detail_url': detail_url,  # Include the generated URL
        })

    context = {
        'houses_data': houses_data
    }
    return render(request, 'settings/houses_map.html', context)
