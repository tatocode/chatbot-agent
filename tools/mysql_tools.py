from langchain_mcp_adapters.client import MultiServerMCPClient

mysql_client = client = MultiServerMCPClient(
    {
        "MySQL": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        }
    }
)