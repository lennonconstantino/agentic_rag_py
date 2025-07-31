from agenticRagSystem import AgenticRAGSystem
from rag.load import load_vectordb
import asyncio

def main():
    # Initialize the Agentic RAG system
    rag_system = AgenticRAGSystem()
    
    # Add some long-term memory
    rag_system.aggregator.memory.add_long_term("company_info", {
        "name": "Apple",
        "founded": "1976",
        "employees": 150000
    })
    
    # Process some queries
    queries = [
        # "What do you know about Apple?",
        # "What are the latest trends in AI?",
        # "How many employees does our company have?",
        # "What is the mission of Apple?",
        # "What is the value proposition of Apple?",
        "List the all products of Apple?",
        "I can't turn off my Mac mini Pro M2",
        "What is the most searched item in the FAQ from Apple?"
    ]
    
    for query in queries:
        print("\n" + "="*60)
        response = rag_system.query(query)
        print(f"\nResponse: {response}")
        print(f"Memory stats: {rag_system.get_memory_stats()}") 

if __name__ == "__main__":
    main()
