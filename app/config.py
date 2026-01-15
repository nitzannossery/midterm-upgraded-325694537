from pydantic import BaseModel
import os

class Settings(BaseModel):
    # "demo" shows capabilities; "live" runs inference pipeline
    ui_mode: str = os.getenv("UI_MODE", "live").lower()  # Default: live

    # Optional: turn retrieval on/off for quick dev
    enable_retrieval: bool = os.getenv("ENABLE_RETRIEVAL", "true").lower() == "true"

    # Safety: require citations/sources in live mode
    require_sources: bool = os.getenv("REQUIRE_SOURCES", "true").lower() == "true"

settings = Settings()
