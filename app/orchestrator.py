from typing import List, Dict, Any
from app.schemas import AnalyzeResponse, AgentOutput
from app.config import settings
from app.retrieval.retriever import Retriever

from app.agents.market_data import MarketDataAgent
from app.agents.fundamental_news import FundamentalNewsAgent
from app.agents.portfolio_risk import PortfolioRiskAgent
from app.agents.summarizer import SummarizerAgent

class Orchestrator:
    def __init__(self) -> None:
        self.retriever = Retriever()
        self.agents = [
            MarketDataAgent(),
            FundamentalNewsAgent(),
            PortfolioRiskAgent(),
        ]
        self.summarizer = SummarizerAgent()

    def run(self, query: str) -> AnalyzeResponse:
        warnings: List[str] = []
        sources = []

        if settings.enable_retrieval:
            sources = self.retriever.retrieve(query=query, top_k=5)
            if settings.require_sources and not sources:
                warnings.append("No sources retrieved. Output may be incomplete; consider expanding the corpus or increasing Top-K.")

        # Run specialized agents
        agent_outputs: List[AgentOutput] = []
        for agent in self.agents:
            out = agent.run(query=query, context={"sources": sources})
            agent_outputs.append(out)

        # Summarize (LLM would run here in real setup)
        summary = self.summarizer.run(
            query=query,
            context={"sources": sources, "agent_outputs": agent_outputs}
        )

        final_answer = summary.content
        if settings.require_sources and not sources:
            # enforce a safe behavior
            final_answer = (
                "I do not have enough retrieved evidence to answer reliably. "
                "Please provide documents or connect a data source, then retry."
            )

        return AnalyzeResponse(
            mode="live",
            final_answer=final_answer,
            agent_outputs=agent_outputs + [summary],
            warnings=warnings,
            meta={"ui_mode": settings.ui_mode}
        )
