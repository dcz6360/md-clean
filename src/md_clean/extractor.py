"""Core extraction and formatting logic for md-clean.

This module is responsible for:

    * fetching a web page and extracting the main article text via trafilatura;
    * converting the extracted HTML to clean Markdown via markdownify;
    * building a metadata header (source URL, fetch date, title, author);
    * exporting Markdown to EPUB via pandoc (with graceful fallback);
    * serializing results to JSON.

Heavy third-party dependencies (trafilatura, markdownify) are imported lazily
inside :func:`fetch_and_extract` so that the rest of the module stays
importable even when those packages are not installed. This keeps unit tests
fast and allows ``--help`` / ``--version`` to work without the full stack.
"""
from __future__ import annotations

import datetime as _dt
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass
from typing import Optional

from rich.console import Console

# Status / error messages go to stderr so stdout stays clean for piping.
console: Console = Console(stderr=True)


@dataclass
class Article:
    """Container for a single extracted article."""

    title: str
    author: str
    date: str
    url: str
    markdown: str


def format_metadata_header(title: str, author: str, date: str, url: str) -> str:
    """Build a YAML front-matter style header for the Markdown output.

    Args:
        title: Article title.
        author: Article author (empty -> rendered as "Unknown").
        date: Article publish date (empty -> rendered as "Unknown").
        url: Source URL the article was fetched from.

    Returns:
        A formatted header string ending with a blank line before the body.
    """
    fetched_at = _dt.datetime.now().strftime("%Y-%m-%d")
    author_line = author.strip() or "Unknown"
    date_line = date.strip() or "Unknown"
    return (
        "---\n"
        f"title: {title}\n"
        f"author: {author_line}\n"
        f"date: {date_line}\n"
        f"source_url: {url}\n"
        f"fetched_at: {fetched_at}\n"
        "---\n\n"
    )


def fetch_and_extract(url: str) -> Optional[Article]:
    """Fetch *url* and return an :class:`Article` with clean Markdown.

    Returns ``None`` and prints a friendly error if the page cannot be
    downloaded or no main content could be extracted.
    """
    try:
        import trafilatura  # lazy import keeps module importable w/o the dep
        from markdownify import markdownify as md_convert
    except ImportError as exc:
        console.print(f"[red]缺少依赖:[/red] {exc.name} 未安装。")
        console.print("[red]请运行:[/red] pip install trafilatura markdownify")
        return None

    try:
        downloaded = trafilatura.fetch_url(url)
    except Exception as exc:  # network failures, timeouts, DNS errors, etc.
        console.print(f"[red]网络抓取失败:[/red] {exc}")
        return None

    if not downloaded:
        console.print("[red]抓取失败:[/red] 无法下载页面内容，请确认 URL 是否可访问。")
        return None

    metadata = trafilatura.bare_extraction(
        downloaded,
        include_comments=False,
        include_tables=True,
        include_images=False,
        as_dict=True,
    )
    html_body = trafilatura.extract(
        downloaded,
        output_format="html",
        include_comments=False,
        include_tables=True,
        include_images=False,
    )

    if not html_body:
        console.print("[red]正文提取失败:[/red] 该页面可能没有可识别的正文内容。")
        return None

    meta = metadata or {}
    title = (meta.get("title") or "").strip() or "Untitled"
    author = (meta.get("author") or "").strip()
    date = (meta.get("date") or "").strip()

    # Strip leftover script/style/noscript defensively even though trafilatura
    # already returns clean article HTML.
    body = md_convert(
        html_body, heading_style="ATX", strip=["script", "style", "noscript"]
    ).strip()
    header = format_metadata_header(title, author, date, url)
    return Article(
        title=title,
        author=author,
        date=date,
        url=url,
        markdown=header + body + "\n",
    )


def export_epub(markdown_path: str, epub_path: str) -> tuple[bool, str]:
    """Convert *markdown_path* to an EPUB at *epub_path* via pandoc.

    Returns a ``(success, message)`` tuple. When pandoc is unavailable a
    descriptive message is returned with ``success == False`` so callers can
    gracefully degrade to Markdown-only output.
    """
    pandoc = shutil.which("pandoc")
    if not pandoc:
        return False, "系统未安装 pandoc，已跳过 EPUB 导出，仅输出 .md 文件。"

    try:
        # Use the fully-resolved executable path: on Windows the bare command
        # name "pandoc" cannot be launched in list form when it resolves to a
        # .cmd/.bat shim (CreateProcess ignores PATHEXT), so the resolved path
        # is required for cross-platform reliability.
        subprocess.run(
            [pandoc, markdown_path, "-o", epub_path, "--toc"],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or str(exc)
        return False, f"pandoc 导出失败: {detail}"
    except FileNotFoundError:
        return False, "系统未安装 pandoc，已跳过 EPUB 导出，仅输出 .md 文件。"

    return True, f"EPUB 已导出: {epub_path}"


def article_to_json(article: Article) -> str:
    """Serialize *article* to a pretty-printed JSON string."""
    return json.dumps(asdict(article), ensure_ascii=False, indent=2)
