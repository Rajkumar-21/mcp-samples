"""Test client for Azure Storage MCP Server."""
import asyncio
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_storage_mcp():
    """Test the Azure Storage MCP Server tools."""
    # Server parameters for connecting to the MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["storage_mcp_server.py"]
    )

    print("Connecting to Azure Storage MCP Server...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List all tools
            tools = await session.list_tools()
            print("\nAvailable tools:", [tool.name for tool in tools])

            # Test list_storage_accounts_with_usage
            print("\nTesting list_storage_accounts_with_usage...")
            result = await session.invoke_tool(
                "list_storage_accounts_with_usage",
                {}
            )
            print("Result:", result)

            # If we got successful results, test get_storage_account_usage
            if result.get("status") == "success" and result.get("storage_accounts"):
                first_account = result["storage_accounts"][0]
                print(f"\nTesting get_storage_account_usage for {first_account['storage_account']}...")
                
                detail_result = await session.invoke_tool(
                    "get_storage_account_usage",
                    {
                        "resource_group": first_account["resource_group"],
                        "account_name": first_account["storage_account"]
                    }
                )
                print("Result:", detail_result)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(test_storage_mcp())
