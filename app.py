from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from twilio.twiml.voice_response import VoiceResponse, Gather
from dotenv import load_dotenv
import os
import csv
from datetime import datetime
from urllib.parse import urlencode

# Import our custom systems
from knowledge_base import COURSE_INFO, FAQS
from question_answerer import detect_question_type, generate_answer
from sales_intelligence import (
    get_intro_message, get_interest_check, get_yes_response, get_no_response,
    get_answer_intro, get_after_answer, get_demo_message, get_close, handle_objection
)
from course_booking import (
    get_course_selection, get_course_confirmation, get_demo_booking,
    get_demo_time, get_booking_confirmation, get_closing,
    extract_course, extract_day, extract_time
)
from booking_system import create_booking, load_bookings
from agentic import LeadOperationsAgent, normalize_call_status

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY", "1000-coders-local-development-key")


@app.after_request
def mark_twiml_response(response):
    if request.path in ("/voice", "/process") and response.status_code == 200:
        response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response

print("=" * 70)
print("🔥 ADVANCED AI SALES AGENT WITH SMART BOOKING SYSTEM")
print("✅ Talks like experienced sales counselor")
print("✅ Course selection & slot booking automation")
print("=" * 70)

# =============================
# CALL STATE TRACKING
# =============================
call_state = {}
conversation_history = {}
turn_count = {}
student_interest = {}
student_phone = {}
CUSTOMER_CSV = os.path.join(os.path.dirname(__file__), "customer_data.csv")
automation_agent = None

def get_state(call_id):
    return call_state.get(call_id, {
        "stage": "collect_language",
        "preferred_language": "en-IN",
        "questions_asked": 0,
        "demo_offered": False,
        "course_selected": None,
        "demo_date": None,
        "demo_time": None,
        "student_name": None,
        "student_mobile": None
    })

def update_state(call_id, state):
    call_state[call_id] = state


def is_affirmative(text):
    text_lower = text.lower()
    return any(word in text_lower for word in ["yes", "ya", "yup", "sure", "okay", "of course", "absolutely", "want", "i do", "నేను", "అవును", "సరే"])


def is_negative(text):
    text_lower = text.lower()
    return any(word in text_lower for word in ["no", "don't", "dont", "nah", "not interested", "కాదు", "లేదు"])


def add_to_history(call_id, role, text):
    if call_id not in conversation_history:
        conversation_history[call_id] = []
    conversation_history[call_id].append({"role": role, "text": text})


def get_turn(call_id):
    return turn_count.get(call_id, 0)


def increment_turn(call_id):
    turn_count[call_id] = get_turn(call_id) + 1


def save_customer_event(customer, event, call_sid=""):
    fields = ["timestamp", "event", "call_sid", "name", "age", "college", "phone", "language", "status", "duration"]
    file_exists = os.path.exists(CUSTOMER_CSV)
    existing_rows = []
    if file_exists:
        with open(CUSTOMER_CSV, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            existing_rows = list(reader)
        if reader.fieldnames != fields:
            file_exists = False
            with open(CUSTOMER_CSV, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fields)
                writer.writeheader()
                for row in existing_rows:
                    writer.writerow({field: row.get(field, "") for field in fields})
            file_exists = True
    with open(CUSTOMER_CSV, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "event": event,
            "call_sid": call_sid,
            "name": customer.get("name", ""),
            "age": customer.get("age", ""),
            "college": customer.get("college", ""),
            "phone": customer.get("phone", ""),
            "language": customer.get("language", ""),
            "status": customer.get("status", "initiated"),
            "duration": customer.get("duration", ""),
        })


def read_customer_events():
    if not os.path.exists(CUSTOMER_CSV):
        return []
    with open(CUSTOMER_CSV, newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))[-40:][::-1]


def call_lead_from_agent(lead):
    from twilio.rest import Client
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    webhook_url = os.getenv("VOICE_WEBHOOK_URL", "").strip()
    if os.getenv("SIMULATE_MODE", "").lower() in ("1", "true", "yes"):
        save_customer_event(lead, "automation_call_started", "SIMULATED_AUTOMATION")
        return
    if not all([account_sid, auth_token, from_number, webhook_url]):
        raise RuntimeError("Twilio configuration is incomplete")
    callback_url = f"{webhook_url.rsplit('/', 1)[0]}/call_status"
    call = Client(account_sid, auth_token).calls.create(
        to=lead["phone"], from_=from_number,
        url=f"{webhook_url}?{urlencode(lead)}",
        status_callback=callback_url,
        status_callback_method="POST",
        status_callback_event=["initiated", "ringing", "answered", "completed"],
    )
    save_customer_event(lead, "automation_call_started", call.sid)
