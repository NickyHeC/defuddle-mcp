"""Defuddle MCP server.

Extracts the main content from web pages using readability-lxml,
returning cleaned HTML or Markdown along with page metadata.

No authentication required. No external CLI dependencies.

To start the server:
    python -m src.main
"""

import asyncio
import os

from dedalus_mcp import MCPServer

from src.tools import tools

server = MCPServer(
    name="defuddle-mcp",
)


async def main() -> None:
    for tool_func in tools:
        server.collect(tool_func)
    port = int(os.environ.get("PORT", "8080"))
    await server.serve(port=port)


if __name__ == "__main__":
    asyncio.run(main())
