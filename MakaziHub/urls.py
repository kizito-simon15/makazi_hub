"""
URL configuration for MakaziHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from owners.views import browse_houses_public_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views_api import api_login_view   # <--- We'll create views_api.py for DRF-based views.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', browse_houses_public_view, name='browse_houses_public'),  # Redirect root URL to the sign-up page
    path('owners/', include('owners.urls')),
    path('settings/', include('settings.urls')),
    path('booking/', include('booking.urls')),  # Adjust path as needed
    path('api/', include('owners.api_urls')),
    path('api/login/', api_login_view, name='api_login'),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
