import requests
import dateparser
from datetime import datetime
from config import AZURE_ENDPOINT, AZURE_KEY, AZURE_DEPLOYMENT, AZURE_API_VERSION
import tools
import firebase_admin
from firebase_admin import firestore, credentials

cred = credentials.Certificate("service.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def get_history(user_id):
    doc_ref = db.collection("conversations").document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("history", [])
    return []


def save_message(user_id, role, content):
    if not user_id:
        user_id = "guest"
    doc_ref = db.collection("conversations").document(user_id)
    doc_ref.set({
        "history": firestore.ArrayUnion([{"role": role, "content": content}])
    }, merge=True)


def azure_chat(messages, temperature=0.3, max_tokens=500):
    url = f"{AZURE_ENDPOINT}"
    headers = {"Content-Type": "application/json", "api-key": AZURE_KEY}
    payload = {"messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Azure API error:", e)
        return "Sorry, I’m having trouble connecting to the AI service right now."


def handle_booking(user_msg, user_name="guest", user_email="guest@example.com"):
    """
    Parse natural date/time from user_msg and create booking in Cal.com
    """
    # Detect service
    service = None
    for s in tools.SERVICES.keys():
        if s.lower() in user_msg.lower():
            service = s
            break

    # Detect barber
    barber = None
    for b in tools.BARBERS.keys():
        if b.lower() in user_msg.lower():
            barber = b
            break

    # Parse datetime
    parsed_dt = dateparser.parse(user_msg, settings={"RETURN_AS_TIMEZONE_AWARE": True})
    if not parsed_dt:
        return "❌ Sorry, I couldn’t understand the date/time. Please try again."

    iso_start = parsed_dt.isoformat()

    try:
        booking = tools.create_booking(
            event_type_id=3217564,  # TODO: Map to actual Cal.com eventTypeId
            start=iso_start,
            timezone="Asia/Kolkata",
            name=user_name,
            email=user_email,
            notes=f"Service: {service}, Barber: {barber}"
        )
        return f"✅ Booking confirmed!\nService: {service}\nBarber: {barber}\nWhen: {iso_start}\nBooking ID: {booking.get('uid')}"
    except Exception as e:
        return f"⚠️ Booking failed: {e}"


def handle_message(user_msg, user="guest", user_email="guest@example.com"):
    msg_lower = user_msg.lower()

    if any(k in msg_lower for k in ["book", "appointment", "schedule"]):
        reply = handle_booking(user_msg, user_name=user, user_email=user_email)
        save_message(user, "user", user_msg)
        save_message(user, "assistant", reply)
        return reply

    if any(k in msg_lower for k in ["price", "cost", "service"]):
        reply = "Sure! Here’s our current price list:\n" + tools.list_services()
        save_message(user, "user", user_msg)
        save_message(user, "assistant", reply)
        return reply

    if any(k in msg_lower for k in ["complain", "bad", "issue", "problem"]):
        reply = "Oh no! I’m really sorry to hear that. Could you tell me what happened so we can fix it?"
        save_message(user, "user", user_msg)
        save_message(user, "assistant", reply)
        return reply

    history = get_history(user)
    messages = [{"role": "system", "content": "You are a friendly barber shop assistant."}] + history + [{"role": "user", "content": user_msg}]
    reply = azure_chat(messages)
    save_message(user, "user", user_msg)
    save_message(user, "assistant", reply)
    return reply
