# defuddle-mcp

MCP server that extracts the main content from web pages using [defuddle](https://github.com/kepano/defuddle). Returns cleaned Markdown or HTML with metadata (title, author, description, etc.), stripping away ads, navigation, sidebars, and other clutter.

No authentication required — defuddle runs locally as a CLI tool.

## Tools

| Tool | Description |
|------|-------------|
| `defuddle_url` | Fetch a URL and extract its main content |
| `defuddle_html` | Extract main content from raw HTML |

Both tools return a structured result with: `title`, `author`, `description`, `domain`, `content`, `word_count`, and other metadata fields. Set `markdown=false` to get HTML instead of Markdown.

## Setup

Requires **Python >= 3.10** and **Node.js >= 18**.

```bash
uv sync
npm install
```

## Run

```bash
uv run python -m src.main
```

The server starts on `http://127.0.0.1:8080/mcp`.

## Test

```bash
uv run python -m src.client
```
