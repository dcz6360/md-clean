"""Command-line interface for md-clean.

Exposes the ``md-clean`` entry point. Parses arguments, drives the extractor
and renders results to stdout / file / JSON / EPUB according to the options.

Design notes:

    * All status / error messages go to stderr (via :data:`console`), so that
      stdout only carries the actual Markdown / JSON content and stays clean
      for shell pipelines (e.g. ``md-clean <url> | ...``).
    * EPUB export needs a Markdown file on disk for pandoc: when ``-o`` is
      provided that file is reused, otherwise a temporary file is written and
      removed after conversion.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence

from rich.console import Console

from . import __version__
from .extractor import (
    article_to_json,
    export_epub,
    fetch_and_extract,
)

# Status messages go to stderr; content goes to stdout via sys.stdout.write.
console: Console = Console(stderr=True)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser with Chinese help text."""
    parser = argparse.ArgumentParser(
        prog="md-clean",
        description="抓取网页文章并输出干净的 Markdown / EPUB，自动剥离广告与追踪脚本。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  md-clean https://example.com/article\n"
            "  md-clean https://example.com/article -o out.md\n"
            "  md-clean https://example.com/article --epub book.epub\n"
            "  md-clean https://example.com/article --json\n"
        ),
    )
    parser.add_argument("url", nargs="?", help="要抓取的文章 URL")
    parser.add_argument(
        "-o", "--output", metavar="FILE", help="将 Markdown 写入指定文件"
    )
    parser.add_argument(
        "--epub",
        metavar="FILE",
        help="同时导出 EPUB（需要系统已安装 pandoc）",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="以 JSON 格式输出结果（含 title/author/date/url/markdown）",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"md-clean {__version__}",
    )
    return parser


def _write_text(path: str, text: str) -> None:
    """Write *text* to *path* (UTF-8), creating parent directories as needed."""
    target = Path(path)
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Entry point for the ``md-clean`` console script.

    Returns the process exit code (0 on success, 1 on error).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.url:
        parser.print_help()
        return 1

    console.print(f"[cyan]正在抓取:[/cyan] {args.url}")
    article = fetch_and_extract(args.url)
    if article is None:
        return 1

    md_path: Optional[str] = args.output

    if args.as_json:
        sys.stdout.write(article_to_json(article) + "\n")
    elif args.output:
        _write_text(args.output, article.markdown)
        console.print(f"[green]已写入 Markdown:[/green] {args.output}")
    else:
        # Plain Markdown to stdout so it can be piped/redirected cleanly.
        sys.stdout.write(article.markdown)

    if args.epub:
        created_tmp = False
        if md_path is None:
            with tempfile.NamedTemporaryFile(
                "w", suffix=".md", delete=False, encoding="utf-8"
            ) as tmp:
                tmp.write(article.markdown)
                md_path = tmp.name
            created_tmp = True
        try:
            ok, message = export_epub(md_path, args.epub)
        finally:
            if created_tmp and md_path:
                Path(md_path).unlink(missing_ok=True)
        style = "green" if ok else "yellow"
        console.print(f"[{style}]{message}[/{style}]")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
