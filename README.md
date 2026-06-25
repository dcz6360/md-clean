# md-clean

![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-WIP-orange)
![CLI](https://img.shields.io/badge/type-CLI-informational)

> 粘贴一个文章链接，得到一份干净、可阅读的 Markdown —— 或者一本可直接放进电子书阅读器的 EPUB。

`md-clean` 是一个命令行工具：给定任意文章 URL，它会抓取网页正文，自动剥离广告、cookie 横幅、导航与追踪脚本，并在 Markdown 顶部附加元信息头（来源 URL、抓取日期、标题、作者），可选导出为 EPUB。

## 特性

- **正文优先**：基于 [trafilatura](https://github.com/adbar/trafilatura) 智能提取主正文，自动剔除广告、评论区与冗余模板。
- **干净输出**：通过 [markdownify](https://github.com/matthewwithanm/python-markdownify) 将提取后的 HTML 转为格式整洁的 Markdown，标题使用 ATX 风格。
- **元信息头**：输出顶部以 YAML front matter 形式附带 `title` / `author` / `date` / `source_url` / `fetched_at`。
- **EPUB 导出**：调用系统 `pandoc` 生成带目录的 EPUB；未安装 pandoc 时自动降级为仅输出 `.md` 并给出友好提示。
- **JSON 输出**：`--json` 一次性输出 `title/author/date/url/markdown`，方便下游脚本处理。
- **友好的终端体验**：使用 [rich](https://github.com/Textualize/rich) 输出彩色状态与错误信息，且状态信息走 stderr，**stdout 只承载干净内容**，便于管道与重定向。
- **管道友好**：`md-clean <url> | ...` 不会混入彩色日志。

## 安装

需要 Python 3.9 及以上。

### 通过 pip 安装

```bash
pip install .
```

### 通过 pipx 安装（推荐，隔离环境）

```bash
pipx install .
```

> EPUB 导出为可选功能，需要系统已安装 [pandoc](https://pandoc.org/installing.html)。未安装时程序仍可正常输出 Markdown。

## 用法

```bash
# 抓取并输出干净 Markdown 到 stdout
md-clean https://en.wikipedia.org/wiki/Python_(programming_language)

# 写入文件
md-clean https://example.com/article -o out.md

# 同时导出 EPUB（需要 pandoc）
md-clean https://example.com/article --epub book.epub

# 以 JSON 格式输出（含 title/author/date/url/markdown）
md-clean https://example.com/article --json

# 查看版本与帮助
md-clean --version
md-clean --help
```

### 输出示例

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

## 选项说明

| 选项 | 说明 |
| --- | --- |
| `url` | 要抓取的文章 URL（位置参数）。未提供时打印帮助并退出。 |
| `-o, --output FILE` | 将 Markdown 写入指定文件（UTF-8），自动创建父目录。 |
| `--epub FILE` | 同时导出 EPUB；未安装 pandoc 时自动降级，仅输出 `.md`。 |
| `--json` | 以 JSON 格式输出结果，字段为 `title/author/date/url/markdown`。 |
| `--version` | 显示版本号并退出。 |
| `--help` | 显示中文帮助文本。 |

## 工作原理

1. **下载**：`trafilatura.fetch_url(url)` 获取网页 HTML。
2. **提取正文**：`trafilatura.bare_extraction(...)` 取得标题、作者、日期等元信息；`trafilatura.extract(..., output_format="html")` 得到剔除广告/导航/评论后的干净正文 HTML。
3. **转 Markdown**：`markdownify` 将干净 HTML 转为 Markdown（ATX 标题），并额外剥离残留的 `script/style/noscript`。
4. **拼接元信息头**：在正文顶部附加 YAML front matter（来源 URL、抓取日期等）。
5. **输出**：按选项输出到 stdout / 文件 / JSON。
6. **EPUB（可选）**：将 Markdown 写入磁盘后调用 `pandoc` 生成 EPUB（带 `--toc` 目录）；pandoc 缺失时友好降级。

数据流：`URL → fetch_url → extract(html) → markdownify → 元信息头 → 输出/EPUB`

## 依赖

- [trafilatura](https://pypi.org/project/trafilatura/) `>=1.6.0` —— 正文提取
- [markdownify](https://pypi.org/project/markdownify/) `>=0.11.0` —— HTML → Markdown
- [rich](https://pypi.org/project/rich/) `>=13.0.0` —— 终端彩色输出
- **可选**：[pandoc](https://pandoc.org/) —— EPUB 导出

开发与测试额外需要 `pytest`。

## 运行测试

```bash
pip install -e .
python -m pytest tests/ -q
```

## 项目结构

```
md-clean/
├── src/md_clean/
│   ├── __init__.py      # 版本号
│   ├── __main__.py      # 支持 python -m md_clean
│   ├── cli.py           # argparse 入口与输出控制
│   └── extractor.py     # 抓取/提取/格式化/EPUB/JSON 核心逻辑
├── tests/
│   └── test_extractor.py
├── conftest.py          # 让测试在未安装时也能导入 src 包
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

## 已知限制

- 需要能访问目标 URL 的网络环境；部分站点可能屏蔽抓取，导致提取为空。
- 高度依赖 JavaScript 动态渲染的页面（SPA）可能无法被 trafilatura 提取到正文。
- EPUB 导出依赖系统 pandoc；未安装时仅输出 Markdown。
- 元信息（作者、日期）取决于页面结构，缺失时会显示为 `Unknown`。

## License

[MIT](./LICENSE) © 2026 md-clean contributors
