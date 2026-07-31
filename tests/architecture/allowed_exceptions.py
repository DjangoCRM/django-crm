"""Explicit allow-list for tolerated cross-app import edges.

Each entry documents a single importing file → imported module pair that is
outside the zero-tolerance core layering rules but intentionally retained.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AllowedException:
    importing_file: str
    imported_module: str
    reason: str
    owner: str

    def as_key(self) -> tuple[str, str]:
        return (self.importing_file, self.imported_module)
