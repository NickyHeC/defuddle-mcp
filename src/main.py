"""Defuddle MCP server.

Extracts the main content from web pages using defuddle
(https://github.com/kepano/defuddle), returning cleaned HTML or Markdown
along with page metadata.

No authentication required — defuddle runs locally via its CLI.
Requires Node.js and the defuddle npm package.

To start the server:
    python -m src.main
"""

import asyncio
from dedalus_mcp import MCPServer

from src.tools import tools


server = MCPServer(
    name="defuddle-mcp",
)


async def main() -> None:
    for tool_func in tools:
        server.collect(tool_func)
    await server.serve(port=8080)


if __name__ == "__main__":
    asyncio.run(main())
