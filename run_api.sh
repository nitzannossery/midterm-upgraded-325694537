#!/bin/bash
# Run FastAPI server

echo "Starting Financial Multi-Agent System API..."
echo "Mode: ${UI_MODE:-live}"
echo ""

export UI_MODE=${UI_MODE:-live}
export ENABLE_RETRIEVAL=${ENABLE_RETRIEVAL:-true}
export REQUIRE_SOURCES=${REQUIRE_SOURCES:-true}

uvicorn app.api:app --reload --port 8000 --host 0.0.0.0
