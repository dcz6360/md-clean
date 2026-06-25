# md-clean

[![CI](https://github.com/dcz6360/md-clean/actions/workflows/ci.yml/badge.svg)](https://github.com/dcz6360/md-clean/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-WIP-orange)
![CLI](https://img.shields.io/badge/type-CLI-informational)

> Paste an article URL and get clean, readable Markdown — or an EPUB ready for an e-reader.

`md-clean` is a command-line tool that fetches a web article, extracts the main content, removes ads, cookie banners, navigation, and tracking scripts, then prepends metadata as YAML front matter. It can also export an EPUB when `pandoc` is available.

Repository: [https://github.com/dcz6360/md-clean](https://github.com/dcz6360/md-clean)

Chinese documentation: [README.md](./README.md)

## Features

- **Article-first extraction**: Uses [trafilatura](https://github.com/adbar/trafilatura) to extract the main body and remove boilerplate.
- **Clean Markdown output**: Converts extracted HTML with [markdownify](https://github.com/matthewwithanm/python-markdownify), using ATX-style headings.
- **Metadata header**: Adds YAML front matter with `title`, `author`, `date`, `source_url`, and `fetched_at`.
- **EPUB export**: Uses system `pandoc` to generate an EPUB with a table of contents. If `pandoc` is missing, Markdown output still works.
- **JSON output**: `--json` emits `title`, `author`, `date`, `url`, and `markdown` for downstream scripts.
- **Pipeline-friendly CLI**: Status messages go to stderr; stdout contains only Markdown or JSON.

## Installation

Python 3.9 or newer is required.

### Install with pip

```bash
pip install .
```

### Install with pipx

```bash
pipx install .
```

EPUB export is optional and requires [pandoc](https://pandoc.org/installing.html).

## Usage

```bash
# Fetch an article and print clean Markdown to stdout
md-clean https://en.wikipedia.org/wiki/Python_(programming_language)

# Write Markdown to a file
md-clean https://example.com/article -o out.md

# Export an EPUB as well (requires pandoc)
md-clean https://example.com/article --epub book.epub

# Emit JSON
md-clean https://example.com/article --json

# Show version and help
md-clean --version
md-clean --help
```

### Example output

```markdown
---
title: Python (programming language)
author: Unknown
date: Unknown
source_url: https://en.wikipedia.org/wiki/Python_(programming_language)
fetched_at: 2026-06-25
---

# Python (programming language)

Python is a high-level, general-purpose programming language. ...
```

## Options

| Option | Description |
| --- | --- |
| `url` | Article URL to fetch. If omitted, the CLI prints help and exits. |
| `-o, --output FILE` | Write Markdown to a UTF-8 file and create parent directories when needed. |
| `--epub FILE` | Also export EPUB; falls back gracefully if `pandoc` is not installed. |
| `--json` | Emit JSON with `title`, `author`, `date`, `url`, and `markdown`. |
| `--version` | Print the package version and exit. |
| `--help` | Show help text. |

## How it works

1. **Fetch**: `trafilatura.fetch_url(url)` downloads the page HTML.
2. **Extract**: `trafilatura.bare_extraction(...)` collects metadata, and `trafilatura.extract(..., output_format="html")` returns clean article HTML.
3. **Convert**: `markdownify` converts clean HTML to Markdown and strips leftover `script`, `style`, and `noscript` elements.
4. **Annotate**: YAML front matter is prepended with source and fetch metadata.
5. **Output**: The CLI writes to stdout, a file, JSON, or EPUB depending on options.

Data flow: `URL → fetch_url → extract(html) → markdownify → metadata header → output/EPUB`

## Dependencies

- [trafilatura](https://pypi.org/project/trafilatura/) `>=1.6.0`
- [markdownify](https://pypi.org/project/markdownify/) `>=0.11.0`
- [rich](https://pypi.org/project/rich/) `>=13.0.0`
- Optional: [pandoc](https://pandoc.org/) for EPUB export

Development and testing also require `pytest`.

## Running tests

```bash
pip install -e .
python -m pytest tests/ -q
```

## Project structure

```text
md-clean/
├── src/md_clean/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   └── extractor.py
├── tests/
│   └── test_extractor.py
├── .github/workflows/ci.yml
├── conftest.py
├── pyproject.toml
├── requirements.txt
├── CONTRIBUTING.md
├── README.md
├── README.en.md
└── LICENSE
```

## Contributing

Issues and pull requests are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before contributing.

## Known limitations

- The target URL must be reachable from your network; some sites may block scraping.
- Highly dynamic JavaScript-rendered pages may not expose enough article HTML to trafilatura.
- EPUB export requires system `pandoc`; without it, Markdown output still works.
- Author and date metadata depend on the page structure and may be reported as `Unknown`.

## License

[MIT](./LICENSE) © 2026 md-clean contributors
