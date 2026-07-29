"""Sample secret files and helpers for configuration accessor tests."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent


def write_temp_secret_file(name: str, content: str) -> str:
    """Write a temporary secret file and return its parent directory path."""
    directory = tempfile.mkdtemp(prefix='forge-config-secrets-')
    secret_path = Path(directory) / name.lower()
    secret_path.write_text(content, encoding='utf-8')
    return directory


def sample_secret_path(filename: str) -> Path:
    return FIXTURES_DIR / filename
