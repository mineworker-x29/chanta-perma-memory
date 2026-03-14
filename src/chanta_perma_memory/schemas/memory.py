"""Core metadata schema models for memory records."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EvidenceType(str, Enum):
    FACT = "fact"
    INTERPRETATION = "interpretation"
    HYPOTHESIS = "hypothesis"


class MemoryTier(str, Enum):
    TRANSIENT = "transient_working_context"
    PROVISIONAL = "provisional_memory"
    DURABLE = "durable_memory"
    ARCHIVE = "archive_memory"


@dataclass(slots=True)
class MemoryRecord:
    title: str
    evidence_type: EvidenceType
    tier: MemoryTier = MemoryTier.PROVISIONAL
    confidence: float = 0.0
    tags: list[str] = field(default_factory=list)
    source: str | None = None
