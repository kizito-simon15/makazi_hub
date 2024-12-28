from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import PropertyOwnerRegistrationForm, ClientRegistrationForm
from .models import User, PropertyOwner, Client
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PropertyOwnerProfilePictureForm, ClientProfilePictureForm
from .models import PropertyOwner, Client

# Store verification codes in memory (for simplicity; use a DB for production)
verification_codes = {}

def unified_register_view(request):
    """
    Handles the registration process for both property owners and clients.
    """
    user_type = request.GET.get('user_type', 'owner')  # Default to property owner
    is_client = user_type == 'client'

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST) if is_client else PropertyOwnerRegistrationForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists. Please use a different email.")
                return redirect('register')

            # Save the user
            user = form.save(commit=False)
            user.is_active = False  # Make user inactive until verification
            user.save()

            # Save related model (PropertyOwner or Client)
            if is_client:
                Client.objects.create(
                    user=user,
                    first_name=form.cleaned_data.get('first_name'),
                    middle_name=form.cleaned_data.get('middle_name', ''),
                    surname=form.cleaned_data.get('surname'),
                    email=email,
                    phone_number=form.cleaned_data.get('phone_number'),
                )
            else:
                PropertyOwner.objects.create(
                    user=user,
                    first_name=form.cleaned_data.get('first_name'),
                    middle_name=form.cleaned_data.get('middle_name', ''),
                    surname=form.cleaned_data.get('surname'),
                )

            # Generate a 6-digit verification code
            verification_code = random.randint(100000, 999999)
            verification_codes[email] = verification_code

            # Send verification email
            send_mail(
                subject="Email Verification Code",
                message=f"Your verification code is {verification_code}. Do not share this code with anyone.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            # Redirect to verification page
            return redirect(f'/accounts/verify-email/?email={email}')
    else:
        form = ClientRegistrationForm() if is_client else PropertyOwnerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'is_client': is_client,
    })


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_related_profile(sender, instance, created, **kwargs):
    """
    Automatically create PropertyOwner or Client profiles when a User is created.
    """
    if created:
        if hasattr(instance, 'property_owner'):
            PropertyOwner.objects.create(user=instance)
        elif hasattr(instance, 'client'):
            Client.objects.create(user=instance)

