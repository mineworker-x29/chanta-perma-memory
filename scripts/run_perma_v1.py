from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "scripts" / "output"

MANIFEST_PATH = OUTPUT_DIR / "inbox_manifest.json"
REVIEW_REPORT_PATH = OUTPUT_DIR / "inbox_review_report.md"
MEMORY_CANDIDATES_PATH = OUTPUT_DIR / "memory_candidates.json"
MEMORY_CANDIDATES_REFINED_PATH = OUTPUT_DIR / "memory_candidates_refined.json"
SNAPSHOT_PATH = OUTPUT_DIR / "perma_v1_snapshot.json"


def load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def count_items(payload: dict[str, Any] | None, key: str) -> int:
    if not payload:
        return 0
    value = payload.get(key, [])
    return len(value) if isinstance(value, list) else 0


def main() -> None:
    manifest = load_json_if_exists(MANIFEST_PATH)
    memory_candidates = load_json_if_exists(MEMORY_CANDIDATES_PATH)
    memory_candidates_refined = load_json_if_exists(MEMORY_CANDIDATES_REFINED_PATH)

    snapshot = {
        "perma_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "components": {
            "manifest_path": str(MANIFEST_PATH) if MANIFEST_PATH.exists() else None,
            "review_report_path": str(REVIEW_REPORT_PATH) if REVIEW_REPORT_PATH.exists() else None,
            "memory_candidates_path": str(MEMORY_CANDIDATES_PATH) if MEMORY_CANDIDATES_PATH.exists() else None,
            "memory_candidates_refined_path": str(MEMORY_CANDIDATES_REFINED_PATH) if MEMORY_CANDIDATES_REFINED_PATH.exists() else None,
        },
        "summary": {
            "item_count": int(manifest.get("item_count", 0)) if manifest else 0,
            "memory_candidate_count": int(memory_candidates.get("candidate_count", 0)) if memory_candidates else 0,
            "refined_candidate_count": count_items(memory_candidates_refined, "candidates"),
        },
    }

    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SNAPSHOT_PATH.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    print("[OK] Perma v1 snapshot built")
    print(f" - Snapshot path: {SNAPSHOT_PATH}")
    print(f" - Item count   : {snapshot['summary']['item_count']}")
    print(f" - Memory cand  : {snapshot['summary']['memory_candidate_count']}")
    print(f" - Refined cand : {snapshot['summary']['refined_candidate_count']}")


if __name__ == "__main__":
    main()