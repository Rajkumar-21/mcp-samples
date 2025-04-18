# mcp-samples

# Model Context Protocol (MCP)
MCP is a communication protocol that allows AI assistants like Claude to access real-time data and tools through external servers. Rather than being limited to information from training data, MCP lets AI models:

* Retrieve live information (like weather or stock prices)
* Use specialized tools (like calculators or code execution)
* Access private data (like your documents or emails)

**Simple Example:** When you ask LLM Application "What's the weather today?", it uses MCP to connect to a weather server to get current conditions for your location, rather than guessing based on old training data.

**Sample codes**

| Example Code                           | Details                                                    |
|--------------------------------|--------------------------------------------------------------------|
| [chat-mcp](chat-mcp/README.md) | chat-mcp using mcp server(duckduckgo search tool) & GROQ LLM       |
| [azure-cli-mcp](azure-cli-mcp/README.md) | azure-cli-mcp server is used to manage azure resource (Under Development...)       |