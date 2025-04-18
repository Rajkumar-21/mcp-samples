import asyncio
import json
import os
import subprocess
from typing import Any, Dict, List, Optional, Union

import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("azure-cli")

# Authentication modes
AUTH_MODE_CURRENT = "current"
AUTH_MODE_SPN = "spn"
AUTH_MODE_MANAGED_IDENTITY = "managed-identity"

# Default authentication mode
current_auth_mode = AUTH_MODE_CURRENT

# Configuration for Service Principal authentication
spn_config = {
    "client_id": None,
    "client_secret": None,
    "tenant_id": None
}

# Configuration for managed identity
managed_identity_config = {
    "identity_id": None
}

# Command prompt from Java implementation
COMMAND_PROMPT = """
Your job is to answer questions about an Azure environment by executing Azure CLI commands. You have the following rules:

- You should use the Azure CLI to manage Azure resources and services. Do not use any other tool.
- You should provide a valid Azure CLI command starting with 'az'. For example: 'az vm list'.
- Whenever a command fails, retry it 3 times before giving up with an improved version of the code based on the returned feedback.
- When listing resources, ensure pagination is handled correctly so that all resources are returned.
- When deleting resources, ALWAYS request user confirmation
- This tool can ONLY write code that interacts with Azure. It CANNOT generate charts, tables, graphs, etc.

Be concise, professional and to the point. Do not give generic advice, always reply with detailed & contextual data sourced from the current Azure environment.
"""

def load_environment_variables():
    """Load environment variables for SPN authentication."""
    load_dotenv()
    spn_config["client_id"] = os.getenv("AZURE_CLIENT_ID")
    spn_config["client_secret"] = os.getenv("AZURE_CLIENT_SECRET")
    spn_config["tenant_id"] = os.getenv("AZURE_TENANT_ID")
    managed_identity_config["identity_id"] = os.getenv("AZURE_USER_IDENTITY_ID")
    
    # Try to authenticate if SPN credentials are available
    if all([spn_config["client_id"], spn_config["client_secret"], spn_config["tenant_id"]]):
        authenticate_with_spn()

