from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput, Source
from app.llm.google_client import GoogleLLMClient

class MarketDataAgent(Agent):
    name = "Market Data Agent"
    
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
            # Use Google Gemini for market data analysis
            prompt = f"""Analyze market data requirements for the following query:
Query: {query}

Provide:
1. Key market metrics needed (prices, returns, volatility, etc.)
2. Timeframe considerations
3. Benchmark comparisons if relevant
4. Market trends and patterns"""
            
            try:
                content = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt="You are a market data analyst specializing in financial market analysis.",
                    temperature=0.3,
                    max_tokens=400
                )
            except Exception as e:
                content = f"Market snapshot prepared. (LLM error: {str(e)})"
        else:
            content = (
                "Market snapshot prepared. (Google API not configured - using placeholder.)"
            )
        
        return AgentOutput(agent=self.name, content=content, sources=sources)
