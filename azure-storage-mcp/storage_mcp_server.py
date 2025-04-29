"""Azure Storage MCP Server Implementation."""
import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List
from utils.azure_storage_usage import get_storage_accounts, get_used_capacity

# Initialize FastMCP server with the name "azure-storage"
mcp = FastMCP("azure-storage")

@mcp.tool()
async def list_storage_accounts_with_usage() -> Dict[str, Any]:
    """
    List all storage accounts in the subscription with their usage information.
    
    Returns:
        Dict containing the list of storage accounts with their usage data
    """
    try:
        # Get subscription ID from environment
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            return {
                "status": "error",
                "message": "AZURE_SUBSCRIPTION_ID environment variable not set"
            }

        # Get storage accounts
        accounts = get_storage_accounts(subscription_id)
        storage_data = []

        # Collect usage data for each account
        for account in accounts:
            account_name = account.name
            resource_group = account.id.split("/")[4]
            sub_id = account.id.split("/")[2]

            used_capacity_str = get_used_capacity(sub_id, resource_group, account_name)

            storage_data.append({
                'storage_account': account_name,
                'resource_group': resource_group,
                'subscription_id': sub_id,
                'used_capacity': used_capacity_str
            })

        return {
            "status": "success",
            "storage_accounts": storage_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@mcp.tool()
async def get_storage_account_usage(resource_group: str, account_name: str) -> Dict[str, Any]:
    """
    Get the usage information for a specific storage account.
    
    Args:
        resource_group: The name of the resource group
        account_name: The name of the storage account
    
    Returns:
        Dict containing the usage information for the specified storage account
    """
    try:
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        if not subscription_id:
            return {
                "status": "error",
                "message": "AZURE_SUBSCRIPTION_ID environment variable not set"
            }

        used_capacity = get_used_capacity(subscription_id, resource_group, account_name)
        
        return {
            "status": "success",
            "data": {
                "storage_account": account_name,
                "resource_group": resource_group,
                "subscription_id": subscription_id,
                "used_capacity": used_capacity
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Run the MCP server
    print("Starting Azure Storage MCP Server...")
    print("Available tools:")
    print("1. list_storage_accounts_with_usage")
    print("2. get_storage_account_usage")
    mcp.run(transport="stdio")
