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

    stream = Start().stream(
        url="wss://testcarbooking-env.up.railway.app/twilio-audio",
         track="inbound_track",
         status_callback="https://testcarbooking-env.up.railway.app/twilio-callback", # YOUR RAILWAY URL HERE
         status_callback_event="start error end" # Twilio will send POST requests for these events
    )
    print("➡️ Adding Stream tag")
    response.append(stream)

    xml_str = str(response)
    print("🛰️ XML sent to Twilio:\n", xml_str)

    return Response(content=xml_str, media_type="application/xml")

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

















# # app.py

# import uvicorn
# import os
# import logging
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import Response
# from fastapi.middleware.cors import CORSMiddleware
# from twilio.twiml.voice_response import VoiceResponse, Start, Stream
# import json # Added for simplified handle_twilio_media
# import asyncio # Added for simplified handle_twilio_media

# # Temporarily comment out or remove this line to use the simplified handler below
# # from services.media_stream_handler import handle_twilio_media 

# # Assuming these exist and work, keep them
# from services.twilio_service import initiate_call 
# from utils.google_credentials import setup_google_credentials_from_env 

# # Configure logging for maximum verbosity to capture all details
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# setup_google_credentials_from_env()

# app = FastAPI()

# # Optional: Enable CORS for development or frontend integration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- SIMPLIFIED handle_twilio_media FOR DEBUGGING WEBSOCKET CONNECTION ---
# # This version will help us isolate if the issue is with the initial WebSocket handshake
# # or something in your Gemini integration.
# async def handle_twilio_media(websocket: WebSocket):
#     logging.debug("🎧 [DEBUG] handle_twilio_media: Function entered (simplified version).")
#     try:
#         # Keep the connection open indefinitely, or until Twilio sends a stop
#         async for message in websocket.iter_json():
#             event_type = message.get("event")
#             sequence_number = message.get("sequenceNumber")
#             logging.info(f"[DEBUG] Received Twilio event: {event_type} (Seq: {sequence_number})")

#             if event_type == "start":
#                 logging.info("🔗 [DEBUG] Twilio stream 'start' event received. Sending mark.")
#                 await websocket.send_text(json.dumps({
#                     "event": "mark",
#                     "mark": {"name": "server_ready_debug"}
#                 }))
#                 logging.info("[DEBUG] Sent 'mark' event to Twilio: server_ready_debug")
#             elif event_type == "media":
#                 # Just log, don't process audio to rule out processing errors
#                 # logging.debug(f"[DEBUG] Received media payload (first 50 chars): {message.get('media', {}).get('payload', '')[:50]}")
#                 pass # Do nothing with media for now
#             elif event_type == "stop":
#                 logging.info("⛔ [DEBUG] Twilio stream 'stop' event received. Closing connection.")
#                 break # Exit the loop
#             elif event_type == "mark":
#                 logging.info(f"✅ [DEBUG] Twilio acknowledged mark: {message.get('mark', {}).get('name')}")
#             elif event_type == "error":
#                 logging.error(f"❌ [DEBUG] Twilio stream 'error' event received: {message.get('error', {}).get('message')}")
#                 break
#             else:
#                 logging.warning(f"❓ [DEBUG] Unknown Twilio event type received: {event_type}")

#     except asyncio.CancelledError:
#         logging.info("[DEBUG] WebSocket handling task cancelled.")
#     except Exception as e:
#         logging.error(f"❌ [DEBUG] Critical error during simplified WebSocket handling: {e}", exc_info=True)
#         if websocket.client_state == 1: # WebSocketState.CONNECTED
#             await websocket.close(code=1011) # Internal Error
#     finally:
#         logging.info("🔗 [DEBUG] Simplified WebSocket handling finished.")
# # --- END SIMPLIFIED handle_twilio_media ---


# @app.get("/")
# async def root():
#     logging.info("GET / - Root endpoint accessed.")
#     return {"message": "🚗 Car Service Voice Agent is running!"}