def authenticate_with_spn():
    """Authenticate with Azure CLI using Service Principal credentials."""
    try:
        login_command = [
            "az", "login", 
            "--service-principal",
            "--tenant", spn_config["tenant_id"],
            "--username", spn_config["client_id"],
            "--password", spn_config["client_secret"]
        ]
        
        result = subprocess.run(
            login_command,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Azure CLI login failed: {result.stderr}")
        else:
            print("Successfully authenticated with Azure CLI using Service Principal")
            
    except Exception as e:
        print(f"Error during Azure CLI authentication: {str(e)}")

async def run_az_command(command_parts: List[str]) -> Dict[str, Any]:
    """
    Run an Azure CLI command and return the result as JSON.
    
    Args:
        command_parts: List of command parts, e.g. ["vm", "list"]
    
    Returns:
        JSON response from Azure CLI
    """
    # Base Azure CLI command
    cmd = ["az"]
    
    # Add command parts
    cmd.extend(command_parts)
    
    # Add JSON output format
    if "--output" not in command_parts and "-o" not in command_parts:
        cmd.extend(["--output", "json"])
    
    # Add authentication parameters based on current mode
    if current_auth_mode == AUTH_MODE_SPN:
        if all([spn_config["client_id"], spn_config["client_secret"], spn_config["tenant_id"]]):
            cmd.extend([
                "--service-principal",
                "--username", spn_config["client_id"],
                "--password", spn_config["client_secret"],
                "--tenant", spn_config["tenant_id"]
            ])
        else:
            return {"error": "Incomplete SPN configuration. Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID environment variables."}
    
    elif current_auth_mode == AUTH_MODE_MANAGED_IDENTITY:
        cmd.append("--identity")
        if managed_identity_config["identity_id"]:
            cmd.extend(["--identity-id", managed_identity_config["identity_id"]])
    
    try:
        # Run the command and capture output
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        
        # Process the output
        if result.returncode != 0:
            return {"error": stderr.decode().strip()}
        
        # Parse JSON output
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {"output": stdout.decode().strip()}
            
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def set_authentication_mode(mode: str, identity_id: str = None) -> str:
    """
    Set the authentication mode for Azure CLI commands.
    
    Args:
        mode: Authentication mode ('current', 'spn', 'managed-identity')
        identity_id: Optional user-assigned managed identity ID
    """
    global current_auth_mode
    
    if mode not in [AUTH_MODE_CURRENT, AUTH_MODE_SPN, AUTH_MODE_MANAGED_IDENTITY]:
        return f"Invalid authentication mode: {mode}. Allowed values: {AUTH_MODE_CURRENT}, {AUTH_MODE_SPN}, {AUTH_MODE_MANAGED_IDENTITY}"
    
    current_auth_mode = mode
    
    if mode == AUTH_MODE_MANAGED_IDENTITY and identity_id:
        managed_identity_config["identity_id"] = identity_id
    
    return f"Authentication mode set to: {mode}"

@mcp.tool()
async def execute_azure_cli_command(command: str) -> str:
    """
    Execute any Azure CLI command directly.
    
    Args:
        command: The full Azure CLI command to execute (must start with 'az')
    """
    if not command.startswith("az "):
        return "Error: Invalid command. Command must start with 'az'."
    
    # Parse command into parts
    command_parts = command.split()
    command_parts = command_parts[1:]  # Remove the 'az' prefix
    
    result = await run_az_command(command_parts)
    
    if "error" in result:
        return f"Error executing command: {result['error']}"
    
    # Return the result as formatted YAML
    try:
        return yaml.dump(result, default_flow_style=False)
    except Exception:
        return json.dumps(result, indent=2)

@mcp.tool()
async def get_resource_groups(subscription_id: str = None) -> str:
    """
    List all resource groups in the specified subscription.
    
    Args:
        subscription_id: Optional subscription ID. Uses the default if not specified.
    """
    cmd = ["group", "list"]
    
    if subscription_id:
        cmd.extend(["--subscription", subscription_id])
    
    result = await run_az_command(cmd)
    
    if "error" in result:
        return f"Error retrieving resource groups: {result['error']}"
    
    # Format the output nicely
    formatted_output = []
    for rg in result:
        formatted_output.append(f"Name: {rg.get('name')}")
        formatted_output.append(f"Location: {rg.get('location')}")
        formatted_output.append(f"Status: {rg.get('properties', {}).get('provisioningState', 'Unknown')}")
        formatted_output.append(f"Tags: {rg.get('tags', 'None')}")
        formatted_output.append("-" * 40)
    
    return "\n".join(formatted_output) if formatted_output else "No resource groups found."

@mcp.tool()
async def get_vm_info(vm_name: str, resource_group: str, subscription_id: str = None) -> str:
    """
    Get detailed information about a virtual machine.
    
    Args:
        vm_name: Name of the virtual machine
        resource_group: Resource group name
        subscription_id: Optional subscription ID
    """
    cmd = ["vm", "show", "--name", vm_name, "--resource-group", resource_group]
    
    if subscription_id:
        cmd.extend(["--subscription", subscription_id])
    
    result = await run_az_command(cmd)
    
    if "error" in result:
        return f"Error retrieving VM information: {result['error']}"
    
    # Format the output as YAML for better readability
    try:
        return yaml.dump(result, default_flow_style=False)
    except Exception:
        return json.dumps(result, indent=2)

@mcp.tool()
async def run_resource_graph_query(query: str, subscription_ids: List[str] = None) -> str:
    """
    Run an Azure Resource Graph query.
    
    Args:
        query: The KQL query to execute
        subscription_ids: Optional list of subscription IDs to query
    """
    cmd = ["graph", "query", "--query", query]
    
    if subscription_ids:
        cmd.extend(["--subscriptions"] + subscription_ids)
    
    result = await run_az_command(cmd)
    
    if "error" in result:
        return f"Error executing Resource Graph query: {result['error']}"
    
    # Extract and format the data
    data = result.get("data", [])
    count = result.get("count", 0)
    
    if not data:
        return "No results found."
    
    output = [f"Results: {count} items found"]
    output.append("-" * 40)
    
    for item in data:
        try:
            output.append(yaml.dump(item, default_flow_style=False))
            output.append("-" * 40)
        except Exception:
            output.append(json.dumps(item, indent=2))
            output.append("-" * 40)
    
    return "\n".join(output)

@mcp.tool()
async def run_log_analytics_query(workspace_id: str, query: str, timespan: str = "P1D") -> str:
    """
    Run a Log Analytics (KQL) query in an Azure Monitor workspace.
    
    Args:
        workspace_id: Log Analytics workspace ID
        query: The KQL query to execute
        timespan: Time span of the query (default: P1D - last 24 hours)
    """
    cmd = ["monitor", "log-analytics", "query", 
           "--workspace", workspace_id,
           "--analytics-query", query,
           "--timespan", timespan]
    
    result = await run_az_command(cmd)
    
    if "error" in result:
        return f"Error executing Log Analytics query: {result['error']}"
    
    # Extract and format tables
    tables = result.get("tables", [])
    if not tables:
        return "No results found."
    
    output = []
    
    for table in tables:
        columns = table.get("columns", [])
        rows = table.get("rows", [])
        
        if not columns or not rows:
            continue
        
        # Table header with column names
        header = " | ".join(col.get("name", "Column") for col in columns)
        output.append(header)
        output.append("-" * len(header))
        
        # Table rows
        for row in rows:
            formatted_row = " | ".join(str(cell) for cell in row)
            output.append(formatted_row)
        
        output.append("\n")
    
    return "\n".join(output) if output else "No results found."

@mcp.tool()
async def list_available_resources(resource_type: str = None, resource_group: str = None, subscription_id: str = None) -> str:
    """
    List available Azure resources of a specific type.
    
    Args:
        resource_type: Optional resource type (e.g., 'Microsoft.Compute/virtualMachines')
        resource_group: Optional resource group name
        subscription_id: Optional subscription ID
    """
    cmd = ["resource", "list"]
    
    if resource_type:
        cmd.extend(["--resource-type", resource_type])
    
    if resource_group:
        cmd.extend(["--resource-group", resource_group])
        
    if subscription_id:
        cmd.extend(["--subscription", subscription_id])
    
    result = await run_az_command(cmd)
    
    if "error" in result:
        return f"Error listing resources: {result['error']}"
    
    if not result:
        return "No resources found matching the criteria."
    
    output = []
    for resource in result:
        output.append(f"Name: {resource.get('name')}")
        output.append(f"Type: {resource.get('type')}")
        output.append(f"Location: {resource.get('location')}")
        output.append(f"Resource Group: {resource.get('resourceGroup')}")
        output.append("-" * 40)
    
    return "\n".join(output)

@mcp.tool()
async def run_custom_az_command(command: str) -> str:
    """
    Run a custom Azure CLI command.
    
    Args:
        command: The full Azure CLI command to execute (without the 'az' prefix)
    """
    # Parse command into parts
    command_parts = command.split()
    
    # Run the command
    result = await run_az_command(command_parts)
    
    if "error" in result:
        return f"Error executing command: {result['error']}"
    
    # Return the result as formatted YAML
    try:
        return yaml.dump(result, default_flow_style=False)
    except Exception:
        return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Load environment variables
    load_environment_variables()
    
    # Initialize and run the server
    print("Starting Azure MCP server...")
    mcp.run(transport='stdio')