import os
import logging
import json # <--- Import the json module
from typing import List, Optional, Dict, Any # <--- Added Dict, Any

from azure.identity.aio import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential
from azure.mgmt.resource.resources.aio import ResourceManagementClient
# Ensure you have this import if you don't already
from azure.mgmt.resource.resources.models import ResourceGroup

from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MCP Server Setup ---
mcp = FastMCP("AzureExplorer")
logger.info("Azure Explorer MCP Server initializing...")

# --- Azure Authentication Helper ---
# (Keep the get_azure_credential function as it was before)
async def get_azure_credential(auth_type: str = "default"):
    """Gets the appropriate Azure credential based on configuration."""
    logger.info(f"Attempting Azure authentication using type: {auth_type}")
    try:
        if auth_type == "spn":
            logger.info("Using Service Principal (ClientSecretCredential)")
            tenant_id = os.getenv("AZURE_TENANT_ID")
            client_id = os.getenv("AZURE_CLIENT_ID")
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            if not all([tenant_id, client_id, client_secret]):
                raise ValueError("AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET must be set for SPN auth.")
            return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        elif auth_type == "identity":
             logger.info("Using Managed Identity (ManagedIdentityCredential)")
             identity_client_id = os.getenv("AZURE_MANAGED_IDENTITY_CLIENT_ID")
             if identity_client_id:
                 logger.info(f"Using specific managed identity client ID: {identity_client_id}")
                 return ManagedIdentityCredential(client_id=identity_client_id)
             else:
                 logger.info("Using system-assigned managed identity or default user-assigned identity.")
                 return ManagedIdentityCredential()
        else: # default
            logger.info("Using DefaultAzureCredential")
            return DefaultAzureCredential()
    except Exception as e:
        logger.error(f"Azure authentication failed: {e}", exc_info=True)
        raise ConnectionError(f"Failed to get Azure credentials for auth_type '{auth_type}': {e}")


# --- MCP Tools ---
@mcp.tool()
async def list_resource_groups(
    subscription_id: str,
    auth_type: Optional[str] = "default",
    ctx: Context = None
    ) -> str: # The return type is still a string, but now it's a JSON string
    """
    Lists details for all resource groups in the specified Azure subscription.
    Returns a JSON string representing a list of resource group objects.

    Args:
        subscription_id: The Azure Subscription ID to query.
        auth_type: The authentication method to use ('default', 'spn', 'identity'). Defaults to 'default'.
    """
    if not subscription_id:
        return json.dumps({"error": "Azure Subscription ID is required."}) # Return error as JSON

    # Handle potential None from client and validate
    effective_auth_type = auth_type if auth_type is not None else "default"
    if effective_auth_type not in ["default", "spn", "identity"]:
         error_msg = f"Error: Invalid auth_type provided ('{auth_type}'). Must be 'default', 'spn', or 'identity'."
         logger.warning(error_msg)
         return json.dumps({"error": error_msg}) # Return error as JSON

    logger.info(f"Listing resource group details for subscription: {subscription_id} using auth: {effective_auth_type}")
    ctx.info(f"Attempting to list resource group details for subscription {subscription_id[:4]}... using {effective_auth_type} auth.")

    try:
        credential = await get_azure_credential(effective_auth_type)
        async with credential:
            async with ResourceManagementClient(credential, subscription_id) as client:
                rg_details_list: List[Dict[str, Any]] = [] # List to hold dictionaries
                logger.info("Iterating through resource groups...")
                count = 0
                async for rg in client.resource_groups.list():
                    # Convert ResourceGroup object to a dictionary
                    # Handle potentially None 'tags' and 'properties'
                    rg_dict = {
                        "id": rg.id,
                        "name": rg.name,
                        "location": rg.location,
                        "tags": rg.tags if rg.tags is not None else {}, # Ensure tags is a dict
                        # Convert properties object if it exists
                        "properties": {
                            "provisioning_state": rg.properties.provisioning_state if rg.properties else None
                        },
                        "managed_by": rg.managed_by
                    }
                    rg_details_list.append(rg_dict)
                    count += 1
                    if count % 10 == 0: # Log progress periodically
                        logger.info(f"Processed {count} resource groups...")
                        ctx.report_progress(count, None, message=f"Processed {count} RGs...") # Report progress

                logger.info(f"Finished iteration. Found {len(rg_details_list)} resource groups.")

                if not rg_details_list:
                    ctx.info(f"No resource groups found in subscription {subscription_id}.")
                    # Return an empty JSON array string if no groups found
                    return "[]"

                ctx.info(f"Successfully listed details for {len(rg_details_list)} resource groups.")
                # Serialize the list of dictionaries to a JSON string with indentation
                return json.dumps(rg_details_list, indent=2)

    except ConnectionError as e:
         logger.error(f"Authentication/Connection Error: {e}", exc_info=True)
         ctx.error(f"Azure Authentication/Connection Error: {e}")
         # Return error as JSON
         return json.dumps({"error": f"Error connecting to Azure: {e}"})
    except Exception as e:
        logger.error(f"Error listing resource groups: {e}", exc_info=True)
        ctx.error(f"Failed to list resource groups: {e}")
        # Return error as JSON
        return json.dumps({"error": f"An error occurred while listing resource groups: {e}"})

# --- Running the Server ---
# Keep this commented out or remove if running via main.py/Uvicorn
if __name__ == "__main__":
    logger.info("Starting Azure Explorer MCP Server for stdio...")
    mcp.run()

# --- main.py (if using Uvicorn for SSE) ---
# No changes needed in main.py if you have it setup as before.
# It just needs to import the 'mcp' app object from this updated server.py
