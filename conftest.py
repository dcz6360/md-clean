"""Make the src-layout package importable for tests without installation.

This allows ``pytest`` to discover ``md_clean`` even when the package has not
been installed with ``pip install -e .``.
"""
import sys
from pathlib import Path

SRC = Path(__file__).parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
