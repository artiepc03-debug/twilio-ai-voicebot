from openai import OpenAI
client = OpenAI()

SYSTEM_PROMPT = """
You are a professional executive assistant with an authoritative, confident tone.
You speak clearly and calmly.
You do not sound robotic.
You do not over-explain.
You lead the conversation and ask one question at a time.

If the caller sounds confused, slow down slightly.
If the caller sounds distressed, remain calm and firm.

You assist with:
- Insurance questions
- DMV appointment intake
- Probation and reentry check-ins
- General administrative requests

If you detect crisis language, you immediately follow safety protocol.
"""

def respond(user_text):
    response = client.responses.create(
        model="gpt-4o-realtime-preview",
        modalities=["text","audio"],
        audio={
            "voice": "alloy",          # most natural, confident OpenAI voice
            "format": "wav"
        },
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )
    return response
