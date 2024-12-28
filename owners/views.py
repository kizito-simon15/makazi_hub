from django.shortcuts import render, redirect, get_object_or_404
from .forms import (
    HouseStep1Form,
    HouseStep2Form,
    RoomForm,
)
from .models import House, Room
from django import forms


from django.shortcuts import render, redirect, get_object_or_404
from .forms import HouseStep1Form
from .models import House

# owners/views.py
from django.shortcuts import render, redirect, get_object_or_404
from settings.models import Region, District, Ward, Street
from .models import House
from .forms import HouseStep1Form
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from settings.models import Region, District, Ward, Street
from .models import House
from .forms import HouseStep1Form
import json

# owners/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import House, Room, HouseMedia, RoomMedia
from .forms import HouseStep1Form, HouseStep2Form, RoomForm
from django.forms import formset_factory

from settings.models import Region, District, Ward, Street
import json

@login_required
def create_house_step1_view(request, house_id=None):
    print("=== create_house_step1_view CALLED ===")
    print(f"Request method: {request.method}")
    print(f"House ID: {house_id}")

    house = None
    if house_id:
        # Updating existing house
        house = get_object_or_404(House, id=house_id)
        if house.owner != request.user.property_owner:
            return HttpResponseForbidden("You do not have permission to edit this house.")
        print(f"Loaded existing house: ID={house.id}, Name={house.house_name} (Update Mode)")
        # Set is_creating to False since we're updating
        request.session['is_creating'] = False
    else:
        # Creating new house
        print("No existing house loaded (Create Mode).")
        # Set is_creating to True since we're creating
        request.session['is_creating'] = True

    if request.method == "POST":
        print("POST request at Step 1. POST data:", request.POST)
        form = HouseStep1Form(request.POST, request.FILES, instance=house)

        # Dynamically set querysets for dependent fields if needed
        region_id = request.POST.get('region')
        district_id = request.POST.get('district')
        ward_id = request.POST.get('ward')

        if region_id:
            form.fields['district'].queryset = District.objects.filter(region_id=region_id)
        else:
            form.fields['district'].queryset = District.objects.none()

        if district_id:
            form.fields['ward'].queryset = Ward.objects.filter(district_id=district_id)
        else:
            form.fields['ward'].queryset = Ward.objects.none()

        if ward_id:
            form.fields['street'].queryset = Street.objects.filter(ward_id=ward_id)
        else:
            form.fields['street'].queryset = Street.objects.none()

        if form.is_valid():
            house = form.save(commit=False)
            if request.session.get('is_creating', True):
                # Assign the owner only if creating new house
                house.owner = request.user.property_owner

            house.save()
            print(f"House saved at Step 1 with ID={house.id}.")

            if request.session.get('is_creating', True):
                # Creating mode: proceed to step 2
                print("Creating mode at Step 1: redirecting to step 2")
                return redirect("create_house_step2", house_id=house.id)
            else:
                # Updating mode: redirect to house_list
                print("Updating mode at Step 1: redirecting to house_list")
                return redirect("house_list")
        else:
            print("Form invalid at Step 1. Errors:", form.errors.as_data())
    else:
        print("GET request at Step 1.")
        form = HouseStep1Form(instance=house)
        # If house exists, set dependent querysets based on existing data
        if house:
            form.fields['district'].queryset = District.objects.filter(region=house.region)
            form.fields['ward'].queryset = Ward.objects.filter(district=house.district)
            form.fields['street'].queryset = Street.objects.filter(ward=house.ward)

    # Preload data for dependent fields as JSON
    regions = list(Region.objects.values("id", "name"))
    districts = list(District.objects.values("id", "name", "region_id"))
    wards = list(Ward.objects.values("id", "name", "district_id"))
    streets = list(Street.objects.values("id", "name", "ward_id"))

    return render(request, "owners/create_house_step1.html", {
        "form": form,
        "house": house,
        "regions_json": json.dumps(regions),
        "districts_json": json.dumps(districts),
        "wards_json": json.dumps(wards),
        "streets_json": json.dumps(streets),
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from owners.models import House, HouseMedia, Room
from owners.forms import HouseStep2Form, RoomForm
from django.forms import formset_factory

# ------------------- CREATION VIEWS ------------------- #
@login_required
def create_house_step2_view(request, house_id=None):
    print("=== create_house_step2_view CALLED ===")
    if house_id is not None:
        # If house_id is provided during creation step2, something's off.
        # Normally, creation step2 should have no house_id yet (unless step1 just created a house)
        house = get_object_or_404(House, id=house_id)
        if house.owner != request.user.property_owner:
            return HttpResponseForbidden("You do not have permission to edit this house.")
    else:
        house = None

    # We are in creation mode
    request.session['is_creating'] = True

    if request.method == "POST":
        form = HouseStep2Form(request.POST, instance=house)
        if form.is_valid():
            saved_house = form.save()
            print("Creating mode at Step 2: redirecting to step 3")
            return redirect("create_house_step3", house_id=saved_house.id)
        else:
            print("Form invalid at Step 2 (creating). Errors:", form.errors.as_data())
    else:
        form = HouseStep2Form(instance=house)

    return render(request, "owners/create_house_step2.html", {"form": form, "house": house})

@login_required
def create_house_step3_view(request, house_id):
    print("=== create_house_step3_view CALLED ===")
    house = get_object_or_404(House, id=house_id)
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("You do not have permission.")

    # We are in creation mode
    request.session['is_creating'] = True

    if request.method == "POST":
        media_indices = {key.split('_')[-1] for key in request.POST if key.startswith('media_type_')}
        saved_any = False
        for idx in media_indices:
            m_type = request.POST.get(f'media_type_{idx}')
            m_file = request.FILES.get(f'media_file_{idx}')
            if m_type and m_file:
                HouseMedia.objects.create(house=house, media_type=m_type, media_file=m_file)
                saved_any = True
        if saved_any:
            print("Media saved at Step 3.")

        print("Creating mode at Step 3: redirecting to step 4")
        return redirect("create_house_step4", house_id=house.id)
    else:
        print("GET request at Step 3 (creating). Rendering template.")

    return render(request, "owners/create_house_step3.html", {"house": house})

@login_required
def create_house_step4_view(request, house_id):
    print("=== create_house_step4_view CALLED ===")
    house = get_object_or_404(House, id=house_id)
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("No permission.")

    # We are in creation mode
    request.session['is_creating'] = True

    number_of_rooms = house.number_of_rooms
    RoomFormSet = formset_factory(RoomForm, extra=number_of_rooms)

    if request.method == "POST":
        formset = RoomFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    Room.objects.create(
                        house=house,
                        room_number=form.cleaned_data['room_number'],
                        description=form.cleaned_data['description'],
                        rental_price=form.cleaned_data['rental_price'],
                        availability_status=form.cleaned_data['availability_status'],
                    )
            print("Creating mode at Step 4: redirecting to step 5")
            return redirect("create_house_step5", house_id=house.id)
        else:
            print("Formset invalid at Step 4 (creating).")
    else:
        formset = RoomFormSet()

    return render(request, "owners/create_house_step4.html", {"house": house, "formset": formset})


# ------------------- UPDATING VIEWS ------------------- #
@login_required
def update_house_step2_view(request, house_id):
    print("=== update_house_step2_view CALLED ===")
    house = get_object_or_404(House, id=house_id)
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("You do not have permission.")

    # We are in updating mode (no is_creating set)
    if request.method == "POST":
        form = HouseStep2Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            print("Updating mode at Step 2: redirecting to house_list")
            return redirect("house_list")
        else:
            print("Form invalid at Step 2 (updating). Errors:", form.errors.as_data())
    else:
        form = HouseStep2Form(instance=house)

    return render(request, "owners/create_house_step2.html", {"form": form, "house": house})

@login_required
def update_house_step3_view(request, house_id):
    print("=== update_house_step3_view CALLED ===")
    house = get_object_or_404(House, id=house_id)
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("No permission.")

    # Updating mode
    if request.method == "POST":
        media_indices = {key.split('_')[-1] for key in request.POST if key.startswith('media_type_')}
        saved_any = False
        for idx in media_indices:
            m_type = request.POST.get(f'media_type_{idx}')
            m_file = request.FILES.get(f'media_file_{idx}')
            if m_type and m_file:
                HouseMedia.objects.create(house=house, media_type=m_type, media_file=m_file)
                saved_any = True

        if saved_any:
            print("Media saved at Step 3 (updating).")

        print("Updating mode at Step 3: redirecting to house_list")
        return redirect("house_list")
    else:
        print("GET request at Step 3 (updating). Rendering template.")

    return render(request, "owners/create_house_step3.html", {"house": house})

@login_required
def update_house_step4_view(request, house_id):
    print("=== update_house_step4_view CALLED ===")
    house = get_object_or_404(House, id=house_id)
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("No permission.")

    # Updating mode
    number_of_rooms = house.number_of_rooms
    RoomFormSet = formset_factory(RoomForm, extra=number_of_rooms)

    if request.method == "POST":
        formset = RoomFormSet(request.POST)
        if formset.is_valid():
            # Save room data
            # First delete all existing rooms or handle logic as needed
            # For simplicity, just add new ones
            for form in formset:
                if form.cleaned_data:
                    Room.objects.create(
                        house=house,
                        room_number=form.cleaned_data['room_number'],
                        description=form.cleaned_data['description'],
                        rental_price=form.cleaned_data['rental_price'],
                        availability_status=form.cleaned_data['availability_status'],
                    )
            print("Updating mode at Step 4: redirecting to house_list")
            return redirect("house_list")
        else:
            print("Formset invalid at Step 4 (updating).")
    else:
        formset = RoomFormSet()

    return render(request, "owners/create_house_step4.html", {"house": house, "formset": formset})


# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import House, RoomMedia

@login_required
def create_house_step5_view(request, house_id):
    print("=== create_house_step5_view CALLED ===")
    print(f"Request method: {request.method}")
    print(f"House ID: {house_id}")

    house = get_object_or_404(House, id=house_id)

    # Ensure this house belongs to the logged-in property owner
    if house.owner != request.user.property_owner:
        return HttpResponseForbidden("You do not have permission to edit this house.")

    rooms = house.rooms.all().order_by('room_number')

    if request.method == "POST":
        # Handle room media uploads
        for room in rooms:
            prefix_type = f'media_type_{room.id}_'
            prefix_file = f'media_file_{room.id}_'
            indices = set()

            for key in request.POST.keys():
                if key.startswith(prefix_type):
                    idx = key.split('_')[-1]
                    indices.add(idx)

            saved_any = False
            for idx in indices:
                m_type_key = f'media_type_{room.id}_{idx}'
                m_file_key = f'media_file_{room.id}_{idx}'
                m_type = request.POST.get(m_type_key)
                m_file = request.FILES.get(m_file_key)

                if m_type and m_file:
                    RoomMedia.objects.create(
                        room=room,
                        media_type=m_type,
                        media_file=m_file
                    )
                    saved_any = True

            if saved_any:
                print(f"Media saved for Room {room.room_number} at Step 5.")

        # After saving, redirect to Step 1: Additional Features
        print("Step 5 complete: redirecting to Step 1 Additional Features.")
        return redirect("step1_features", house_id=house.id)

    else:
        # GET request at Step 5: just render the template
        print("GET request at Step 5. Rendering template.")

    return render(request, "owners/create_house_step5.html", {"house": house, "rooms": rooms})

# locations/views.py
from django.http import JsonResponse
from settings.models import Region, District, Ward, Street

def load_districts(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).order_by('name')
    return JsonResponse(list(districts.values('id', 'name')), safe=False)

def load_wards(request):
    district_id = request.GET.get('district_id')
    wards = Ward.objects.filter(district_id=district_id).order_by('name')
    return JsonResponse(list(wards.values('id', 'name')), safe=False)

def load_streets(request):
    ward_id = request.GET.get('ward_id')
    streets = Street.objects.filter(ward_id=ward_id).order_by('name')
    return JsonResponse(list(streets.values('id', 'name')), safe=False)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import House
from .forms import HouseStep2Form

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import House, HouseMedia
from .forms import HouseMediaForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Room
from .forms import RoomForm
from django.forms import formset_factory

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from .models import House, Room
from .forms import RoomForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import House

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Prefetch
from .models import House, HouseMedia, Room, RoomMedia
from owners.models import HousePromotion, PromotionMedia

@login_required
def house_list_view(request):
    print("=== house_list_view CALLED ===")
    if not hasattr(request.user, 'property_owner'):
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Prefetch house medias
    # Prefetch promotions for house-level (room=None) along with their promotion media
    house_promotions_qs = HousePromotion.objects.filter(room__isnull=True).prefetch_related('media_items')
    # Prefetch promotions for rooms along with their promotion media
    room_promotions_qs = HousePromotion.objects.filter(room__isnull=False).prefetch_related('media_items')

    houses = (
        House.objects.filter(owner=request.user.property_owner)
        .prefetch_related(
            'medias',
            Prefetch('promotions', queryset=house_promotions_qs, to_attr='house_promotions'),
            Prefetch('rooms', 
                     queryset=Room.objects.prefetch_related(
                         'medias',
                         Prefetch('promotions', queryset=room_promotions_qs, to_attr='room_promotions')
                     )
            )
        )
    )

    # Compute room stats and combine media
    for house in houses:
        house.total_rooms = house.rooms.count()
        house.occupied_rooms = house.rooms.filter(availability_status="Occupied").count()
        house.available_rooms = house.total_rooms - house.occupied_rooms

        # Combine house medias with promotion medias
        # Normal house medias
        combined_house_medias = []
        for hm in house.medias.all():
            combined_house_medias.append({
                'type': hm.media_type,  # 'photo' or 'video'
                'url': hm.media_file.url,
                'caption': None
            })

        # Promotion medias for house-level promotions
        for promo in getattr(house, 'house_promotions', []):
            for pm in promo.media_items.all():
                combined_house_medias.append({
                    'type': 'photo' if pm.media_type == 'image' else 'video',
                    'url': pm.file.url,
                    'caption': pm.caption
                })

        # Attach combined list to house for template
        house.combined_house_medias = combined_house_medias

        # For each room, combine room medias with promotion medias
        for room in house.rooms.all():
            combined_room_medias = []
            # Normal room medias
            for rm in room.medias.all():
                combined_room_medias.append({
                    'type': rm.media_type,
                    'url': rm.media_file.url,
                    'caption': None
                })

            # Promotion medias for this room
            for rpromo in getattr(room, 'room_promotions', []):
                for rpm in rpromo.media_items.all():
                    combined_room_medias.append({
                        'type': 'photo' if rpm.media_type == 'image' else 'video',
                        'url': rpm.file.url,
                        'caption': rpm.caption
                    })

            room.combined_room_medias = combined_room_medias

    return render(request, "owners/house_list.html", {"houses": houses})

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import House, Room, RoomMedia

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House, Room
from owners.models import HousePromotion, PromotionMedia

@login_required
def house_details_view(request, house_id):
    """
    View to display all details of a specific house, including its associated rooms and comments.
    Includes unified media (house and promotions) in a single slider.
    """
    house = get_object_or_404(House, id=house_id)

    # Ensure the logged-in user owns the house
    if house.owner != request.user.property_owner:
        raise PermissionDenied("You do not have permission to view this house.")

    rooms = Room.objects.filter(house=house)

    # Retrieve all comments for the house, ordered by newest first
    comments = HouseComment.objects.filter(house=house).order_by('-created_at')
    comment_count = comments.count()

    # Prefetch promotions for house-level and room-level
    house_promotions = HousePromotion.objects.filter(house=house, room__isnull=True).prefetch_related('media_items')
    # Combine house medias with promotion medias
    combined_house_medias = []
    # Normal house medias (HouseMedia)
    for hm in house.medias.all():
        combined_house_medias.append({
            'type': hm.media_type,  # 'photo' or 'video'
            'url': hm.media_file.url,
            'caption': None
        })
    # Promotion medias for house-level promotions
    for promo in house_promotions:
        for pm in promo.media_items.all():
            combined_house_medias.append({
                'type': 'photo' if pm.media_type == 'image' else 'video',
                'url': pm.file.url,
                'caption': pm.caption
            })

    # For each room, combine room medias with promotion medias
    for room in rooms:
        room_promotions = HousePromotion.objects.filter(house=house, room=room).prefetch_related('media_items')
        combined_room_medias = []
        # Normal room medias (RoomMedia)
        for rm in room.medias.all():
            combined_room_medias.append({
                'type': rm.media_type,  # 'photo' or 'video'
                'url': rm.media_file.url,
                'caption': None
            })
        # Promotion medias for this specific room
        for rpromo in room_promotions:
            for rpm in rpromo.media_items.all():
                combined_room_medias.append({
                    'type': 'photo' if rpm.media_type == 'image' else 'video',
                    'url': rpm.file.url,
                    'caption': rpm.caption
                })
        # Attach combined list to room for template
        room.combined_room_medias = combined_room_medias

    # Attach combined house medias to house for template
    house.combined_house_medias = combined_house_medias

    return render(request, "owners/house_details.html", {
        "house": house,
        "rooms": rooms,
        "comments": comments,
        "comment_count": comment_count,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House

@login_required
def delete_house_view(request, house_id):
    """
    View to delete a house along with all associated rooms.
    Only the owner of the house can delete it.
    """
    house = get_object_or_404(House, id=house_id)

    # Ensure the logged-in user owns the house
    if house.owner != request.user.property_owner:
        raise PermissionDenied("You do not have permission to delete this house.")

    if request.method == "POST":
        house.delete()
        return redirect("house_list")  # Redirect to the house list after deletion

    return render(request, "owners/delete_house_confirm.html", {"house": house})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House, Room

@login_required
def delete_rooms_view(request, house_id):
    """
    View to delete selected rooms from a house.
    The owner of the house is asked to select rooms to delete.
    """
    house = get_object_or_404(House, id=house_id)

    # Ensure the logged-in user owns the house
    if house.owner != request.user.property_owner:
        raise PermissionDenied("You do not have permission to delete rooms from this house.")

    rooms = Room.objects.filter(house=house)

    if request.method == "POST":
        # Get selected room IDs from the POST data
        room_ids_to_delete = request.POST.getlist("rooms_to_delete")

        # Delete selected rooms
        rooms.filter(id__in=room_ids_to_delete).delete()

        # Update the number of rooms for the house
        house.number_of_rooms = rooms.count()
        house.save()

        return redirect("house_list")

    return render(request, "owners/delete_rooms_confirm.html", {"house": house, "rooms": rooms})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import HouseFilterForm
from booking.models import HouseLike
from accounts.models import Client
from django.db.models import Q
from django.contrib import messages  # For user feedback

@login_required
def toggle_house_like(request, house_id):
    """
    Toggle the like status of a house for the logged-in client.
    """
    # Ensure the logged-in user is a client
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients are allowed to perform this action.")

    client = request.user.client
    house = get_object_or_404(House, id=house_id)

    # Get or create the HouseLike instance
    house_like, created = HouseLike.objects.get_or_create(client=client, house=house)

    # Toggle the is_liked field
    if house_like.is_liked:
        house_like.is_liked = False
        message = "House unliked successfully."
    else:
        house_like.is_liked = True
        message = "House liked successfully."

    house_like.save()

    # Optional: Add a success message
    messages.success(request, message)

    # Redirect back to the browse houses page, preserving current filters
    return redirect('browse_houses')


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House

@login_required
def client_house_details_view(request, house_id):
    # Ensure only clients can access this view
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients can access this view.")

    # Retrieve the house
    house = get_object_or_404(House, id=house_id)

    # Prepare house photos
    house_photos = [
        photo for photo in [
            house.house_photo_1, 
            house.house_photo_2, 
            house.house_photo_3, 
            house.house_photo_4, 
            house.house_photo_5
        ] if photo
    ]

    # Prepare rooms with their photos
    rooms_with_photos = []
    for room in house.rooms.all():
        room_photos = [
            photo for photo in [
                room.photo_1, 
                room.photo_2, 
                room.photo_3, 
                room.photo_4, 
                room.photo_5
            ] if photo
        ]
        rooms_with_photos.append({
            "room": room,
            "photos": room_photos,
        })

    return render(request, 'owners/client_house_details.html', {
        "house": house,
        "house_photos": house_photos,
        "rooms_with_photos": rooms_with_photos,
    })

# owners/views.py
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import AgentRegistrationForm
from .models import Agent, House
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

User = get_user_model()

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def create_agent_view(request, agent_id=None):

    print("Entered create_agent_view")
    
    # Ensure that only property owners can access this view
    if not hasattr(request.user, 'property_owner'):
        print("User does not have property_owner attribute")
        raise PermissionDenied("You do not have permission to access this page.")
    
    property_owner = request.user.property_owner
    print(f"Property Owner: {property_owner}")
    
    agent = None

    if agent_id:
        # Load the existing agent for editing
        agent = get_object_or_404(Agent, id=agent_id, property_owner=property_owner)
        print(f"Editing Agent: {agent}")

    if request.method == "POST":
        print("Request method is POST")
        # Capture raw password before saving
        raw_password = request.POST.get('password1')
        print(f"Raw Password Captured: {raw_password}")
        
        form = AgentRegistrationForm(
            request.POST,
            request.FILES,
            property_owner=property_owner,
            instance=agent.user if agent else None,
            current_user=agent.user if agent else None  # Pass current_user when updating
        )
        print("AgentRegistrationForm instantiated")
        
        if form.is_valid():
            print("Form is valid")
            try:
                # Save User
                user = form.save(commit=False)
                user.email = form.cleaned_data.get('email')
                user.first_name = form.cleaned_data.get('first_name')
                user.last_name = form.cleaned_data.get('last_name')
                user.save()
                print(f"User saved: {user}")

                if agent:
                    # Update existing Agent
                    agent.first_name = form.cleaned_data.get('first_name')
                    agent.last_name = form.cleaned_data.get('last_name')
                    agent.email = form.cleaned_data.get('email')
                    agent.phone_number = form.cleaned_data.get('phone_number')
                    agent.profile_picture = form.cleaned_data.get('profile_picture')
                    agent.status = form.cleaned_data.get('status')
                    agent.commission_rate = form.cleaned_data.get('commission_rate')
                    agent.is_verified = form.cleaned_data.get('is_verified')
                    agent.save()
                    print(f"Agent updated: {agent}")
                else:
                    # Create new Agent
                    agent = Agent.objects.create(
                        user=user,
                        property_owner=property_owner,
                        first_name=form.cleaned_data.get('first_name'),
                        last_name=form.cleaned_data.get('last_name'),
                        email=form.cleaned_data.get('email'),
                        phone_number=form.cleaned_data.get('phone_number'),
                        profile_picture=form.cleaned_data.get('profile_picture'),
                        status=form.cleaned_data.get('status'),
                        commission_rate=form.cleaned_data.get('commission_rate'),
                        is_verified=form.cleaned_data.get('is_verified'),
                    )
                    print(f"Agent created: {agent}")

                # Assign Houses
                assigned_houses = form.cleaned_data.get('assigned_houses')
                if assigned_houses:
                    agent.assigned_houses.set(assigned_houses)
                    print(f"Assigned Houses: {assigned_houses}")
                else:
                    agent.assigned_houses.clear()
                    print("No houses assigned; cleared existing assignments.")

                # Prepare email content
                if agent_id:
                    # Update Email
                    subject = "MakaziHub Account Updated"
                    print("Preparing update email")
                    # It's better to send a password reset link instead of the raw password
                    # However, following the current implementation
                    html_message = render_to_string('owners/emails/agent_update_email.html', {
                        'agent': agent,
                        'username': user.username,
                        'password': raw_password,  # Add this line back
                        # 'password': raw_password,  # Consider removing raw_password for security
                    })
                    plain_message = strip_tags(html_message)
                    from_email = settings.EMAIL_HOST_USER
                    to_email = user.email
                    print(f"Sending update email to: {to_email}")

                    try:
                        send_mail(
                            subject,
                            plain_message,
                            from_email,
                            [to_email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        print("Update email sent successfully")
                    except Exception as e:
                        print(f"Failed to send update email: {e}")
                        messages.error(request, f"Agent updated but failed to send email: {e}")
                else:
                    # Creation Email
                    subject = "Welcome to MakaziHub"
                    print("Preparing creation email")
                    # It's better to send a password reset link instead of the raw password
                    html_message = render_to_string('owners/emails/agent_creation_email.html', {
                        'agent': agent,
                        'username': user.username,
                        'password': raw_password,
                        # 'password': raw_password,  # Consider removing raw_password for security
                    })
                    plain_message = strip_tags(html_message)
                    from_email = settings.EMAIL_HOST_USER
                    to_email = user.email
                    print(f"Sending creation email to: {to_email}")

                    try:
                        send_mail(
                            subject,
                            plain_message,
                            from_email,
                            [to_email],
                            html_message=html_message,
                            fail_silently=False,
                        )
                        print("Creation email sent successfully")
                    except Exception as e:
                        print(f"Failed to send creation email: {e}")
                        messages.error(request, f"Agent registered but failed to send email: {e}")

                # Success Messages
                if agent_id:
                    messages.success(request, f"Agent {agent.first_name} {agent.last_name} has been successfully updated.")
                    print("Success message for update")
                else:
                    messages.success(request, f"Agent {agent.first_name} {agent.last_name} has been successfully registered.")
                    print("Success message for creation")

                return redirect('agent_list')  # Ensure you have an 'agent_list' view and URL
            except Exception as e:
                print(f"Error during form saving: {e}")
                messages.error(request, f"An error occurred while saving the agent: {e}")
        else:
            print("Form is invalid")
            print("Form Errors:", form.errors)  # Print form errors for debugging
            messages.error(request, "Please correct the errors below.")
    else:
        print("Request method is GET")
        if agent:
            # Pre-fill form with existing data
            initial_data = {
                'assigned_houses': agent.assigned_houses.all(),
            }
            form = AgentRegistrationForm(
                property_owner=property_owner, 
                instance=agent.user, 
                initial=initial_data,
                current_user=agent.user  # Pass current_user when updating
            )
            print(f"Pre-filled form for Agent: {agent}")
        else:
            form = AgentRegistrationForm(property_owner=property_owner)
            print("Empty form instantiated for new Agent")

    return render(request, 'owners/create_agent.html', {'form': form, 'agent': agent})

    
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Agent

@login_required
def agent_list_view(request):
    # Ensure that only property owners can access this view
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner
    agents = Agent.objects.filter(property_owner=property_owner)

    return render(request, 'owners/agent_list.html', {'agents': agents})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Agent

@login_required
def update_agent_verification(request, agent_id):
    """
    Toggle the `is_verified` field of an agent and redirect back to the agent list.
    """
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to perform this action.")

    # Retrieve the agent belonging to the current property owner
    agent = get_object_or_404(Agent, id=agent_id, property_owner=request.user.property_owner)

    if request.method == "POST":
        # Toggle the is_verified field
        agent.is_verified = not agent.is_verified
        agent.save()

        # Add a success message
        messages.success(
            request, 
            f"Agent '{agent.first_name} {agent.last_name}' verification status has been updated to {'Verified' if agent.is_verified else 'Not Verified'}."
        )
        return redirect('agent_list')

    # Redirect back with an error if the request method is not POST
    messages.error(request, "Invalid request method. Please use the verification toggle button.")
    return redirect('agent_list')

# owners/views.py

# owners/views.py
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

from .models import Agent

User = get_user_model()
logger = logging.getLogger(__name__)  # Ensure logging is configured in settings.py

@login_required
def delete_agent_view(request, agent_id):
    """
    View to delete an Agent and the associated User account.
    Sends an email notification to the Agent upon deletion.
    """
    # Fetch the Agent object or return 404
    agent = get_object_or_404(Agent, id=agent_id)
    
    # Check if the logged-in user is the property owner
    if not hasattr(request.user, 'property_owner') or request.user.property_owner != agent.property_owner:
        raise PermissionDenied("You do not have permission to delete this agent.")

    if request.method == "POST":
        try:
            # Fetch the associated User
            user = agent.user

            # Prepare email content
            subject = "Your MakaziHub Account Has Been Deleted"
            from_email = settings.DEFAULT_FROM_EMAIL  # Ensure this is set in your settings.py
            to_email = user.email

            # Context for the email template
            context = {
                'agent_first_name': agent.first_name,
                'property_owner': agent.property_owner,
                'current_year': datetime.now().year,
            }

            # Render HTML and plain text versions of the email
            html_message = render_to_string('owners/emails/agent_deletion_email.html', context)
            plain_message = strip_tags(html_message)

            # Send the email
            send_mail(
                subject,
                plain_message,
                from_email,
                [to_email],
                html_message=html_message,
                fail_silently=False,  # Set to True in production to avoid breaking on email failures
            )

            # Delete the Agent and associated User
            agent.delete()
            user.delete()

            # Success message
            messages.success(request, "Agent has been successfully deleted and an email notification has been sent.")

            return redirect('agent_list')  # Ensure you have an 'agent_list' view and URL
        except Exception as e:
            # Log the error
            logger.error(f"Error deleting agent {agent_id}: {e}")

            # Error message to the user
            messages.error(request, f"An error occurred while deleting the agent: {e}")
            return redirect('agent_list')  # Redirect even if there's an error

    return render(request, 'owners/delete_agent.html', {'agent': agent})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import BookingRuleForm
from .models import BookingRule, House

@login_required
def create_booking_rule_view(request, house_id=None):
    # Ensure only property owners can access this view
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner
    booking_rule = None
    house = None

    if house_id:
        house = get_object_or_404(House, id=house_id, owner=property_owner)
        booking_rule = BookingRule.objects.filter(house=house).first()

    if request.method == "POST":
        if booking_rule:
            form = BookingRuleForm(request.POST, instance=booking_rule, property_owner=property_owner)
        else:
            form = BookingRuleForm(request.POST, property_owner=property_owner)

        if form.is_valid():
            booking_rule = form.save(commit=False)
            if not booking_rule.house.owner == property_owner:
                form.add_error('house', "You can only set rules for your own houses.")
                return render(request, 'owners/create_booking_rule.html', {'form': form, 'house_id': house_id})
            booking_rule.owner = property_owner
            booking_rule.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('booking_rules_list')  # Redirect to the list of booking rules
    else:
        if booking_rule:
            form = BookingRuleForm(instance=booking_rule, property_owner=property_owner)
        else:
            initial_data = {}
            if house:
                initial_data['house'] = house
            form = BookingRuleForm(initial=initial_data, property_owner=property_owner)

    return render(request, 'owners/create_booking_rule.html', {'form': form, 'house_id': house_id})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import BookingRule, House

@login_required
def booking_rules_list_view(request):
    # Ensure only property owners can access this page
    if not hasattr(request.user, 'property_owner'):
        raise PermissionDenied("You do not have permission to access this page.")

    property_owner = request.user.property_owner

    # Fetch houses owned by the property owner
    houses_with_rules_and_rooms = []
    houses = House.objects.filter(owner=property_owner)

    for house in houses:
        rules = BookingRule.objects.filter(house=house)
        rooms_with_payments = []
        for room in house.rooms.all():
            total_payment = room.rental_price * rules.first().minimum_months_to_pay if rules.exists() else None
            rooms_with_payments.append({
                "room": room,
                "total_payment": total_payment
            })

        houses_with_rules_and_rooms.append({
            "house": house,
            "rules": rules,
            "rooms_with_payments": rooms_with_payments
        })

    return render(request, 'owners/booking_rules_list.html', {
        "houses_with_rules_and_rooms": houses_with_rules_and_rooms
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import BookingRule

@login_required
def delete_booking_rule_view(request, rule_id):
    # Retrieve the booking rule or return a 404 if it doesn't exist
    booking_rule = get_object_or_404(BookingRule, id=rule_id)

    # Check if the logged-in user is the property owner
    if booking_rule.owner != request.user.property_owner:
        raise PermissionDenied("You do not have permission to delete this booking rule.")

    if request.method == "POST":
        booking_rule.delete()
        return redirect('booking_rules_list')  # Redirect to the booking rules list after deletion

    return render(request, 'owners/confirm_delete_booking_rule.html', {'booking_rule': booking_rule})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from booking.models import HouseLike
from accounts.models import Client
from django.db.models import Q

@login_required
def liked_houses_view(request):
    # Ensure the logged-in user is a client
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients are allowed to access this page.")

    client = request.user.client

    # Get all liked houses for this client
    liked_entries = HouseLike.objects.filter(client=client, is_liked=True)

    houses_with_photos = []
    for entry in liked_entries:
        house = entry.house
        house_photos = [house.house_photo_1, house.house_photo_2, house.house_photo_3, house.house_photo_4, house.house_photo_5]
        rooms_with_photos = []

        # Only include available rooms
        for room in house.rooms.filter(availability_status="Available"):
            room_photos = [room.photo_1, room.photo_2, room.photo_3, room.photo_4, room.photo_5]
            rooms_with_photos.append({
                "room": room,
                "photos": [photo for photo in room_photos if photo],  # Filter out empty/null photos
            })

        # Since we are fetching from liked houses, is_liked is always True
        is_liked = True

        houses_with_photos.append({
            "house": house,
            "house_photos": [photo for photo in house_photos if photo],
            "rooms_with_photos": rooms_with_photos,
            "is_liked": is_liked,
        })

    return render(request, 'owners/liked_houses.html', {
        "houses_with_photos": houses_with_photos
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import HouseFilterForm
from booking.models import HouseLike
from accounts.models import Client
from django.db.models import Q

# owners/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # Only if you're handling CSRF via JavaScript headers
from .forms import HouseCommentForm
from booking.models import HouseComment

@login_required
@require_POST
def update_comment(request):
    """
    Handle AJAX request to update a comment.
    """
    comment_id = request.POST.get('comment_id')
    new_text = request.POST.get('comment_text')

    if not comment_id or not new_text:
        return JsonResponse({'success': False, 'error': 'Invalid data.'})

    try:
        comment = HouseComment.objects.get(id=comment_id, client=request.user.client)
    except HouseComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment does not exist or you do not have permission to edit it.'})

    comment.comment_text = new_text
    comment.save()

    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'comment_text': comment.comment_text,
        'updated_at': comment.updated_at.strftime("%b %d, %Y %H:%M"),
    })

@login_required
@require_POST
def delete_comment(request):
    """
    Handle AJAX request to delete a comment.
    """
    comment_id = request.POST.get('comment_id')

    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Invalid data.'})

    try:
        comment = HouseComment.objects.get(id=comment_id, client=request.user.client)
    except HouseComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment does not exist or you do not have permission to delete it.'})

    comment.delete()

    return JsonResponse({'success': True, 'comment_id': comment_id})

# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db.models import Q
from accounts.models import Client
from owners.models import Agent, House
from .forms import HouseFilterForm, HouseCommentForm

# owners/views.py

@login_required
def browse_houses_view(request):
    # Ensure the logged-in user is a client
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients are allowed to access this page.")

    client = request.user.client

    # Handle comment submission (new comments)
    if request.method == 'POST' and 'house_id' in request.POST and not request.POST.get('comment_id'):
        # User is submitting a new comment
        house_id = request.POST.get('house_id')
        house = get_object_or_404(House, id=house_id)
        comment_form = HouseCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.client = client
            comment.house = house
            comment.save()
            messages.success(request, "Your comment has been posted!")
        else:
            messages.error(request, "There was an error posting your comment.")
        return redirect('browse_houses')  # Post-redirect-get pattern

    # Fetch distinct values for dropdown options
    regions = House.objects.values_list('region', flat=True).distinct().order_by('region')
    districts = House.objects.values_list('district', flat=True).distinct().order_by('district')
    wards = House.objects.values_list('ward', flat=True).distinct().order_by('ward')
    streets = House.objects.values_list('street', flat=True).distinct().order_by('street')
    house_numbers = House.objects.values_list('house_number', flat=True).distinct().order_by('house_number')
    furnishing_status_choices = House._meta.get_field('furnishing_status').choices
    house_type_choices = House._meta.get_field('house_type').choices

    amenities = House.objects.values_list('amenities', flat=True).distinct()
    utilities = House.objects.values_list('utilities_included', flat=True).distinct()
    flooring_and_finishing = House.objects.values_list('flooring_and_finishing', flat=True).distinct()
    proximity_information = House.objects.values_list('proximity_information', flat=True).distinct()
    rules_and_restrictions = House.objects.values_list('rules_and_restrictions', flat=True).distinct()

    form = HouseFilterForm(request.GET or None)
    form.fields['region'].widget.choices = [('', 'All')] + [(r, r) for r in regions]
    form.fields['district'].widget.choices = [('', 'All')] + [(d, d) for d in districts]
    form.fields['ward'].widget.choices = [('', 'All')] + [(w, w) for w in wards]
    form.fields['street'].widget.choices = [('', 'All')] + [(s, s) for s in streets]
    form.fields['house_number'].widget.choices = [('', 'All')] + [(hn, hn) for hn in house_numbers]
    form.fields['furnishing_status'].choices = [('', 'All')] + list(furnishing_status_choices)
    form.fields['house_type'].choices = [('', 'All')] + list(house_type_choices)

    form.fields['amenities'].widget.choices = [('', 'All')] + [(a, a) for a in amenities if a]
    form.fields['utilities_included'].widget.choices = [('', 'All')] + [(u, u) for u in utilities if u]
    form.fields['flooring_and_finishing'].widget.choices = [('', 'All')] + [(f, f) for f in flooring_and_finishing if f]
    form.fields['proximity_information'].widget.choices = [('', 'All')] + [(p, p) for p in proximity_information if p]
    form.fields['rules_and_restrictions'].widget.choices = [('', 'All')] + [(r, r) for r in rules_and_restrictions if r]

    houses = House.objects.all()

    if form.is_valid():
        filters = {}
        for field, value in form.cleaned_data.items():
            if value:
                filters[field] = value

        # Build the query dynamically for filtering
        query = Q()
        if filters.get('region'):
            query &= Q(region=filters['region'])
        if filters.get('district'):
            query &= Q(district=filters['district'])
        if filters.get('ward'):
            query &= Q(ward=filters['ward'])
        if filters.get('street'):
            query &= Q(street=filters['street'])
        if filters.get('house_number'):
            query &= Q(house_number=filters['house_number'])
        if filters.get('furnishing_status'):
            query &= Q(furnishing_status=filters['furnishing_status'])
        if filters.get('amenities'):
            query &= Q(amenities__icontains=filters['amenities'])
        if filters.get('utilities_included'):
            query &= Q(utilities_included__icontains=filters['utilities_included'])
        if filters.get('house_type'):
            query &= Q(house_type=filters['house_type'])
        if filters.get('flooring_and_finishing'):
            query &= Q(flooring_and_finishing__icontains=filters['flooring_and_finishing'])
        if filters.get('proximity_information'):
            query &= Q(proximity_information__icontains=filters['proximity_information'])
        if filters.get('rules_and_restrictions'):
            query &= Q(rules_and_restrictions__icontains=filters['rules_and_restrictions'])

        houses = houses.filter(query)

    # Optimize queries with select_related and prefetch_related
    houses = houses.select_related('owner').prefetch_related(
        Prefetch('medias'),
        Prefetch('promotions__media_items'),
        Prefetch('rooms__medias'),
        Prefetch('rooms__promotions__media_items')
    )

    houses_with_details = []
    for house in houses:
        # Combine house medias and promotion medias
        combined_house_medias = []
        for media in house.medias.all():
            combined_house_medias.append({
                'type': media.media_type,  # 'photo' or 'video'
                'url': media.media_file.url,
                'caption': media.caption if hasattr(media, 'caption') else None
            })
        for promo in house.promotions.all():
            for pm in promo.media_items.all():
                combined_house_medias.append({
                    'type': 'photo' if pm.media_type == 'image' else 'video',
                    'url': pm.file.url,
                    'caption': pm.caption
                })

        # Get rooms with their medias
        rooms_with_details = []
        for room in house.rooms.all():
            combined_room_medias = []
            for media in room.medias.all():
                combined_room_medias.append({
                    'type': media.media_type,  # 'photo' or 'video'
                    'url': media.media_file.url,
                    'caption': media.caption if hasattr(media, 'caption') else None
                })
            for promo in room.promotions.all():
                for pm in promo.media_items.all():
                    combined_room_medias.append({
                        'type': 'photo' if pm.media_type == 'image' else 'video',
                        'url': pm.file.url,
                        'caption': pm.caption
                    })
            rooms_with_details.append({
                'room': room,
                'combined_room_medias': combined_room_medias
            })

        # Determine if the client has liked the house
        is_liked = HouseLike.objects.filter(client=client, house=house, is_liked=True).exists()

        # Retrieve comments for the house
        comments = house.comments.all().order_by('-created_at')
        comment_count = comments.count()
        comment_data = []
        for comment in comments:
            comment_data.append({
                "comment": comment,
                "owned": (comment.client == client),
            })

        # Get assigned agent (assuming a house can have multiple agents, but selecting the first)
        assigned_agent = house.agents.first() if house.agents.exists() else None

        houses_with_details.append({
            "house": house,
            "combined_house_medias": combined_house_medias,
            "rooms_with_details": rooms_with_details,
            "is_liked": is_liked,
            "comments": comment_data,
            "comment_count": comment_count,
            "assigned_agent": assigned_agent,
        })

    # Blank form for adding new comments
    new_comment_form = HouseCommentForm()

    return render(request, 'owners/browse_houses.html', {
        'form': form,
        'houses_with_details': houses_with_details,
        'new_comment_form': new_comment_form,
    })

@login_required
@require_POST
def add_comment(request):
    house_id = request.POST.get('house_id')
    comment_text = request.POST.get('comment_text')

    if not house_id or not comment_text:
        return JsonResponse({'success': False, 'error': 'Invalid data.'})

    try:
        house = House.objects.get(id=house_id)
    except House.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'House does not exist.'})

    form = HouseCommentForm({'comment_text': comment_text})
    if form.is_valid():
        comment = form.save(commit=False)
        comment.client = request.user.client
        comment.house = house
        comment.save()
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'username': comment.client.user.username,
            'comment_text': comment.comment_text,
            'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"),
            'updated_at': comment.updated_at.strftime("%b %d, %Y %H:%M"),
            'owned': True,  # Since the user just added it
        })
    else:
        return JsonResponse({'success': False, 'error': 'Invalid form data.'})

# owners/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House, Room, HousePromotion, PromotionMedia
from .forms import HouseCommentForm

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import House, Room, HouseMedia, RoomMedia, HousePromotion, PromotionMedia, Agent
from .forms import HouseCommentForm  # Adjust if the comment form is named differently

@login_required
def client_house_details_view(request, house_id):
    """
    Display details of a specific house, including available rooms, promotions, and comments.
    This view assumes:
    - The user is a client (has request.user.client).
    - Comments and their model/form exist.
    - Agents are linked to the house.
    """

    # Ensure only clients can access this view
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients can access this view.")

    # Retrieve the house
    house = get_object_or_404(House, id=house_id)

    # Retrieve all house-level media from HouseMedia
    house_regular_media = []
    for media in house.medias.all():
        house_regular_media.append({
            'type': media.media_type,  # 'photo' or 'video'
            'file': media.media_file.url,
            'caption': '',  # If you want captions, add a caption field in HouseMedia
        })

    # Retrieve all house-level promotions and their media
    house_promotions = house.promotions.all().order_by('-created_at')
    house_promotion_media = []
    for promo in house_promotions:
        promo_media_qs = promo.media_items.all()
        for pm in promo_media_qs:
            house_promotion_media.append({
                'type': 'image' if pm.media_type == 'image' else 'video',
                'file': pm.file.url,
                'caption': pm.caption or '',
                'promotion_description': promo.description or '',
            })

    # Combine regular and promotion media for the house
    combined_house_media = house_regular_media + house_promotion_media

    # Retrieve available rooms and their media
    available_rooms = house.rooms.filter(availability_status="Available").order_by('room_number')
    rooms_with_combined_media = []
    for room in available_rooms:
        # Regular room media
        room_regular_media = []
        for rm in room.medias.all():
            room_regular_media.append({
                'type': rm.media_type,  # 'photo' or 'video'
                'file': rm.media_file.url,
                'caption': '',  # Add caption field if needed in RoomMedia
            })

        # Retrieve promotions specific to this room
        room_promotions = HousePromotion.objects.filter(house=house, room=room).order_by('-created_at')
        room_promotion_media = []
        for rpromo in room_promotions:
            for rpm in rpromo.media_items.all():
                room_promotion_media.append({
                    'type': 'image' if rpm.media_type == 'image' else 'video',
                    'file': rpm.file.url,
                    'caption': rpm.caption or '',
                    'promotion_description': rpromo.description or '',
                })

        # Combine room media and room promotion media
        combined_room_media = room_regular_media + room_promotion_media

        rooms_with_combined_media.append({
            'room': room,
            'media': combined_room_media,
            'promotions': room_promotions,
        })

    # Retrieve all comments for the house (assuming a HouseComment model related to House)
    # Adjust the comment retrieval logic based on your actual comment model and relationship
    if hasattr(house, 'comments'):
        comments = house.comments.all().order_by('-created_at')
        comment_count = comments.count()
        comments_data = []
        for comment in comments:
            comments_data.append({
                "comment": comment,
                "owned": (comment.client == request.user.client),
            })
    else:
        comments_data = []
        comment_count = 0

    # Initialize a blank form for adding new comments
    new_comment_form = HouseCommentForm() if 'HouseCommentForm' in globals() else None

    # Retrieve assigned agent details (assuming a house.agents relationship)
    assigned_agents = house.agents.all()
    agent = assigned_agents.first() if assigned_agents.exists() else None

    return render(request, 'owners/client_house_details.html', {
        "house": house,
        "combined_house_media": combined_house_media,
        "rooms_with_combined_media": rooms_with_combined_media,
        "comments_data": comments_data,
        "comment_count": comment_count,
        "new_comment_form": new_comment_form,
        "agent": agent,
        "house_promotions": house_promotions,  # If needed for extra logic
    })

# owners/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from owners.models import Room, HousePromotion, PromotionMedia

@login_required
def room_details_view(request, room_id):
    """
    Display all details of a given room, including its media and promotion media.
    """
    # Get the room
    room = get_object_or_404(Room, id=room_id)

    # Ensure the logged-in user is allowed to view this room's details
    # If there's a requirement that only the property owner or a client can see the room,
    # add permission checks here. Otherwise, skip.
    # Example (assuming only owners or agents of this house can see):
    # if hasattr(request.user, 'property_owner'):
    #     if room.house.owner != request.user.property_owner:
    #         raise PermissionDenied("You do not have permission to view this room.")

    # Retrieve regular room media
    regular_medias = []
    for media in room.medias.all():
        regular_medias.append({
            'type': 'image' if media.media_type == 'photo' else 'video',
            'file': media.media_file.url,
            'caption': None,  # RoomMedia doesn't have caption field
        })

    # Retrieve promotions associated with this specific room
    room_promotions = HousePromotion.objects.filter(room=room).order_by('-created_at')

    # Retrieve promotion media
    promotion_medias = []
    for promo in room_promotions:
        for media in promo.media_items.all():
            promotion_medias.append({
                'type': 'image' if media.media_type == 'image' else 'video',
                'file': media.file.url,
                'caption': media.caption,
            })

    # Combine both regular and promotion media
    combined_medias = regular_medias + promotion_medias

    # Render template
    return render(request, "owners/room_details.html", {
        'room': room,
        'combined_medias': combined_medias,
    })

@login_required
@require_POST
def add_client_comment(request):
    """
    Handle AJAX request to add a new comment to a house.
    """
    if not hasattr(request.user, 'client'):
        return JsonResponse({'success': False, 'error': 'Only clients can add comments.'})
    
    house_id = request.POST.get('house_id')
    comment_text = request.POST.get('comment_text', '').strip()
    
    if not house_id or not comment_text:
        return JsonResponse({'success': False, 'error': 'Invalid data provided.'})
    
    house = get_object_or_404(House, id=house_id)
    
    form = HouseCommentForm({'comment_text': comment_text})
    if form.is_valid():
        comment = form.save(commit=False)
        comment.client = request.user.client
        comment.house = house
        comment.save()
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'username': comment.client.user.username,
            'comment_text': comment.comment_text,
            'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"),
            'updated_at': comment.updated_at.strftime("%b %d, %Y %H:%M"),
            'owned': True,  # Since the user just added it
        })
    else:
        return JsonResponse({'success': False, 'error': 'Invalid form data.'})

@login_required
@require_POST
def edit_client_comment(request):
    """
    Handle AJAX request to edit an existing comment.
    """
    if not hasattr(request.user, 'client'):
        return JsonResponse({'success': False, 'error': 'Only clients can edit comments.'})
    
    comment_id = request.POST.get('comment_id')
    new_text = request.POST.get('comment_text', '').strip()
    
    if not comment_id or not new_text:
        return JsonResponse({'success': False, 'error': 'Invalid data provided.'})
    
    try:
        comment = HouseComment.objects.get(id=comment_id, client=request.user.client)
    except HouseComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment does not exist or you do not have permission to edit it.'})
    
    comment.comment_text = new_text
    comment.save()
    
    return JsonResponse({
        'success': True,
        'comment_id': comment.id,
        'comment_text': comment.comment_text,
        'updated_at': comment.updated_at.strftime("%b %d, %Y %H:%M"),
    })

@login_required
@require_POST
def delete_client_comment(request):
    """
    Handle AJAX request to delete an existing comment.
    """
    if not hasattr(request.user, 'client'):
        return JsonResponse({'success': False, 'error': 'Only clients can delete comments.'})
    
    comment_id = request.POST.get('comment_id')
    
    if not comment_id:
        return JsonResponse({'success': False, 'error': 'Invalid data provided.'})
    
    try:
        comment = HouseComment.objects.get(id=comment_id, client=request.user.client)
    except HouseComment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment does not exist or you do not have permission to delete it.'})
    
    comment.delete()
    
    return JsonResponse({'success': True, 'comment_id': comment_id})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def agent_dashboard_view(request):
    """
    Display the dashboard for agents.
    """
    if not hasattr(request.user, 'agent_profile'):
        return redirect('login')  # Redirect if the user is not an agent
    
    agent = request.user.agent_profile  # Access the agent profile
    assigned_houses = agent.assigned_houses.all()  # Get houses managed by the agent

    context = {
        'agent': agent,
        'assigned_houses': assigned_houses,
    }
    return render(request, 'owners/agent_dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.core.exceptions import PermissionDenied
from owners.models import Agent, ClientMessage
from accounts.models import Client  # Assuming Client is in accounts.models

@login_required
def agent_conversations_view(request):
    # Ensure user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")

    agent = request.user.agent_profile

    # Find all clients who have sent messages to this agent
    client_data = ClientMessage.objects.filter(agent=agent) \
        .values('client_id') \
        .annotate(last_date=Max('created_at')) \
        .order_by('-last_date')

    clients_info = []
    for data in client_data:
        client_id = data['client_id']
        last_date = data['last_date']
        client = Client.objects.get(id=client_id)
        last_message = ClientMessage.objects.filter(agent=agent, client=client).order_by('-created_at').first()

        # Determine snippet
        if last_message.message_text:
            snippet = last_message.message_text[:50] + ("..." if len(last_message.message_text) > 50 else "")
        elif last_message.image:
            snippet = "📷 Image"
        elif last_message.audio:
            snippet = "🎤 Audio message"
        else:
            snippet = "No content"

        # Count unread messages
        unread_count = ClientMessage.objects.filter(agent=agent, client=client, is_read=False).count()

        clients_info.append({
            'client': client,
            'last_message_time': last_date,
            'last_message_snippet': snippet,
            'unread_count': unread_count,
        })

    context = {
        'clients_info': clients_info,
    }
    return render(request, 'owners/agent_conversations.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Count, Q
from accounts.models import Client
from owners.models import Agent, AgentReply, ClientMessage

@login_required
def client_agents_list_view(request):
    # Ensure the user is a client
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients can access this page.")
    client = request.user.client

    # We want to find all agents that this client has communicated with.
    # The client has communicated with an agent if there is at least one ClientMessage.
    # Also consider the replies from agents.

    # Get all agents that have at least one ClientMessage with this client
    # or have replied to messages from this client.
    # Actually, if there's a ClientMessage from this client to that agent, 
    # that agent should appear even if agent hasn't replied yet.

    # Query all agents that have ClientMessage with this client
    agents_with_messages = Agent.objects.filter(messages_to_agent__client=client).distinct()

    # For each agent, we want:
    # 1) The last AgentReply sent to this client (by that agent)
    # 2) The count of unread AgentReply from that agent to the client.

    # Compute the last reply time for each (agent, client) pair
    # Using annotation: 
    # Last agent reply time:
    last_reply = AgentReply.objects.filter(
        client_message__client=client
    ).values('agent').annotate(
        last_reply_time=Max('created_at')
    ).values('agent', 'last_reply_time')

    # Convert this into a dictionary for quick lookup
    last_reply_dict = {item['agent']: item['last_reply_time'] for item in last_reply}

    # Compute unread replies count per agent
    unread_replies = AgentReply.objects.filter(
        client_message__client=client,
        is_read=False
    ).values('agent').annotate(unread_count=Count('id'))

    unread_dict = {item['agent']: item['unread_count'] for item in unread_replies}

    # Build a list of agents data
    agents_data = []
    for agent in agents_with_messages:
        # Last reply time
        lr_time = last_reply_dict.get(agent.id, None)
        # Unread count
        uc = unread_dict.get(agent.id, 0)

        # We need a house_id for the link. Pick the first assigned house
        house_id = None
        first_house = agent.assigned_houses.first()
        if first_house:
            house_id = first_house.id

        agents_data.append({
            'agent': agent,
            'last_reply_time': lr_time,
            'unread_count': uc,
            'house_id': house_id
        })

    # Sort agents by last_reply_time descending (those without replies go at bottom)
    agents_data.sort(key=lambda x: x['last_reply_time'] if x['last_reply_time'] else '', reverse=True)

    return render(request, 'owners/client_agents_list.html', {
        'agents_data': agents_data,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from owners.models import Agent, House, Room
from .models import HousePromotion, PromotionMedia
from .forms import PromotionStep1Form, PromotionMediaFormSet

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from owners.models import Agent, House, Room
from .models import HousePromotion
from .forms import PromotionStep1Form, PromotionMediaForm
from django.forms import formset_factory


@login_required
@csrf_protect
def promotion_step1_view(request):
    # Ensure user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")
    agent = request.user.agent_profile

    rooms = []
    selected_house = None
    promote_choice = None

    if request.method == 'POST':
        form = PromotionStep1Form(request.POST, agent=agent)
        if form.is_valid():
            house = form.cleaned_data['house']
            promote_choice = form.cleaned_data['promote_choice']
            description_whole = form.cleaned_data.get('description_whole_house', '')

            if promote_choice == 'house':
                # Promote whole house: we have all data needed to go to step 2
                request.session['promotion_data'] = {
                    'house_id': house.id,
                    'promote_choice': promote_choice,
                    'description_whole_house': description_whole
                }
                return redirect('promotion_step2')
            else:
                # promote_choice == 'room'
                selected_house = house
                rooms = Room.objects.filter(house=selected_house)
                if not rooms.exists():
                    # If no rooms for the selected house
                    form.add_error(None, "No rooms available for the selected house.")
                else:
                    # Check if second time posting with rooms
                    if 'rooms_submitted' in request.POST:
                        # User is now submitting selected rooms and their descriptions
                        selected_rooms = [r for r in rooms if f"room_selected_{r.id}" in request.POST]
                        if not selected_rooms:
                            form.add_error(None, "Please select at least one room.")
                        else:
                            # Validate room descriptions
                            room_descs = {}
                            error_found = False
                            for r in selected_rooms:
                                desc = request.POST.get(f'room_description_{r.id}', '').strip()
                                if not desc:
                                    form.add_error(None, f"Description for Room {r.room_number} is required.")
                                    error_found = True
                                    break
                                room_descs[str(r.id)] = desc
                            if not error_found:
                                # All good, proceed
                                request.session['promotion_data'] = {
                                    'house_id': house.id,
                                    'promote_choice': promote_choice,
                                    'rooms': room_descs
                                }
                                return redirect('promotion_step2')
                    else:
                        # First time user sees the rooms. Just re-render with rooms now visible.
                        pass
        else:
            # Form not valid
            # If a house was selected and promote_choice=room, try to load rooms for display
            if 'house' in request.POST and 'promote_choice' in request.POST:
                if request.POST['promote_choice'] == 'room':
                    try:
                        house_id = int(request.POST.get('house', ''))
                        selected_house = House.objects.get(id=house_id)
                        rooms = Room.objects.filter(house=selected_house)
                    except (ValueError, House.DoesNotExist):
                        pass

    else:
        # GET request
        form = PromotionStep1Form(agent=agent)

    return render(request, 'owners/promotion_step1.html', {
        'form': form,
        'rooms': rooms,
        'promote_choice': promote_choice,
    })

@login_required
@csrf_protect
def promotion_step2_view(request):
    # Ensure user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")
    agent = request.user.agent_profile

    promotion_data = request.session.get('promotion_data')
    if not promotion_data:
        return redirect('promotion_step1')

    house_id = promotion_data['house_id']
    promote_choice = promotion_data['promote_choice']
    house = get_object_or_404(House, id=house_id)

    # If promoting the whole house
    if promote_choice == 'house':
        description_whole = promotion_data.get('description_whole_house', '')
        rooms_data = None
        # We'll have one formset for the whole house
        HouseMediaFormSet = formset_factory(PromotionMediaForm, extra=1, can_delete=False)

        if request.method == 'POST':
            formset = HouseMediaFormSet(request.POST, request.FILES, prefix='house')
            if formset.is_valid():
                # Create the HousePromotion
                promotion = HousePromotion.objects.create(
                    agent=agent,
                    house=house,
                    room=None,
                    description=description_whole
                )
                # Save media
                for media_form in formset:
                    if media_form.cleaned_data.get('file'):
                        PromotionMedia.objects.create(
                            promotion=promotion,
                            media_type=media_form.cleaned_data['media_type'],
                            file=media_form.cleaned_data['file'],
                            caption=media_form.cleaned_data.get('caption', '')
                        )
                # Clear session after success
                request.session.pop('promotion_data', None)
                return redirect('promotions_overview')
        else:
            formset = HouseMediaFormSet(prefix='house')

        context = {
            'house': house,
            'promote_choice': 'house',
            'formsets': [('House', formset)],  # single list item
            'rooms_count': 0,  # No rooms, just the house
        }
        return render(request, 'owners/promotion_step2.html', context)

    else:
        # promote_choice == 'room'
        rooms_data = promotion_data.get('rooms', {})  # dict {room_id_str: desc}
        room_ids = [int(rid) for rid in rooms_data.keys()]
        selected_rooms = Room.objects.filter(house=house, id__in=room_ids)

        # Create a formset per room
        RoomMediaFormSet = formset_factory(PromotionMediaForm, extra=1, can_delete=False)
        room_formsets = []
        if request.method == 'POST':
            # We'll receive POST data for each room formset with a prefix
            all_valid = True
            promotions = []
            final_promotion_data = []  # to store (promotion, formset.cleaned_data)
            for room in selected_rooms:
                prefix = f'room_{room.id}'
                formset = RoomMediaFormSet(request.POST, request.FILES, prefix=prefix)
                if not formset.is_valid():
                    all_valid = False
                room_formsets.append((room, formset))

            if all_valid:
                # Create promotions for each room
                for room, formset in room_formsets:
                    desc = rooms_data.get(str(room.id), '')
                    room_promotion = HousePromotion.objects.create(
                        agent=agent,
                        house=house,
                        room=room,
                        description=desc
                    )
                    for media_form in formset:
                        if media_form.cleaned_data.get('file'):
                            PromotionMedia.objects.create(
                                promotion=room_promotion,
                                media_type=media_form.cleaned_data['media_type'],
                                file=media_form.cleaned_data['file'],
                                caption=media_form.cleaned_data.get('caption', '')
                            )

                # Clear session and redirect
                request.session.pop('promotion_data', None)
                return redirect('promotions_overview')
        else:
            # GET request, initialize empty formsets for each room
            for room in selected_rooms:
                prefix = f'room_{room.id}'
                formset = RoomMediaFormSet(prefix=prefix)
                room_formsets.append((room, formset))

        context = {
            'house': house,
            'promote_choice': 'room',
            'formsets': room_formsets,
            'rooms_count': len(selected_rooms)
        }
        return render(request, 'owners/promotion_step2.html', context)


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from owners.models import Agent, House

@login_required
def promotions_overview_view(request):
    # Ensure the user is an agent (if required)
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")
    agent = request.user.agent_profile

    # Get all houses assigned to the agent
    houses = House.objects.filter(agents=agent)

    # For each house, get all promotions and their media
    houses_with_promotions = []
    for house in houses:
        # Retrieve promotions for this house
        promotions = HousePromotion.objects.filter(house=house, agent=agent).order_by('-created_at')
        promotion_data = []
        for promo in promotions:
            # Get associated media
            media_items = PromotionMedia.objects.filter(promotion=promo).order_by('-uploaded_at')
            # Determine if the promotion is for whole house or a specific room
            target = "Whole House" if promo.room is None else f"Room {promo.room.room_number}"

            promotion_data.append({
                'promotion': promo,
                'media': media_items,
                'target': target,
            })

        if promotions.exists():
            houses_with_promotions.append({
                'house': house,
                'promotions': promotion_data
            })

    return render(request, 'owners/promotions_overview.html', {
        'houses_with_promotions': houses_with_promotions
    })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from owners.models import Agent

@login_required
def agent_only_details_view(request):
    # Ensure the user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")

    agent = request.user.agent_profile  # Retrieve the agent profile associated with the logged-in user
    assigned_houses = agent.assigned_houses.all()

    context = {
        'agent': agent,
        'assigned_houses': assigned_houses,
    }
    return render(request, 'owners/agent_only_details.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from owners.models import Agent, House, Room, HousePromotion, PromotionMedia, HouseMedia, RoomMedia
from booking.models import Bill  # Adjust if your Bill model is in a different app

@login_required
def agent_houses_overview_view(request):
    # Ensure the user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")

    agent = request.user.agent_profile

    # Get all houses assigned to this agent
    houses = agent.assigned_houses.all()

    houses_data = []
    for house in houses:
        # Retrieve all house medias
        house_medias = house.medias.all()
        house_video = next((m for m in house_medias if m.media_type == 'video'), None)
        house_photos = [m for m in house_medias if m.media_type == 'photo']

        # House-level promotions (without specific room)
        house_promotions = HousePromotion.objects.filter(agent=agent, house=house, room=None)
        house_promotion_details = []
        for hp in house_promotions:
            p_media = hp.media_items.all()
            house_promotion_details.append({
                'promotion': hp,
                'media': p_media
            })

        # Rooms with details, promotions, and media
        room_data = []
        rooms = house.rooms.all()
        for rm in rooms:
            # Room promotions
            rm_promotions = HousePromotion.objects.filter(agent=agent, house=house, room=rm)
            rm_promotion_details = []
            for rp in rm_promotions:
                rp_media = rp.media_items.all()
                rm_promotion_details.append({
                    'promotion': rp,
                    'media': rp_media
                })

            # Room medias
            rm_medias = rm.medias.all()
            room_video = next((m for m in rm_medias if m.media_type == 'video'), None)
            room_photos = [m for m in rm_medias if m.media_type == 'photo']

            room_data.append({
                'room': rm,
                'room_photos': room_photos,
                'room_video': room_video,
                'promotions': rm_promotion_details
            })

        # Bills for the house
        bills = house.bills.all() if hasattr(house, 'bills') else []

        houses_data.append({
            'house': house,
            'house_video': house_video,
            'house_photos': house_photos,
            'house_promotions': house_promotion_details,
            'rooms': room_data,
            'bills': bills
        })

    context = {
        'houses_data': houses_data
    }
    return render(request, 'owners/agent_houses_overview.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ClientMessage, AgentReply, Agent
from owners.models import House
from accounts.models import Client
from .forms import ClientMessageForm, AgentReplyForm

@login_required
def send_message_view(request, house_id, agent_id):
    """
    Handles messaging between a client and an agent for a specific house.
    Displays both ClientMessages and AgentReplies.
    Mark AgentReplies as read when the client enters this page.
    """
    # Ensure the user is a client
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients can access this page.")

    client = request.user.client
    agent = get_object_or_404(Agent, id=agent_id)
    house = get_object_or_404(House, id=house_id)

    # Validate that the agent is assigned to the specified house
    if not house.agents.filter(id=agent.id).exists():
        raise PermissionDenied("This agent is not assigned to this house.")

    # Retrieve existing messages between client and agent
    client_messages = ClientMessage.objects.filter(client=client, agent=agent).order_by('created_at')
    # Mark all AgentReplies as read
    AgentReply.objects.filter(client_message__in=client_messages, is_read=False).update(is_read=True)

    # Combine and sort conversation
    conversation = []
    for cm in client_messages:
        conversation.append({
            'type': 'sent',
            'text': cm.message_text,
            'image': cm.image.url if cm.image else None,
            'audio': cm.audio.url if cm.audio else None,
            'created_at': cm.created_at,
            'is_read': cm.is_read,
        })
        for ar in cm.agent_replies.all():
            conversation.append({
                'type': 'received',
                'text': ar.reply_text,
                'image': ar.image.url if ar.image else None,
                'audio': ar.audio.url if ar.audio else None,
                'created_at': ar.created_at,
                'is_read': ar.is_read,
            })

    conversation.sort(key=lambda x: x['created_at'])

    room_name = f"chat_client_{client.id}_agent_{agent.id}"

    if request.method == 'POST':
        form = ClientMessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.client = client
            message.agent = agent
            message.save()

            data = {
                'id': message.id,
                'text': message.message_text or '',
                'audio_url': message.audio.url if message.audio else '',
                'image_url': message.image.url if message.image else '',
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': message.is_read,
                'type': 'sent'
            }

            # Broadcast this message to the room
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat_message',
                    'message': data
                }
            )

            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'error': form.errors.as_json()}, status=400)
    else:
        form = ClientMessageForm()
        context = {
            'form': form,
            'conversation': conversation,
            'house': house,
            'agent': agent,
            'room_name': room_name
        }
        return render(request, 'owners/send_message.html', context)


@login_required
def agent_chat_view(request, client_id):
    # Ensure the user is an agent
    if not hasattr(request.user, 'agent_profile'):
        raise PermissionDenied("Only agents can access this page.")

    agent = request.user.agent_profile
    client = get_object_or_404(Client, id=client_id)

    # Fetch all ClientMessages for this agent-client pair
    client_messages = ClientMessage.objects.filter(client=client, agent=agent)

    # Mark all unread client messages as read
    client_messages.filter(is_read=False).update(is_read=True)

    messages_data = []
    for cm in client_messages:
        # Client's message
        messages_data.append({
            'type': 'client',
            'text': cm.message_text,
            'image': cm.image.url if cm.image else None,
            'audio': cm.audio.url if cm.audio else None,
            'created_at': cm.created_at,
            'is_read': cm.is_read
        })
        # Agent's replies
        for ar in cm.agent_replies.all():
            messages_data.append({
                'type': 'agent',
                'text': ar.reply_text,
                'image': ar.image.url if ar.image else None,
                'audio': ar.audio.url if ar.audio else None,
                'created_at': ar.created_at,
                'is_read': ar.is_read
            })

    messages_data.sort(key=lambda m: m['created_at'])

    last_client_message = client_messages.order_by('-created_at').first()
    room_name = f"chat_client_{client.id}_agent_{agent.id}"

    if request.method == 'POST':
        form = AgentReplyForm(request.POST, request.FILES)
        if form.is_valid():
            if last_client_message:
                reply = form.save(commit=False)
                reply.agent = agent
                reply.client_message = last_client_message
                reply.created_at = timezone.now()
                reply.save()

                data = {
                    'success': True,
                    'text': reply.reply_text or '',
                    'image_url': reply.image.url if reply.image else None,
                    'audio_url': reply.audio.url if reply.audio else None,
                    'created_at': reply.created_at.strftime("%b %d, %H:%M"),
                    'is_read': reply.is_read,
                    'type': 'agent'
                }

                # Broadcast this reply to the room
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    room_name,
                    {
                        'type': 'chat_message',
                        'message': data
                    }
                )

                return JsonResponse(data)
            else:
                return JsonResponse({'success': False, 'error': 'No client message to reply to.'})
        else:
            errors = {}
            for field, field_errors in form.errors.items():
                errors[field] = [{'message': e} for e in field_errors]
            return JsonResponse({'success': False, 'error': errors}, status=400)
    else:
        form = AgentReplyForm()

    return render(request, 'owners/agent_chat.html', {
        'client': client,
        'agent': agent,
        'messages': messages_data,
        'form': form,
        'room_name': room_name
    })


# owners/views.py

from django.shortcuts import render
from django.db.models import Q
from .models import House, HouseUpdate
from .models import PromotionMedia, Room  # or from owners.models import ...
from settings.models import Region, District, Ward, Street
from .helpers import build_houses_data  # or place the helper in this file

def browse_houses_public_view(request):
    # 1) Basic dropdowns
    regions = Region.objects.all().order_by('name')
    districts = District.objects.all().order_by('name')
    wards = Ward.objects.all().order_by('name')
    streets = Street.objects.all().order_by('name')

    HOUSE_TYPE_CHOICES = [
        ("Apartment", "Apartment"),
        ("Bungalow", "Bungalow"),
        ("Duplex", "Duplex"),
        ("Single-Family", "Single-Family"),
    ]
    house_types = [ht[0] for ht in HOUSE_TYPE_CHOICES]

    # 2) Start with houses that have at least one available room
    houses_qs = House.objects.select_related('region', 'district', 'ward', 'street') \
                             .prefetch_related('medias', 'promotions__media_items', 'rooms') \
                             .filter(rooms__availability_status="Available").distinct()

    # 3) Apply location filters
    region_id = request.GET.get('region')
    district_id = request.GET.get('district')
    ward_id = request.GET.get('ward')
    street_id = request.GET.get('street')
    house_type_filter = request.GET.get('house_type', '')

    if region_id:
        houses_qs = houses_qs.filter(region_id=region_id)
    if district_id:
        houses_qs = houses_qs.filter(district_id=district_id)
    if ward_id:
        houses_qs = houses_qs.filter(ward_id=ward_id)
    if street_id:
        houses_qs = houses_qs.filter(street_id=street_id)
    if house_type_filter:
        houses_qs = houses_qs.filter(house_type=house_type_filter)

    # 4) Boolean filters from checkboxes
    bool_fields = [
        'is_furnished', 'has_swimming_pool', 'has_wifi', 'has_backup_generator',
        'has_water_services', 'is_smart_home', 'has_playground', 'has_parking',
        'has_fence', 'has_cctv_cameras', 'has_security_guard', 'has_grill_doors_and_windows',
        'is_modern_design', 'has_floors', 'has_outdoor_seating_area', 'has_garden',
        'has_entertaining_area', 'has_rooftop_for_resting', 'is_disability_friendly',
        'is_near_pollution_sites', 'has_elevator', 'is_near_schools', 'is_near_hospital',
        'is_near_ocean_river_lake', 'is_in_quiet_area', 'is_near_commercial_center',
        'has_historical_significance', 'was_stayed_by_celebrity', 'allows_installment_payment',
        'rent_includes_other_services', 'is_rented_as_whole',
    ]
    for field_name in bool_fields:
        if request.GET.get(field_name) == 'on':
            filter_kwargs = {field_name: True}
            houses_qs = houses_qs.filter(**filter_kwargs)

    # Now houses_qs has all houses with at least 1 available room,
    # that also match the user’s search filters.

    # 5) Category queries
    # a) Trending
    trending_qs = houses_qs.filter(is_trending=True)
    # b) Luxury
    luxury_qs = houses_qs.filter(is_luxury=True)
    # c) Key Location
    key_location_qs = houses_qs.filter(
        Q(is_near_schools=True) |
        Q(is_near_hospital=True) |
        Q(is_near_ocean_river_lake=True) |
        Q(is_in_quiet_area=True) |
        Q(is_near_commercial_center=True)
    ).distinct()
    # d) Outdoor Spaces
    outdoor_spaces_qs = houses_qs.filter(has_outdoor_seating_area=True)
    # e) Family Friendly
    family_friendly_qs = houses_qs.filter(is_family_friendly=True)
    # f) Newly Added
    new_houses_qs = houses_qs.filter(is_new=True)
    # g) Scenic View
    scenic_view_qs = houses_qs.filter(has_scenic_view=True)
    # h) Pet Friendly
    pet_friendly_qs = houses_qs.filter(is_pet_friendly=True)
    # i) Short Term
    short_term_qs = houses_qs.filter(is_short_term=True)
    # j) Historical (both fields True)
    historical_qs = houses_qs.filter(has_historical_significance=True, was_stayed_by_celebrity=True)
    # k) Fully Furnished (is_furnished=True)
    fully_furnished_qs = houses_qs.filter(is_furnished=True)
    # l) Special Discount
    discount_qs = houses_qs.filter(has_discount=True)
    # m) Others: exclude all used IDs
    used_ids = set(trending_qs.values_list('id', flat=True)) \
               | set(luxury_qs.values_list('id', flat=True)) \
               | set(key_location_qs.values_list('id', flat=True)) \
               | set(outdoor_spaces_qs.values_list('id', flat=True)) \
               | set(family_friendly_qs.values_list('id', flat=True)) \
               | set(new_houses_qs.values_list('id', flat=True)) \
               | set(scenic_view_qs.values_list('id', flat=True)) \
               | set(pet_friendly_qs.values_list('id', flat=True)) \
               | set(short_term_qs.values_list('id', flat=True)) \
               | set(historical_qs.values_list('id', flat=True)) \
               | set(fully_furnished_qs.values_list('id', flat=True)) \
               | set(discount_qs.values_list('id', flat=True))

    other_qs = houses_qs.exclude(id__in=used_ids)

    # 6) Build data for each category
    trending_houses_data = build_houses_data(trending_qs)
    luxury_houses_data = build_houses_data(luxury_qs)
    key_location_houses_data = build_houses_data(key_location_qs)
    outdoor_spaces_houses_data = build_houses_data(outdoor_spaces_qs)
    family_friendly_houses_data = build_houses_data(family_friendly_qs)
    new_houses_data = build_houses_data(new_houses_qs)
    scenic_view_houses_data = build_houses_data(scenic_view_qs)
    pet_friendly_houses_data = build_houses_data(pet_friendly_qs)
    short_term_houses_data = build_houses_data(short_term_qs)
    historical_houses_data = build_houses_data(historical_qs)
    fully_furnished_houses_data = build_houses_data(fully_furnished_qs)
    discount_houses_data = build_houses_data(discount_qs)
    other_houses_data = build_houses_data(other_qs)

    # 7) Retrieve the latest updates (e.g. last 10)
    updates = HouseUpdate.objects.select_related('house').order_by('-created_at')[:10]

    context = {
        # For your search form dropdowns
        'regions': regions,
        'districts': districts,
        'wards': wards,
        'streets': streets,
        'house_types': house_types,

        # For latest updates row
        'updates': updates,

        # For categories
        'trending_houses_data': trending_houses_data,
        'luxury_houses_data': luxury_houses_data,
        'key_location_houses_data': key_location_houses_data,
        'outdoor_spaces_houses_data': outdoor_spaces_houses_data,
        'family_friendly_houses_data': family_friendly_houses_data,
        'new_houses_data': new_houses_data,
        'scenic_view_houses_data': scenic_view_houses_data,
        'pet_friendly_houses_data': pet_friendly_houses_data,
        'short_term_houses_data': short_term_houses_data,
        'historical_houses_data': historical_houses_data,
        'fully_furnished_houses_data': fully_furnished_houses_data,
        'discount_houses_data': discount_houses_data,
        'other_houses_data': other_houses_data,
    }
    return render(request, 'owners/browse_houses_public.html', context)

def build_houses_data(houses_qs):
    """
    Builds a list of dicts for each house, merging house medias +
    promotion medias, counting available vs. occupied rooms, etc.
    Returns a list of objects like:
      {
        'house': house_obj,
        'media': [...],
        'available_rooms': X,
        'occupied_rooms': Y,
      }
    """
    houses_data_list = []
    for house in houses_qs:
        # Combine house medias + promotion medias
        combined_media = []
        # 1) HouseMedia
        for hm in house.medias.all():
            combined_media.append({
                'type': 'photo' if hm.media_type == 'photo' else 'video',
                'file': hm.media_file.url,
                'caption': "",
            })
        # 2) PromotionMedia
        house_promos = [p for p in house.promotions.all() if p.room is None]
        for promo in house_promos:
            for pm in promo.media_items.all():
                combined_media.append({
                    'type': 'photo' if pm.media_type == 'image' else 'video',
                    'file': pm.file.url,
                    'caption': pm.caption if pm.caption else "",
                })

        # Count total, occupied, available
        total_rooms = house.rooms.count()
        occupied_count = house.rooms.filter(availability_status="Occupied").count()
        available_count = total_rooms - occupied_count

        houses_data_list.append({
            'house': house,
            'media': combined_media,
            'available_rooms': available_count,
            'occupied_rooms': occupied_count,
        })

    return houses_data_list


from django.shortcuts import render, get_object_or_404
from owners.models import House, HouseMedia, HousePromotion, Room, RoomMedia, PromotionMedia, Agent
from booking.models import Bill

def house_full_details_view(request, house_id):
    # Retrieve the specific house
    house = get_object_or_404(House, id=house_id)

    # Retrieve all house medias
    house_medias = list(house.medias.all())

    # Retrieve house-level promotions (those with room=None) and their medias
    house_promotions = HousePromotion.objects.filter(house=house, room__isnull=True)
    house_promotion_details = []
    for hp in house_promotions:
        promo_medias = hp.media_items.all()
        pm_list = [{
            'type': 'photo' if pm.media_type == 'image' else 'video',
            'file': pm.file.url,
            'caption': pm.caption or ""
        } for pm in promo_medias]
        house_promotion_details.append({
            'promotion': hp,
            'media': pm_list,
        })

    # Combine house medias with promotion medias
    combined_house_medias = [{
        'type': 'photo' if hm.media_type == 'photo' else 'video',
        'file': hm.media_file.url,
        'caption': ""
    } for hm in house_medias]

    for promo_block in house_promotion_details:
        for pm in promo_block['media']:
            combined_house_medias.append(pm)

    # Retrieve all rooms of the house
    rooms = house.rooms.all()
    rooms_data = []
    for rm in rooms:
        # Room medias
        room_medias = rm.medias.all()
        room_media_list = [{
            'type': 'photo' if rmm.media_type == 'photo' else 'video',
            'file': rmm.media_file.url,
            'caption': ""
        } for rmm in room_medias]

        # Room promotions and their medias
        room_promotions = rm.promotions.all()
        room_promotion_details = []
        for rp in room_promotions:
            rp_medias = rp.media_items.all()
            rp_media_list = [{
                'type': 'photo' if rpm.media_type == 'image' else 'video',
                'file': rpm.file.url,
                'caption': rpm.caption or ""
            } for rpm in rp_medias]
            room_promotion_details.append({
                'promotion': rp,
                'media': rp_media_list,
            })

        # Combine room media + room promotion media
        combined_room_medias = room_media_list[:]
        for rp_block in room_promotion_details:
            combined_room_medias.extend(rp_block['media'])

        rooms_data.append({
            'room': rm,
            'room_medias': combined_room_medias,
            'promotions': room_promotion_details,
        })

    # Retrieve assigned agents for this house (if any)
    # If you have a ManyToMany or a direct link, adjust accordingly
    assigned_agents = house.agents.all()  # This returns QuerySet of Agent objects

    # Retrieve bills for this house
    bills = house.bills.all()

    context = {
        'house': house,
        'combined_house_medias': combined_house_medias,
        'house_promotions': house_promotion_details,
        'rooms_data': rooms_data,
        'agents': assigned_agents,
        'bills': bills,
    }
    return render(request, 'owners/house_full_details.html', context)


from django.shortcuts import render

def register_error_view(request):
    # This view simply displays the template indicating that the user must register.
    return render(request, 'owners/register_error.html', {})


# owners/views.py
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

@csrf_exempt  # For simple testing; in production, use safer methods or token-based auth
def login_view_api(request):
    """
    API for login that returns JSON with success, message, and role.
    """
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # from form-data
        password = request.POST.get('password')
        
        user = authenticate(request, username=identifier, password=password)
        
        if user is not None:
            login(request, user)
            
            # Determine user role
            if user.is_superuser:
                role = 'superuser'
            elif hasattr(user, 'agent_profile'):
                role = 'agent'
            elif hasattr(user, 'property_owner'):
                if not user.property_owner.is_allowed:
                    return JsonResponse({
                        'success': False,
                        'message': 'Your account is not allowed to log in. Please contact support.'
                    }, status=403)
                role = 'propertyowner'
            elif hasattr(user, 'client'):
                role = 'client'
            else:
                role = 'unknown'
            
            return JsonResponse({
                'success': True,
                'message': f'Login success {role}',
                'role': role,
            }, status=200)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid username/email or password.'
            }, status=401)
    
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)

# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House
from .forms import HouseAdditionalFeaturesStep1Form

@login_required
def step1_additional_features_view(request, house_id):
    """
    Step 1: A view that allows a property owner to set the initial
    additional features (Boolean fields) for a given house.
    """
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # Redirect to some page in your app

    property_owner = request.user.property_owner

    # Get the house with matching ID that belongs to this property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseAdditionalFeaturesStep1Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "Step 1 features have been updated.")
            # Redirect to the next step, or wherever you want
            return redirect('step2_features', house_id=house_id)  
    else:
        form = HouseAdditionalFeaturesStep1Form(instance=house)

    context = {
        'form': form,
        'house': house
    }
    return render(request, 'owners/step1_additional_features.html', context)

# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House
from .forms import HouseAdditionalFeaturesStep2Form

@login_required
def step2_additional_features_view(request, house_id):
    """
    Step 2: A view that allows a property owner to set security features,
    design/structure details, location info, historical significance, etc.
    """
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or wherever you want non-owners to go

    property_owner = request.user.property_owner

    # Ensure the house belongs to the current property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseAdditionalFeaturesStep2Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "Step 2 features have been updated.")
            # Redirect to the next step (house_rent_as_whole) instead of house_list
            return redirect('house_rent_as_whole', house_id=house_id)
    else:
        form = HouseAdditionalFeaturesStep2Form(instance=house)

    context = {
        'form': form,
        'house': house,
    }
    return render(request, 'owners/step2_additional_features.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from .models import House
from .forms import HouseRentAsWholeForm

@login_required
def house_rent_as_whole_view(request, house_id):
    """
    A view that allows a property owner to set the house as
    rented as a whole and optionally set the total rent amount.
    """
    # Ensure only property owners can access
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or some fallback

    # Get the house, checking ownership
    house = get_object_or_404(House, pk=house_id, owner=request.user.property_owner)

    if request.method == 'POST':
        form = HouseRentAsWholeForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "House rent-as-whole settings updated successfully!")
            # Redirect to wherever you want after success:
            return redirect('house_list')  # or house detail, step, etc.
    else:
        form = HouseRentAsWholeForm(instance=house)

    context = {
        'form': form,
        'house': house
    }
    return render(request, 'owners/house_rent_as_whole.html', context)


# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House
from .forms import HouseAdditionalFeaturesStep1Form

@login_required
def update_house_step1_features(request, house_id):
    """
    Allows the property owner to update Step 1 additional features
    (boolean fields) of the given house.
    """
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or some other fallback page

    property_owner = request.user.property_owner

    # Fetch the House object owned by this property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseAdditionalFeaturesStep1Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "Step 1 additional features have been updated.")
            # Redirect to wherever you want after step1 is updated
            return redirect('house_list')  # or 'house_details', 'update_house_step2', etc.
    else:
        form = HouseAdditionalFeaturesStep1Form(instance=house)

    context = {
        'form': form,
        'house': house,
    }
    return render(request, 'owners/step1_additional_features.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House
from .forms import HouseAdditionalFeaturesStep2Form

@login_required
def update_house_step3_features(request, house_id):
    """
    Allows the property owner to update Step 3 additional features
    (Security, Design/Structure, Location, Historical Significance, Payment/Utilities)
    of the given house.
    """
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or wherever you want to redirect non-owners

    property_owner = request.user.property_owner

    # Fetch the House object owned by this property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseAdditionalFeaturesStep2Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "Step 3 additional features have been updated.")
            # Redirect wherever you want after a successful update
            return redirect('house_list')  # e.g., 'house_details' or next step
    else:
        form = HouseAdditionalFeaturesStep2Form(instance=house)

    context = {
        'form': form,
        'house': house,
    }
    return render(request, 'owners/step2_additional_features.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House
from .forms import HouseRentAsWholeForm

@login_required
def update_house_rent_as_whole(request, house_id):
    """
    Allows the property owner to update whether the house is rented as a whole,
    and the total rent for the whole house if applicable.
    """
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or wherever your app sends non-owners

    property_owner = request.user.property_owner

    # Fetch the House object, ensuring it belongs to the current property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseRentAsWholeForm(request.POST, instance=house)
        if form.is_valid():
            form.save()
            messages.success(request, "Rent-as-whole information updated successfully!")
            # Redirect wherever appropriate (house list, detail page, next step, etc.)
            return redirect('house_list')
    else:
        form = HouseRentAsWholeForm(instance=house)

    context = {
        'form': form,
        'house': house,
    }
    return render(request, 'owners/house_rent_as_whole.html', context)


# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import House, HouseUpdate
from .forms import HouseUpdateForm

@login_required
def create_house_update(request, house_id):
    """
    Allows a property owner to create a new HouseUpdate (photo or video)
    for one of their houses.
    """
    # Ensure the user is indeed a property owner
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')  # or some fallback

    property_owner = request.user.property_owner

    # Fetch the house, ensuring it belongs to this property owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    if request.method == 'POST':
        form = HouseUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't commit yet, we must assign the house first
            new_update = form.save(commit=False)
            new_update.house = house
            new_update.save()
            messages.success(request, "House update posted successfully!")
            # Redirect wherever you want after creation
            return redirect('house_list')
    else:
        form = HouseUpdateForm()

    context = {
        'form': form,
        'house': house,
    }
    return render(request, 'owners/create_house_update.html', context)

# owners/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import House, HouseUpdate

@login_required
def house_updates_view(request, house_id):
    """
    Retrieves all updates for the given house, deletes any updates older
    than 24 hours, and displays the remaining updates (photo or video).
    Also calculates the time remaining for each update.
    """
    if not hasattr(request.user, 'property_owner'):
        messages.error(request, "Only property owners can access this page.")
        return redirect('home')

    property_owner = request.user.property_owner
    house = get_object_or_404(House, pk=house_id, owner=property_owner)

    now = timezone.now()

    # Delete any updates older than 24 hours
    updates_qs = HouseUpdate.objects.filter(house=house)
    for update in updates_qs:
        if (now - update.created_at) >= timedelta(hours=24):
            update.delete()

    # Re-fetch updates
    updates = HouseUpdate.objects.filter(house=house)

    # For each update, compute the time remaining
    # e.g., "23 hours, 59 minutes left"
    for u in updates:
        elapsed = now - u.created_at
        # 24 hours minus elapsed
        remain = timedelta(hours=24) - elapsed
        # Convert remain to hours & minutes
        remain_hours = remain.seconds // 3600
        remain_minutes = (remain.seconds % 3600) // 60
        # e.g. "23h 59m"
        u.remaining_str = f"{remain_hours}h {remain_minutes}m left"

    context = {
        'house': house,
        'updates': updates,
    }
    return render(request, 'owners/house_updates.html', context)
