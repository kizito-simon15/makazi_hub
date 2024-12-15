import requests
from django.conf import settings

def send_sms(to, message):
    url = 'https://api.nextsms.co.tz/api/sms/send'
    headers = {
        'Authorization': f'Bearer {settings.NEXTSMS_API_KEY}',
        'Content-Type': 'application/json',
    }
    payload = {
        'from': settings.NEXTSMS_SENDER_ID,
        'to': to,
        'text': message,
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
