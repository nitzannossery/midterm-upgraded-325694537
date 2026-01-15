from typing import Dict, Any, List
from app.agents.base import Agent
from app.schemas import AgentOutput, Source
from app.llm.google_client import GoogleLLMClient

class SummarizerAgent(Agent):
    name = "Summarizer Agent"
    
    def __init__(self):
        """Initialize summarizer with Google LLM client."""
        try:
            self.llm_client = GoogleLLMClient()
            self.use_llm = True
        except Exception as e:
            print(f"Warning: Google API not available, using deterministic summary: {e}")
            self.llm_client = None
            self.use_llm = False

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        sources: List[Source] = context.get("sources", [])
        agent_outputs = context.get("agent_outputs", [])

        # Use LLM if available, otherwise use deterministic summary
        if self.use_llm and self.llm_client:
            content = self._generate_llm_summary(query, agent_outputs, sources)
        else:
            content = self._generate_summary(query, agent_outputs, sources)

        return AgentOutput(agent=self.name, content=content, sources=sources)
    
    def _generate_llm_summary(self, query: str, agent_outputs: List[AgentOutput], sources: List[Source]) -> str:
        """Generate summary using Google Gemini LLM."""
        system_prompt = """You are a financial analyst summarizing multi-agent analysis results.
Provide a structured summary with:
1. Investment Thesis (3 key points)
2. Key Risks (3 main risks)
3. Evidence & Sources (list sources used)
4. Recommendation (actionable advice)

Format the response clearly with sections."""
        
        # Build context from agent outputs
        agent_context = []
        for agent_out in agent_outputs:
            agent_context.append(f"{agent_out.agent}:\n{agent_out.content}")
        
        sources_context = []
        for source in sources:
            sources_context.append(f"- {source.title}: {source.snippet or 'No snippet available'}")
        
        prompt = f"""Query: {query}

Agent Analysis Results:
{chr(10).join(agent_context)}

Sources:
{chr(10).join(sources_context) if sources_context else 'No sources retrieved'}

Please provide a comprehensive financial analysis summary."""
        
        try:
            summary = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for more focused analysis
                max_tokens=1000
            )
            return summary
        except Exception as e:
            print(f"Error generating LLM summary: {e}")
            # Fallback to deterministic summary
            return self._generate_summary(query, agent_outputs, sources)
    
    def _generate_summary(self, query: str, agent_outputs: List[AgentOutput], sources: List[Source]) -> str:
        """Generate structured summary without LLM (deterministic)."""
        
        # Extract key information from agent outputs
        market_data = ""
        fundamental_data = ""
        portfolio_data = ""
        
        for agent_out in agent_outputs:
            agent_name = agent_out.agent.lower()
            if "market" in agent_name:
                market_data = agent_out.content
            elif "fundamental" in agent_name or "news" in agent_name:
                fundamental_data = agent_out.content
            elif "portfolio" in agent_name or "risk" in agent_name:
                portfolio_data = agent_out.content
        
        # Build structured summary
        summary_parts = []
        
        # Thesis (3 bullets)
        summary_parts.append("## 📊 Investment Thesis")
        summary_parts.append("")
        if market_data:
            summary_parts.append(f"• **Market Analysis**: {self._extract_key_point(market_data)}")
        if fundamental_data:
            summary_parts.append(f"• **Fundamental Analysis**: {self._extract_key_point(fundamental_data)}")
        if portfolio_data:
            summary_parts.append(f"• **Risk Assessment**: {self._extract_key_point(portfolio_data)}")
        summary_parts.append("")
        
        # Risks (3 bullets)
        summary_parts.append("## ⚠️ Key Risks")
        summary_parts.append("")
        summary_parts.append("• **Market Volatility**: Price movements may be unpredictable")
        summary_parts.append("• **Fundamental Changes**: Financial metrics may deteriorate")
        summary_parts.append("• **Portfolio Concentration**: High exposure to specific assets increases risk")
        summary_parts.append("")
        
        # Evidence (sources)
        summary_parts.append("## 📚 Evidence & Sources")
        summary_parts.append("")
        if sources:
            for i, source in enumerate(sources, 1):
                summary_parts.append(f"{i}. **{source.title}**")
                if source.snippet:
                    summary_parts.append(f"   - {source.snippet}")
        else:
            summary_parts.append("• Analysis based on agent outputs (sources to be retrieved)")
        summary_parts.append("")
        
        # Recommendation
        summary_parts.append("## 💡 Recommendation")
        summary_parts.append("")
        summary_parts.append("Based on the multi-agent analysis:")
        if market_data and fundamental_data:
            summary_parts.append("• Consider the investment opportunity with careful risk management")
            summary_parts.append("• Monitor market trends and fundamental indicators regularly")
            summary_parts.append("• Diversify portfolio to mitigate concentration risk")
        else:
            summary_parts.append("• Additional data required for comprehensive recommendation")
        summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _extract_key_point(self, text: str, max_length: int = 100) -> str:
        """Extract a key point from agent output."""
        # Simple extraction: take first sentence or truncate
        sentences = text.split('.')
        if sentences and len(sentences[0]) > 0:
            key_point = sentences[0].strip()
            if len(key_point) > max_length:
                return key_point[:max_length] + "..."
            return key_point
        return text[:max_length] + "..." if len(text) > max_length else text