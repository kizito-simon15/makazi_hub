from django.test import TestCase
from unittest.mock import patch
from booking.views import get_mpesa_token, initiate_stk_push
from owners.models import Room, BookingRule, House
from settings.models import Payment
from accounts.models import Client, User, PropertyOwner
from django.urls import reverse


class MpesaIntegrationTests(TestCase):

    def setUp(self):
        # Create test user and assign roles
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password"
        )
        self.client_user = Client.objects.create(
            user=self.user, 
            phone_number="+255741943155"
        )

        # Create a property owner with a unique email
        self.owner_user = User.objects.create_user(
            username="owneruser",
            email="owneruser@example.com",
            password="password"
        )
        self.property_owner = PropertyOwner.objects.create(
            user=self.owner_user,
            first_name="OwnerFirstName",
            surname="OwnerSurname",
            is_allowed=True,
        )

        # Create a payment method for the property owner
        self.payment_method = Payment.objects.create(
            property_owner=self.property_owner,
            provider="M-Pesa",
            method_name="Mobile Money",
            account_details="Test Account",
            status="Active",
        )

        # Create a test house (if needed for the room)
        self.house = House.objects.create(
            owner=self.property_owner,
            house_name="Test House",
            region="Test Region",
            district="Test District",
            ward="Test Ward",
            street="Test Street",
            house_number="1234",
        )

        # Create a test room
        self.room = Room.objects.create(
            house=self.house,
            room_number=100,
            description="Test Room",
            rental_price=60000,
            availability_status="Available",
        )

        # Create a booking rule for the house
        self.booking_rule = BookingRule.objects.create(
            owner=self.property_owner,
            house=self.house,
            minimum_months_to_pay=2,
        )

    @patch("requests.get")
    def test_get_mpesa_token(self, mock_get):
        # Mock the MPesa token response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"access_token": "test_token", "expires_in": "3599"}

        token = get_mpesa_token()
        self.assertEqual(token, "test_token")
        mock_get.assert_called_once_with(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            auth=("test_key", "test_secret")
        )

    @patch("requests.post")
    @patch("requests.get")
    def test_initiate_stk_push(self, mock_get, mock_post):
        # Mock token generation
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"access_token": "test_token"}

        # Mock STK push response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"ResponseCode": "0", "CustomerMessage": "Success"}

        response = initiate_stk_push(
            phone_number="254708374149",  # Sandbox test number
            amount=40000.0,
            account_reference="Room-1",
            transaction_desc="Payment for Room 100",
            callback_url="http://127.0.0.1:8000/mpesa/callback/",
        )
        self.assertEqual(response["ResponseCode"], "0")
        self.assertEqual(response["CustomerMessage"], "Success")
        mock_post.assert_called_once()

    def test_room_booking_flow(self):
        # Simulate booking flow
        self.client.login(username="testuser", password="password")

        response = self.client.get(reverse("create_booking", args=[self.room.id]))
        self.assertEqual(response.status_code, 200)

        post_data = {
            "payment_method": self.payment_method.id,
        }
        response = self.client.post(reverse("create_booking", args=[self.room.id]), post_data)
        self.assertEqual(response.status_code, 302)  # Redirect to booking confirmation
        self.room.refresh_from_db()
        self.assertEqual(self.room.availability_status, "Occupied")
