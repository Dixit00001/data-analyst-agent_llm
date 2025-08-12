import os

# Securely load from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_MODEL = "gpt-4o-mini"

# Optional: ngrok token — leave empty if already set using ngrok CLI config
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN", "")

TIMEOUT = 100  # seconds for execution