def verify_email_view(request):
    """
    Handles the email verification process.
    Activates the user if the verification code matches.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')

        if email in verification_codes and str(verification_codes[email]) == code:
            # Activate the user
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()

            # Remove the code from memory
            del verification_codes[email]

            # Redirect to success page
            return redirect('success')

        # Invalid code
        messages.error(request, "Invalid verification code. Please try again.")
        return render(request, 'accounts/verify_email.html', {'email': email})

    # Handle GET requests with email in the query string
    email = request.GET.get('email', None)
    if email:
        return render(request, 'accounts/verify_email.html', {'email': email})
    
    return redirect('register')

def success_view(request):
    """
    Displays a success message after successful registration and email verification.
    Redirects the user to the login page after 10 seconds.
    """
    return render(request, 'accounts/success.html')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import random

# Store verification codes in memory (for simplicity; use a DB for production)
verification_codes = {}

def resend_verification_code_view(request):
    """
    Handles resending the verification code to the user's email.
    """
    email = request.GET.get('email')  # Retrieve the email from the query parameters

    if not email or not User.objects.filter(email=email).exists():
        messages.error(request, "Invalid email address or email not registered.")
        return redirect('register')

    # Generate a new 6-digit verification code
    verification_code = random.randint(100000, 999999)
    verification_codes[email] = verification_code

    # Send the new verification email
    send_mail(
        subject="Resend Email Verification Code",
        message=f"Your new verification code is {verification_code}. Do not share this code with anyone.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

    messages.success(request, "A new verification code has been sent to your email.")
    return redirect(f'/accounts/verify-email/?email={email}')


# owners/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()
def login_view(request):
    """
    Handles user login and redirects based on user type.
    Allows authentication using either username or email.
    Utilizes a custom authentication backend.
    """
    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # Can be username or email
        password = request.POST.get('password')

        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)

            # Superuser redirection
            if user.is_superuser:
                return redirect('admin_dashboard')

            # Agent login
            if hasattr(user, 'agent_profile'):
                return redirect('agent_dashboard')

            # Property owner restriction
            if hasattr(user, 'property_owner'):
                if not user.property_owner.is_allowed:
                    messages.error(request, "Your account is not allowed to log in. Please contact support.")
                    return render(request, 'accounts/login.html')
                else:
                    return redirect('owner_dashboard')

            # Client login (allowed regardless of is_allowed)
            if hasattr(user, 'client'):
                return redirect('client_dashboard')

            # Default redirection if user type not matched
            return redirect('login')
        else:
            messages.error(request, "Invalid username/email or password. Please try again.")

    return render(request, 'accounts/login.html')

# accounts/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

User = get_user_model()

@csrf_exempt
def login_json_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        identifier = data.get('identifier')
        password = data.get('password')
        if not identifier or not password:
            return JsonResponse({"success": False, "message": "Missing fields"}, status=400)

        user = authenticate(username=identifier, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "message": "Login success"}, status=200)
        else:
            return JsonResponse({"success": False, "message": "Invalid creds"}, status=401)
    else:
        return JsonResponse({"success": False, "message": "Use POST"}, status=405)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from accounts.models import PropertyOwner, Client
from owners.models import Agent
from accounts.utils import (
    generate_growth_chart,
    generate_statistics_bar_chart,
    generate_houses_by_region_chart,
    generate_rooms_pie_chart,
)

@login_required
def admin_dashboard(request):
    """
    Admin dashboard accessible only to superusers.
    Shows multiple statistics and charts:
    - Totals: Users, Owners, Clients, Agents
    - Growth chart (line) + advice
    - Statistics bar chart (Owners, Agents, Clients, Houses, Rooms)
    - Houses by region bar chart + advice
    - Rooms distribution pie chart (by region) + advice
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")

    User = get_user_model()
    total_users = User.objects.count()
    total_owners = PropertyOwner.objects.count()
    total_clients = Client.objects.count()
    total_agents = Agent.objects.count()

    # Generate growth chart and advice
    growth_image_base64, growth_advice = generate_growth_chart()

    # Generate statistics bar chart (owners, agents, clients, houses, rooms)
    statistics_image_base64, totals_info = generate_statistics_bar_chart()

    # Generate houses by region chart
    houses_region_image, region_counts, region_advice, total_houses = generate_houses_by_region_chart()

    # Generate rooms pie chart by region
    rooms_pie_image, rooms_pie_advice, rooms_pie_total, rooms_distribution = generate_rooms_pie_chart()

    context = {
        'total_users': total_users,
        'total_owners': total_owners,
        'total_clients': total_clients,
        'total_agents': total_agents,
        'growth_chart': growth_image_base64,
        'growth_advice': growth_advice,
        'statistics_chart': statistics_image_base64,
        'totals_info': totals_info,
        'houses_region_chart': houses_region_image,
        'region_counts': region_counts,
        'region_advice': region_advice,
        'total_houses': total_houses,
        'rooms_pie_chart': rooms_pie_image,
        'rooms_pie_advice': rooms_pie_advice,
        'rooms_pie_total': rooms_pie_total,
        'rooms_distribution': rooms_distribution,
    }

    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def owner_dashboard(request):
    """
    Owner dashboard accessible only to property owners.
    """
    if not hasattr(request.user, 'property_owner'):
        return HttpResponseForbidden("You are not authorized to access this page.")
    return render(request, 'accounts/owner_dashboard.html')

@login_required
def client_dashboard(request):
    """
    Client dashboard accessible only to clients.
    """
    if not hasattr(request.user, 'client'):
        return HttpResponseForbidden("You are not authorized to access this page.")
    return render(request, 'accounts/client_dashboard.html')

from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import User
import random

# Store reset codes in memory (use a DB for production)
reset_codes = {}

