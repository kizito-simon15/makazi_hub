import requests
import base64
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from django.http import JsonResponse
from owners.models import Room, BookingRule
from settings.models import Payment
from accounts.models import Client
from .models import Booking
from .forms import CreateBookingForm
from django.conf import settings
import os
import json


def get_mpesa_token():
    """Generate an access token for MPesa API."""
    try:
        print("Fetching MPesa access token...")
        consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        auth_url = os.getenv("MPESA_AUTH_URL")

        response = requests.get(auth_url, auth=(consumer_key, consumer_secret))
        print("MPesa token response:", response.json())

        response_data = response.json()
        if "access_token" in response_data:
            print("Access token fetched successfully.")
            return response_data["access_token"]
        raise Exception("Failed to get MPesa token")
    except Exception as e:
        print("Error fetching MPesa token:", str(e))
        raise e

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc, callback_url):
    """Initiate an STK Push request."""
    try:
        print(f"Initiating STK push for {phone_number}, Amount: {amount}...")
        access_token = get_mpesa_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        shortcode = os.getenv("MPESA_SHORTCODE")
        passkey = os.getenv("MPESA_PASSKEY")
        api_url = os.getenv("MPESA_API_URL")

        password = base64.b64encode((shortcode + passkey + timestamp).encode()).decode()

        # Ensure the phone number is in the correct format (strip '+' and ensure only digits)
        sanitized_phone_number = "".join(filter(str.isdigit, phone_number.lstrip('+')))

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Convert Decimal amount to float for JSON serialization
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": float(amount),  # Convert Decimal to float
            "PartyA": sanitized_phone_number,  # Customer's MPesa number
            "PartyB": shortcode,  # Business shortcode
            "PhoneNumber": sanitized_phone_number,  # Customer's MPesa number
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        print("Sanitized Phone Number:", sanitized_phone_number)
        print("Payload for STK push:", payload)
        response = requests.post(api_url, json=payload, headers=headers)
        print("STK push response:", response.json())

        return response.json()
    except Exception as e:
        print("Error initiating STK push:", str(e))
        return {"error": str(e)}

@login_required
def create_booking_view(request, room_id):
    # Ensure the user is a client
    if not hasattr(request.user, "client"):
        raise PermissionDenied("Only clients can book rooms.")

    print("Fetching room and client details...")
    client = request.user.client
    room = get_object_or_404(Room, id=room_id)

    # Check if the room is already occupied
    if room.availability_status == "Occupied":
        print(f"Room {room.room_number} is already occupied.")
        messages.error(request, f"Room {room.room_number} is already occupied and cannot be booked.")
        return redirect("browse_houses")

    house = room.house

    # Get the property owner's payment methods
    print(f"Fetching payment methods for house owner: {house.owner}")
    payment_methods = Payment.objects.filter(
        property_owner=house.owner, status=Payment.StatusChoices.ACTIVE
    )

    # Get the booking rule associated with this room's house
    rule = BookingRule.objects.filter(house=house).first()
    minimum_months_to_pay = rule.minimum_months_to_pay if rule else 1

    # Perform calculations
    total_amount_to_pay = room.rental_price * minimum_months_to_pay
    initial_amount_to_owner = (minimum_months_to_pay - 1) * room.rental_price
    amount_to_agent = room.rental_price  # 1 month's rent is paid to the agent

    print(f"Total Amount: {total_amount_to_pay}, Initial Amount to Owner: {initial_amount_to_owner}, Amount to Agent: {amount_to_agent}")

    if request.method == "POST":
        print("Handling form submission...")
        payment_method_id = request.POST.get("payment_method")
        selected_payment_method = Payment.objects.filter(id=payment_method_id).first()

        if selected_payment_method and selected_payment_method.provider == "M-Pesa":
            print(f"Selected Payment Method: {selected_payment_method.provider}")
            # Trigger MPesa STK Push
            callback_url = request.build_absolute_uri("/mpesa/callback/")
            transaction_desc = f"Payment for Room {room.room_number}"
            account_reference = f"Room-{room.id}"

            response = initiate_stk_push(
                phone_number=client.phone_number,
                amount=initial_amount_to_owner,
                account_reference=account_reference,
                transaction_desc=transaction_desc,
                callback_url=callback_url,
            )

            if "ResponseCode" in response and response["ResponseCode"] == "0":
                print("STK push successful.")
                messages.success(request, "Payment initiated. Please check your phone to complete the transaction.")
                return redirect("booking_confirmation", booking_id=room_id)
            else:
                print("STK push failed:", response.get('error', 'Unknown error'))
                messages.error(request, f"Failed to initiate payment: {response.get('error', 'Unknown error')}")
        else:
            print("Invalid or no payment method selected.")
            messages.error(request, "Please select a valid MPesa payment method.")

    return render(request, "booking/create_booking.html", {
        "room": room,
        "house": house,
        "rule": rule,
        "payment_methods": payment_methods,
        "total_amount_to_pay": total_amount_to_pay,
        "initial_amount_to_owner": initial_amount_to_owner,
        "amount_to_agent": amount_to_agent,
    })


