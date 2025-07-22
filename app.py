# app.py

import uvicorn
import os
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from services.media_stream_handler import handle_twilio_media
from services.twilio_service import initiate_call
from utils.google_credentials import setup_google_credentials_from_env
setup_google_credentials_from_env()

app = FastAPI()

# Optional: Enable CORS for development or frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "🚗 Car Service Voice Agent is running!"}


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
# @app.post("/voice")
# async def voice():
#     response = VoiceResponse()
#     response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

#     stream = Start().stream(
#         url="wss://testcarbooking-env.up.railway.app/twilio-audio",  # <== use your WebSocket route here
#         track="inbound_track"
#     )
#     print("Going to websocket")
#     response.append(stream)
#     print("Going to websocket__1")

#     return Response(content=str(response), media_type="application/xml")

@app.post("/voice")
async def voice():
    response = VoiceResponse()
    response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

    # stream = Start().stream(
    #     url="wss://testcarbooking-env.up.railway.app/twilio-audio",
    #     track="inbound_track"
    # )
    <Stream track="inbound_track" url="wss://testcarbooking-env.up.railway.app/twilio-audio" statusCallbackEvent="start error end" statusCallback="https://yourserver.com/twilio-callback" />
    print("➡️ Adding Stream tag")
    response.append(stream)

    xml_str = str(response)
    print("🛰️ XML sent to Twilio:\n", xml_str)

    return Response(content=xml_str, media_type="application/xml")



# # ✅ WebSocket route for real-time audio from Twilio
# @app.websocket("/twilio-audio")
# async def twilio_audio_stream(websocket: WebSocket):
#     await websocket.accept()
#     await handle_twilio_media(websocket)
@app.websocket("/twilio-audio")
async def twilio_audio_stream(websocket: WebSocket):
    print("🎧 Incoming WebSocket connection from Twilio")
    try:
        await websocket.accept()
        print("✅ WebSocket accepted")
        await handle_twilio_media(websocket)
    except Exception as e:
        print("❌ WebSocket Error:", e)

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
