from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput
from app.llm.google_client import GoogleLLMClient

class PortfolioRiskAgent(Agent):
    name = "Portfolio & Risk Agent"
    
    def __init__(self):
        """Initialize agent with Google LLM client."""
        try:
            self.llm_client = GoogleLLMClient()
            self.use_llm = True
        except Exception:
            self.llm_client = None
            self.use_llm = False

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        sources = context.get("sources", [])
        
        if self.use_llm and self.llm_client:
            # Use Google Gemini for risk analysis
            prompt = f"""Analyze portfolio risk for the following query:
Query: {query}

Provide:
1. Risk metrics (volatility, VaR, concentration risk)
2. Portfolio composition analysis
3. Stress test scenarios
4. Risk mitigation recommendations"""
            
            try:
                content = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt="You are a quantitative risk analyst specializing in portfolio risk management.",
                    temperature=0.3,
                    max_tokens=500
                )
            except Exception as e:
                content = f"Portfolio risk analysis prepared. (LLM error: {str(e)})"
        else:
            content = (
                "Portfolio risk analysis prepared. (Google API not configured - using placeholder.)"
            )
        
        return AgentOutput(agent=self.name, content=content, sources=sources)
