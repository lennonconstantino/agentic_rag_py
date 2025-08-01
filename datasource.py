from abc import ABC, abstractmethod
import asyncio
import json
from typing import Dict, Any

from mcp_base.client.mcp_client import McpClient

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
        return asyncio.run(self._fetch(query))
    
    async def _fetch(self, query: str) -> Dict[str, Any]:
        # Simple keyword matching - replace with vector search in practice
        results = {}
        for key, value in self.data.items():
            if any(word.lower() in str(value).lower() for word in query.split()):
                results[key] = value

        print("...")
        print(results)

        client = McpClient()

        try:
            await client.initialize_with_stdio("mcp", ["run", "mcp_base/server/server_support_apple.py"])

            tools = await client.get_tools()  # await aqui
            for tool in tools:
                if tool.name == 'get_info_support_apple':
                    print(f'Name: {tool.name}, description: {tool.description}')
                    results = await client.call_tool("get_info_support_apple", {"query": query})
                    print(results.content[0].text)
                    jsons = []
                    for textContent in results.content:
                        jsons.append(json.loads(textContent.text))

                    responses = "\n".join([f"{response["page_content"]}" for response in jsons if response["page_content"]])
            return {
                "source": "local",
                "results": responses
            }
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            # Fechar cliente explicitamente
            try:
                await client.cleanup()
                print("Cliente MCP fechado corretamente")
            except Exception as e:
                print(f"Aviso: Erro ao fechar cliente: {e}")


class SearchEngineSource(DataSource):
    """Search engine data source implementation"""
    
    def fetch(self, query: str) -> Dict[str, Any]:
        # Placeholder for actual search engine integration
        return asyncio.run(self._fetch(query))
    
    async def _fetch(self, query: str) -> Dict[str, Any]:
        print("...")
        print("SearchEngineSource")

        client = McpClient()

        try:
            await client.initialize_with_stdio("mcp", ["run", "mcp_base/server/server_support_apple.py"])

            tools = await client.get_tools()
            for tool in tools:
                if tool.name == 'search_web':
                    print(f'Name: {tool.name}, description: {tool.description}')
                    results = await client.call_tool("search_web", {"query": query})
                    jsons = []
                    for textContent in results.content:
                        jsons.append(json.loads(textContent.text))

                    responses = "\n".join([f"{response["content"]}" for response in jsons])
                    urls = [response["url"] for response in jsons]
            return {
                "source": "search_engine",
                "results": responses,
                "urls": urls
            }

        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            # Fechar cliente explicitamente
            try:
                await client.cleanup()
                print("Cliente MCP fechado corretamente")
            except Exception as e:
                print(f"Aviso: Erro ao fechar cliente: {e}")

class CloudEngineSource(DataSource):
    """Cloud engine data source implementation"""
    
    def fetch(self, query: str) -> Dict[str, Any]:
        # Placeholder for cloud API integration
        return {
            "source": "cloud_engine",
            "results": f"Cloud data for: {query}",
            "metadata": {"confidence": 0.95}
        }
