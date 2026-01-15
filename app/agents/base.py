from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas import AgentOutput, Source

class Agent(ABC):
    name: str

    @abstractmethod
    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        raise NotImplementedError
