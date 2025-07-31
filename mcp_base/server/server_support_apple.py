import json
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP
import os, sys
from langchain_tavily import TavilySearch

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


# creating tool search
@mcp.tool()
def search_web(query: str):
    """
    Searches for information on the web based on the given query.

    Arguments:
    Query: Terms to search for data on the web

    Returns:
    The information found on the web or a message below that no information was found
    """
    tavily_search = TavilySearch(max_results=3)
    search_docs = tavily_search.invoke(query)

    return search_docs["results"]

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

