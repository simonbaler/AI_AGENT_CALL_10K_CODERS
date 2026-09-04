from twilio.rest import Client
from dotenv import load_dotenv
import os
import sys
import urllib.parse
import urllib.request

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "").strip()
VOICE_WEBHOOK_URL = os.getenv("VOICE_WEBHOOK_URL", "").strip()
SIMULATE_MODE = os.getenv("SIMULATE_MODE", "").strip().lower() in ("1", "true", "yes")

# Detect --simulate flag and remove it from arg list
simulate_flag = "--simulate"
args = [arg for arg in sys.argv[1:] if arg != simulate_flag]
if simulate_flag in sys.argv:
    SIMULATE_MODE = True

# Get phone number from command line argument, or use env default with prompt override
if len(args) > 0:
    STUDENT_PHONE_NUMBER = args[0].strip()
else:
    default_number = os.getenv("STUDENT_PHONE_NUMBER", "").strip()
    if default_number:
        entered = input(f"Enter the phone number to call [{default_number}]: ").strip()
        STUDENT_PHONE_NUMBER = entered or default_number
    else:
        STUDENT_PHONE_NUMBER = input("Enter the phone number to call (with country code, e.g. +1234567890): ").strip()

required = [
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    VOICE_WEBHOOK_URL,
]

if not all(required):
    missing = [
        name
        for name, value in [
            ("TWILIO_ACCOUNT_SID", TWILIO_ACCOUNT_SID),
            ("TWILIO_AUTH_TOKEN", TWILIO_AUTH_TOKEN),
            ("TWILIO_FROM_NUMBER", TWILIO_FROM_NUMBER),
            ("VOICE_WEBHOOK_URL", VOICE_WEBHOOK_URL),
        ]
        if not value
    ]
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

if not STUDENT_PHONE_NUMBER:
    raise RuntimeError("Phone number not provided. Pass it as command line argument or set STUDENT_PHONE_NUMBER in .env")

if SIMULATE_MODE:
    print("\n[SIMULATION MODE] No real Twilio call will be placed.")
    print(f"Simulating call from {TWILIO_FROM_NUMBER} to {STUDENT_PHONE_NUMBER}")
    form_data = urllib.parse.urlencode({
        "CallSid": "SIMULATED_CALL_SID",
        "From": STUDENT_PHONE_NUMBER,
        "To": TWILIO_FROM_NUMBER,
        "CallStatus": "in-progress",
    }).encode("utf-8")
    request = urllib.request.Request(
        VOICE_WEBHOOK_URL,
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode("utf-8")
            print("\nWebhook response received:")
            print(body)
            print("\nSimulation complete. The AI endpoint has been invoked.")
    except Exception as exc:
        print(f"Simulation failed: {exc}")
        sys.exit(1)
else:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    print(f"Starting call from {TWILIO_FROM_NUMBER} to {STUDENT_PHONE_NUMBER}")
    try:
        call = client.calls.create(
            to=STUDENT_PHONE_NUMBER,
            from_=TWILIO_FROM_NUMBER,
            url=VOICE_WEBHOOK_URL,
        )
        print("Call started successfully!")
        print("Call SID:", call.sid)
    except Exception as exc:
        error_message = str(exc)
        print("Unable to create call:")
        print(error_message)
        if hasattr(exc, "code") and exc.code == 21219:
            print("\nTwilio trial restriction detected:")
            print("- Trial accounts can only call verified numbers.")
            print("- Verify the destination number in Twilio, or upgrade to a paid account to call any number.")
        sys.exit(1)



