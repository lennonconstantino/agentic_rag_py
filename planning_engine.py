from typing import Dict, Any
from reasoning import ReasoningType
from plan import Plan


class PlanningEngine:
    """Handles planning and reasoning for information retrieval"""
    
    def __init__(self, reasoning_type: ReasoningType = ReasoningType.REACT):
        self.reasoning_type = reasoning_type
    
    def create_plan(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        """Create an execution plan based on query and memory context"""
        
        if self.reasoning_type == ReasoningType.REACT:
            return self._react_planning(query, memory_context)
        else:
            return self._cot_planning(query, memory_context)
    
    def _react_planning(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        """ReACT (Reasoning + Acting) planning approach"""
        reasoning_trace = [
            f"Thought: I need to find information about '{query}'",
            f"Action: Check memory for relevant context",
            f"Observation: Found {len(memory_context)} relevant items in memory"
        ]
        
        # Determine data sources based on query type
        data_sources = ["local"]
        if "current" in query.lower() or "latest" in query.lower():
            data_sources.extend(["search_engine", "cloud_engine"])
        
        steps = [
            "Analyze query intent",
            "Check memory for existing information",
            "Identify required data sources",
            "Fetch information from sources",
            "Synthesize and rank results"
        ]
        
        return Plan(steps=steps, data_sources=data_sources, reasoning_trace=reasoning_trace)
    
    def _cot_planning(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        """Chain of Thought planning approach"""
        reasoning_trace = [
            f"Let me think step by step about '{query}'",
            "First, I should understand what information is being requested",
            "Then, I should check what I already know from memory",
            "Finally, I should determine what additional sources I need"
        ]
        
        data_sources = ["local", "search_engine"]
        steps = [
            "Break down query into components",
            "Map components to available data sources",
            "Execute retrieval in order of importance"
        ]
        
        return Plan(steps=steps, data_sources=data_sources, reasoning_trace=reasoning_trace)

