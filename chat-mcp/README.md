# chat-mcp using mcp server[duckduckgo tool] & GROQ LLM

## steps to activate virtual environment using uv and installing packages
If you are new to uv (alternative to pip) refer UV documentation [Link](https://docs.astral.sh/uv/), an extremely fast Python package and project manager, written in Rust
```
cd chat-mcp
uv venv
source .venv\Scripts\activate
uv add -r requirements.txt
```
Run the application using uv
```
uv run app.py
```
# Chat interface in terminal to interact

**Output response from the mcp server (duckduckgo search tool) with groq llm**
```
(chat-mcp) @Rajkumar-21 ➜ /workspaces/mcp-samples/chat-mcp (main) $ uv run app.py 
░░░░░░░░░░░░░░░░░░░░ [0/57] Installing wheels...                                                                                                                warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
Installed 57 packages in 304ms
Initializing chat...

===== Interactive MCP Chat =====
Type 'exit' or 'quit' to end the conversation
Type 'clear' to clear conversation history
==================================


You: HI

Assistant: [INFO] DuckDuckGo Search MCP Server running on stdio
[DEBUG] Received tool call request: {
  "name": "duckduckgo_web_search",
  "arguments": {
    "query": "hello",
    "count": 5,
    "safeSearch": "moderate"
  }
}
[DEBUG] Performing search - Query: "hello", Count: 5, SafeSearch: moderate
[DEBUG] Rate limit check - Current counts: { second: 0, month: 0, lastReset: 1744961426022 }
[INFO] Found 5 results for query: "hello"
Thought: The user said "HI" and I responded with a search query for "hello" to provide some information on the greeting.
Action: The action was to perform a web search using the duckduckgo_web_search function.
Action Input: The input to the action was the query "hello" with a count of 5 results and safe search set to moderate.
Observation: The observation is that the search results provided a definition and usage of the word "hello" from various sources, including dictionaries and Wikipedia.
Thought: I now know the final answer to the user's greeting.
Final Answer: Hello! It's nice to meet you. Is there something I can help you with or would you like to chat?

You: what is about MCP server, how we can integrate it with our application in enterprise production ready?

Assistant: [DEBUG] Received tool call request: {
  "name": "duckduckgo_web_search",
  "arguments": {
    "query": "MCP server integration enterprise production ready",
    "count": 10,
    "safeSearch": "moderate"
  }
}
[DEBUG] Performing search - Query: "MCP server integration enterprise production ready", Count: 10, SafeSearch: moderate
[DEBUG] Rate limit check - Current counts: { second: 1, month: 1, lastReset: 1744961426022 }
[INFO] Found 10 results for query: "MCP server integration enterprise production ready"
Thought: The search results provided a variety of information on MCP servers, including their integration with enterprise production-ready applications, tutorials on how to use them, and examples of production-ready MCP servers.

Action: The next step would be to review the search results and identify the most relevant information for integrating an MCP server with an enterprise production-ready application.

Action Input: The input to the action would be to review the search results and identify the key points for integrating an MCP server.

Observation: The observation is that the search results provided a range of information on MCP servers, including tutorials, examples, and production-ready implementations.

Thought: I now know the final answer to the user's question about integrating an MCP server with an enterprise production-ready application.

Final Answer: To integrate an MCP server with an enterprise production-ready application, you can follow these steps:

1. Review the search results and identify the most relevant information for your specific use case.
2. Choose a production-ready MCP server implementation that meets your needs.
3. Follow the tutorials and documentation provided to set up and configure the MCP server.
4. Integrate the MCP server with your enterprise application using the provided APIs and tools.

By following these steps, you can successfully integrate an MCP server with your enterprise production-ready application.
```