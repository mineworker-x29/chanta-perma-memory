from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "scripts" / "output" / "inbox_manifest.json"
OUTPUT_PATH = PROJECT_ROOT / "scripts" / "output" / "memory_candidates.json"


MEMORY_VERSION = "0.8"


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest file does not exist: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def make_memory_id(source_path: str, memory_type: str, content: str) -> str:
    raw = f"{source_path}|{memory_type}|{content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def build_candidates_from_item(item: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    source_path = str(item.get("path", ""))
    source_name = str(item.get("name", ""))
    candidate_domain = item.get("candidate_domain")
    tags = [str(tag).strip().lower() for tag in safe_list(item.get("tags")) if str(tag).strip()]
    confidence = item.get("confidence")
    content_preview = item.get("content_preview")

    # 1. domain memory candidate
    if candidate_domain:
        content = f"Document '{source_name}' is likely associated with domain '{candidate_domain}'."
        candidates.append(
            {
                "memory_id": make_memory_id(source_path, "document-domain", content),
                "source_path": source_path,
                "source_name": source_name,
                "memory_type": "document-domain",
                "memory_layer": "provisional",
                "related_domain": candidate_domain,
                "content": content,
                "tags": tags,
                "confidence": confidence,
                "status": "candidate",
                "reason": "Candidate domain was inferred from filename/path/content-based light parsing."
            }
        )

    # 2. topic/tag memory candidate
    if tags:
        content = f"Document '{source_name}' is associated with tags: {', '.join(tags)}."
        candidates.append(
            {
                "memory_id": make_memory_id(source_path, "document-topic", content),
                "source_path": source_path,
                "source_name": source_name,
                "memory_type": "document-topic",
                "memory_layer": "provisional",
                "related_domain": candidate_domain,
                "content": content,
                "tags": tags,
                "confidence": confidence,
                "status": "candidate",
                "reason": "Tags were inferred from extension, keyword rules, and optional content preview."
            }
        )

    # 3. preview candidate
    if content_preview:
        trimmed_preview = content_preview[:400].strip()
        content = f"Document preview for '{source_name}': {trimmed_preview}"
        candidates.append(
            {
                "memory_id": make_memory_id(source_path, "document-preview", content),
                "source_path": source_path,
                "source_name": source_name,
                "memory_type": "document-preview",
                "memory_layer": "provisional",
                "related_domain": candidate_domain,
                "content": content,
                "tags": tags,
                "confidence": confidence,
                "status": "candidate",
                "reason": "A light content preview was extracted from a text-based file."
            }
        )

    # 4. fallback reference candidate for unclassified docs
    if not candidate_domain and not tags:
        content = f"Document '{source_name}' exists in inbox and remains unclassified."
        candidates.append(
            {
                "memory_id": make_memory_id(source_path, "document-reference", content),
                "source_path": source_path,
                "source_name": source_name,
                "memory_type": "document-reference",
                "memory_layer": "provisional",
                "related_domain": None,
                "content": content,
                "tags": [],
                "confidence": confidence,
                "status": "candidate",
                "reason": "The item was retained as a provisional reference because no strong domain or tag signal was found."
            }
        )

    return candidates


def build_memory_candidates(manifest: dict[str, Any]) -> dict[str, Any]:
    items = safe_list(manifest.get("items"))
    source_manifest_version = str(manifest.get("manifest_version", "unknown"))

    candidates: list[dict[str, Any]] = []
    for item in items:
        candidates.extend(build_candidates_from_item(item))

    return {
        "memory_version": MEMORY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest_version": source_manifest_version,
        "source_manifest_path": str(MANIFEST_PATH),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def save_output(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def print_summary(payload: dict[str, Any]) -> None:
    candidates = safe_list(payload.get("candidates"))
    type_counter = Counter(str(c.get("memory_type")) for c in candidates)
    layer_counter = Counter(str(c.get("memory_layer")) for c in candidates)

    print("[OK] Memory candidates generated")
    print(f" - Memory version : {payload.get('memory_version')}")
    print(f" - Source manifest: {payload.get('source_manifest_version')}")
    print(f" - Candidate count: {payload.get('candidate_count')}")
    print(f" - Output path    : {OUTPUT_PATH}")
    print(f" - By type        : {dict(type_counter)}")
    print(f" - By layer       : {dict(layer_counter)}")


def main() -> None:
    manifest = load_manifest(MANIFEST_PATH)
    payload = build_memory_candidates(manifest)
    save_output(payload, OUTPUT_PATH)
    print_summary(payload)


if __name__ == "__main__":
    main()