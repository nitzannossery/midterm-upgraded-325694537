from typing import Dict, Any, List
from app.agents.base import Agent
from app.schemas import AgentOutput, Source

class SummarizerAgent(Agent):
    name = "Summarizer Agent"

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        sources: List[Source] = context.get("sources", [])
        agent_outputs = context.get("agent_outputs", [])

        # Replace with real LLM summarization prompt
        content = "Final recommendation (placeholder). Replace with LLM summarization over agent outputs."

        return AgentOutput(agent=self.name, content=content, sources=sources)
