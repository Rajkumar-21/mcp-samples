#!/bin/bash

# File used when I'm running the server locally during development
source .venv/bin/activate

export $(grep -v '^#' .env | xargs)

python mcp_azure_devops/server.py