# # ✅ Route: Start Twilio call via API
# @app.post("/call")
# async def call_customer(request: Request):
#     logging.info("POST /call - Initiating call request.")
#     data = await request.json()
#     to_number = data.get("to")
#     if not to_number:
#         logging.warning("POST /call - Missing 'to' number in request.")
#         return {"error": "Missing 'to' number"}

#     try:
#         result = initiate_call(to_number)
#         logging.info(f"POST /call - Call initiated successfully. SID: {result.sid}")
#         return {"status": "Call initiated", "sid": result.sid}
#     except Exception as e:
#         logging.error(f"POST /call - Error initiating call: {e}", exc_info=True)
#         return {"error": f"Failed to initiate call: {e}"}


# # ✅ Route: Twilio webhook to respond with <Start><Stream>
# @app.post("/voice")
# async def voice():
#     response = VoiceResponse()
#     response.say("Connecting you to the car service assistant.", voice="Polly.Joanna")

#     # **************************************************************************
#     # *** IMPORTANT: STATUS CALLBACK IS CRITICAL FOR DEBUGGING ***
#     # *** Using your provided Railway URL for status_callback ***
#     # **************************************************************************
#     stream = Start().stream(
#         url="wss://testcarbooking-env.up.railway.app/twilio-audio",
#         track="inbound_track",
#         status_callback="https://testcarbooking-env.up.railway.app/twilio-callback", # YOUR RAILWAY URL HERE
#         status_callback_event="start error end" # Twilio will send POST requests for these events
#     )
#     logging.info("➡️ Adding Stream tag to TwiML with statusCallback.")
#     response.append(stream)

#     xml_str = str(response)
#     logging.info("🛰️ XML sent to Twilio:\n%s", xml_str)

#     return Response(content=xml_str, media_type="application/xml")


# # ✅ WebSocket route for real-time audio from Twilio
# @app.websocket("/twilio-audio")
# async def twilio_audio_stream(websocket: WebSocket):
#     # Log immediately when the function is entered
#     logging.info("🎧 [VERY EARLY DEBUG] Incoming WebSocket connection request to /twilio-audio endpoint.")
#     try:
#         # Log before accepting the connection
#         logging.info("Attempting to accept WebSocket connection...")
#         await websocket.accept()
#         # Log after successfully accepting
#         logging.info("✅ WebSocket connection accepted for /twilio-audio.")
#         # Call the simplified handle_twilio_media defined above for debugging connection issues
#         await handle_twilio_media(websocket) 
#     except Exception as e:
#         # Log any exception during the connection or handling
#         logging.error(f"❌ WebSocket connection error in /twilio-audio endpoint: {e}", exc_info=True)
#     finally:
#         logging.info("🔗 WebSocket connection handler finished for /twilio-audio.")


# # ✅ Route: Twilio status callback for Media Streams
# @app.post("/twilio-callback")
# async def twilio_callback(request: Request):
#     form_data = await request.form()
#     logging.info("🔔 Received Twilio Status Callback!")
#     logging.info("Callback Data: %s", dict(form_data))
    
#     stream_status = form_data.get("StreamStatus")
#     if stream_status == "error":
#         error_code = form_data.get("ErrorCode")
#         error_message = form_data.get("ErrorMessage")
#         logging.error(f"❌ Twilio Stream Error: Code={error_code}, Message={error_message}")
#         # THIS IS THE ERROR MESSAGE YOU NEED TO SEE!
#     elif stream_status == "started":
#         logging.info("✅ Twilio Stream reported as STARTED.")
#     elif stream_status == "stopped":
#         logging.info("🛑 Twilio Stream reported as STOPPED.")
#     else:
#         logging.info(f"ℹ️ Twilio Stream status: {stream_status}")

#     return Response(content="", media_type="text/plain")


# # Run the FastAPI app
# if __name__ == "__main__":
#     uvicorn.run("app:app", host="0.0.0.0", port=8000, log_level="debug") # Set Uvicorn's log_level to debug
