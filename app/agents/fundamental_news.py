from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput

class FundamentalNewsAgent(Agent):
    name = "Fundamental & News Agent"

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        sources = context.get("sources", [])
        content = (
            "Fundamental + news analysis prepared. (Replace with real filings/news reasoning.)"
        )
        return AgentOutput(agent=self.name, content=content, sources=sources)
