# makazihub/views_api.py
# If you prefer a separate "api" app, you could place it there as well.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(["POST"])
def api_login_view(request):
    """
    DRF-based endpoint to handle login via POST {identifier, password}.
    Returns JSON with user type or error.
    """
    identifier = request.data.get("identifier")
    password = request.data.get("password")

    # Basic validation
    if not identifier or not password:
        return Response(
            {"error": "Please provide both identifier and password"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Attempt authentication (using your custom EmailOrUsernameBackend)
    user = authenticate(request, username=identifier, password=password)
    if user is not None:
        # Actually log them in (creates a session if using SESSION auth)
        login(request, user)

        # Check the user type and return something descriptive
        if user.is_superuser:
            return Response({
                "status": "ok",
                "userType": "admin",
                "message": "Superuser login success",
            })

        elif hasattr(user, 'agent_profile'):
            return Response({
                "status": "ok",
                "userType": "agent",
                "message": "Agent login success",
            })

        elif hasattr(user, 'property_owner'):
            # Check if the property owner is allowed
            if not user.property_owner.is_allowed:
                return Response({
                    "status": "error",
                    "userType": "owner",
                    "message": "Your account is not allowed to log in. Please contact support."
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    "status": "ok",
                    "userType": "owner",
                    "message": "Owner login success",
                })

        elif hasattr(user, 'client'):
            return Response({
                "status": "ok",
                "userType": "client",
                "message": "Client login success",
            })

        # Default
        return Response({
            "status": "ok",
            "userType": "unknown",
            "message": "Login success, but user type not matched",
        })
    else:
        # Invalid credentials
        return Response({
            "error": "Invalid username/email or password. Please try again."
        }, status=status.HTTP_401_UNAUTHORIZED)