def forgot_password_view(request):
    """
    Handles the forgot password process.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        new_username = request.POST.get('new_username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/forgot_password.html')

        # Check if email exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            return render(request, 'accounts/forgot_password.html')

        # Generate a 6-digit code
        confirmation_code = random.randint(100000, 999999)
        reset_codes[email] = {'code': confirmation_code, 'new_username': new_username, 'new_password': new_password}

        # Send confirmation email
        send_mail(
            subject="Password Reset Confirmation Code",
            message=f"Your password reset confirmation code is {confirmation_code}. Do not share this code with anyone.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, "A confirmation code has been sent to your email.")
        return redirect(f'/accounts/confirm-reset/?email={email}')

    return render(request, 'accounts/forgot_password.html')


def confirm_reset_view(request):
    """
    Handles confirmation of reset codes and updates the username and password.
    """
    email = request.GET.get('email')
    if request.method == 'POST':
        code = request.POST.get('code')

        # Verify the code
        if email in reset_codes and str(reset_codes[email]['code']) == code:
            new_username = reset_codes[email]['new_username']
            new_password = reset_codes[email]['new_password']

            # Update username and password
            user = User.objects.get(email=email)
            user.username = new_username
            user.password = make_password(new_password)
            user.save()

            # Remove the code from memory
            del reset_codes[email]

            messages.success(request, "Your username and password have been updated.")
            return redirect('success')

        messages.error(request, "Invalid confirmation code. Please try again.")
        return render(request, 'accounts/confirm_reset.html', {'email': email})

    return render(request, 'accounts/confirm_reset.html', {'email': email})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import PropertyOwner, Client

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import PropertyOwner, Client

from django.shortcuts import render
from .models import PropertyOwner, Client

def users_overview_view(request):
    if not request.user.is_superuser:
        return redirect('login')  # Only superuser can access

    # Retrieve property owners
    owner_users = [
        {
            'id': owner.user.id,
            'username': owner.user.username,
            'fullname': f"{owner.first_name} {owner.middle_name or ''} {owner.surname}".strip(),
            'email': owner.user.email,
            'phone_number1': owner.user.phone_number1,
            'phone_number2': owner.user.phone_number2,
            'is_allowed': owner.is_allowed,
        }
        for owner in PropertyOwner.objects.select_related('user').all()
    ]

    # Retrieve clients
    client_users = [
        {
            'id': client.user.id,
            'username': client.user.username,
            'fullname': f"{client.first_name} {client.middle_name or ''} {client.surname}".strip(),
            'email': client.email,
            'phone_number1': client.phone_number,
            'is_allowed': client.is_allowed,
        }
        for client in Client.objects.select_related('user').all()
    ]

    return render(request, 'accounts/users_overview.html', {
        'owner_users': owner_users,
        'client_users': client_users,
    })

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)
    return redirect('login')


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import User

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import User

@login_required
def delete_user_confirmation_view(request, user_id):
    """
    Displays a confirmation page for deleting a user.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        # If confirmed, delete the user
        user.delete()
        return redirect('users_overview')  # Redirect to the users overview page
    
    return render(request, 'accounts/confirm_delete.html', {'user': user})


@login_required
def toggle_is_allowed_view(request, user_id):
    """
    Toggles the `is_allowed` field for a user (superuser-only access).
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    
    if hasattr(user, 'property_owner'):
        user.property_owner.is_allowed = not user.property_owner.is_allowed
        user.property_owner.save()
    elif hasattr(user, 'client'):
        user.client.is_allowed = not user.client.is_allowed
        user.client.save()
    else:
        return HttpResponseForbidden("This user does not have a valid profile to toggle permissions.")
    
    return redirect('users_overview')  # Redirect to the users overview page

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden
from .models import User

@login_required
def delete_user_view(request, user_id):
    """
    Deletes a user if the logged-in user is a superuser.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to perform this action.")
    
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('users_overview')  # Redirect to the users overview page

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.models import PropertyOwner  # Ensure correct import path

@login_required
def owner_details_view(request):
    # Check if user has a property_owner profile
    if not hasattr(request.user, 'property_owner'):
        return HttpResponseForbidden("You do not have permission to view this page.")

    owner = request.user.property_owner
    return render(request, "accounts/owner_details.html", {"owner": owner})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from accounts.forms import PropertyOwnerUpdateForm

