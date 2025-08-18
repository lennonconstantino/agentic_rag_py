import json
from typing import Dict, Any
from llm_provider import OpenAIProvider
from reasoning import ReasoningType
from plan import Plan


class PlanningEngine:
    """Handles planning and reasoning for information retrieval"""
    
    def __init__(self):
        self.reasoning_type = None
    
    def create_plan(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        """Create an execution plan based on query and memory context"""
        
        prompt = f"""
Analyze the following prompt and return ONLY a valid JSON object with the specified format.

Prompt: {query}

Return ONLY valid JSON in this exact format (no additional text, explanations, or formatting):

{{
    "task_type": "classification|generation|analysis|troubleshooting|etc",
    "prompt_strategy": "CoT|ReAct|zero-shot|few-shot|etc", 
    "domain": "math|programming|creative|technology|etc",
    "action": "true|false"
}}
        """
        llm_provider = OpenAIProvider()
        response = llm_provider.query(prompt=prompt)
        response = json.loads(response)

        if response["action"]:
            return self._react_planning(query, memory_context)
        else:
            return self._cot_planning(query, memory_context)
    
    def _react_planning(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        """ReACT (Reasoning + Acting) planning approach"""
        self.reasoning_type: ReasoningType = ReasoningType.REACT
        reasoning_trace = [
            f"Thought: I need to find information about '{query}'",
            f"Action: Check memory for relevant context",
            f"Observation: Found {len(memory_context)} relevant items in memory"
        ]
        
        # Determine data sources based on query type
        # TODO: dealing routes
        data_sources = ["local"]
        # if "current" in query.lower() or "latest" in query.lower():
        #     data_sources.extend(["search_engine", "cloud_engine"])

        # if ("searched", "search", "find") in query.lower():
        #     data_sources.extend(["search_engine"])

        # if ("ticket", "article", "customer", "status", "update", "statistics") in query.lower():
        #     data_sources.extend(["cloud_engine"])
        
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
        self.reasoning_type: ReasoningType = ReasoningType.COT
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

