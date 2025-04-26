# Terminal Server


| MCP Server                           | Details                                                    |
|--------------------------------|--------------------------------------------------------------------|
| [terminal-server](mcp/server/terminal-server/README.md) | Interact with filesystem using terminal(execute command to create files, etc) 


***Settings.json for VS code***


```
{
    "mcp": {


        "inputs": [],
        "servers": {
            "terminal-server":{
                "command": "docker",
                "args": [
                    "run",
                    "--rm",
                    "-i",
                    "--init",
                    "-e", "DOCKER_CONTAINER=true",
                    "-v", "/workspaces/mcp-samples/mcp/workspace/:/root/workspace/",
                    "rajkumar218/terminal-server:v1"

                ],
                "env": {}
            }
        }
    }
}
```