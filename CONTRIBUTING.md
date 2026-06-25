# Contributing to md-clean

Thanks for your interest in improving `md-clean`.

## Development setup

1. Fork and clone the repository:

   ```bash
   git clone https://github.com/dcz6360/md-clean.git
   cd md-clean
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install the package in editable mode and install test tools:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e .
   python -m pip install pytest
   ```

## Running tests

Run the unit test suite before opening a pull request:

```bash
python -m pytest tests/ -q
```

The GitHub Actions CI workflow runs the same test command on Python 3.9, 3.10, 3.11, and 3.12.

## Pull request guidelines

- Keep changes focused and easy to review.
- Add or update tests when changing behavior.
- Update `README.md` and `README.en.md` when changing user-facing behavior.
- Keep stdout clean for CLI content; status and errors should go to stderr.
- Do not commit generated files such as `__pycache__`, `.pytest_cache`, build artifacts, or EPUB outputs.

## Reporting issues

When reporting a bug, include:

- Your operating system and Python version.
- The `md-clean` command you ran.
- The URL or a minimal reproducible example, when possible.
- Expected behavior and actual behavior.

Please avoid sharing private URLs, credentials, or copyrighted article text unless you have permission to do so.
