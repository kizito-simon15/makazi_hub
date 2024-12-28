from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])  # Let anyone attempt login
def login_api_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)

            # Determine the user's role
            if user.is_superuser:
                role = 'superuser'
            elif hasattr(user, 'agent_profile'):
                role = 'agent'
            elif hasattr(user, 'property_owner'):
                # Check if allowed
                if not user.property_owner.is_allowed:
                    return JsonResponse({
                        'success': False,
                        'message': 'Your account is not allowed to log in. Please contact support.'
                    }, status=403)
                role = 'propertyowner'
            elif hasattr(user, 'client'):
                role = 'client'
            else:
                # Fallback if no matched role
                role = 'unknown'

            return JsonResponse({
                'success': True,
                'message': f'Login success {role}',
                'role': role
            })

        # If authentication fails
        return JsonResponse({
            'success': False,
            'message': 'Invalid username/email or password.'
        }, status=401)

    # If not POST, return method not allowed
    return JsonResponse({'detail': 'Method not allowed.'}, status=405)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

from accounts.models import PropertyOwner, Client
from owners.models import Agent
from accounts.utils import (
    generate_growth_chart,
    generate_statistics_bar_chart,
    generate_houses_by_region_chart,
    generate_rooms_pie_chart,
)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_dashboard_api(request):
    """
    Returns JSON data similar to what the admin_dashboard view provides:
    - Totals: Users, Owners, Clients, Agents
    - Growth chart + advice
    - Statistics bar chart data
    - Houses by region chart data
    - Rooms pie chart data
    NOTE: This requires the user be a superuser (admin).
    """
    # Ensure the user is superuser
    if not request.user.is_superuser:
        return Response(
            {"detail": "You are not authorized to access this page."},
            status=403
        )

    User = get_user_model()
    total_users = User.objects.count()
    total_owners = PropertyOwner.objects.count()
    total_clients = Client.objects.count()
    total_agents = Agent.objects.count()

    # Generate the same charts/data as your HTML admin_dashboard
    growth_image_base64, growth_advice = generate_growth_chart()
    statistics_image_base64, totals_info = generate_statistics_bar_chart()
    houses_region_image, region_counts, region_advice, total_houses = generate_houses_by_region_chart()
    rooms_pie_image, rooms_pie_advice, rooms_pie_total, rooms_distribution = generate_rooms_pie_chart()

    # Prepare JSON response
    data = {
        "total_users": total_users,
        "total_owners": total_owners,
        "total_clients": total_clients,
        "total_agents": total_agents,
        "growth_chart": growth_image_base64,
        "growth_advice": growth_advice,
        "statistics_chart": statistics_image_base64,
        "totals_info": totals_info,
        "houses_region_chart": houses_region_image,
        "region_counts": region_counts,
        "region_advice": region_advice,
        "total_houses": total_houses,
        "rooms_pie_chart": rooms_pie_image,
        "rooms_pie_advice": rooms_pie_advice,
        "rooms_pie_total": rooms_pie_total,
        "rooms_distribution": rooms_distribution,
    }

    return Response(data, status=200)
