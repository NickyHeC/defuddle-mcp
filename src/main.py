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
import os
import shutil
import subprocess

from dedalus_mcp import MCPServer

from src.tools import tools

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server = MCPServer(
    name="defuddle-mcp",
)


def _ensure_defuddle() -> None:
    """Install the defuddle npm package locally if it isn't already available."""
    local_bin = os.path.join(PROJECT_ROOT, "node_modules", ".bin", "defuddle")
    if os.path.isfile(local_bin) or shutil.which("defuddle"):
        return

    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("npm not found — install Node.js >= 18")

    subprocess.run(
        [npm, "install", "--save", "defuddle"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
    )


async def main() -> None:
    _ensure_defuddle()
    for tool_func in tools:
        server.collect(tool_func)
    await server.serve(port=8080)


if __name__ == "__main__":
    asyncio.run(main())
