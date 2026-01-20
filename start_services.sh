#!/bin/bash
# Start all services with proper environment variables

echo "🚀 Starting Financial Multi-Agent System Services..."
echo ""

# Set environment variables
export GOOGLE_API_KEY=AIzaSyBLfAQj_ZhK7bnyGBHPs-UCTSbklgk-5NM
export GOOGLE_MODEL=gemini-2.5-flash
export UI_MODE=live
export ENABLE_RETRIEVAL=true
export REQUIRE_SOURCES=true
export API_URL=http://localhost:8000

# Kill existing processes if running
echo "Checking for existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
sleep 1

# Start API server
echo "📡 Starting API server on http://localhost:8000..."
cd "$(dirname "$0")"
uvicorn app.api:app --reload --port 8000 --host 0.0.0.0 > api.log 2>&1 &
API_PID=$!
echo "   API PID: $API_PID"

# Wait for API to be ready
sleep 3
curl -s http://localhost:8000/health > /dev/null && echo "   ✅ API is ready!" || echo "   ⏳ API starting..."

# Start Streamlit UI
echo ""
echo "🌐 Starting Streamlit UI on http://localhost:8501..."
streamlit run ui/streamlit_app.py --server.port 8501 --server.headless true > streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "   Streamlit PID: $STREAMLIT_PID"

# Wait for Streamlit to be ready
sleep 3
curl -s http://localhost:8501 > /dev/null && echo "   ✅ Streamlit UI is ready!" || echo "   ⏳ Streamlit starting..."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ All services started!"
echo ""
echo "📊 Services:"
echo "   - API: http://localhost:8000"
echo "   - Streamlit UI: http://localhost:8501"
echo ""
echo "📝 Logs:"
echo "   - API: api.log"
echo "   - Streamlit: streamlit.log"
echo ""
echo "🌐 Opening UI in browser..."
sleep 2
open http://localhost:8501 2>/dev/null || echo "   Please open http://localhost:8501 in your browser"
