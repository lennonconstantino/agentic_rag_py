from mcp.server.fastmcp import FastMCP
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rag.load import get_query

mcp = FastMCP("AssistentSupportApple")

@mcp.tool()
def get_info_support_apple(query: str):
    """Tool to get information about Apple support"""
    print("...")
    response = get_query(query)
    #return "Apple support information"
    return response

if __name__ == "__main__":
    # Para desenvolvimento local, usar stdio
    mcp.run(transport="stdio")
    
    # Para servidor remoto, usar HTTP streamable (recomendado para produção)
    # mcp.run(
    #     transport="http",
    #     host="127.0.0.1",
    #     port=4200,
    #     log_level="info"
    # )
