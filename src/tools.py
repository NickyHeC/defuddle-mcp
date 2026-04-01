"""Defuddle tools.

Uses the defuddle CLI (https://github.com/kepano/defuddle) to extract
main content from web pages. Requires Node.js >= 18 and the defuddle
npm package (install globally with `npm install -g defuddle`).
"""

import asyncio
import json
import os
import shutil
import tempfile

from dedalus_mcp import tool
from pydantic import BaseModel


class DefuddleResult(BaseModel):
    success: bool = True
    error: str | None = None
    title: str = ""
    author: str = ""
    description: str = ""
    domain: str = ""
    favicon: str = ""
    image: str = ""
    language: str = ""
    published: str = ""
    site: str = ""
    content: str = ""
    word_count: int = 0
    parse_time_ms: float = 0


def _find_defuddle_bin() -> list[str]:
    """Resolve the defuddle CLI binary, preferring a local install."""
    local_bin = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "node_modules", ".bin", "defuddle",
    )
    if os.path.isfile(local_bin):
        return [local_bin]

    if shutil.which("defuddle"):
        return ["defuddle"]

    npx = shutil.which("npx")
    if npx:
        return [npx, "defuddle"]

    raise RuntimeError(
        "defuddle CLI not found. Install it with: npm install -g defuddle"
    )


async def _run_defuddle(target: str, *, markdown: bool = True) -> dict:
    """Run the defuddle CLI and return parsed JSON output."""
    bin_cmd = _find_defuddle_bin()
    args = [*bin_cmd, "parse", target, "--json"]
    if markdown:
        args.append("--markdown")

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        err = stderr.decode().strip() or f"defuddle exited with code {proc.returncode}"
        raise RuntimeError(err)

    return json.loads(stdout.decode())


def _to_result(data: dict) -> DefuddleResult:
    return DefuddleResult(
        title=data.get("title") or "",
        author=data.get("author") or "",
        description=data.get("description") or "",
        domain=data.get("domain") or "",
        favicon=data.get("favicon") or "",
        image=data.get("image") or "",
        language=data.get("language") or "",
        published=data.get("published") or "",
        site=data.get("site") or "",
        content=data.get("content") or "",
        word_count=data.get("wordCount") or 0,
        parse_time_ms=data.get("parseTime") or 0,
    )


@tool(description="Extract the main content from a web page URL. Returns cleaned Markdown (or HTML) with metadata such as title, author, and description. Removes clutter like ads, sidebars, headers, and footers.")
async def defuddle_url(url: str, markdown: bool = True) -> DefuddleResult:
    """Fetch a URL and extract its main content using defuddle.

    Args:
        url: The URL of the web page to parse.
        markdown: Return content as Markdown (True) or HTML (False).

    """
    try:
        data = await _run_defuddle(url, markdown=markdown)
        return _to_result(data)
    except Exception as e:
        return DefuddleResult(success=False, error=str(e))


@tool(description="Extract the main content from raw HTML. Returns cleaned Markdown (or HTML) with metadata. Useful when you already have page HTML and want to extract the readable content.")
async def defuddle_html(html: str, markdown: bool = True) -> DefuddleResult:
    """Parse raw HTML and extract its main content using defuddle.

    Args:
        html: Raw HTML content to parse.
        markdown: Return content as Markdown (True) or HTML (False).

    """
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".html")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(html)
            data = await _run_defuddle(tmp_path, markdown=markdown)
            return _to_result(data)
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        return DefuddleResult(success=False, error=str(e))


tools = [defuddle_url, defuddle_html]
