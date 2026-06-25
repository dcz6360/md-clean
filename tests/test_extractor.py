"""Unit tests for md_clean.extractor.

These tests focus on the pure / mockable pieces of the extractor so they run
fast and do not require network access or the heavy trafilatura dependency to
be installed.
"""
from __future__ import annotations

import json
from unittest import mock

from md_clean.extractor import (
    Article,
    article_to_json,
    export_epub,
    format_metadata_header,
)


def test_format_metadata_header_contains_all_fields():
    """The header should expose title, author, date, source URL and fetch date."""
    header = format_metadata_header(
        title="我的文章标题",
        author="张三",
        date="2026-01-02",
        url="https://example.com/article",
    )
    assert header.startswith("---\n")
    assert "title: 我的文章标题" in header
    assert "author: 张三" in header
    assert "date: 2026-01-02" in header
    assert "source_url: https://example.com/article" in header
    assert "fetched_at:" in header
    # Header ends with the closing fence plus a blank line before the body.
    assert header.endswith("---\n\n")


def test_format_metadata_header_handles_empty_author_and_date():
    """Empty author / date should fall back to a readable placeholder."""
    header = format_metadata_header(
        title="T", author="", date="", url="https://x.io/p"
    )
    assert "author: Unknown" in header
    assert "date: Unknown" in header


def test_article_to_json_has_required_fields():
    """JSON output must expose title/author/date/url/markdown."""
    article = Article(
        title="T", author="A", date="2026-01-01", url="u", markdown="# Hi"
    )
    data = json.loads(article_to_json(article))
    for key in ("title", "author", "date", "url", "markdown"):
        assert key in data
    assert data["markdown"] == "# Hi"


def test_export_epub_falls_back_when_pandoc_missing():
    """When pandoc is absent, export must report failure with a clear message."""
    with mock.patch(
        "md_clean.extractor.shutil.which", return_value=None
    ):
        ok, message = export_epub("in.md", "out.epub")
    assert ok is False
    assert "pandoc" in message


def test_export_epub_success_invokes_pandoc():
    """When pandoc is present, a successful run returns success and the path."""
    fake_result = mock.Mock()
    fake_result.returncode = 0
    with mock.patch(
        "md_clean.extractor.shutil.which", return_value="/usr/bin/pandoc"
    ), mock.patch(
        "md_clean.extractor.subprocess.run", return_value=fake_result
    ) as run_mock:
        ok, message = export_epub("in.md", "out.epub")
    assert ok is True
    assert "out.epub" in message
    # pandoc should be called once with the resolved executable path.
    run_mock.assert_called_once()
    called_args = run_mock.call_args[0][0]
    assert called_args[0] == "/usr/bin/pandoc"
    assert "in.md" in called_args
    assert "out.epub" in called_args
