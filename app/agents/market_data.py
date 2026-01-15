from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput, Source

class MarketDataAgent(Agent):
    name = "Market Data Agent"

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        # Replace with real market data retrieval / calculations
        sources = context.get("sources", [])
        content = (
            "Market snapshot prepared. (Replace this with real prices/returns/volatility.)"
        )
        return AgentOutput(agent=self.name, content=content, sources=sources)
