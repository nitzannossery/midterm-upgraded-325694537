from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import subprocess
import asyncio
from typing import Dict
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.config import settings
from app.orchestrator import Orchestrator

app = FastAPI(title="Financial Multi-Agent System", version="1.0.0")

# Enable CORS for UI (including file:// protocol for local HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows file://, localhost, and any origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

orch = Orchestrator()

def get_git_version() -> str:
    """Get git commit hash for version endpoint."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"

@app.get("/health")
def health():
    return {"status": "ok", "ui_mode": settings.ui_mode}

@app.get("/version")
def version():
    """Return version information including git commit."""
    return {
        "version": "1.0.0",
        "git_commit": get_git_version(),
        "ui_mode": settings.ui_mode,
        "enable_retrieval": settings.enable_retrieval,
        "require_sources": settings.require_sources
    }

@app.get("/metrics")
def metrics():
    """Return system metrics."""
    return {
        "ui_mode": settings.ui_mode,
        "retrieval_enabled": settings.enable_retrieval,
        "sources_required": settings.require_sources,
        "agents_count": len(orch.agents) + 1,  # +1 for summarizer
        "retrieval_top_k": 5
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, request: Request):
    """Analyze financial query through multi-agent system."""
    start_time = time.time()
    
    try:
        if settings.ui_mode == "demo":
            # Demo mode: DO NOT run inference; show capabilities only
            return AnalyzeResponse(
                mode="demo",
                final_answer="Demo mode: This UI shows capabilities only. Switch UI_MODE=live to run the full pipeline.",
                agent_outputs=[],
                warnings=["DEMO_MODE enabled; no inference executed."],
                meta={"ui_mode": settings.ui_mode}
            )

        # Live inference with timeout protection
        try:
            # Run orchestrator with timeout (25 seconds max)
            # Use asyncio.to_thread to run sync code in async context
            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(orch.run, req.query),
                    timeout=25.0
                )
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=504,
                    detail="Request timeout: Analysis took too long (>25s). Please try a simpler query."
                )
            
            elapsed_time = time.time() - start_time
            
            # Add timing to meta
            result.meta["execution_time_seconds"] = f"{elapsed_time:.2f}"
            result.meta["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error during analysis: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        # Generic error handling
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e),
                "mode": "error"
            }
        )
