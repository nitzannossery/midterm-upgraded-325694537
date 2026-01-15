from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.config import settings
from app.orchestrator import Orchestrator

app = FastAPI(title="Financial Multi-Agent System", version="1.0.0")

# Enable CORS for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orch = Orchestrator()

@app.get("/health")
def health():
    return {"status": "ok", "ui_mode": settings.ui_mode}

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if settings.ui_mode == "demo":
        # Demo mode: DO NOT run inference; show capabilities only
        return AnalyzeResponse(
            mode="demo",
            final_answer="Demo mode: This UI shows capabilities only. Switch UI_MODE=live to run the full pipeline.",
            agent_outputs=[],
            warnings=["DEMO_MODE enabled; no inference executed."],
            meta={"ui_mode": settings.ui_mode}
        )

    # Live inference
    return orch.run(req.query)
