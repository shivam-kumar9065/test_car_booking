# # app.py

# import uvicorn
# import os
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import Response
# from fastapi.middleware.cors import CORSMiddleware
# from twilio.twiml.voice_response import VoiceResponse, Start, Stream
# from services.media_stream_handler import handle_twilio_media
# from services.twilio_service import initiate_call
# from utils.google_credentials import setup_google_credentials_from_env
# setup_google_credentials_from_env()

# app = FastAPI()

# # Optional: Enable CORS for development or frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# async def root():
#     return {"message": "🚗 Car Service Voice Agent is running!"}


# # ✅ Route: Start Twilio call via API
# @app.post("/call")
# async def call_customer(request: Request):
#     data = await request.json()
#     to_number = data.get("to")
#     if not to_number:
#         return {"error": "Missing 'to' number"}

#     result = initiate_call(to_number)
#     return {"status": "Call initiated", "sid": result.sid}

# # ✅ Route: Twilio webhook to respond with <Start><Stream>
# # @app.post("/voice")
# # async def voice():
# #     response = VoiceResponse()
# #     response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

# #     stream = Start().stream(
# #         url="wss://testcarbooking-env.up.railway.app/twilio-audio",  # <== use your WebSocket route here
# #         track="inbound_track"
# #     )
# #     print("Going to websocket")
# #     response.append(stream)
# #     print("Going to websocket__1")

# #     return Response(content=str(response), media_type="application/xml")

# @app.post("/voice")
# async def voice():
#     response = VoiceResponse()
#     response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

#     stream = Start().stream(
#         url="wss://testcarbooking-env.up.railway.app/twilio-audio",
#         track="inbound_track"
#     )
#     #<Stream track="inbound_track" url="wss://testcarbooking-env.up.railway.app/twilio-audio" statusCallbackEvent="start error end" statusCallback="https://yourserver.com/twilio-callback" />
#     print("➡️ Adding Stream tag")
#     response.append(stream)

#     xml_str = str(response)
#     print("🛰️ XML sent to Twilio:\n", xml_str)

#     return Response(content=xml_str, media_type="application/xml")



# # # ✅ WebSocket route for real-time audio from Twilio
# # @app.websocket("/twilio-audio")
# # async def twilio_audio_stream(websocket: WebSocket):
# #     await websocket.accept()
# #     await handle_twilio_media(websocket)
# @app.websocket("/twilio-audio")
# async def twilio_audio_stream(websocket: WebSocket):
#     print("🎧 Incoming WebSocket connection from Twilio")
#     try:
#         await websocket.accept()
#         print("✅ WebSocket accepted")
#         await handle_twilio_media(websocket)
#     except Exception as e:
#         print("❌ WebSocket Error:", e)

# # Run the FastAPI app
# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000)


















# app.py

import uvicorn
import os
import logging # Import the logging module
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Start, Stream
from services.media_stream_handler import handle_twilio_media
from services.twilio_service import initiate_call # Assuming this exists and works
from utils.google_credentials import setup_google_credentials_from_env # Assuming this exists and works

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# For more detailed WebSocket debugging, you might set level=logging.DEBUG temporarily

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
    logging.info("GET / - Root endpoint accessed.")
    return {"message": "🚗 Car Service Voice Agent is running!"}


# ✅ Route: Start Twilio call via API
@app.post("/call")
async def call_customer(request: Request):
    logging.info("POST /call - Initiating call request.")
    data = await request.json()
    to_number = data.get("to")
    if not to_number:
        logging.warning("POST /call - Missing 'to' number in request.")
        return {"error": "Missing 'to' number"}

    try:
        result = initiate_call(to_number)
        logging.info(f"POST /call - Call initiated successfully. SID: {result.sid}")
        return {"status": "Call initiated", "sid": result.sid}
    except Exception as e:
        logging.error(f"POST /call - Error initiating call: {e}", exc_info=True)
        return {"error": f"Failed to initiate call: {e}"}


# ✅ Route: Twilio webhook to respond with <Start><Stream>
@app.post("/voice")
async def voice():
    response = VoiceResponse()
    response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

    # **************************************************************************
    # *** IMPORTANT: ADD STATUS CALLBACK FOR DEBUGGING ***
    # *** REPLACE "https://yourserver.com/twilio-callback" ***
    # *** WITH YOUR ACTUAL PUBLIC URL ON RAILWAY FOR THIS CALLBACK ***
    # **************************************************************************
    stream = Start().stream(
        url="wss://testcarbooking-env.up.railway.app/twilio-audio",
        track="inbound_track",
        status_callback="https://testcarbooking-env.up.railway.app/twilio-callback", # <--- REPLACE THIS
        status_callback_event="start error end" # Twilio will send POST requests for these events
    )
    logging.info("➡️ Adding Stream tag to TwiML with statusCallback.")
    response.append(stream)

    xml_str = str(response)
    logging.info("🛰️ XML sent to Twilio:\n%s", xml_str)

    return Response(content=xml_str, media_type="application/xml")


# ✅ WebSocket route for real-time audio from Twilio
@app.websocket("/twilio-audio")
async def twilio_audio_stream(websocket: WebSocket):
    logging.info("🎧 Incoming WebSocket connection request to /twilio-audio")
    try:
        await websocket.accept()
        logging.info("✅ WebSocket connection accepted for /twilio-audio")
        # Call your actual handle_twilio_media from services.media_stream_handler
        await handle_twilio_media(websocket)
    except Exception as e:
        logging.error(f"❌ WebSocket connection error in /twilio-audio endpoint: {e}", exc_info=True)
    finally:
        logging.info("🔗 WebSocket connection handler finished for /twilio-audio")


# ✅ Route: Twilio status callback for Media Streams
@app.post("/twilio-callback")
async def twilio_callback(request: Request):
    form_data = await request.form()
    logging.info("🔔 Received Twilio Status Callback!")
    logging.info("Callback Data: %s", dict(form_data))
    
    stream_status = form_data.get("StreamStatus")
    if stream_status == "error":
        error_code = form_data.get("ErrorCode")
        error_message = form_data.get("ErrorMessage")
        logging.error(f"❌ Twilio Stream Error: Code={error_code}, Message={error_message}")
        # THIS IS THE ERROR MESSAGE YOU NEED TO SEE!
    elif stream_status == "started":
        logging.info("✅ Twilio Stream reported as STARTED.")
    elif stream_status == "stopped":
        logging.info("🛑 Twilio Stream reported as STOPPED.")
    else:
        logging.info(f"ℹ️ Twilio Stream status: {stream_status}")

    return Response(content="", media_type="text/plain")


# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)


