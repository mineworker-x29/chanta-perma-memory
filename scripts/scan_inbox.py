from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ============================================================
# Version
# ============================================================

MANIFEST_VERSION = "0.2"


# ============================================================
# Configuration
# ============================================================

REPOSITORY_ROOT = Path(r"D:\ChantaResearchGroup")
INBOX_PATH = REPOSITORY_ROOT / "00_Inbox"

# Output stays inside the Perma repo, not inside the real source repository.
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_PATH = OUTPUT_DIR / "inbox_manifest.json"

# Optional schema path for reference / future validation.
SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "schemas"
    / "inbox_manifest.schema.json"
)

RECURSIVE_SCAN = True

SKIP_NAMES = {
    ".DS_Store",
    "Thumbs.db",
}

SKIP_PREFIXES = {
    ".",
}

ALLOWED_EXTENSIONS: set[str] = set()
BLOCKED_EXTENSIONS: set[str] = {
    ".tmp",
    ".log",
    ".pyc",
}


# ============================================================
# Data Model
# ============================================================

@dataclass
class RepositoryItem:
    path: str
    relative_path: str
    name: str
    extension: str
    size: int
    modified_time: str
    status: str
    candidate_domain: str | None
    tags: list[str]
    confidence: str | None
    is_file: bool


# ============================================================
# Helpers
# ============================================================

def should_skip(path: Path) -> bool:
    """Return True if the file should be skipped."""
    name = path.name

    if name in SKIP_NAMES:
        return True

    if any(name.startswith(prefix) for prefix in SKIP_PREFIXES):
        return True

    extension = path.suffix.lower()

    if ALLOWED_EXTENSIONS and extension not in ALLOWED_EXTENSIONS:
        return True

    if extension in BLOCKED_EXTENSIONS:
        return True

    return False


def to_iso_utc(timestamp: float) -> str:
    """Convert POSIX timestamp to ISO-8601 UTC string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def extract_file_metadata(file_path: Path, inbox_root: Path) -> RepositoryItem:
    """Extract minimal repository metadata for a single file."""
    stat = file_path.stat()

    try:
        relative_path = file_path.relative_to(inbox_root)
    except ValueError:
        relative_path = Path(file_path.name)

    return RepositoryItem(
        path=str(file_path),
        relative_path=str(relative_path),
        name=file_path.name,
        extension=file_path.suffix.lower(),
        size=stat.st_size,
        modified_time=to_iso_utc(stat.st_mtime),
        status="inbox",
        candidate_domain=None,
        tags=[],
        confidence=None,
        is_file=file_path.is_file(),
    )


def iter_candidate_files(inbox_path: Path) -> list[Path]:
    """Collect files from the inbox according to scan settings."""
    if RECURSIVE_SCAN:
        candidates = inbox_path.rglob("*")
    else:
        candidates = inbox_path.glob("*")

    files: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        files.append(path)

    return sorted(files, key=lambda p: str(p).lower())


def scan_inbox(inbox_path: Path) -> list[RepositoryItem]:
    """Scan the inbox and return repository item metadata."""
    files = iter_candidate_files(inbox_path)
    return [extract_file_metadata(file_path, inbox_path) for file_path in files]


def build_manifest(items: list[RepositoryItem], inbox_path: Path) -> dict[str, Any]:
    """Build the manifest payload according to manifest v0.2."""
    generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": generated_at,
        "repository_root": str(REPOSITORY_ROOT),
        "inbox_path": str(inbox_path),
        "item_count": len(items),
        "items": [asdict(item) for item in items],
    }


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save manifest JSON to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


# ============================================================
# Main
# ============================================================

def main() -> None:
    if not REPOSITORY_ROOT.exists():
        raise FileNotFoundError(
            f"Repository root does not exist: {REPOSITORY_ROOT}"
        )

    if not INBOX_PATH.exists():
        raise FileNotFoundError(
            f"Inbox path does not exist: {INBOX_PATH}"
        )

    if not INBOX_PATH.is_dir():
        raise NotADirectoryError(
            f"Inbox path is not a directory: {INBOX_PATH}"
        )

    items = scan_inbox(INBOX_PATH)
    manifest = build_manifest(items, INBOX_PATH)
    save_manifest(manifest, OUTPUT_PATH)

    print("[OK] Inbox scan complete")
    print(f" - Manifest ver : {MANIFEST_VERSION}")
    print(f" - Inbox path   : {INBOX_PATH}")
    print(f" - Items found  : {len(items)}")
    print(f" - Output file  : {OUTPUT_PATH}")
    print(f" - Schema path  : {SCHEMA_PATH}")


if __name__ == "__main__":
    main()