import json
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
import os, sys
from langchain_tavily import TavilySearch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from mcp_base.server.apple_helpdesk_manager import AppleHelpDeskDB
from rag.load import get_query

mcp = FastMCP("AssistantSupportApple")

@mcp.tool()
def get_info_support_apple(query: str):
    """
    Tool to get information about Apple support

    Arguments:
    Query: Terms to search on documents

    Returns:
    All information that we can
    """
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

##################################################################
####
## SEARCH UTILITY FUNCTIONS
##################################################################
@mcp.tool()
def search_tickets(**kwargs) -> List[Dict]:
    try:
        db = AppleHelpDeskDB()
        return db.search_tickets(**kwargs)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def search_knowledge_base(search_term: str, category_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
    try:
        db = AppleHelpDeskDB()
        return db.search_knowledge_base(search_term=search_term, category_id=category_id, limit=limit)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def get_customer_by_email(email: str) -> Optional[Dict]:
    try:
        db = AppleHelpDeskDB()
        return db.get_customer_by_email(email=email)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def get_agent_workload(agent_id: int) -> Dict:
    try:
        db = AppleHelpDeskDB()
        return db.get_agent_workload(agent_id)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

##################################################################
# PERSISTENCE UTILITY FUNCTIONS
##################################################################
@mcp.tool()
def create_ticket(customer_id: int, category_id: int, subject: str, description: str, 
                     priority: str = 'Medium', product_id: Optional[int] = None, 
                     serial_number: Optional[str] = None, ios_version: Optional[str] = None) -> str:
    try:
        db = AppleHelpDeskDB()
        return db.create_ticket(
            customer_id=customer_id, 
            category_id=category_id, 
            subject=subject, 
            description=description,
            priority=priority,
            product_id=product_id,
            serial_number=serial_number,
            ios_version=ios_version,
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def update_ticket_status(ticket_id: int, status: str, agent_id: Optional[int] = None, 
                           resolution: Optional[str] = None) -> bool:
    try:
        db = AppleHelpDeskDB()
        return db.update_ticket_status(ticket_id=ticket_id, status=status, agent_id=agent_id, resolution=resolution)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def add_ticket_comment(ticket_id: int, content: str, agent_id: Optional[int] = None, 
                          comment_type: str = 'note', is_public: bool = False) -> int:
    try:
        db = AppleHelpDeskDB()
        return db.add_ticket_comment(
            ticket_id=ticket_id,
            content=content,
            agent_id=agent_id,
            comment_type=comment_type,
            is_public=is_public,
        )
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def create_customer(first_name: str, last_name: str, email: str, 
                       phone: Optional[str] = None, apple_id: Optional[str] = None) -> int:
    try:
        db = AppleHelpDeskDB()
        return db.create_customer(first_name, last_name, email, phone, apple_id)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def create_kb_article(title: str, content: str, category_id: int, 
                         created_by: int, product_id: Optional[int] = None, 
                         tags: Optional[str] = None) -> int:
    try:
        db = AppleHelpDeskDB()
        return db.create_kb_article(title, content, category_id, created_by, product_id, tags)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@mcp.tool()
def increment_kb_view_count(article_id: int):
    try:
        db = AppleHelpDeskDB()
        return db.increment_kb_view_count(article_id)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

##################################################################
# Reporting functions
##################################################################
@mcp.tool()
def get_ticket_statistics() -> Dict:
    try:
        db = AppleHelpDeskDB()
        return db.get_ticket_statistics()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

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

