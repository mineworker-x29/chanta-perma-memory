"""Dry-run ingest policy helpers.

This module intentionally produces suggested actions only.
It does not move, delete, or mutate files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class IngestDecision:
    source_path: Path
    suggested_bucket: str
    reason: str


def evaluate_inbox(inbox_path: Path) -> list[IngestDecision]:
    """Scan inbox and return deterministic, dry-run placement suggestions."""

    if not inbox_path.exists():
        return []

    decisions: list[IngestDecision] = []
    for path in sorted(inbox_path.iterdir()):
        if path.name.startswith("."):
            continue

        suffix = path.suffix.lower()
        if suffix in {".md", ".txt", ".pdf"}:
            bucket = "90_Shared"
            reason = "Document-like file; requires explicit classification review."
        else:
            bucket = "00_Inbox"
            reason = "Unknown type; keep in inbox for manual handling."

        decisions.append(
            IngestDecision(source_path=path, suggested_bucket=bucket, reason=reason)
        )

    return decisions
