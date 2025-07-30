from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Memory:
    """Memory system for storing short-term and long-term information"""
    short_term: Dict[str, Any]
    long_term: Dict[str, Any]
    
    def add_short_term(self, key: str, value: Any):
        self.short_term[key] = value
    
    def add_long_term(self, key: str, value: Any):
        self.long_term[key] = value
    
    def get_relevant_context(self, query: str) -> Dict[str, Any]:
        # Simple relevance matching - in practice, use embeddings/semantic search
        relevant = {}
        for key, value in {**self.short_term, **self.long_term}.items():
            if any(word.lower() in str(value).lower() for word in query.split()):
                relevant[key] = value
        return relevant
