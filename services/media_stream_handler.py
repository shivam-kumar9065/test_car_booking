# services/media_stream_handler.py

import asyncio
import base64
import json
import websockets
import sounddevice as sd
from services.gemini_client import start_live_session

async def handle_twilio_media(websocket):
    print("🎧 Incoming WebSocket connection from Twilio")

    async with start_live_session() as session:
        print("🧠 Gemini session started")

        # Task to stream audio from Gemini → Twilio
        async def gemini_to_twilio():
            async for chunk in session.stream_responses():
                if chunk.audio:
                    await websocket.send(
                        json.dumps({
                            "event": "media",
                            "media": {
                                "payload": base64.b64encode(chunk.audio).decode("utf-8")
                            }
                        })
                    )

        gemini_task = asyncio.create_task(gemini_to_twilio())

        try:
            async for message in websocket:
                data = json.loads(message)

                if data.get("event") == "start":
                    print("🔗 Twilio stream started")

                elif data.get("event") == "media":
                    audio_data = base64.b64decode(data["media"]["payload"])
                    await session.send_audio(audio_data)

                elif data.get("event") == "stop":
                    print("⛔ Twilio stream stopped")
                    break

        finally:
            await session.end()
            gemini_task.cancel()
            print("✅ Session closed")
