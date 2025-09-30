import requests
from datetime import datetime
from openai import AzureOpenAI
from config import (
    CAL_BASE, CAL_API_KEY, CAL_API_VERSION,
    AZURE_ENDPOINT, AZURE_KEY, AZURE_DEPLOYMENT, AZURE_API_VERSION
)


client = AzureOpenAI(
    api_key=AZURE_KEY,
    api_version=AZURE_API_VERSION,
    azure_endpoint=AZURE_ENDPOINT,
)

# In-memory storage for demo
BOOKINGS = {}
COMPLAINTS = []
SERVICES = {
    "haircut": {"duration_minutes": 30, "price": 300},
    "beard_trim": {"duration_minutes": 20, "price": 150},
    "Spa": {"duration_minutes": 25, "price": 1000}
}

BARBERS = {
    "ravi": {"id": 1, "name": "Ravi", "specialty": "Haircuts"},
    "rahul": {"id": 2, "name": "Rahul", "specialty": "Beard Trims"},
    "rohan": {"id": 3, "name": "Rohan", "specialty": "Spa"}
}

def list_barbers():
    lines = ["Here are our available barbers:"]
    for b in BARBERS.values():
        lines.append(f"- {b['name']} ({b['specialty']})")
    return "\n".join(lines)



def list_services():
    lines = ["Here are our services:"]
    for s, meta in SERVICES.items():
        lines.append(f"- {s.replace('_',' ').title()}: ₹{meta['price']} ({meta['duration_minutes']} mins)")
    return "\n".join(lines)


def create_booking(event_type_id, start, timezone, name, email, notes=""):
    url = f"{CAL_BASE}/v2/bookings"
    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": CAL_API_VERSION,
        "Content-Type": "application/json"
    }
    payload = {
        "eventTypeId": int(event_type_id),
        "start": start,
        "timeZone": timezone,
        "language": "en",
        "metadata": {},
        "attendees": [{"name": name, "email": email}],
        "notes": notes,
        "location": {},   
        "responses": {    
            "name": name,
            "email": email
        }
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=30)

    if resp.status_code != 201:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        raise Exception(f"Booking failed ({resp.status_code}): {err}")

    return resp.json()

def list_bookings():
    return list(BOOKINGS.values())


def submit_complaint(user, text, booking_uid=None):
    complaint = {
        "id": len(COMPLAINTS) + 1,
        "user": user,
        "booking_uid": booking_uid,
        "text": text,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "status": "received"
    }
    COMPLAINTS.append(complaint)
    return complaint
