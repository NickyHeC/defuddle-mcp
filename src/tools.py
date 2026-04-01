"""Defuddle tools.

Extracts main content from web pages using pure Python libraries:
- readability-lxml for content extraction (Mozilla Readability port)
- markdownify for HTML-to-Markdown conversion
- beautifulsoup4 for metadata extraction
- httpx for async HTTP fetching
"""

import time
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from dedalus_mcp import tool
from markdownify import markdownify as md
from pydantic import BaseModel
from readability import Document


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


def _extract_metadata(soup: BeautifulSoup, url: str | None = None) -> dict:
    """Pull metadata from <meta> tags, <title>, and structured data."""

    def meta(name: str) -> str:
        tag = (
            soup.find("meta", attrs={"property": name})
            or soup.find("meta", attrs={"name": name})
        )
        return (tag.get("content", "") if tag else "").strip()

    title = (
        meta("og:title")
        or meta("twitter:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else "")
    )

    author = (
        meta("author")
        or meta("article:author")
        or meta("twitter:creator")
    )

    description = (
        meta("og:description")
        or meta("description")
        or meta("twitter:description")
    )

    image = meta("og:image") or meta("twitter:image")
    language = meta("og:locale") or ""
    if not language:
        html_tag = soup.find("html")
        if html_tag:
            language = html_tag.get("lang", "")

    published = (
        meta("article:published_time")
        or meta("date")
        or meta("pubdate")
    )

    site = meta("og:site_name") or ""
    domain = ""
    favicon = ""
    if url:
        parsed = urlparse(url)
        domain = parsed.netloc
        favicon = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    return {
        "title": title,
        "author": author,
        "description": description,
        "domain": domain,
        "favicon": favicon,
        "image": image,
        "language": language,
        "published": published,
        "site": site,
    }


def _parse_html(html: str, *, markdown: bool = True, url: str | None = None) -> DefuddleResult:
    """Extract main content and metadata from raw HTML."""
    start = time.perf_counter()

    soup = BeautifulSoup(html, "lxml")
    metadata = _extract_metadata(soup, url)

    doc = Document(html)
    article_html = doc.summary()

    if not metadata["title"]:
        metadata["title"] = doc.short_title() or doc.title() or ""

    if markdown:
        content = md(article_html, heading_style="ATX", strip=["img"]).strip()
    else:
        content = article_html

    word_count = len(content.split())
    elapsed = (time.perf_counter() - start) * 1000

    return DefuddleResult(
        **metadata,
        content=content,
        word_count=word_count,
        parse_time_ms=round(elapsed, 2),
    )


@tool(
    description=(
        "Extract the main content from a web page URL. Returns cleaned "
        "Markdown (or HTML) with metadata such as title, author, and "
        "description. Removes clutter like ads, sidebars, headers, and footers."
    ),
)
async def defuddle_url(url: str, markdown: bool = True) -> DefuddleResult:
    """Fetch a URL and extract its main content.

    Args:
        url: The URL of the web page to parse.
        markdown: Return content as Markdown (True) or HTML (False).

    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(url, headers={
                "User-Agent": (
                    "Mozilla/5.0 (compatible; DefuddleMCP/1.0; "
                    "+https://github.com/kepano/defuddle)"
                ),
            })
            resp.raise_for_status()
        return _parse_html(resp.text, markdown=markdown, url=url)
    except Exception as e:
        return DefuddleResult(success=False, error=str(e))


@tool(
    description=(
        "Extract the main content from raw HTML. Returns cleaned Markdown "
        "(or HTML) with metadata. Useful when you already have page HTML "
        "and want to extract the readable content."
    ),
)
async def defuddle_html(html: str, markdown: bool = True) -> DefuddleResult:
    """Parse raw HTML and extract its main content.

    Args:
        html: Raw HTML content to parse.
        markdown: Return content as Markdown (True) or HTML (False).

    """
    try:
        return _parse_html(html, markdown=markdown)
    except Exception as e:
        return DefuddleResult(success=False, error=str(e))


tools = [defuddle_url, defuddle_html]
