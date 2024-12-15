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
from settings.models import Region, District, Ward, Street
from .models import House
from .forms import HouseStep1Form
import json

def create_house_step1_view(request, house_id=None):
    print("=== create_house_step1_view CALLED ===")
    print(f"Request method: {request.method}")
    print(f"House ID: {house_id}")

    house = get_object_or_404(House, id=house_id) if house_id else None
    if house:
        print(f"Loaded existing house: ID={house.id}, Name={house.house_name}")
    else:
        print("No existing house loaded (creating new).")

    if request.method == "POST":
        print("POST request received. POST data:")
        print(request.POST)
        print("FILES data:")
        print(request.FILES)

        form = HouseStep1Form(request.POST, request.FILES, instance=house)
        print("Form initialized with POST and FILES")

        # Dynamically set querysets based on user selection
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
            print("Form is valid. Cleaning and saving data.")
            house = form.save(commit=False)
            print(f"Before assigning owner: House owner_id={house.owner_id}, Name={house.house_name}")
            print("Assigning house owner to current user's property_owner")
            house.owner = request.user.property_owner
            print("Saving house...")
            house.save()
            print(f"House saved successfully with ID={house.id}. Redirecting to step 2.")
            return redirect("create_house_step2", house_id=house.id)
        else:
            print("Form is not valid. Errors:")
            print(form.errors.as_data())
    else:
        print("GET request received. Initializing form with instance if present.")
        form = HouseStep1Form(instance=house)

    # Preload all data into Python lists
    regions = list(Region.objects.values("id", "name"))
    districts = list(District.objects.values("id", "name", "region_id"))
    wards = list(Ward.objects.values("id", "name", "district_id"))
    streets = list(Street.objects.values("id", "name", "ward_id"))

    print("Data preloaded for regions, districts, wards, and streets.")
    print(f"Number of Regions: {len(regions)}, Districts: {len(districts)}, Wards: {len(wards)}, Streets: {len(streets)}")

    context = {
        "form": form,
        "house": house,
        "regions_json": json.dumps(regions),
        "districts_json": json.dumps(districts),
        "wards_json": json.dumps(wards),
        "streets_json": json.dumps(streets),
    }
    print("Rendering template owners/create_house_step1.html with context.")
    return render(request, "owners/create_house_step1.html", context)

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

def create_house_step2_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    if request.method == "POST":
        form = HouseStep2Form(request.POST, instance=house)
        if form.is_valid():
            form.save()
            return redirect("create_house_step3", house_id=house.id)  # Redirect to step 3
    else:
        form = HouseStep2Form(instance=house)
    return render(request, "owners/create_house_step2.html", {"form": form, "house": house})


from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from .models import House, HouseMedia
from .forms import HouseMediaForm

def create_house_step3_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    if request.method == "POST":
        # We will look for fields like media_type_0, media_file_0, media_type_1, media_file_1, etc.
        # We'll iterate over all keys and group them by index
        prefix = 'media_'
        media_indices = set()
        for key in request.POST.keys():
            if key.startswith('media_type_'):
                idx = key.split('_')[-1]
                media_indices.add(idx)
        
        # For each idx in media_indices, we try to get the corresponding fields
        for idx in media_indices:
            m_type = request.POST.get(f'media_type_{idx}')
            m_file = request.FILES.get(f'media_file_{idx}')
            if m_type and m_file:
                # Create a HouseMedia object
                HouseMedia.objects.create(
                    house=house,
                    media_type=m_type,
                    media_file=m_file
                )

        return redirect("create_house_step4", house_id=house.id)  # Redirect to step 4
    else:
        # Just render the template with one media form set by default
        pass

    return render(request, "owners/create_house_step3.html", {"house": house})

from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Room
from .forms import RoomForm
from django.forms import formset_factory

from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Room
from .forms import RoomForm
from django.forms import formset_factory

