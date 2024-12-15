from django.urls import path
from .views import create_booking_view, mpesa_callback, booked_rooms_view, owner_booked_rooms_view, owner_clients_view, create_bills_view, house_bills_view, update_bill_view, delete_bill_view

from . import views

urlpatterns = [
    path('rooms/<int:room_id>/book/', create_booking_view, name='create_booking'),
    path('mpesa/callback/', mpesa_callback, name='mpesa_callback'),
    path('booked/rooms/', booked_rooms_view, name="booked_rooms"),
    path('owner/booked/rooms/', owner_booked_rooms_view, name="owner_booked_rooms"),
    path('owner/clients/', owner_clients_view, name="owner_clients"),
    path("create-bills/", create_bills_view, name="create_bills"),
    path("house-bills/", house_bills_view, name="house_bills"),
    path("update-bill/<int:bill_id>/", update_bill_view, name="update_bill"),
    path("delete-bill/<int:bill_id>/", delete_bill_view, name="delete_bill"),
]
