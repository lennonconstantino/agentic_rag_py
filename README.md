# Agentic RAG System

A sophisticated Retrieval-Augmented Generation (RAG) system that combines intelligent planning, multi-source data retrieval, and contextual memory to provide accurate and relevant responses to user queries.

## 🚀 Features

- **Intelligent Planning**: Uses ReACT (Reasoning + Acting) and Chain of Thought reasoning to create optimal information retrieval strategies
- **Multi-Source Data Retrieval**: Integrates local, search engine, and cloud data sources
- **Contextual Memory**: Maintains both short-term and long-term memory for enhanced context awareness
- **Modular Architecture**: Extensible design with abstract base classes for easy customization
- **LLM Integration**: OpenAI integration with fallback to mock responses
- **Real-time Processing**: Step-by-step query processing with detailed logging

## 🏗️ Architecture

The system follows a modular, agent-based architecture:

```
AgenticRAGSystem
├── AggregatorAgent (Orchestrator)
│   ├── PlanningEngine (Strategy)
│   ├── Memory (Context)
│   ├── DataSources (Information)
│   └── LLMProvider (Generation)
```

### Core Components

- **`AgenticRAGSystem`**: Main user interface and system coordinator
- **`AggregatorAgent`**: Orchestrates the entire RAG pipeline
- **`PlanningEngine`**: Creates intelligent execution plans using reasoning strategies
- **`Memory`**: Manages short-term and long-term contextual information
- **`DataSource`**: Abstract interface for various data sources (local, search, cloud)
- **`LLMProvider`**: Handles language model interactions

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agentic_rag
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🚀 Quick Start

```python
from agenticRagSystem import AgenticRAGSystem

# Initialize the system
rag_system = AgenticRAGSystem()

# Add some context to memory
rag_system.aggregator.memory.add_long_term("company_info", {
    "name": "TechCorp",
    "founded": "2020",
    "employees": 150
})

# Query the system
response = rag_system.query("What do you know about TechCorp?")
print(response)
```

## 📋 Usage Examples

### Basic Query Processing

```python
# Simple query
response = rag_system.query("What are the latest trends in AI?")
```

### Adding Custom Data Sources

```python
from datasource import LocalDataSource

# Create custom data source
custom_data = {"products": ["AI Assistant", "ML Platform"]}
custom_source = LocalDataSource(custom_data)

# Add to system
rag_system.add_data_source("products", custom_source)
```

### Memory Management

```python
# Add long-term memory
rag_system.aggregator.memory.add_long_term("user_preferences", {
    "language": "English",
    "expertise_level": "Intermediate"
})

# Check memory stats
stats = rag_system.get_memory_stats()
print(f"Memory: {stats}")
```

## 🔧 Configuration

### LLM Provider Configuration

The system supports different LLM providers. Currently implemented:

- **OpenAI Provider**: Uses GPT models (default: `gpt-3.5-turbo`)
- **Mock Provider**: Fallback for testing without API keys

### Planning Strategies

Two reasoning strategies are available:

1. **ReACT (Reasoning + Acting)**: Default strategy that combines reasoning with action planning
2. **Chain of Thought**: Step-by-step reasoning approach

## 📊 System Flow

1. **Query Input**: User submits a query
2. **Planning Phase**: System creates an execution plan using reasoning strategies
3. **Memory Retrieval**: Relevant context is retrieved from memory
4. **Data Fetching**: Information is gathered from multiple data sources
5. **Context Enhancement**: All information is combined and enhanced
6. **Generation**: LLM generates the final response
7. **Memory Update**: Query and response are stored in memory

## 🛠️ Development

### Adding New Data Sources

```python
from datasource import DataSource

class CustomDataSource(DataSource):
    def fetch(self, query: str) -> Dict[str, Any]:
        # Implement your data fetching logic
        return {"source": "custom", "results": "your_data"}
```

### Extending Planning Engine

```python
from planning_engine import PlanningEngine

class CustomPlanningEngine(PlanningEngine):
    def _custom_planning(self, query: str, memory_context: Dict[str, Any]) -> Plan:
        # Implement custom planning logic
        pass
```

## 📁 Project Structure

```
agentic_rag/
├── agenticRagSystem.py    # Main system interface
├── aggregator.py          # Core orchestrator
├── planning_engine.py     # Planning and reasoning
├── datasource.py          # Data source abstractions
├── memory.py             # Memory management
├── llm_provider.py       # LLM integration
├── plan.py               # Plan data structures
├── reasoning.py          # Reasoning types
├── main.py               # Example usage
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Ensure your API key is correctly set in `.env`
2. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
3. **Memory Issues**: Check that your data structures are JSON-serializable

### Debug Mode

Enable detailed logging by modifying the `process_query` method in `aggregator.py` to include more verbose output.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with OpenAI's GPT models
- Inspired by ReACT and Chain of Thought reasoning approaches
- Designed for extensibility and modularity

---

**Note**: This is a research prototype. For production use, consider implementing proper error handling, security measures, and performance optimizations. 