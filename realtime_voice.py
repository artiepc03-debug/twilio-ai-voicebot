import os
import json
import asyncio
import websockets
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

OPENAI_MODEL = "gpt-4o-realtime-preview"

SYSTEM_PROMPT = """
You are an authoritative, confident professional assistant.
You speak clearly, calmly, and naturally.
You do not sound robotic.
You ask one question at a time.
You assist with DMV appointments, insurance, and general requests.
If crisis language is detected, follow safety protocol immediately.
"""

async def openai_realtime(ws_twilio):
    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=" + OPENAI_MODEL,
        extra_headers={
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as ws_openai:

        # Send system prompt
        await ws_openai.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["audio", "text"],
                "instructions": SYSTEM_PROMPT,
                "audio": { "voice": "alloy" }
            }
        }))

        async def twilio_to_openai():
            async for msg in ws_twilio:
                await ws_openai.send(msg)

        async def openai_to_twilio():
            async for msg in ws_openai:
                await ws_twilio.send(msg)

        await asyncio.gather(
            twilio_to_openai(),
            openai_to_twilio()
        )