@app.errorhandler(Exception)
def voice_safe_error(error):
    app.logger.exception("Unhandled request error: %s", error)
    if request.path in ("/voice", "/process"):
        response = VoiceResponse()
        response.say("We are sorry, our voice assistant needs a moment. Please stay on the line and try again.", voice="Polly.Aditi", language="en-IN")
        response.redirect("/voice", method="POST")
        return str(response), 200, {"Content-Type": "text/xml"}
    if request.path.startswith("/") and request.accept_mimetypes.best == "application/json":
        return jsonify({"error": "The request could not be completed"}), 500
    return "The request could not be completed", 500


def customer_from_payload(payload):
    return {
        "name": (payload.get("name") or "").strip(),
        "age": (payload.get("age") or "").strip(),
        "college": (payload.get("college") or "").strip(),
        "phone": (payload.get("phone") or "").strip(),
        "language": payload.get("language", "en-IN"),
        "status": "initiated",
    }


LANGUAGE_CONFIG = {
    "en-IN": {"name_prompt": "Welcome to 10,000 Coders. May I know your name?", "college_prompt": "Which college or university are you studying at?", "language_prompt": "Welcome to 10,000 Coders. We help learners build real AI and full-stack applications with experienced mentors, practical projects, and placement support. Are you interested in becoming a software engineer? Please say yes or no.", "course_prompt": "We offer Python Full Stack and Java Full Stack. Which path sounds right for you?", "demo_prompt": "Great choice. I can reserve a free, no-pressure demo with a mentor. Would you like me to book it?", "time_prompt": "Which day works best for your demo: Monday, Tuesday, Wednesday, Thursday or Friday?", "objection_prompt": "I understand. One useful thing about 10,000 Coders is that you can experience a real mentor-led class and projects before deciding. There is no pressure. Would a free demo help you evaluate it?", "closing_prompt": "No problem at all. Thank you for your time, and I wish you the very best.", "voice": "Polly.Aditi"},
    "hi-IN": {"name_prompt": "10,000 Coders mein aapka swagat hai. Aapka naam kya hai?", "college_prompt": "Aap kis college ya university mein padh rahe hain?", "language_prompt": "10,000 Coders mein aapka swagat hai. Hum experienced mentors, practical projects aur placement support ke saath AI aur full-stack applications banana sikhate hain. Kya aap software engineer banna chahte hain? Haan ya nahi boliye.", "course_prompt": "Hum Python Full Stack aur Java Full Stack offer karte hain. Aapko kaunsa path pasand hai?", "demo_prompt": "Bahut achha. Main aapke liye mentor ke saath free demo reserve kar sakta hoon. Kya main book kar doon?", "time_prompt": "Aapke demo ke liye kaunsa din theek rahega: Monday, Tuesday, Wednesday, Thursday ya Friday?", "objection_prompt": "Main samajh sakta hoon. 10,000 Coders mein aap decision lene se pehle real mentor-led class aur projects dekh sakte hain. Koi pressure nahi hai. Kya free demo se aapko help milegi?", "closing_prompt": "Koi baat nahi. Aapke samay ke liye dhanyavaad. Aapke bhavishya ke liye shubhkamnayein.", "voice": "Google.hi-IN-Standard-A"},
    "te-IN": {"name_prompt": "10,000 Coders కు స్వాగతం. మీ పేరు చెప్పగలరా?", "college_prompt": "మీరు ఏ college లేదా university లో చదువుతున్నారు?", "language_prompt": "10,000 Coders కు స్వాగతం. Experienced mentors, practical projects మరియు placement support తో AI మరియు full-stack applications నిర్మించడం నేర్పిస్తాము. మీరు software engineer అవ్వాలనుకుంటున్నారా? అవును లేదా కాదు చెప్పండి.", "course_prompt": "మా దగ్గర Python Full Stack మరియు Java Full Stack ఉన్నాయి. మీకు ఏ path ఇష్టం?", "demo_prompt": "చాలా బాగుంది. Mentor తో free, no-pressure demo reserve చేయగలను. Book చేయనా?", "time_prompt": "మీ demo కి ఏ రోజు convenient: Monday, Tuesday, Wednesday, Thursday లేదా Friday?", "objection_prompt": "మీ మాట అర్థమైంది. 10,000 Coders లో decision తీసుకునే ముందు real mentor-led class మరియు projects చూడవచ్చు. ఎలాంటి pressure లేదు. Free demo మీకు సహాయపడుతుందా?", "closing_prompt": "పర్లేదు. మీ సమయానికి ధన్యవాదాలు. మీ భవిష్యత్తుకు శుభాకాంక్షలు.", "voice": "Google.te-IN-Standard-A"},
    "ta-IN": {"name_prompt": "10,000 Coders-க்கு வரவேற்கிறோம். உங்கள் பெயர் என்ன?", "college_prompt": "நீங்கள் எந்த கல்லூரி அல்லது பல்கலைக்கழகத்தில் படிக்கிறீர்கள்?", "language_prompt": "10,000 Coders-க்கு வரவேற்கிறோம். அனுபவமுள்ள mentors, practical projects மற்றும் placement support மூலம் AI மற்றும் full-stack applications உருவாக்க கற்றுக்கொடுக்கிறோம். நீங்கள் software engineer ஆக விரும்புகிறீர்களா? ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.", "course_prompt": "Python Full Stack மற்றும் Java Full Stack ஆகியவற்றை வழங்குகிறோம். உங்களுக்கு எந்த பாதை விருப்பம்?", "demo_prompt": "மிகவும் நல்லது. Mentor உடன் free demo-வை reserve செய்யலாம். Book செய்யவா?", "time_prompt": "உங்கள் demo-க்கு எந்த நாள் வசதியாக இருக்கும்: Monday, Tuesday, Wednesday, Thursday அல்லது Friday?", "objection_prompt": "புரிகிறது. 10,000 Coders-ல் முடிவு எடுப்பதற்கு முன் real mentor-led class மற்றும் projects-ஐ பார்க்கலாம். எந்த pressure-மும் இல்லை. Free demo உதவுமா?", "closing_prompt": "பரவாயில்லை. உங்கள் நேரத்திற்கு நன்றி. உங்கள் எதிர்காலத்திற்கு வாழ்த்துகள்.", "voice": "Google.ta-IN-Standard-A"},
    "kn-IN": {"name_prompt": "10,000 Coders ge swagata. Nimma hesaru enu?", "college_prompt": "Neevu yaava college athava university alli oduttiddira?", "language_prompt": "10,000 Coders ge swagata. Anubhavi mentors, practical projects mattu placement support jothe AI mattu full-stack applications nirmisalu kalisutteve. Neevu software engineer agalu bayasutteera? Howdu athava illa heli.", "course_prompt": "Python Full Stack mattu Java Full Stack nammalli ive. Nimge yaava path ishta?", "demo_prompt": "Chennagide. Mentor jothe free demo reserve madabahudu. Book madona?", "time_prompt": "Nimma demo ge yaava dina anukoola: Monday, Tuesday, Wednesday, Thursday athava Friday?", "objection_prompt": "Nimma maatu artha ayitu. 10,000 Coders nalli nirnaya maduva modalu real mentor-led class mattu projects nodabahudu. Yavude pressure illa. Free demo sahaya maduttadeye?", "closing_prompt": "Parvagilla. Nimma samayakke dhanyavadagalu. Nimma bhavishyakkagi shubhashayagalu.", "voice": "Google.kn-IN-Standard-A"},
}


