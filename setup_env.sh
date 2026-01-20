#!/bin/bash
# Setup environment variables for the Financial Multi-Agent System

echo "Setting up environment variables..."
echo ""

# Google API Key
export GOOGLE_API_KEY=AIzaSyBLfAQj_ZhK7bnyGBHPs-UCTSbklgk-5NM
export GOOGLE_MODEL=gemini-2.5-flash

# UI Configuration
export UI_MODE=live

# Retrieval Configuration
export ENABLE_RETRIEVAL=true
export REQUIRE_SOURCES=true

# API Configuration
export API_URL=http://localhost:8000

echo "✅ Environment variables set:"
echo "  - GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:20}..."
echo "  - GOOGLE_MODEL: $GOOGLE_MODEL"
echo "  - UI_MODE: $UI_MODE"
echo "  - ENABLE_RETRIEVAL: $ENABLE_RETRIEVAL"
echo ""
echo "To use these variables, run:"
echo "  source setup_env.sh"
echo ""
echo "Or create a .env file with:"
echo "  GOOGLE_API_KEY=AIzaSyBLfAQj_ZhK7bnyGBHPs-UCTSbklgk-5NM"
echo "  GOOGLE_MODEL=gemini-2.5-flash"
echo "  UI_MODE=live"
echo "  ENABLE_RETRIEVAL=true"
echo "  REQUIRE_SOURCES=true"
