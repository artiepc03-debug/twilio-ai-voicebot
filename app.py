import os
import json
import asyncio
from datetime import datetime

from flask import Flask, request, Response, abort
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

import websockets
from openai import OpenAI

# =========================
# APP SETUP
# =========================

app = Flask(__name__)

# =========================
# ENVIRONMENT
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

ALERT_PHONE = os.getenv("ALERT_PHONE")  # YOU (admin)

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
    "not safe", "hurt myself", "kill myself",
    "suicide", "emergency", "danger"
]

SYSTEM_PROMPT = """
You are an authoritative, confident professional assistant.
You speak clearly, calmly, and naturally.
You do not sound robotic.
You ask one question at a time.
You assist with DMV appointments, insurance, and general requests.

When DMV intake is complete:
- Clearly confirm the information back to the caller
- Ask if anything needs to be corrected
- Close professionally

If crisis language is detected:
- Stay calm and firm
- Tell the caller to call 911 if in immediate danger
- Provide 988 as support
"""

# =========================
# SIMPLE IN-MEMORY STORAGE
# (Can later be replaced with DB/CRM)
# =========================

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

    vr.say("This is Artie’s assistant.", voice="alice")

    vr.start().stream(
        url=f"wss://{request.host}/voice"
    )

    vr.record(
        transcribe=True,
        recording_status_callback="/recording",
        recording_status_callback_method="POST",
        max_length=300
    )

    return Response(str(vr), mimetype="text/xml")

# =========================
# OPENAI REALTIME VOICE BRIDGE
# =========================

@app.route("/voice", methods=["GET", "POST"])
def voice_ws():
    if request.headersget("Upgrade", "").lower() != "websocket":
        abort(400)

    ws = request.environ.get("wsgi.websocket")
    asyncio.run(handle_realtime_voi
