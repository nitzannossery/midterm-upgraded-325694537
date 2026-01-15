from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class AnalyzeRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000)
    ticker: Optional[str] = None  # optional helper if your system supports it

class Source(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    snippet: Optional[str] = None

class AgentOutput(BaseModel):
    agent: str
    content: str
    sources: List[Source] = []

class AnalyzeResponse(BaseModel):
    mode: str  # demo/live
    final_answer: str
    agent_outputs: List[AgentOutput] = []
    warnings: List[str] = []
    meta: Dict[str, str] = {}
