"""Test client for the Defuddle MCP server.

Start the server first:
    python -m src.main

Then run this script to verify the tools work:
    python -m src.client
"""

import asyncio
from dedalus_mcp.client import MCPClient


async def main() -> None:
    client = await MCPClient.connect("http://127.0.0.1:8080/mcp")

    tools = await client.list_tools()
    print("Available tools:", [t.name for t in tools.tools])

    sample_html = """
    <html>
    <head><title>Test Article</title></head>
    <body>
        <nav><a href="/">Home</a> | <a href="/about">About</a></nav>
        <article>
            <h1>Test Article</h1>
            <p>By Jane Doe</p>
            <p>This is the main content of the article. It contains multiple
            paragraphs of text that defuddle should extract as the primary
            content of the page.</p>
            <p>Defuddle removes clutter like navigation, sidebars, and footers,
            leaving only the meaningful content behind.</p>
        </article>
        <aside>Related links sidebar</aside>
        <footer>Copyright 2025</footer>
    </body>
    </html>
    """

    print("\n--- defuddle_html ---")
    result = await client.call_tool("defuddle_html", {
        "html": sample_html,
        "markdown": True,
    })
    print(result.content[0].text)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
