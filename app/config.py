from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # "demo" shows capabilities; "live" runs inference pipeline
    ui_mode: str = os.getenv("UI_MODE", "live").lower()  # Default: live

    # Optional: turn retrieval on/off for quick dev
    enable_retrieval: bool = os.getenv("ENABLE_RETRIEVAL", "true").lower() == "true"

    # Safety: require citations/sources in live mode
    require_sources: bool = os.getenv("REQUIRE_SOURCES", "true").lower() == "true"
    
    # API Keys
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    google_model: str = os.getenv("GOOGLE_MODEL", "gemini-2.5-flash")  # Default to gemini-2.5-flash (fast) or gemini-2.5-pro (more capable)

settings = Settings()
