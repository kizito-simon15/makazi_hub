import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
SENDER_ID = os.getenv('NEXTSMS_SENDER_ID')  # Your Sender ID
PHONE_NUMBER = '255741943155'  # Test phone number
PRODUCTION_API_URL = 'https://messaging-service.co.tz/api/sms/v1/text/single'  # Production URL

# Use the Base64-encoded username:password string
BASE64_AUTH_STRING = "Ym9henNpbW9uN0BnbWFpbC5jb206dWZ1bnVvMzk="

def send_sms(to, message):
    """
    Sends an SMS using the NextSMS API with detailed debugging.
    :param to: Recipient phone number.
    :param message: Message content.
    :return: Response from the API.
    """
    headers = {
        'Authorization': f'Basic {BASE64_AUTH_STRING}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    payload = {
        'from': SENDER_ID,
        'to': to,
        'text': message,
        'reference': 'prod_reference_001',  # Optional reference
    }

    print("\n--- Debugging Information ---")
    print(f"Request URL: {PRODUCTION_API_URL}")
    print(f"Authorization Header: {headers['Authorization']}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\nSending request...")

    try:
        response = requests.post(PRODUCTION_API_URL, headers=headers, json=payload)
        print("\n--- Response Information ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("\n--- Error Occurred ---")
        print(f"Error: {e}")
        print("\n--- Headers ---")
        print(headers)
        print("\n--- Payload ---")
        print(json.dumps(payload, indent=2))
        return {'error': str(e)}

# Test the function
if __name__ == '__main__':
    test_message = "Hello, this is a test message from MakaziHub!"
    response = send_sms(PHONE_NUMBER, test_message)
    print("\n--- Final Response ---")
    print(response)
