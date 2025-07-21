# utils/google_credentials.py

import os
import base64

def setup_google_credentials_from_env():
    """
    Decode base64-encoded Google service account credentials from an env variable
    and set the GOOGLE_APPLICATION_CREDENTIALS path.
    """

    base64_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_BASE64")

    if not base64_creds:
        raise EnvironmentError("❌ GOOGLE_APPLICATION_CREDENTIALS_BASE64 is not set.")

    key_path = "/tmp/service_account.json"

    # Decode and save to a file
    with open(key_path, "wb") as f:
        f.write(base64.b64decode(base64_creds))

    # Set GOOGLE_APPLICATION_CREDENTIALS env for Google SDK to pick it up
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    print("✅ Google Application Credentials set from base64.")
