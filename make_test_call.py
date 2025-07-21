# make_test_call.py

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://your-ngrok-id.ngrok-free.app")  # 👈 Set in .env

app = FastAPI()
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.post("/call")
async def make_call(request: Request):
    data = await request.json()
    to_number = data.get("to")

    if not to_number:
        return JSONResponse(status_code=400, content={"error": "Missing 'to' number"})

    call = twilio_client.calls.create(
        to=to_number,
        from_=TWILIO_PHONE_NUMBER,
        url=f"{PUBLIC_URL}/voice"
    )

    return {"message": "Call initiated", "call_sid": call.sid}

@app.post("/voice")
async def voice():
    response = VoiceResponse()
    start = Start()
    start.stream(url=f"wss://{PUBLIC_URL.replace('https://', '')}/ws")  # Convert to WSS for streaming
    response.append(start)
    response.say("Connecting you to the car service assistant.", voice="Polly.Joanna", language="en-US")

    return JSONResponse(content=str(response), media_type="application/xml")
