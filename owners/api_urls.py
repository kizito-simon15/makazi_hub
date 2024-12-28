from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import HouseViewSet, RoomViewSet

router = DefaultRouter()
router.register('houses', HouseViewSet, basename='house')
router.register('rooms', RoomViewSet, basename='room')

urlpatterns = [
    path('', include(router.urls)),
]
