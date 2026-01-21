from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}, 200

@app.post("/ai_entry")
def ai_entry():
    vr = VoiceResponse()
    vr.say("Hello. This is Artie’s assistant. I can help you right now.", voice="alice")

    gather = Gather(
        input="speech",
        timeout=6,
        speech_timeout="auto",
        action="/ai_intake",
        method="POST"
    )
    gather.say("Please tell me your name and what you are calling about.", voice="alice")
    vr.append(gather)

    vr.say("I did not hear anything. Please call back. Goodbye.", voice="alice")
    vr.hangup()
    return Response(str(vr), mimetype="text/xml")

@app.post("/ai_intake")
def ai_intake():
    vr = VoiceResponse()
    vr.say("Thank you. I have recorded your message. Goodbye.", voice="alice")
    vr.hangup()
    return Response(str(vr), mimetype="text/xml")
