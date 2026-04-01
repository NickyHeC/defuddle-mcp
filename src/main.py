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
import logging
import os
import shutil
import subprocess

from dedalus_mcp import MCPServer

from src.tools import tools

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

server = MCPServer(
    name="defuddle-mcp",
)


def _ensure_defuddle() -> None:
    """Try to install the defuddle npm package. Non-fatal if it fails."""
    local_bin = os.path.join(PROJECT_ROOT, "node_modules", ".bin", "defuddle")
    if os.path.isfile(local_bin) or shutil.which("defuddle"):
        return

    npm = shutil.which("npm")
    if not npm:
        logger.warning("npm not found — defuddle CLI won't be available until Node.js is installed")
        return

    try:
        subprocess.run(
            [npm, "install", "--save", "defuddle"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except Exception as e:
        logger.warning("Failed to install defuddle: %s", e)


async def main() -> None:
    _ensure_defuddle()
    for tool_func in tools:
        server.collect(tool_func)
    port = int(os.environ.get("PORT", "8080"))
    await server.serve(port=port)


if __name__ == "__main__":
    asyncio.run(main())
