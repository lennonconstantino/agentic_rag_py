from abc import ABC, abstractmethod
from typing import Dict, Any

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def fetch(self, query: str) -> Dict[str, Any]:
        pass

class LocalDataSource(DataSource):
    """Local data source implementation"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
    
    def fetch(self, query: str) -> Dict[str, Any]:
        # Simple keyword matching - replace with vector search in practice
        results = {}
        for key, value in self.data.items():
            if any(word.lower() in str(value).lower() for word in query.split()):
                results[key] = value
        return {"source": "local", "results": results}


class SearchEngineSource(DataSource):
    """Search engine data source implementation"""
    
    def fetch(self, query: str) -> Dict[str, Any]:
        # Placeholder for actual search engine integration
        return {
            "source": "search_engine",
            "results": f"Search results for: {query}",
            "urls": ["http://example1.com", "http://example2.com"]
        }

class CloudEngineSource(DataSource):
    """Cloud engine data source implementation"""
    
    def fetch(self, query: str) -> Dict[str, Any]:
        # Placeholder for cloud API integration
        return {
            "source": "cloud_engine",
            "results": f"Cloud data for: {query}",
            "metadata": {"confidence": 0.95}
        }
