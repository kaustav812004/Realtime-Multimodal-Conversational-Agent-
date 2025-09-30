import requests
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

def handle_message(user_msg, user="guest"):
    msg_lower = user_msg.lower()

    if any(k in msg_lower for k in ["book", "appointment", "schedule"]):
        reply = "Great! Let’s book you in. Can you tell me the service, date & time, and your email?"
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