def get_language_config(state):
    return LANGUAGE_CONFIG.get(state.get("preferred_language"), LANGUAGE_CONFIG["en-IN"])


def localized_course_confirmation(state, course_key):
    from booking_system import get_course_info
    course = get_course_info(course_key)
    if not course:
        return get_language_config(state)["course_prompt"]
    config = get_language_config(state)
    return f"Excellent choice. {course['name']} runs for {course['duration']} and covers {', '.join(course['topics'])}. The fee is {course['fee']}. {config['demo_prompt']}"

def detect_course(value):
    value = (value or "").lower().strip()
    if value == "1" or "python" in value:
        return "python"
    if value == "2" or "java" in value:
        return "java"
    return None


def detect_demo_day(value):
    value = (value or "").lower().strip()
    numbered_days = {"1": "Monday", "2": "Tuesday", "3": "Wednesday", "4": "Thursday", "5": "Friday"}
    if value in numbered_days:
        return numbered_days[value]
    return extract_day(value)

def course_selection_prompt(state):
    prompts = {
        "en-IN": "Please choose a course. Press 1 for Python Full Stack, or press 2 for Java Full Stack. You can also say Python or Java.",
        "hi-IN": "Course choose kijiye. Python Full Stack ke liye 1 dabaiye, Java Full Stack ke liye 2 dabaiye. Aap Python ya Java bhi bol sakte hain.",
        "te-IN": "Course ఎంచుకోండి. Python Full Stack కోసం 1 నొక్కండి, Java Full Stack కోసం 2 నొక్కండి. Python లేదా Java అని కూడా చెప్పవచ్చు.",
        "ta-IN": "Course தேர்வு செய்யவும். Python Full Stackக்கு 1 அழுத்தவும், Java Full Stackக்கு 2 அழுத்தவும். Python அல்லது Java என்றும் சொல்லலாம்.",
        "kn-IN": "Course ಆಯ್ಕೆ ಮಾಡಿ. Python Full Stack ಗೆ 1 ಒತ್ತಿ, Java Full Stack ಗೆ 2 ಒತ್ತಿ. Python ಅಥವಾ Java ಎಂದೂ ಹೇಳಬಹುದು.",
    }
    return prompts.get(state.get("preferred_language"), prompts["en-IN"])


