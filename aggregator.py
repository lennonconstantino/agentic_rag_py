from memory import Memory
from planning_engine import PlanningEngine
from datasource import LocalDataSource, SearchEngineSource, CloudEngineSource
from llm_provider import OpenAIProvider
import json

class AggregatorAgent:
    """Main aggregator agent that orchestrates the RAG process"""
    
    def __init__(self):
        self.memory = Memory(short_term={}, long_term={})
        self.planning_engine = PlanningEngine()
        self.data_sources = {
            "local": LocalDataSource({"ai": "starting"}),
            "search_engine": SearchEngineSource(),
            "cloud_engine": CloudEngineSource()
        }
        self.llm_provider = OpenAIProvider()
    
    def process_query(self, query: str) -> str:
        """Main method to process user query through agentic RAG pipeline"""
        
        print(f"📥 Processing query: {query}")
        
        # Step 1: Planning Phase
        print("🧠 Planning Phase...")
        memory_context = self.memory.get_relevant_context(query)
        plan = self.planning_engine.create_plan(query, memory_context)
        
        print(f"   Plan created with {len(plan.steps)} steps")
        print(f"   Data sources: {plan.data_sources}")
        
        # Step 2: Information Retrieval Phase
        print("🔍 Fetching Phase...")
        retrieved_context = {}
        
        for source_name in plan.data_sources:
            if source_name in self.data_sources:
                source_data = self.data_sources[source_name].fetch(query)
                retrieved_context[source_name] = source_data
                print(f"   ✓ Fetched from {source_name}")
        
        # Step 3: Context Enhancement
        print("🔧 Context Enhancement...")
        enhanced_context = {
            "memory_context": memory_context,
            "retrieved_context": retrieved_context,
            "reasoning_trace": plan.reasoning_trace,
            "query": query
        }
        
        # Step 4: Generation Phase
        print("✨ Generation Phase...")
        context_str = json.dumps(enhanced_context, indent=2)
        response = self.llm_provider.generate(query, context_str)
        
        # Step 5: Memory Update
        print("💾 Memory Update...")
        self.memory.add_short_term(f"query_{len(self.memory.short_term)}", {
            "query": query,
            "response": response,
            "context": enhanced_context
        })
        
        print("✅ Process complete!")
        return response
