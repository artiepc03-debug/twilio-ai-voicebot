import os
from datetime import datetime

from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from openai import OpenAI

# =========================
# APP SETUP
# =========================

app = Flask(__name__)

# =========================
# ENVIRONMENT VARIABLES
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
ALERT_PHONE = os.getenv("ALERT_PHONE")  # your phone

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# CONSTANTS
# =========================

DMV_QUESTIONS = [
    "Have you ever had an ID in the state of North Carolina?",
    "Do you have your Social Security Card?",
    "Do you have your birth certificate?",
    "What is your full name?",
    "What is the best phone number?",
    "What is your email address?"
]

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "hurt myself",
    "not safe", "emergency", "danger"
]

DMV_SESSIONS = {}

# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health():
    return {"ok": True}, 200

# =========================
# ENTRY POINT (TWILIO)
# =========================

@app.post("/ai_entry")
def ai_entry():
    vr = VoiceResponse()

    vr.say(
        "This is Artie’s assistant. I can help you now.",
        voice="alice"
    )

    gather = Gather(
        input="speech",
        timeout=6,
        speech_timeout="auto",
        action="/ai_router",
        method="POST"
    )
    gather.say("How can I assist you today?")
    vr.append(gather)

    vr.say("I didn’t catch that. Please call back if you need help.")
    vr.hangup()

    return Response(str(vr), mimetype="text/xml")

# =========================
# INTENT ROUTER
# =========================

@app.post("/ai_router")
def ai_router():
    speech = (request.form.get("SpeechResult") or "").lower()
    vr = VoiceResponse()

    # Crisis detection
    if any(word in speech for word in CRISIS_KEYWORDS):
        vr.say(
            "If you are in immediate danger, call 9 1 1 now.",
            voice="alice"
        )
        vr.say(
            "You can also call or text 9 8 8 for immediate support.",
            voice="alice"
        )
        vr.hangup()
        return Response(str(vr), mimetype="text/xml")

    # DMV intent
    if "dmv" in speech or "license" in speech or "id" in speech:
        vr.say(
            "Understood. I will help with your DMV appointment.",
            voice="alice"
        )
        vr.redirect("/dmv_flow?step=0")
        return Response(str(vr), mimetype="text/xml")

    # Default
    vr.say(
        "Thank you. I’ve recorded your request and Artie will follow up.",
        voice="alice"
    )
    vr.hangup()
    return Response(str(vr), mimetype="text/xml")

# =========================
# DMV FLOW (WITH CONFIRMATION)
# =========================

@app.post("/dmv_flow")
def dmv_flow():
    call_sid = request.form.get("CallSid")
    step = int(request.args.get("step", 0))
    speech = (request.form.get("SpeechResult") or "").strip()

    if call_sid not in DMV_SESSIONS:
        DMV_SESSIONS[call_sid] = []

    if speech:
        DMV_SESSIONS[call_sid].append(speech)

    vr = VoiceResponse()

    if step < len(DMV_QUESTIONS):
        gather = Gather(
            input="speech",
            timeout=6,
            speech_timeout="auto",
            action=f"/dmv_flow?step={step + 1}",
            method="POST"
        )
        gather.say(DMV_QUESTIONS[step], voice="alice")
        vr.append(gather)
        vr.hangup()
    else:
        responses = DMV_SESSIONS.get(call_sid, [])

        vr.say("Here is what I have on file.", voice="alice")
        for q, a in zip(DMV_QUESTIONS, responses):
            vr.say(f"{q} You said {a}.", voice="alice")

        vr.say(
            "If anything needs to be corrected, Artie will follow up.",
            voice="alice"
        )
        vr.say(
            "Your DMV information has been recorded. Thank you.",
            voice="alice"
        )
        vr.hangup()

        send_sms_summary(call_sid, responses)

    return Response(str(vr), mimetype="text/xml")

# =========================
# SMS SUMMARY
# =========================

def send_sms_summary(call_sid, responses):
    body = "DMV Intake Summary:\n"
    for q, a in zip(DMV_QUESTIONS, responses):
        body += f"- {q}: {a}\n"

    if ALERT_PHONE:
        twilio_client.messages.create(
            to=ALERT_PHONE,
            from_=TWILIO_NUMBER,
            body=body
        )

# =========================
# RECORDING CALLBACK (OPTIONAL)
# =========================

@app.post("/recording")
def recording():
    caller = request.form.get("From")
    transcription = request.form.get("TranscriptionText", "")
    timestamp = datetime.utcnow().isoformat()

    summary = f"Call from {caller} at {timestamp}\n{transcription}"

    if ALERT_PHONE:
        twilio_client.messages.create(
            to=ALERT_PHONE,
            from_=TWILIO_NUMBER,
            body=summary
        )

    return ("", 204)

# =========================
# RUN LOCAL
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
