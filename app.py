# app.py

import uvicorn
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from services.media_stream_handler import handle_twilio_media_stream
from services.twilio_service import initiate_call

app = FastAPI()

# Optional: Enable CORS for development or frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Route: Start Twilio call via API
@app.post("/call")
async def call_customer(request: Request):
    data = await request.json()
    to_number = data.get("to")
    if not to_number:
        return {"error": "Missing 'to' number"}

    result = initiate_call(to_number)
    return {"status": "Call initiated", "sid": result.sid}

# ✅ Route: Twilio webhook to respond with <Start><Stream>
@app.post("/voice")
async def voice():
    response = VoiceResponse()
    response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

    stream = Start().stream(
        url="wss://your-domain.com/twilio-audio",  # <== use your WebSocket route here
        track="inbound_track"
    )
    response.append(stream)

    return Response(content=str(response), media_type="application/xml")


# ✅ WebSocket route for real-time audio from Twilio
@app.websocket("/twilio-audio")
async def twilio_audio_stream(websocket: WebSocket):
    await websocket.accept()
    await handle_twilio_media_stream(websocket)

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