def create_house_step4_view(request, house_id):
    print("=== create_house_step4_view CALLED ===")
    print(f"Request method: {request.method}")
    print(f"House ID: {house_id}")

    house = get_object_or_404(House, id=house_id)
    print(f"Loaded house: ID={house.id}, Name={house.house_name}, Number of Rooms={house.number_of_rooms}")
    
    number_of_rooms = house.number_of_rooms
    print(f"Number of rooms to create formset for: {number_of_rooms}")

    RoomFormSet = formset_factory(RoomForm, extra=number_of_rooms)

    if request.method == "POST":
        print("POST request received.")
        print("POST Data:", request.POST)
        print("FILES Data:", request.FILES)

        formset = RoomFormSet(request.POST, request.FILES)
        print("Formset initialized with POST data.")

        if formset.is_valid():
            print("Formset is valid. Proceeding to save rooms.")
            for i, form in enumerate(formset):
                if form.cleaned_data:
                    print(f"Room {i+1} cleaned_data:", form.cleaned_data)
                    room = Room(
                        house=house,
                        room_number=form.cleaned_data['room_number'],
                        description=form.cleaned_data['description'],
                        rental_price=form.cleaned_data['rental_price'],
                        availability_status=form.cleaned_data['availability_status'],
                    )
                    room.save()
                    print(f"Room {i+1} saved with ID={room.id}, Room number={room.room_number}")
                else:
                    print(f"Room {i+1} has no cleaned data. Skipping.")
            print("All rooms processed. Redirecting to step 5.")
            return redirect("create_house_step5", house_id=house.id)
        else:
            print("Formset is not valid. Errors:")
            # Print non-form errors from the formset
            non_form_errors = formset.non_form_errors()
            if non_form_errors:
                print("Formset non_form_errors:", non_form_errors)
            else:
                print("No non_form_errors in formset.")

            # Print management form errors if any
            management_form_errors = formset.management_form.errors
            if management_form_errors:
                print("Management form errors:", management_form_errors)
            else:
                print("No management form errors.")

            # Print each form's errors
            for i, form in enumerate(formset):
                if form.errors:
                    print(f"Room {i+1} errors:", form.errors.as_data())
                else:
                    print(f"Room {i+1} has no errors.")
    else:
        print("GET request received. Initializing formset with empty forms.")
        formset = RoomFormSet()

    print("Rendering create_house_step4.html with formset.")
    return render(request, "owners/create_house_step4.html", {"house": house, "formset": formset})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import House

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.db.models import Prefetch
from .models import House, HouseMedia, Room, RoomMedia

@login_required
def house_list_view(request):
    print("=== house_list_view CALLED ===")
    if not hasattr(request.user, 'property_owner'):
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Prefetch rooms and their media, house medias
    houses = (
        House.objects.filter(owner=request.user.property_owner)
        .prefetch_related(
            'medias',
            Prefetch('rooms', queryset=Room.objects.prefetch_related('medias'))
        )
    )

    # Compute room stats
    for house in houses:
        house.total_rooms = house.rooms.count()
        house.occupied_rooms = house.rooms.filter(availability_status="Occupied").count()
        house.available_rooms = house.total_rooms - house.occupied_rooms

    return render(request, "owners/house_list.html", {"houses": houses})

# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import House, Room, RoomMedia

def create_house_step5_view(request, house_id):
    house = get_object_or_404(House, id=house_id)
    rooms = house.rooms.all().order_by('room_number')

    if request.method == "POST":
        # We'll look for keys like media_type_{room_id}_{index} and media_file_{room_id}_{index}
        # For each room, find all indices and create RoomMedia objects.
        for room in rooms:
            # Collect indices for this room
            prefix_type = f'media_type_{room.id}_'
            prefix_file = f'media_file_{room.id}_'
            # Find all indices for this room
            indices = set()
            for key in request.POST.keys():
                if key.startswith(prefix_type):
                    idx = key.split('_')[-1]
                    indices.add(idx)

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

        return redirect("house_list")  # Redirect to next step
    else:
        # Just render the template with one media form set per room initially
        pass

    return render(request, "owners/create_house_step5.html", {"house": house, "rooms": rooms})