def mpesa_callback(request):
    """Handle MPesa STK Push callback."""
    print("Received MPesa callback...")
    try:
        data = request.body.decode("utf-8")
        print("Callback Data:", data)

        callback_data = json.loads(data)
        result_code = callback_data.get("Body", {}).get("stkCallback", {}).get("ResultCode", None)
        metadata = callback_data.get("Body", {}).get("stkCallback", {}).get("CallbackMetadata", {}).get("Item", [])
        room_id = None
        for item in metadata:
            if item.get("Name") == "AccountReference":
                room_id = int(item.get("Value", 0))

        if result_code == 0:  # Transaction successful
            print(f"Transaction successful for Room ID: {room_id}")
            room = Room.objects.filter(id=room_id).first()
            if room:
                room.availability_status = "Occupied"
                room.save()
                print(f"Room {room.room_number} marked as occupied.")
                return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})
        else:
            print("Transaction failed or canceled.")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Transaction Failed"})
    except Exception as e:
        print("Error handling callback:", str(e))
        return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal Server Error"})

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from booking.models import Booking
from accounts.models import Client
from owners.models import House

@login_required
def booked_rooms_view(request):
    # Ensure the logged-in user is a client
    if not hasattr(request.user, "client"):
        raise PermissionDenied("Only clients can view their booked rooms.")

    client = request.user.client

    # Fetch all bookings for this client
    bookings = Booking.objects.filter(client=client).select_related("room", "room__house", "room__house__owner")

    booked_rooms = []
    for booking in bookings:
        room = booking.room
        house = room.house
        owner = house.owner
        agents = house.agents.all()  # Fetch all agents managing the house

        house_photos = [house.house_photo_1, house.house_photo_2, house.house_photo_3, house.house_photo_4, house.house_photo_5]
        room_photos = [room.photo_1, room.photo_2, room.photo_3, room.photo_4, room.photo_5]

        booked_rooms.append({
            "booking": booking,
            "room": room,
            "room_photos": [photo for photo in room_photos if photo],
            "house": house,
            "house_photos": [photo for photo in house_photos if photo],
            "owner": owner,
            "agents": agents,
        })

    return render(request, "booking/booked_rooms.html", {
        "booked_rooms": booked_rooms,
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from booking.models import Booking
from owners.models import House

@login_required
def owner_booked_rooms_view(request):
    try:
        # Ensure the logged-in user is a property owner
        if not hasattr(request.user, 'property_owner'):
            return HttpResponseForbidden("You do not have permission to view this page.")

        # Retrieve all houses for the logged-in property owner
        houses = House.objects.filter(owner=request.user.property_owner)

        # Create a context dictionary to group bookings by houses
        houses_with_booked_rooms = []

        for house in houses:
            booked_rooms = Booking.objects.filter(room__house=house)
            house_photos = [
                house.house_photo_1, house.house_photo_2, house.house_photo_3,
                house.house_photo_4, house.house_photo_5
            ]
            agents = house.agents.all()  # Fetch agents assigned to the house

            house_data = {
                "house": house,
                "photos": [photo for photo in house_photos if photo],
                "agents": agents,  # Include agent details
                "booked_rooms": [],
            }

            for booking in booked_rooms:
                room_photos = [
                    booking.room.photo_1, booking.room.photo_2, booking.room.photo_3,
                    booking.room.photo_4, booking.room.photo_5
                ]
                house_data["booked_rooms"].append({
                    "booking": booking,
                    "photos": [photo for photo in room_photos if photo]
                })

            houses_with_booked_rooms.append(house_data)

        return render(request, "booking/owner_booked_rooms.html", {
            "houses_with_booked_rooms": houses_with_booked_rooms,
        })
    except Exception as e:
        # Handle unexpected errors gracefully
        print(f"Error in owner_booked_rooms_view: {e}")
        return render(request, "booking/owner_booked_rooms.html", {
            "houses_with_booked_rooms": []
        })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from booking.models import Booking
from accounts.models import Client
from owners.models import House

@login_required
def owner_clients_view(request):
    try:
        # Ensure the logged-in user is a property owner
        if not hasattr(request.user, 'property_owner'):
            return HttpResponseForbidden("You do not have permission to view this page.")

        # Get all houses of the property owner
        houses = House.objects.filter(owner=request.user.property_owner)

        # Fetch all clients who have booked rooms in these houses
        bookings = Booking.objects.filter(room__house__in=houses).select_related("room", "client", "room__house")

        # Organize data by clients
        clients = {}
        for booking in bookings:
            client = booking.client
            house = booking.room.house
            if client not in clients:
                clients[client] = {
                    "client": client,
                    "bookings": [],
                    "house_photos": {
                        house: [
                            house.house_photo_1,
                            house.house_photo_2,
                            house.house_photo_3,
                            house.house_photo_4,
                            house.house_photo_5,
                        ]
                    },
                }
            clients[client]["bookings"].append(booking)

        return render(request, "booking/owner_clients.html", {
            "clients": clients.values(),
        })
    except Exception as e:
        print(f"Error in owner_clients_view: {e}")
        return render(request, "booking/owner_clients.html", {"clients": []})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import HttpResponseForbidden
from .forms import BillForm, SelectHouseForm
from .models import Bill
from owners.models import House


@login_required
def create_bills_view(request):
    print("Step 1: Property owner verification started.")
    if not hasattr(request.user, "property_owner"):
        print("Error: User is not a property owner.")
        return HttpResponseForbidden("You do not have permission to access this page.")
    print("Step 1: Property owner verified.")

    # Create forms
    print("Step 2: Rendering forms.")
    SelectHouseFormInstance = SelectHouseForm(owner=request.user.property_owner)
    BillFormSet = modelformset_factory(Bill, form=BillForm, extra=1)

    if request.method == "POST":
        print("Step 2: Processing POST request.")
        select_house_form = SelectHouseForm(request.POST, owner=request.user.property_owner)
        bill_formset = BillFormSet(request.POST, queryset=Bill.objects.none())

        if select_house_form.is_valid():
            print("Step 3: House selection form is valid.")
        else:
            print("Error: House selection form is invalid.")
            print(select_house_form.errors)

        if not bill_formset.is_valid():
            print("Error: Bill formset is invalid.")
            for i, form in enumerate(bill_formset):
                print(f"Form {i} errors: {form.errors}")
                if not form.cleaned_data:
                    print(f"Form {i} is empty.")
        else:
            print("Step 4: Bill formset is valid.")

        if select_house_form.is_valid() and bill_formset.is_valid():
            house = select_house_form.cleaned_data["house"]
            print(f"Step 5: Selected house: {house}")

            for form in bill_formset:
                if form.cleaned_data:  # Ignore empty forms
                    print(f"Step 6: Processing bill form: {form.cleaned_data}")
                    bill = form.save(commit=False)
                    bill.property_owner = request.user.property_owner
                    bill.house = house

                    try:
                        bill.save()
                        print(f"Step 7: Bill saved successfully: {bill}")
                    except Exception as e:
                        print(f"Error: Failed to save bill. {e}")
            print("Step 7: All valid bills saved. Redirecting to house bills.")
            return redirect("house_bills")  # Replace with your desired redirect URL
        else:
            print("Error: Form validation failed.")

    else:
        print("Step 2: Rendering GET request.")
        select_house_form = SelectHouseFormInstance
        bill_formset = BillFormSet(queryset=Bill.objects.none())

    print("Step 8: Rendering template.")
    return render(request, "booking/create_bills.html", {
        "select_house_form": select_house_form,
        "bill_formset": bill_formset,
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bill
from owners.models import House

@login_required
def house_bills_view(request):
    # Ensure the logged-in user is a property owner
    if not hasattr(request.user, "property_owner"):
        return HttpResponseForbidden("You do not have permission to view this page.")

    # Retrieve all houses with bills for the logged-in property owner
    houses_with_bills = House.objects.filter(
        owner=request.user.property_owner, bills__isnull=False
    ).distinct()

    # Include bills in the context
    context = {
        "houses_with_bills": [
            {"house": house, "bills": Bill.objects.filter(house=house)}
            for house in houses_with_bills
        ]
    }

    return render(request, "booking/house_bills.html", context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import BillForm
from .models import Bill

@login_required
def update_bill_view(request, bill_id):
    print("Step 1: Retrieving the bill for update.")
    bill = get_object_or_404(Bill, id=bill_id)

    # Ensure the logged-in user is the property owner of the bill
    if bill.property_owner != request.user.property_owner:
        print("Error: User is not authorized to update this bill.")
        return HttpResponseForbidden("You do not have permission to update this bill.")

    if request.method == "POST":
        print("Step 2: Processing POST request.")
        form = BillForm(request.POST, instance=bill)

        if form.is_valid():
            print("Step 3: Form is valid. Saving the bill.")
            form.save()
            print("Step 4: Bill updated successfully.")
            return redirect("house_bills")  # Replace with the appropriate URL
        else:
            print("Error: Form is invalid.")
            print(form.errors)
    else:
        print("Step 2: Rendering GET request.")
        form = BillForm(instance=bill)

    print("Step 5: Rendering template.")
    return render(request, "booking/update_bill.html", {"form": form, "bill": bill})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Bill

@login_required
def delete_bill_view(request, bill_id):
    print("Step 1: Retrieving the bill for deletion.")
    bill = get_object_or_404(Bill, id=bill_id)

    # Ensure the logged-in user is the property owner of the bill
    if bill.property_owner != request.user.property_owner:
        print("Error: User is not authorized to delete this bill.")
        return HttpResponseForbidden("You do not have permission to delete this bill.")

    if request.method == "POST":
        print("Step 2: Processing POST request for deletion.")
        bill.delete()
        print("Step 3: Bill deleted successfully.")
        return redirect("house_bills")  # Replace with the appropriate URL

    print("Step 2: Rendering GET request for confirmation.")
    return render(request, "booking/delete_bill.html", {"bill": bill})
