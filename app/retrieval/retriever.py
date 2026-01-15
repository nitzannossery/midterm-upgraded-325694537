from typing import List
from app.schemas import Source

class Retriever:
    def retrieve(self, query: str, top_k: int = 5) -> List[Source]:
        # Replace with vector DB / search
        # Return empty list if you have no corpus yet
        return [
            Source(id="src1", title="Example Source", url=None, snippet="Example snippet relevant to the query.")
        ][:top_k]
