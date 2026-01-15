# API Integration Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run FastAPI Server
```bash
# Option 1: Using the script
chmod +x run_api.sh
./run_api.sh

# Option 2: Direct command
export UI_MODE=live
uvicorn app.api:app --reload --port 8000
```

### 3. Access the UI

**HTML UI (recommended):**
- Open `evaluation/ui/dashboard.html` in your browser
- The UI will automatically connect to `http://localhost:8000`

**Streamlit UI (alternative):**
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
# Or: streamlit run ui/streamlit_app.py
```

## Environment Variables

```bash
# UI Mode: "demo" or "live"
export UI_MODE=live

# Enable/disable retrieval
export ENABLE_RETRIEVAL=true

# Require sources in responses
export REQUIRE_SOURCES=true

# API URL (for Streamlit)
export API_URL=http://localhost:8000
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Analyze Query
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I invest in AAPL?"}'
```

## Architecture

```
┌─────────────────┐
│   HTML/Streamlit │
│      UI         │
└────────┬────────┘
         │ HTTP POST /analyze
         ▼
┌─────────────────┐
│   FastAPI       │
│   app/api.py    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Orchestrator   │
│ app/orchestrator│
└────────┬────────┘
         │
    ┌────┴────┬──────────┬─────────────┐
    ▼         ▼          ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│ Market │ │Fundam. │ │Portfolio│ │Summarizer│
│  Data  │ │  News  │ │  Risk   │ │  Agent   │
└────────┘ └────────┘ └────────┘ └──────────┘
```

## Important Notes

1. **Evaluation vs UI**: 
   - UI is for real user inference
   - Evaluation runs offline via `evaluation/runners/`
   - Never mix test cases with UI

2. **Demo Mode**:
   - Set `UI_MODE=demo` to show capabilities without running inference
   - Useful for demonstrations

3. **Production**:
   - Replace placeholder agent logic with real implementations
   - Connect to actual data sources
   - Implement proper retrieval (vector DB, etc.)

## Next Steps

1. Implement real agent logic in `app/agents/`
2. Connect to data sources (market data APIs, financial databases)
3. Implement retrieval with vector database
4. Add LLM integration for summarization
5. Deploy API to production server