def interest_prompt(state):
    prompts = {
        "en-IN": "Are you interested in becoming a software engineer? Please say yes or no.",
        "hi-IN": "Kya aap software engineer banna chahte hain? Haan ya nahi boliye.",
        "te-IN": "మీరు software engineer అవ్వాలనుకుంటున్నారా? అవును లేదా కాదు చెప్పండి.",
        "ta-IN": "நீங்கள் software engineer ஆக விரும்புகிறீர்களா? ஆம் அல்லது இல்லை என்று சொல்லுங்கள்.",
        "kn-IN": "Neevu software engineer agalu bayasutteera? Howdu athava illa heli.",
    }
    return prompts.get(state.get("preferred_language"), prompts["en-IN"])


def detect_language(value):
    value = (value or "").lower().strip()
    choices = {"1": "en-IN", "2": "hi-IN", "3": "te-IN", "4": "ta-IN", "5": "kn-IN"}
    if value in choices:
        return choices[value]
    for language, code in [("english", "en-IN"), ("hindi", "hi-IN"), ("हिंदी", "hi-IN"), ("telugu", "te-IN"), ("తెలుగు", "te-IN"), ("tamil", "ta-IN"), ("தமிழ்", "ta-IN"), ("kannada", "kn-IN"), ("ಕನ್ನಡ", "kn-IN")]:
        if language in value:
            return code
    return None


def get_stage_followup_prompt(state):
    stage = state.get("stage", "intro")
    if stage == "intro":
        return interest_prompt(state)
    elif stage == "course_selection":
        return course_selection_prompt(state)
    elif stage == "demo_interest":
        return get_language_config(state)["demo_prompt"]
    elif stage == "demo_date_selection":
        return demo_date_prompt(state)
    elif stage == "demo_time_selection":
        return get_language_config(state)["time_prompt"]
    elif stage == "collect_student_details":
        if state.get("student_name") is None:
            return "నీ పేరు చెప్పు బ్రో, please."
        elif state.get("student_mobile") is None:
            return "నీ mobile number ఇవ్వండి బ్రో."
        else:
            return "ఇది correct కాదా బ్రో? yes or no చెప్పు బ్రో."
    elif stage == "collect_college":
        return get_language_config(state)["college_prompt"]
    return get_after_answer()


def demo_date_prompt(state):
    prompts = {
        "en-IN": "Choose your demo day: press 1 for Monday, 2 for Tuesday, 3 for Wednesday, 4 for Thursday, or 5 for Friday. You can also say the day.",
        "hi-IN": "Demo ka din chuniye: Monday ke liye 1, Tuesday ke liye 2, Wednesday ke liye 3, Thursday ke liye 4, ya Friday ke liye 5 dabaiye. Aap din bol bhi sakte hain.",
        "te-IN": "Demo రోజు ఎంచుకోండి: Monday కోసం 1, Tuesday కోసం 2, Wednesday కోసం 3, Thursday కోసం 4, Friday కోసం 5 నొక్కండి. మీరు రోజు పేరు కూడా చెప్పవచ్చు.",
        "ta-IN": "Demo நாளை தேர்வு செய்யவும்: Mondayக்கு 1, Tuesdayக்கு 2, Wednesdayக்கு 3, Thursdayக்கு 4, Fridayக்கு 5 அழுத்தவும். நாளை சொல்லவும்லாம்.",
        "kn-IN": "Demo dina aayke maadi: Monday ge 1, Tuesday ge 2, Wednesday ge 3, Thursday ge 4, Friday ge 5 otti. Dina hesarannu helabahudu.",
    }
    return prompts.get(state.get("preferred_language"), prompts["en-IN"])


