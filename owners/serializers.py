from rest_framework import serializers
from .models import House, Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'description', 'rental_price', 'availability_status', 'house']

class HouseSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)  # To include rooms info if needed
    class Meta:
        model = House
        fields = [
            'id', 'owner', 'profile_picture', 'region', 'district', 'ward', 'street', 
            'house_number', 'house_name', 'number_of_rooms', 'furnishing_status', 'amenities', 
            'utilities_included', 'house_type', 'flooring_and_finishing', 'land_size', 
            'proximity_information', 'rules_and_restrictions', 'contact_information', 'insurance_details',
            'rooms'
        ]
