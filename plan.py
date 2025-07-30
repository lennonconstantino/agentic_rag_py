from dataclasses import dataclass
from typing import List

@dataclass
class Plan:
    """Represents an execution plan for information retrieval"""
    steps: List[str]
    data_sources: List[str]
    reasoning_trace: List[str]
    priority: int = 1