from django.views.decorators.http import require_GET
@login_required
def house_details_view(request, house_id):
    """
    View to display all details of a specific house, including its associated rooms and comments.
    """
    house = get_object_or_404(House, id=house_id)

    # Ensure the logged-in user owns the house
    if house.owner != request.user.property_owner:
        raise PermissionDenied("You do not have permission to view this house.")

    rooms = Room.objects.filter(house=house)

    # Retrieve all comments for the house, ordered by newest first
    comments = HouseComment.objects.filter(house=house).order_by('-created_at')
    comment_count = comments.count()

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

    houses_with_photos = []
    for house in houses:
        house_photos = [house.house_photo_1, house.house_photo_2, house.house_photo_3, house.house_photo_4, house.house_photo_5]
        rooms_with_photos = []

        # Only include rooms that are available
        for room in house.rooms.filter(availability_status="Available"):
            room_photos = [room.photo_1, room.photo_2, room.photo_3, room.photo_4, room.photo_5]
            rooms_with_photos.append({
                "room": room,
                "photos": [photo for photo in room_photos if photo]
            })

        # Determine if the current client has liked this house
        is_liked = HouseLike.objects.filter(client=client, house=house, is_liked=True).exists()

        # Retrieve the first assigned agent for this house (if any)
        assigned_agent = house.agents.first() if house.agents.exists() else None

        # Retrieve comments for the house
        comments = house.comments.all().order_by('-created_at')
        comment_count = comments.count()
        comment_data = []
        for comment in comments:
            comment_data.append({
                "comment": comment,
                "owned": (comment.client == client),
            })

        houses_with_photos.append({
            "house": house,
            "house_photos": [photo for photo in house_photos if photo],
            "rooms_with_photos": rooms_with_photos,
            "is_liked": is_liked,
            "comments": comment_data,
            "comment_count": comment_count,
            "assigned_agent": assigned_agent,  # Include the assigned agent
        })

    # Blank form for adding new comments
    new_comment_form = HouseCommentForm()

    return render(request, 'owners/browse_houses.html', {
        'form': form,
        'houses_with_photos': houses_with_photos,
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

@login_required
def client_house_details_view(request, house_id):
    """
    Display details of a specific house, including available rooms, promotions, and comments.
    """
    # Ensure only clients can access this view
    if not hasattr(request.user, 'client'):
        raise PermissionDenied("Only clients can access this view.")

    # Retrieve the house
    house = get_object_or_404(House, id=house_id)

    # Prepare combined house media (regular + promotion)
    house_regular_media = [
        {'type': 'video', 'file': house.house_video.url} if house.house_video else None,
    ] + [
        {'type': 'image', 'file': getattr(house, f'house_photo_{i}').url} 
        for i in range(1, 6) 
        if getattr(house, f'house_photo_{i}')
    ]

    # Remove None entries
    house_regular_media = [media for media in house_regular_media if media]

    # Retrieve house promotions and their media
    house_promotions = HousePromotion.objects.filter(house=house).order_by('-created_at')
    house_promotion_media = []
    for promo in house_promotions:
        for media in promo.media_items.all():
            house_promotion_media.append({
                'type': media.media_type,
                'file': media.file.url,
                'caption': media.caption,
                'promotion_description': promo.description,
            })

    # Combine regular and promotion media for house
    combined_house_media = house_regular_media + house_promotion_media

    # Prepare available rooms with combined media (regular + promotion)
    available_rooms = house.rooms.filter(availability_status="Available").order_by('room_number')
    rooms_with_combined_media = []
    for room in available_rooms:
        # Regular room media
        room_regular_media = [
            {'type': 'video', 'file': room.room_video.url} if room.room_video else None,
        ] + [
            {'type': 'image', 'file': getattr(room, f'photo_{i}').url} 
            for i in range(1, 6) 
            if getattr(room, f'photo_{i}')
        ]

        # Remove None entries
        room_regular_media = [media for media in room_regular_media if media]

        # Retrieve room promotions and their media
        room_promotions = HousePromotion.objects.filter(room=room).order_by('-created_at')
        room_promotion_media = []
        for promo in room_promotions:
            for media in promo.media_items.all():
                room_promotion_media.append({
                    'type': media.media_type,
                    'file': media.file.url,
                    'caption': media.caption,
                    'promotion_description': promo.description,
                })

        # Combine regular and promotion media for room
        combined_room_media = room_regular_media + room_promotion_media

        rooms_with_combined_media.append({
            'room': room,
            'media': combined_room_media,
            'promotions': room_promotions,  # Optional: if you want to display promotion descriptions
        })

    # Retrieve all comments for the house
    comments = house.comments.all().order_by('-created_at')
    comment_count = comments.count()

    # Prepare comments data
    comments_data = []
    for comment in comments:
        comments_data.append({
            "comment": comment,
            "owned": (comment.client == request.user.client),
        })

    # Initialize a blank form for adding new comments
    new_comment_form = HouseCommentForm()

    # Retrieve assigned agent details
    assigned_agents = house.agents.all()
    # Assuming each house has only one assigned agent; adjust if multiple agents can be assigned
    agent = assigned_agents.first() if assigned_agents.exists() else None

    return render(request, 'owners/client_house_details.html', {
        "house": house,
        "combined_house_media": combined_house_media,
        "rooms_with_combined_media": rooms_with_combined_media,
        "comments_data": comments_data,
        "comment_count": comment_count,
        "new_comment_form": new_comment_form,
        "agent": agent,
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from owners.models import Agent, House, Room, HousePromotion, PromotionMedia
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
        # House promotions (those with room=None)
        house_promotions = HousePromotion.objects.filter(agent=agent, house=house, room=None)
        house_promotion_details = []
        for hp in house_promotions:
            media = hp.media_items.all()
            house_promotion_details.append({
                'promotion': hp,
                'media': media
            })

        # Rooms with details, promotions, media
        room_data = []
        rooms = house.rooms.all()
        for rm in rooms:
            rm_promotions = HousePromotion.objects.filter(agent=agent, house=house, room=rm)
            rm_promotion_details = []
            for rp in rm_promotions:
                rm_media = rp.media_items.all()
                rm_promotion_details.append({
                    'promotion': rp,
                    'media': rm_media
                })

            # Gather room details and photos
            room_photos = [ph for ph in [rm.photo_1, rm.photo_2, rm.photo_3, rm.photo_4, rm.photo_5] if ph]
            room_data.append({
                'room': rm,
                'room_photos': room_photos,
                'room_video': rm.room_video,
                'promotions': rm_promotion_details,
            })

        # Bills for the house
        bills = house.bills.all()

        # House photos and video
        house_photos = [ph for ph in [house.house_photo_1, house.house_photo_2, house.house_photo_3, house.house_photo_4, house.house_photo_5] if ph]

        houses_data.append({
            'house': house,
            'house_video': house.house_video,
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
