import argparse
import os
from azure_mcp import mcp, load_environment_variables

def main():
    """
    Main entry point for the Azure MCP server.
    """
    parser = argparse.ArgumentParser(description='Azure CLI MCP Server')
    
    # Add transport option (stdio or http)
    parser.add_argument(
        '--transport', 
        choices=['stdio', 'http'], 
        default='stdio',
        help='Transport protocol (stdio or http)'
    )
    
    # Add port option for HTTP transport
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Port number for HTTP transport'
    )
    
    # Add host option for HTTP transport
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host address for HTTP transport'
    )
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Load environment variables
    load_environment_variables()
    
    # Print startup message
    print(f"Starting Azure CLI MCP server with {args.transport} transport")
    
    # Start the MCP server with the specified transport
    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport='http', host=args.host, port=args.port)

if __name__ == "__main__":
    main()
