# Agentic RAG System with Apple Helpdesk Integration

A sophisticated Retrieval-Augmented Generation (RAG) system that combines intelligent planning, multi-source data retrieval, contextual memory, and MCP (Model Context Protocol) server integration to provide accurate and relevant responses to user queries. The system is specifically designed for Apple technical support scenarios with integrated helpdesk management capabilities.

## 🚀 Features

- **Intelligent Planning**: Uses ReACT (Reasoning + Acting) and Chain of Thought reasoning to create optimal information retrieval strategies
- **Multi-Source Data Retrieval**: Integrates local, search engine, and cloud data sources
- **Contextual Memory**: Maintains both short-term and long-term memory for enhanced context awareness
- **Modular Architecture**: Extensible design with abstract base classes for easy customization
- **LLM Integration**: OpenAI integration with fallback to mock responses
- **Real-time Processing**: Step-by-step query processing with detailed logging
- **MCP Server Integration**: Model Context Protocol server for Apple support assistance
- **Vector Database**: Chroma-based document retrieval with PDF processing
- **Apple Helpdesk Management**: Complete ticket management and knowledge base system
- **Multi-language Support**: English and Portuguese technical documentation

## 🏗️ Architecture

The system follows a modular, agent-based architecture with MCP server integration:

```
AgenticRAGSystem
├── AggregatorAgent (Orchestrator)
│   ├── PlanningEngine (Strategy)
│   ├── Memory (Context)
│   ├── DataSources (Information)
│   └── LLMProvider (Generation)
├── MCP Server (Apple Support)
│   ├── AppleHelpDeskDB
│   ├── Ticket Management
│   ├── Knowledge Base
│   └── Customer Management
└── RAG Pipeline
    ├── PDF Document Processing
    ├── Vector Database (Chroma)
    └── Retrieval-Augmented Generation
```

### Core Components

- **`AgenticRAGSystem`**: Main user interface and system coordinator
- **`AggregatorAgent`**: Orchestrates the entire RAG pipeline
- **`PlanningEngine`**: Creates intelligent execution plans using reasoning strategies
- **`Memory`**: Manages short-term and long-term contextual information
- **`DataSource`**: Abstract interface for various data sources (local, search, cloud)
- **`LLMProvider`**: Handles language model interactions
- **`MCP Server`**: Apple support server with helpdesk management tools
- **`Vector Database`**: Chroma-based document storage and retrieval

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd agentic_rag_py
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## 🚀 Quick Start

```python
from agenticRagSystem import AgenticRAGSystem
from rag.load import load_vectordb

# Initialize the system
rag_system = AgenticRAGSystem(True)

# Load vector database with Apple technical documentation
vectordb = load_vectordb()

# Add some context to memory
rag_system.aggregator.memory.add_long_term("company_info", {
    "name": "Apple",
    "founded": "1976",
    "employees": 150000
})

# Query the system
response = rag_system.query("I can't turn off my Mac mini Pro M2")
print(response)
```

## 📋 Usage Examples

### Basic Query Processing

```python
# Apple support queries
response = rag_system.query("My Apple Music is not working")
response = rag_system.query("How to reset iPhone settings")
```

### MCP Server Tools

The system includes a comprehensive MCP server with the following tools:

```python
# Ticket Management
search_tickets(customer_id=123, status="Open")
create_ticket(customer_id=123, category_id=1, subject="iPhone won't turn on", description="...")

# Knowledge Base Search
search_knowledge_base("iPhone battery", category_id=2, limit=5)

# Customer Management
get_customer_by_email("customer@example.com")

# Agent Workload
get_agent_workload(agent_id=456)

# Web Search Integration
search_web("latest iPhone iOS update")
```

### Vector Database Operations

```python
from rag.load import get_query

# Direct vector database queries
results = get_query("Mac mini troubleshooting")
```

## 🔧 Configuration

### LLM Provider Configuration

The system supports different LLM providers. Currently implemented:

- **OpenAI Provider**: Uses GPT models (default: `gpt-4o-mini`)
- **Mock Provider**: Fallback for testing without API keys

### Vector Database Configuration

- **Chroma**: Local vector database with OpenAI embeddings
- **Document Processing**: PDF support with recursive text splitting
- **Search Methods**: Similarity search and Max Marginal Relevance (MMR)

### MCP Server Configuration

The MCP server provides tools for:
- Ticket creation and management
- Knowledge base search and retrieval
- Customer information lookup
- Agent workload monitoring
- Web search integration via Tavily

## 📊 System Flow

1. **Query Input**: User submits a query
2. **Planning Phase**: System creates an execution plan using reasoning strategies
3. **Memory Retrieval**: Relevant context is retrieved from memory
4. **Data Fetching**: Information is gathered from multiple data sources including vector database
5. **MCP Tool Execution**: Relevant MCP tools are invoked if needed
6. **Context Enhancement**: All information is combined and enhanced
7. **Generation**: LLM generates the final response
8. **Memory Update**: Query and response are stored in memory

## 🛠️ Development

### Adding New MCP Tools

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("YourServerName")

@mcp.tool()
def your_custom_tool(param: str):
    """Description of your tool"""
    # Implement your tool logic
    return "result"
```

### Extending Vector Database

```python
from rag.load import load_vectordb

# Add new document paths
paths = [
    "rag/docs/your_new_document.pdf",
    # ... existing paths
]
```

### Custom Data Sources

```python
from datasource import DataSource

class CustomDataSource(DataSource):
    def fetch(self, query: str) -> Dict[str, Any]:
        # Implement your data fetching logic
        return {"source": "custom", "results": "your_data"}
```

## 📁 Project Structure

```
agentic_rag_py/
├── agenticRagSystem.py           # Main system interface
├── aggregator.py                 # Core orchestrator
├── planning_engine.py            # Planning and reasoning
├── memory.py                     # Memory management
├── llm_provider.py              # LLM integration
├── plan.py                      # Plan data structures
├── reasoning.py                 # Reasoning types
├── main.py                      # Example usage and testing
├── requirements.txt             # Dependencies
├── mcp_base/                    # MCP server implementation
│   ├── client/                  # MCP client utilities
│   └── server/                  # Apple helpdesk MCP server
│       ├── server_support_apple.py  # Main MCP server
│       ├── apple_helpdesk_manager.py # Database management
│       └── apple_helpdesk.db       # SQLite database
├── rag/                         # RAG pipeline components
│   ├── load.py                  # Vector database operations
│   ├── docs/                    # PDF documentation
│   │   ├── apple_technical_support_guide_en.pdf
│   │   └── guia_de_assistencia_tecnica_apple_pt.pdf
│   └── files/                   # Vector database storage
└── README.md                    # This file
```

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Errors**: Ensure your API key is correctly set in `.env`
2. **Tavily API Errors**: Check your Tavily API key configuration
3. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
4. **Vector Database Issues**: Ensure the `rag/files/chat_retrieval_db` directory exists
5. **PDF Processing Errors**: Verify PDF files are accessible in the `rag/docs/` directory

### Debug Mode

Enable detailed logging by modifying the `process_query` method in `aggregator.py` to include more verbose output.

### MCP Server Debugging

Check the MCP server logs for tool execution details and database connection issues.

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
- MCP (Model Context Protocol) integration for enhanced tool capabilities
- Chroma vector database for efficient document retrieval

---

**Note**: This is a research prototype with Apple helpdesk integration. For production use, consider implementing proper error handling, security measures, performance optimizations, and database connection pooling. 