def try_general_question_response(response, call_id, user_input, state):
    question_type, direct_answer = detect_question_type(user_input)
    if question_type == "unclear":
        return False

    if direct_answer:
        ai_response = direct_answer
    else:
        ai_response = generate_answer(question_type, user_input)

    if question_type not in ["who_are_you", "what_can_you_do"]:
        ai_response = get_answer_intro(question_type) + " " + ai_response

    response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
    add_to_history(call_id, "Agent", ai_response)

    follow_up = get_stage_followup_prompt(state)
    gather = Gather(
        input="dtmf speech" if state.get("stage") == "collect_language" else "speech",
        action="/process",
        method="POST",
        timeout=10,
        speechTimeout="auto",
        language=state.get("preferred_language", "en-IN")
    )
    gather.say(follow_up, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
    response.append(gather)
    return True

# =============================
# HEALTH CHECK
# =============================
@app.route("/", methods=["GET"])
def welcome():
    return render_template("welcome.html")


@app.route("/auth", methods=["GET", "POST"])
def auth():
    if request.method == "POST":
        session["user"] = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "mode": request.form.get("mode", "register"),
        }
        return redirect(url_for("dashboard"))
    return render_template("auth.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("welcome"))


@app.route("/assistant", methods=["POST"])
def assistant():
    if "user" not in session:
        return jsonify({"error": "Sign in required"}), 401
    question = (request.json or {}).get("message", "").strip()
    if not question:
        return jsonify({"error": "Message required"}), 400
    question_type, direct_answer = detect_question_type(question)
    answer = direct_answer or generate_answer(question_type, question)
    if question_type == "unclear":
        answer = "I can help with course tracks, fees, placements, projects, demo sessions, call activity, and automation. What would you like to explore?"
    return jsonify({"answer": answer, "intent": question_type})


# =============================
# SIMPLE WEB DASHBOARD
# =============================
@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth"))
    return render_template("index.html", user=session["user"], call_logs=read_customer_events(), agent_status=automation_agent.snapshot() if automation_agent else {"queued": 0, "completed": 0, "running": False, "last_error": ""})


@app.route("/call_logs", methods=["GET"])
def call_logs():
    return jsonify({"logs": read_customer_events(), "agent": automation_agent.snapshot() if automation_agent else {"queued": 0, "completed": 0, "running": False}})


@app.route("/selected_courses", methods=["GET"])
def selected_courses():
    bookings = load_bookings()
    return jsonify({"courses": bookings[::-1]})


@app.route("/upload_customers", methods=["POST"])
def upload_customers():
    global automation_agent
    uploaded = request.files.get("file")
    if not uploaded or not uploaded.filename.lower().endswith(".csv"):
        return jsonify({"error": "Upload a CSV file"}), 400
    if automation_agent is None:
        automation_agent = LeadOperationsAgent(CUSTOMER_CSV, call_lead_from_agent)
    leads = automation_agent.import_csv(uploaded)
    return jsonify({"imported": len(leads), "agent": automation_agent.snapshot()})


@app.route("/automation", methods=["POST"])
def automation():
    global automation_agent
    if automation_agent is None:
        automation_agent = LeadOperationsAgent(CUSTOMER_CSV, call_lead_from_agent)
    enabled = request.json.get("enabled", True) if request.is_json else True
    if not enabled:
        automation_agent.stop()
        return jsonify({"started": False, "agent": automation_agent.snapshot()})
    started = automation_agent.start()
    return jsonify({"started": started, "agent": automation_agent.snapshot()})


@app.route("/call_status", methods=["POST"])
def call_status():
    status = normalize_call_status(request.form)
    matching = next((row for row in reversed(read_customer_events()) if row.get("call_sid") == status["call_sid"]), {})
    customer = {"name": matching.get("name", ""), "age": matching.get("age", ""), "college": matching.get("college", ""), "phone": matching.get("phone", ""), "language": matching.get("language", ""), "status": status["status"], "duration": status.get("duration", "")}
    save_customer_event(customer, status["event"], status["call_sid"])
    return "", 204


@app.route("/trigger_call", methods=["POST"])
def trigger_call():
    """Trigger an outbound call via Twilio (uses same env vars as call.py).
    Expects JSON: { "phone": "+123..." }
    """
    from twilio.rest import Client
    payload = request.json if request.is_json else request.form
    phone = payload.get("phone")
    customer = customer_from_payload(payload)
    preferred_language = customer["language"]
    if preferred_language not in LANGUAGE_CONFIG:
        preferred_language = "en-IN"
        customer["language"] = preferred_language
    if not phone:
        return jsonify({"error": "Phone number required"}), 400
    if not customer["name"]:
        return jsonify({"error": "Customer name is required"}), 400

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "").strip()
    VOICE_WEBHOOK_URL = os.getenv("VOICE_WEBHOOK_URL", "").strip()
    SIMULATE_MODE = os.getenv("SIMULATE_MODE", "").strip().lower() in ("1", "true", "yes")

    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, VOICE_WEBHOOK_URL]):
        return jsonify({"error": "Missing Twilio configuration in environment"}), 500

    if SIMULATE_MODE or os.getenv("SIMULATE_MODE", "").lower() in ("1", "true", "yes"):
        # Simulate invocation of the webhook similar to call.py
        import urllib.parse, urllib.request
        form_data = urllib.parse.urlencode({
            "CallSid": "SIMULATED_CALL_SID",
            "From": phone,
            "To": TWILIO_FROM_NUMBER,
            "CallStatus": "in-progress",
        }).encode("utf-8")
        webhook_url = f"{VOICE_WEBHOOK_URL}?{urlencode(customer)}"
        req = urllib.request.Request(webhook_url, data=form_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
            save_customer_event(customer, "call_started", "SIMULATED_CALL_SID")
            return jsonify({"status": "simulated", "webhook_response": body})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # Real call via Twilio
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        webhook_url = f"{VOICE_WEBHOOK_URL}?{urlencode(customer)}"
        callback_url = f"{VOICE_WEBHOOK_URL.rsplit('/', 1)[0]}/call_status"
        call = client.calls.create(to=phone, from_=TWILIO_FROM_NUMBER, url=webhook_url, status_callback=callback_url, status_callback_method="POST", status_callback_event=["initiated", "ringing", "answered", "completed"])
        save_customer_event(customer, "call_started", call.sid)
        return jsonify({"status": "started", "call_sid": call.sid})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

# =============================
# INITIAL VOICE CALL ENDPOINT
# =============================
@app.route("/voice", methods=["POST"])
def voice():
    """
    When student receives the call, this is what they hear first
    """
    call_id = request.form.get("CallSid", "default")
    phone = request.form.get("From", "unknown")
    preferred_language = request.args.get("language", "en-IN")
    if preferred_language not in LANGUAGE_CONFIG:
        preferred_language = "en-IN"
    
    # Store student phone number for booking
    student_phone[call_id] = phone
    
    call_state[call_id] = {
        "stage": "collect_language",
        "preferred_language": preferred_language,
        "questions_asked": 0,
        "demo_offered": False,
        "course_selected": None,
        "demo_date": None,
        "demo_time": None,
        "student_name": request.args.get("name", ""),
        "student_mobile": phone,
        "college": ""
    }
    call_state[call_id]["customer_age"] = request.args.get("age", "")
    call_state[call_id]["customer_name"] = request.args.get("name", "")
    
    response = VoiceResponse()
    language_config = get_language_config(call_state[call_id])
    
    gather = Gather(
        input="dtmf speech",
        action="/process",
        method="POST",
        timeout=10,
        speechTimeout="auto",
        language="en-IN"
    )

    gather.say("Welcome to 10,000 Coders. For the best experience, choose your comfortable language. Press 1 for English, 2 for Hindi, 3 for Telugu, 4 for Tamil, or 5 for Kannada. You can also say the language name.", voice="alice", language="en-IN")
    response.append(gather)
    
    return str(response)

# =============================
# MAIN PROCESSING ENDPOINT
# =============================
@app.route("/process", methods=["POST"])
def process():
    """
    MAIN ENGINE: Listens to student, detects question, gives REAL answer
    """
    user_input = request.form.get("SpeechResult", "").strip()
    if not user_input:
        user_input = request.form.get("Digits", "").strip()
    call_id = request.form.get("CallSid", "default")
    
    response = VoiceResponse()
    state = get_state(call_id)
    current_turn = get_turn(call_id)

    gather = Gather(
        input="dtmf speech" if state.get("stage") == "course_selection" else "speech",
        action="/process",
        method="POST",
        timeout=10,
        speechTimeout="auto",
        language=state.get("preferred_language", "en-IN")
    )
    
    # =============================
    # HANDLE NO SPEECH
    # =============================
    if not user_input:
        response.say(
            "Sorry, I could not hear you clearly. Please repeat. Ask about course, fees, placements, or anything else.",
            voice="Polly.Aditi",
            language=state.get("preferred_language", "en-IN")
        )
        response.append(gather)
        return str(response)
    
    # =============================
    # HANDLE HARD EXIT
    # =============================
    if any(word in user_input.lower() for word in ["stop calling", "don't call", "remove me", "not interested at all"]):
        response.say("Okay, no problem! All the best!", voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
        response.hangup()
        return str(response)
    
    # =============================
    # TRACK THE CONVERSATION
    # =============================
    add_to_history(call_id, "Student", user_input)
    increment_turn(call_id)
    current_turn = get_turn(call_id)
    
    print(f"\n[Turn {current_turn}] Student: {user_input}")

    if state["stage"] == "collect_language":
        selected_language = detect_language(user_input)
        if not selected_language:
            response.say("I did not catch that. Please press 1 for English, 2 for Hindi, 3 for Telugu, 4 for Tamil, or 5 for Kannada.", voice="Polly.Aditi", language="en-IN")
            response.append(gather)
            return str(response)
        state["preferred_language"] = selected_language
        state["stage"] = "collect_name" if not state.get("student_name") else "collect_college"
        update_state(call_id, state)
        language_config = get_language_config(state)
        if state["stage"] == "collect_name":
            response.say(language_config["name_prompt"], voice=language_config["voice"], language=selected_language)
        else:
            response.say(f"Thank you. I have your customer profile, {state['student_name']}. {language_config['college_prompt']}", voice=language_config["voice"], language=selected_language)
        language_gather = Gather(input="speech", action="/process", method="POST", timeout=10, speechTimeout="auto", language=selected_language)
        response.append(language_gather)
        return str(response)

    if state["stage"] == "collect_name":
        state["student_name"] = user_input
        state["stage"] = "collect_college"
        update_state(call_id, state)
        language_config = get_language_config(state)
        ai_response = f"Thank you, {user_input}. {language_config['college_prompt']}"
        response.say(ai_response, voice=language_config["voice"], language=state["preferred_language"])
        response.append(gather)
        return str(response)

    if state["stage"] == "collect_college":
        state["college"] = user_input
        state["stage"] = "intro"
        update_state(call_id, state)
        language_config = get_language_config(state)
        response.say(language_config["language_prompt"], voice=language_config["voice"], language=state["preferred_language"])
        response.append(gather)
        return str(response)
    
    # =============================
    # INITIAL STAGE: YES/NO TO BECOME SOFTWARE ENGINEER
    # =============================
    if state["stage"] == "intro":
        if is_affirmative(user_input):
            ai_response = get_yes_response()
            state["stage"] = "course_selection"
            update_state(call_id, state)
        elif is_negative(user_input):
            if not state.get("objection_offered"):
                state["objection_offered"] = True
                update_state(call_id, state)
                language_config = get_language_config(state)
                ai_response = get_language_config(state)["objection_prompt"]
                response.say(ai_response, voice=language_config["voice"], language=state.get("preferred_language", "en-IN"))
                response.append(gather)
                return str(response)
            closing_msg = get_no_response()
            response.say(closing_msg, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.hangup()
            return str(response)
        else:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            ai_response = interest_prompt(state)
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.append(gather)
            return str(response)
    
    # =============================
    # STAGE: COURSE SELECTION
    # =============================
    elif state["stage"] == "course_selection":
        course = detect_course(user_input)
        if course:
            ai_response = localized_course_confirmation(state, course)
            state["course_selected"] = course
            state["stage"] = "demo_interest"
            update_state(call_id, state)
        else:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            ai_response = course_selection_prompt(state)
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.append(gather)
            return str(response)
    
    # =============================
    # STAGE: DEMO INTEREST
    # =============================
    elif state["stage"] == "demo_interest":
        course_name = state.get("course_selected")
        if is_affirmative(user_input):
            ai_response = get_language_config(state)["demo_prompt"]
            state["stage"] = "demo_date_selection"
            update_state(call_id, state)
        elif is_negative(user_input):
            ai_response = get_language_config(state)["closing_prompt"]
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.hangup()
            return str(response)
        else:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            ai_response = get_demo_booking(course_name)
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.append(gather)
            return str(response)
    
    # =============================
    # STAGE: DEMO DATE SELECTION
    # =============================
    elif state["stage"] == "demo_date_selection":
        demo_day = detect_demo_day(user_input)
        if demo_day:
            ai_response = get_language_config(state)["time_prompt"]
            state["demo_date"] = demo_day
            state["stage"] = "demo_time_selection"
            update_state(call_id, state)
        else:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            course_name = state["course_selected"]
            ai_response = get_stage_followup_prompt(state)
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.append(gather)
            return str(response)
    
    # =============================
    # STAGE: DEMO TIME SELECTION
    # =============================
    elif state["stage"] == "demo_time_selection":
        demo_time = extract_time(user_input)
        if demo_time:
            ai_response = f"Perfect. I have reserved {demo_time} for your demo. I am confirming your customer details now."
            state["demo_time"] = demo_time
            state["stage"] = "collect_student_details"
            update_state(call_id, state)
        else:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            ai_response = get_language_config(state)["time_prompt"]
            response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
            response.append(gather)
            return str(response)
    
    # =============================
    # STAGE: COLLECT STUDENT DETAILS
    # =============================
    elif state["stage"] == "collect_student_details":
        if state["student_name"] is None:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            # First time - asking for name
            state["student_name"] = user_input.strip()
            ai_response = "ధన్యవాదాలు {name} బ్రో! ఇప్పుడు నీ mobile number చెప్పు బ్రో?".format(name=state["student_name"])
            update_state(call_id, state)
        elif state["student_mobile"] is None:
            if try_general_question_response(response, call_id, user_input, state):
                return str(response)
            # Got name, now asking for mobile
            state["student_mobile"] = user_input.strip()
            course_name = state["course_selected"]
            from booking_system import get_course_info
            course_info = get_course_info(course_name)
            course_display = course_info["name"] if course_info else course_name
            ai_response = "సరే {name} బ్రో! నీ mobile number {mobile} ని confirm చేస్తున్నాను 브ோ. నీ course: {course} బ్రో. ఇది correct ఆ బ్రో? Yes or No బ్రో?".format(
                name=state["student_name"], 
                mobile=state["student_mobile"],
                course=course_display
            )
            update_state(call_id, state)
        else:
            # Confirming course selection
            if is_affirmative(user_input):
                # Create booking with all details
                course_name = state["course_selected"]
                from booking_system import get_course_info
                course_info = get_course_info(course_name)
                
                booking = create_booking(
                    phone_number=state["student_mobile"],
                    course_name=course_info["name"] if course_info else "Unknown",
                    demo_date=state["demo_date"],
                    demo_time=state["demo_time"],
                    student_name=state["student_name"],
                    college=state.get("college", ""),
                    language=state.get("preferred_language", "en-IN")
                )
                
                ai_response = "పర్ఫెక్ట్ బ్రో! {name}, నీ booking confirmed బ్రో! Course: {course} బ్రో, Date: {date} బ్రో, Time: {time} బ్రో. ఈ details నీ mobile కి message లో కూడా పంపిస్తాం బ్రో.".format(
                    name=state["student_name"],
                    course=course_info["name"] if course_info else course_name,
                    date=state["demo_date"],
                    time=state["demo_time"]
                )
                state["stage"] = "booking_complete"
                update_state(call_id, state)
            elif is_negative(user_input):
                ai_response = get_course_selection()
                state["stage"] = "course_selection"
                update_state(call_id, state)
            else:
                if try_general_question_response(response, call_id, user_input, state):
                    return str(response)
                ai_response = "సరే బ్రో, ఈ డీటెయిల్స్ confirm కావాలా? Yes లేదా No చెప్పు బ్రో."
        
        response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
        response.append(gather)
        return str(response)
    
    # =============================
    # STAGE: BOOKING COMPLETE
    # =============================
    elif state["stage"] == "booking_complete":
        course_name = state["course_selected"]
        from booking_system import get_course_info, get_student_booking
        course_info = get_course_info(course_name)
        booking = get_student_booking(student_phone.get(call_id, "unknown"))
        
        closing_msg = get_closing(booking) if booking else "Thank you!"
        response.say(closing_msg, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
        response.hangup()
        return str(response)
    
    # =============================
    # STAGE: ACTIVE (QUESTIONS)
    # =============================
    else:
        # DETECT QUESTION TYPE & GET ANSWER - MID FLOW
        question_type, direct_answer = detect_question_type(user_input)
        
        if direct_answer:
            # Add introduction to answer like experienced sales person
            intro = get_answer_intro(question_type)
            actual_answer = generate_answer(question_type, user_input)
            ai_response = intro + " " + actual_answer
            print(f"[Answer Type] {question_type}")
        elif question_type == "general_doubt":
            # Handle general doubts
            ai_response = generate_answer(question_type, user_input)
            print(f"[Doubt Detected] General doubt clarification")
        else:
            ai_response = (
                "నీ question నాకు clear కాలేదు బ్రో. "
                "దయచేసి course content, fees, placement, projects, internship, లేదా schedule గురించి అడగండి బ్రో. "
                "నేను honest answer ఇస్తాను బ్రో."
            )

    # =============================
    # SPEAK THE RESPONSE
    # =============================
    response.say(ai_response, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
    add_to_history(call_id, "Agent", ai_response)
    
    # =============================
    # DECIDE NEXT STEP - INTELLIGENT FOLLOW UP
    # =============================
    gather = Gather(
        input="dtmf speech" if state.get("stage") in ["course_selection", "demo_date_selection"] else "speech",
        action="/process",
        method="POST",
        timeout=10,
        speechTimeout="auto",
        language=state.get("preferred_language", "en-IN")
    )
    
    # Use smart continuation from sales intelligence
    demo_msg = get_demo_message(current_turn)
    
    if state.get("stage") in ["course_selection", "demo_interest", "demo_date_selection", "demo_time_selection"]:
        follow_up = get_stage_followup_prompt(state)
    elif demo_msg and not state["demo_offered"]:
        # Time to push demo
        follow_up = demo_msg
        state["demo_offered"] = True
        update_state(call_id, state)
    elif current_turn >= 8:
        # If too many turns, prepare to close call
        follow_up = get_after_answer()
    else:
        # Normal continuation - ask for more questions
        follow_up = get_after_answer()
    
    gather.say(follow_up, voice=get_language_config(state)["voice"], language=state.get("preferred_language", "en-IN"))
    response.append(gather)
    
    print(f"[Follow-up] {follow_up}\n")
    
    return str(response)

# =============================
# RUN THE APP
# =============================
if __name__ == "__main__":
    print("\n🚀 Starting ADVANCED AI Sales Agent (10+ Years Experience)...")
    print("📱 Webhook endpoint: POST /voice")
    print("✅ Talks like experienced institute sales counselor")
    print("✅ Human-like responses with intelligence")
    print("✅ Uses real knowledge base for answers\n")
    port = int(os.getenv("PORT", "5050"))
    print(f"🌐 Dashboard available at http://localhost:{port}/dashboard")
    app.run(host="0.0.0.0", port=port, debug=True)
