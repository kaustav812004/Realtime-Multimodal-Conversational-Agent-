import agent
import tools
from tools import list_barbers, BARBERS
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

def show_menu(user_name):
    print(f"\n Hey {user_name}, I can help you with:")
    print("1. Pricing Inquiry (see services & costs)")
    print("2. Book an Appointment")
    print("3. Complaint / Issue")
    print("4. General Chat")
    print("5. Exit")

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Barber Shop Assistant is running! Use /whatsapp for Twilio WhatsApp webhook."

def run_console():
    print("=== Barber Shop Assistant ===")
    user_name = input("Please enter your name: ").strip()
    if not user_name:
        user_name = "Guest"

    while True:
        show_menu(user_name)
        choice = input("\n Choose an option (1-5): ").strip()

        # Pricing
        if choice == "1":
            print("\nAgent:\n" + tools.list_services())

        # Booking
        elif choice == "2":
            print("\nAgent: Awesome Let's book your appointment!")
            event_type_id = 3217564
            start = input(" Enter appointment start datetime (YYYY-MM-DDTHH:MM:SSZ in UTC): ").strip()
            tz = "Asia/Kolkata"
            email = input(" Your email for confirmation: ").strip()
            print(list_barbers())
            barber_choice = input(" Which barber do you want? (type their name): ").strip().lower()
            if barber_choice not in BARBERS:
                print(" Sorry, that barber is not available.")
                continue

            try:
                booking = tools.create_booking(
                    event_type_id=event_type_id,
                    start=start,
                    timezone=tz,
                    name=user_name,
                    email=email
                )
                print(f"\n Thanks {user_name}! Your appointment is booked 🎉")
                print(f" Booking details:\n{booking}\n")
            except Exception as e:
                if "no_available_users_found_error" in str(e):
                    print(" Sorry, no barber is available at that time. Please try another slot!")
                else:
                    print(f" Failed to create booking: \n{e}")

        # Complaint
        elif choice == "3":
            print("\nAgent:  Sorry you faced an issue.")
            text = input("Please describe your complaint: ").strip()
            booking_uid = input("Enter booking ID (if any, else press Enter): ").strip() or None
            complaint = tools.submit_complaint(user_name, text, booking_uid)
            print(f"\n Thanks {user_name}, we’ve logged your complaint with ID {complaint['id']}.")
            print(" Our team will get back to you shortly!\n")

        # General Chat
        elif choice == "4":
            print("\nAgent:  You can chat with me! (type 'exit' to stop)\n")
            while True:
                user_msg = input("You: ").strip()
                if user_msg.lower() in ["exit", "quit", "bye"]:
                    print("Agent: Okay, chat ended.")
                    break
                try:
                    reply = agent.handle_message(user_msg, user=user_name)
                    print(f"Agent: {reply}\n")
                except Exception as e:
                    print(" Chat error:", e)
                    break

        # Exit
        elif choice == "5":
            print(f"\n Goodbye {user_name}, see you soon at the Barber Shop!")
            break

        else:
            print(" Invalid choice, please select 1-5.")

# Twilio WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    try:
        incoming_msg = request.form.get("Body", "").strip()
        from_number = request.form.get("From", "guest")  
        reply = agent.handle_message(incoming_msg, user=from_number)

        twiml = MessagingResponse()
        twiml.message(reply)
        return Response(str(twiml), mimetype="application/xml")
    except Exception as e:
        twiml = MessagingResponse()
        twiml.message("Sorry, something went wrong")
        return Response(str(twiml), mimetype="application/xml")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "whatsapp":
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        run_console()