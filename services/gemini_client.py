# # services/gemini_client.py

# import os
# from google import genai
# from google.genai.types import LiveConnectConfig, HttpOptions, Modality

# # Hardcoded or environment-based project settings
# PROJECT_ID = "qwiklabs-gcp-01-26190ba831b1"
# LOCATION = "us-central1"
# MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# # Initialize Gemini Client with Vertex AI
# client = genai.Client(
#     vertexai=True,
#     project=PROJECT_ID,
#     location=LOCATION,
#     http_options=HttpOptions(api_version="v1beta1"),
# )

# # Gemini configuration for audio output
# CONFIG = LiveConnectConfig(response_modalities=[Modality.AUDIO])


# def start_live_session():
#     """Return Gemini Live session async context manager."""
#     return client.aio.live.connect(model=MODEL, config=CONFIG)



# services/gemini_client.py

import os
import base64
from google import genai
from google.genai.types import LiveConnectConfig, HttpOptions, Modality

# Load service account from base64 environment variable (for Railway)
def load_service_account_from_env():
    base64_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")
    if base64_key:
        key_path = "/tmp/service_account.json"
        with open(key_path, "wb") as f:
            f.write(base64.b64decode(base64_key))
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

# Ensure credentials are loaded before initializing Gemini
load_service_account_from_env()

# Project settings
PROJECT_ID = "qwiklabs-gcp-01-26190ba831b1"
LOCATION = "us-central1"
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Initialize Gemini Client using Vertex AI backend
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    http_options=HttpOptions(api_version="v1beta1"),
)

# Gemini configuration to receive audio responses
CONFIG = LiveConnectConfig(response_modalities=[Modality.AUDIO])

def start_live_session():
    """Return Gemini Live session async context manager."""
    return client.aio.live.connect(model=MODEL, config=CONFIG)

class GeminiAudioSession:
    """
    Helper class for sending audio to Gemini and receiving audio back.
    Wraps the async session context.
    """

    def __init__(self):
        self.session = None
        self.generator = None

    async def __aenter__(self):
        self.session = start_live_session()
        self.generator = await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def send_audio(self, audio_bytes: bytes):
        """Send raw 16kHz PCM audio to Gemini."""
        await self.generator.send_audio(audio_bytes)

    async def receive_audio(self):
        """Receive response audio bytes from Gemini."""
        async for response in self.generator:
            if response.audio:
                return response.audio.bytes
        return None

def start_gemini_audio_session():
    """Convenience function to use with `async with`."""
    return GeminiAudioSession()
