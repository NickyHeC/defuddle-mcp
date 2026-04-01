# PROJECT.md — Platform Research Notes

> This file is a working notepad for the developer (or AI coding agent) building
> this MCP server. Fill in each section as you research the target platform.
> The information here drives the implementation in `src/main.py` and `src/tools.py`.
>
> **Do not commit secrets.** Store credentials in `.env` (which is gitignored).

---

## Platform Overview

**Platform name:** Defuddle
**Official docs:** https://github.com/kepano/defuddle
**Base URL:** N/A — defuddle is a local CLI/library, not a remote API.

Defuddle extracts the main content from web pages by removing clutter like
ads, sidebars, headers, footers, comments, and other non-essential elements.
It returns cleaned HTML or Markdown along with metadata (title, author,
description, etc.). It was created for Obsidian Web Clipper but runs in any
environment.

We are building an MCP server so that AI agents can use defuddle to read and
understand web pages — fetching a URL and getting back clean, structured
content instead of raw noisy HTML.

---

## Authentication

**Auth type:** No Auth

Defuddle is a local tool — it runs as a CLI process on the same machine as the
MCP server. No API keys, tokens, or OAuth flows are needed.

---

## Endpoints / Features to Implement

Defuddle is invoked via its CLI. The MCP server exposes two tools that wrap it:

| Tool name       | CLI command                              | Description                                           |
|-----------------|------------------------------------------|-------------------------------------------------------|
| `defuddle_url`  | `defuddle parse <url> --json [--markdown]` | Fetch a URL and extract its main content             |
| `defuddle_html` | `defuddle parse <file> --json [--markdown]` | Parse raw HTML (written to a temp file) and extract content |

### CLI flags used

- `--json` / `-j` — Output as JSON with metadata and content
- `--markdown` / `-m` — Convert content to Markdown format
- `--property <name>` / `-p` — Extract a specific property (not exposed as a tool)
- `--debug` — Enable debug mode (not exposed)

---

## Rate Limits and Restrictions

- **Rate limit:** None — defuddle runs locally.
- **Network:** The CLI fetches URLs over HTTP, so network access is required
  for the `defuddle_url` tool but not for `defuddle_html`.
- **Dependencies:** Requires Node.js >= 18 and the `defuddle` npm package.

---

## Response Format Notes

When invoked with `--json`, defuddle returns a JSON object:

```json
{
  "title": "Article Title",
  "author": "Author Name",
  "description": "A summary of the article",
  "domain": "example.com",
  "favicon": "https://example.com/favicon.ico",
  "image": "https://example.com/hero.jpg",
  "language": "en",
  "published": "2025-01-15",
  "site": "Example Site",
  "content": "<p>Cleaned HTML or Markdown content...</p>",
  "wordCount": 1234,
  "parseTime": 42
}
```

When `--markdown` is combined with `--json`, the `content` field contains
Markdown instead of HTML.

---

## Token / Credential Notes

N/A — no credentials required.

---

## Additional References

- [Defuddle GitHub repo](https://github.com/kepano/defuddle)
- [Defuddle npm package](https://www.npmjs.com/package/defuddle)
- [Obsidian Web Clipper](https://obsidian.md/clipper) (the project defuddle was created for)

---

## Notes for README

- MCP server wrapping defuddle for AI-agent-friendly web content extraction
- Two tools: `defuddle_url` (parse a URL) and `defuddle_html` (parse raw HTML)
- No authentication required — defuddle runs locally
- Returns structured metadata (title, author, description, etc.) plus clean content
- Supports Markdown and HTML output formats
- Requires Node.js >= 18 and the defuddle npm package
