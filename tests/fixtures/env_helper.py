"""Helpers for ConfigAccessor tests that use temporary secret files."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path

FIXTURES_ENV_DIR = Path(__file__).resolve().parent / 'env'


@contextmanager
def temp_secrets_dir():
    """Yield a temporary directory path suitable for ConfigAccessor secrets_dir."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def write_secret_file(secrets_dir: str | os.PathLike[str], name: str, value: str) -> Path:
    """Write a lowercased secret file and return its path."""
    path = Path(secrets_dir) / name.lower()
    path.write_text(value, encoding='utf-8')
    return path