@login_required
def owner_update_view(request):
    if not hasattr(request.user, 'property_owner'):
        return HttpResponseForbidden("You do not have permission to view this page.")
    
    owner = request.user.property_owner

    if request.method == "POST":
        form = PropertyOwnerUpdateForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            # Update PropertyOwner fields
            owner.first_name = form.cleaned_data['first_name']
            owner.middle_name = form.cleaned_data['middle_name']
            owner.surname = form.cleaned_data['surname']

            if form.cleaned_data.get('profile_picture'):
                owner.profile_picture = form.cleaned_data['profile_picture']

            owner.save()

            # Update User fields
            user = request.user
            user.phone_number1 = form.cleaned_data['phone_number1']
            user.phone_number2 = form.cleaned_data['phone_number2']
            user.save()

            return redirect('owner_details')  # Redirect to owner details page
    else:
        form = PropertyOwnerUpdateForm(request.user)

    return render(request, 'accounts/owner_update.html', {'form': form})

@login_required
def upload_property_owner_picture(request):
    property_owner = get_object_or_404(PropertyOwner, user=request.user)
    if request.method == 'POST':
        form = PropertyOwnerProfilePictureForm(request.POST, request.FILES, instance=property_owner)
        if form.is_valid():
            form.save()
            return redirect('house_list')  # Redirect to an appropriate page
    else:
        form = PropertyOwnerProfilePictureForm(instance=property_owner)
    return render(request, 'accounts/upload_property_owner_picture.html', {'form': form})


@login_required
def upload_client_picture(request):
    client = get_object_or_404(Client, user=request.user)
    if request.method == 'POST':
        form = ClientProfilePictureForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            form.save()
            return redirect('client_dashboard')  # Redirect to an appropriate page
    else:
        form = ClientProfilePictureForm(instance=client)
    return render(request, 'accounts/upload_client_picture.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Client

@login_required
def customer_details_view(request):
    """
    View to retrieve and display all details of the logged-in customer.
    """
    try:
        # Retrieve the logged-in client's details
        client = get_object_or_404(Client, user=request.user)
    except Client.DoesNotExist:
        return render(request, "clients/error.html", {"message": "Client profile not found."})

    return render(request, "accounts/customer_details.html", {"client": client})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
from .forms import ClientUpdateForm

@login_required
def update_client_details(request):
    """
    View to update client details.
    """
    client = get_object_or_404(Client, user=request.user)

    if request.method == 'POST':
        form = ClientUpdateForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Your details have been updated successfully.")
            return redirect('customer_details')  # Redirect to client details page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ClientUpdateForm(instance=client)

    return render(request, 'accounts/update_client_details.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from accounts.models import Client

@login_required
def list_clients_view(request):
    # Ensure only superuser can access
    if not request.user.is_superuser:
        raise PermissionDenied("Only superusers can access this page.")
    
    clients = Client.objects.select_related('user').all().order_by('id')
    return render(request, 'accounts/client_list.html', {'clients': clients})


from django.shortcuts import render
from owners.models import Agent

def admin_agent_list_view(request):
    agents = Agent.objects.all()  # Retrieve all agents from the database
    context = {
        'agents': agents
    }
    return render(request, 'accounts/agents_list.html', context)

from django.shortcuts import render
from .models import Client

def admin_client_list_view(request):
    # Retrieve all clients from the database
    clients = Client.objects.all()
    context = {
        'clients': clients
    }
    return render(request, 'accounts/admin_client_list.html', context)

from django.shortcuts import render
from accounts.models import PropertyOwner

def admin_owner_list_view(request):
    owners = PropertyOwner.objects.all().select_related('user').prefetch_related('houses__promotions__media_items')
    # Using select_related and prefetch_related to optimize DB queries:
    # - select_related('user') will fetch the related user for each PropertyOwner in one go.
    # - prefetch_related('houses__promotions__media_items') will fetch all related houses, their promotions, and media.

    context = {
        'owners': owners
    }
    return render(request, 'accounts/admin_owners_list.html', context)

from django.http import JsonResponse

@login_required
def admin_dashboard_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    # e.g. gather data for the admin
    data = {
        'total_users': 100,
        'total_owners': 30,
        'total_agents': 20,
        'total_clients': 50,
        # maybe base64 for charts or text advice
    }
    return JsonResponse(data, status=200)
