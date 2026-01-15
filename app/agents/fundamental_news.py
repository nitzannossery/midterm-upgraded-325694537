from typing import Dict, Any
from app.agents.base import Agent
from app.schemas import AgentOutput
from app.llm.google_client import GoogleLLMClient

class FundamentalNewsAgent(Agent):
    name = "Fundamental & News Agent"
    
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
            # Use Google Gemini for analysis
            prompt = f"""Analyze the following financial query focusing on fundamental analysis and news:
Query: {query}

Available sources:
{chr(10).join([f"- {s.title}: {s.snippet or 'No snippet'}" for s in sources]) if sources else "No sources available"}

Provide:
1. Key fundamental metrics to consider
2. Recent news that may impact the analysis
3. Financial statement insights
4. Risk factors from filings"""
            
            try:
                content = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt="You are a financial analyst specializing in fundamental analysis and news interpretation.",
                    temperature=0.4,
                    max_tokens=500
                )
            except Exception as e:
                content = f"Fundamental analysis prepared. (LLM error: {str(e)})"
        else:
            content = (
                "Fundamental + news analysis prepared. (Google API not configured - using placeholder.)"
            )
        
        return AgentOutput(agent=self.name, content=content, sources=sources)
