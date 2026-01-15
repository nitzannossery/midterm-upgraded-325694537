from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput

class PortfolioRiskAgent(Agent):
    name = "Portfolio & Risk Agent"

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        sources = context.get("sources", [])
        content = (
            "Portfolio risk analysis prepared. (Replace with real VaR/stress/scenario logic.)"
        )
        return AgentOutput(agent=self.name, content=content, sources=sources)
