import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terminal-server 📟")
DEFAULT_WORKSPACE = os.path.expanduser("/workspaces/mcp-samples/mcp/client/terminal-client/workspace")

@mcp.tool()  
def run_command(command: str):  
    """  
    Run a terminal command inside the workspace directory.

    Args:
        command (str): The shell command to run.
    
    Returns:
        str: The output of the command or error message.
    """  
    try:  
        result = subprocess.run(command, shell=True, cwd=DEFAULT_WORKSPACE, capture_output=True, text=True)  
        return result.stdout or result.stderr  
    except Exception as e:  
        return str(e)
    
if __name__ == "__main__":  
    mcp.run(transport='stdio')  