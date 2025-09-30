import requests
import json
from config import CAL_API_KEY, CAL_API_VERSION, CAL_BASE


def create_booking(event_type_id, start, timezone, name, email, notes=""):
    """
    Creates a booking in Cal.com v2 API
    Args:
        event_type_id (int): The Cal.com Event Type ID
        start (str): Start datetime in UTC ISO format (YYYY-MM-DDTHH:MM:SSZ)
        timezone (str): User timezone (IANA format, e.g., Asia/Kolkata)
        name (str): Customer name
        email (str): Customer email
        notes (str): Optional notes
    """
    url = f"{CAL_BASE}/v2/bookings"

    headers = {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "Content-Type": "application/json",
        "cal-api-version": CAL_API_VERSION,
    }

    payload = {
        "eventTypeId": int(event_type_id),
        "start": start,                  # only start required, no "end"
        "timeZone": timezone,            # must be capital Z
        "language": "en",
        "metadata": {},                  # must be object (not None)
        "attendees": [
            {"name": name, "email": email}
        ],
        "notes": notes,
        "location": {},
        "responses": {
            "name": name,
            "email": email
        }
    }

    # Debug: print the payload before sending
    print("\n=== Sending payload to Cal.com ===")
    print(json.dumps(payload, indent=2))

    response = requests.post(url, headers=headers, json=payload)
    print("\n=== Response ===")
    print("Status:", response.status_code)

    try:
        print("Response JSON:", response.json())
    except Exception:
        print("Raw Response:", response.text)


if __name__ == "__main__":
    # Example run
    create_booking(
        event_type_id=3217564,                   # Replace with your real eventTypeId
        start="2025-09-20T04:30:00.000Z",        # UTC datetime
        timezone="Asia/Kolkata",
        name="Kaustav",
        email="kaustav812004@gmail.com"
    )
