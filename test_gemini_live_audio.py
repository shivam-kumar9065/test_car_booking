# test_gemini_live_audio.py

import asyncio
import os
import pyaudio
import traceback
from services.gemini_client import start_live_session

# Audio Config
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000     # Mic input
RECEIVE_SAMPLE_RATE = 24000  # Gemini output
CHUNK_SIZE = 1024

pya = pyaudio.PyAudio()

class AudioChat:
    def __init__(self):
        self.session = None
        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize=5)
        self.audio_stream = None

    async def listen_mic(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )

        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def send_audio(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

    async def receive_response(self):
        while True:
            turn = self.session.receive()
            async for response in turn:
                if response.data:
                    self.audio_in_queue.put_nowait(response.data)
                if response.text:
                    print("Gemini:", response.text.strip())

    async def play_audio(self):
        speaker = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )

        while True:
            audio_bytes = await self.audio_in_queue.get()
            await asyncio.to_thread(speaker.write, audio_bytes)

    async def run(self):
        try:
            session_ctx = start_live_session()
            async with session_ctx as session:
                self.session = session
                print("🎙️ Gemini Voice Chat started. Speak into your microphone (Ctrl+C to stop).")

                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.listen_mic())
                    tg.create_task(self.send_audio())
                    tg.create_task(self.receive_response())
                    tg.create_task(self.play_audio())

        except Exception as e:
            if self.audio_stream:
                self.audio_stream.close()
            traceback.print_exception(e)
        finally:
            print("Voice chat ended.")

if __name__ == "__main__":
    try:
        audio_chat = AudioChat()
        asyncio.run(audio_chat.run())
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        pya.terminate()
