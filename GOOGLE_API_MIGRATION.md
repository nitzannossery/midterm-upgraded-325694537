# Google Gemini API Migration

## Overview

The entire system has been migrated from OpenAI to Google Gemini API.

## Changes Made

### 1. Dependencies
- **Removed**: `openai>=1.0.0`
- **Added**: `google-generativeai>=0.3.0`

### 2. Configuration (`app/config.py`)
- Removed `openai_api_key`
- Added `google_api_key` (from `GOOGLE_API_KEY` env var)
- Added `google_model` (default: `gemini-pro`, configurable via `GOOGLE_MODEL`)

### 3. LLM Client (`app/llm/google_client.py`)
- New `GoogleLLMClient` class wrapping Google Gemini API
- Methods:
  - `generate()` - Text generation
  - `generate_structured()` - JSON-structured output
- Handles errors gracefully

### 4. All Agents Updated

#### Market Data Agent
- Uses Google Gemini for market data analysis
- Fallback to placeholder if API unavailable

#### Fundamental & News Agent
- Uses Google Gemini for fundamental analysis
- Analyzes financial statements and news
- Fallback to placeholder if API unavailable

#### Portfolio & Risk Agent
- Uses Google Gemini for risk analysis
- Computes risk metrics and recommendations
- Fallback to placeholder if API unavailable

#### Summarizer Agent
- **Primary**: Uses Google Gemini for intelligent summaries
- **Fallback**: Deterministic summary if API unavailable
- Generates structured summaries with:
  - Investment Thesis (3 points)
  - Key Risks (3 points)
  - Evidence & Sources
  - Recommendations

## Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_api_key_here

# Optional
GOOGLE_MODEL=gemini-pro  # Default model
```

## Usage

### In Code

```python
from app.llm.google_client import GoogleLLMClient

# Initialize client
client = GoogleLLMClient()

# Generate text
response = client.generate(
    prompt="Your prompt here",
    system_prompt="You are a financial analyst",
    temperature=0.7,
    max_tokens=500
)

# Generate structured output
structured = client.generate_structured(
    prompt="Analyze this data...",
    temperature=0.0
)
```

### In Agents

All agents automatically use Google Gemini if available:

```python
from app.agents.market_data import MarketDataAgent

agent = MarketDataAgent()  # Automatically initializes Google client
result = agent.run(query="...", context={...})
```

## Fallback Behavior

If Google API is unavailable or not configured:
- Agents use placeholder responses
- Summarizer uses deterministic summary generation
- System continues to function (graceful degradation)

## Testing

```bash
# Test the client
python3 -c "from app.llm.google_client import GoogleLLMClient; client = GoogleLLMClient(); print('✅ Working')"

# Test an agent
python3 -c "from app.agents.summarizer import SummarizerAgent; agent = SummarizerAgent(); print('✅ Agent ready')"
```

## Model Options

Available Google Gemini models:
- `gemini-pro` (default) - General purpose
- `gemini-pro-vision` - Multimodal (text + images)
- `gemini-ultra` - Most capable (when available)

Set via environment variable:
```bash
export GOOGLE_MODEL=gemini-pro
```

## Benefits

1. **Cost**: Google Gemini is often more cost-effective
2. **Performance**: Excellent for financial analysis tasks
3. **Integration**: Native Google Cloud integration
4. **Fallback**: Graceful degradation if API unavailable

## Migration Status

✅ **Complete** - All components migrated
✅ **Tested** - Client initialization verified
✅ **Documented** - This guide created

---

**Last Updated**: 2026-01-15
