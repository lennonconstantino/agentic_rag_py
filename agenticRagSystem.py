from aggregator import AggregatorAgent
from datasource import DataSource
from typing import Dict

class AgenticRAGSystem:
    """Main system class that provides the user interface"""
    
    def __init__(self):
        self.aggregator = AggregatorAgent()
    
    def query(self, user_input: str) -> str:
        """Process user query and return response"""
        return self.aggregator.process_query(user_input)
    
    def add_data_source(self, name: str, source: DataSource):
        """Add a new data source to the system"""
        self.aggregator.data_sources[name] = source
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get memory usage statistics"""
        return {
            "short_term_items": len(self.aggregator.memory.short_term),
            "long_term_items": len(self.aggregator.memory.long_term)
        }
