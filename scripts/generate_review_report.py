from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "scripts" / "output" / "inbox_manifest.json"
REPORT_PATH = PROJECT_ROOT / "scripts" / "output" / "inbox_review_report.md"


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest file does not exist: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def summarize_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    extension_counter: Counter[str] = Counter()
    domain_counter: Counter[str] = Counter()
    confidence_counter: Counter[str] = Counter()
    tag_counter: Counter[str] = Counter()

    ambiguous_items: list[dict[str, Any]] = []
    unclassified_items: list[dict[str, Any]] = []

    for item in items:
        extension = str(item.get("extension") or "").strip().lower()
        candidate_domain = item.get("candidate_domain")
        confidence = item.get("confidence")
        tags = [str(tag).strip().lower() for tag in safe_list(item.get("tags")) if str(tag).strip()]

        if extension:
            extension_counter[extension] += 1

        if candidate_domain:
            domain_counter[str(candidate_domain)] += 1
        else:
            unclassified_items.append(item)

        if confidence:
            confidence_counter[str(confidence)] += 1

        for tag in tags:
            tag_counter[tag] += 1

        if candidate_domain is None and confidence == "low":
            ambiguous_items.append(item)

    return {
        "extension_counter": extension_counter,
        "domain_counter": domain_counter,
        "confidence_counter": confidence_counter,
        "tag_counter": tag_counter,
        "ambiguous_items": ambiguous_items,
        "unclassified_items": unclassified_items,
    }


def format_counter_table(counter: Counter[str], headers: tuple[str, str]) -> str:
    if not counter:
        return "_None_\n"

    lines = [
        f"| {headers[0]} | {headers[1]} |",
        "|---|---:|",
    ]
    for key, value in counter.most_common():
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines) + "\n"


def format_item_list(items: list[dict[str, Any]]) -> str:
    if not items:
        return "_None_\n"

    lines: list[str] = []
    for item in items:
        name = item.get("name", "<unknown>")
        candidate_domain = item.get("candidate_domain")
        confidence = item.get("confidence")
        tags = ", ".join(safe_list(item.get("tags"))) if safe_list(item.get("tags")) else "-"
        extension = item.get("extension", "")
        relative_path = item.get("relative_path", "")
        preview = item.get("content_preview", None)

        lines.append(f"- **{name}**")
        lines.append(f"  - relative_path: `{relative_path}`")
        lines.append(f"  - extension: `{extension}`")
        lines.append(f"  - candidate_domain: `{candidate_domain}`")
        lines.append(f"  - confidence: `{confidence}`")
        lines.append(f"  - tags: {tags}")
        if preview:
            lines.append(f"  - content_preview: {preview[:240]}")
    return "\n".join(lines) + "\n"


def format_top_tags(counter: Counter[str], top_n: int = 15) -> str:
    if not counter:
        return "_None_\n"

    lines = [f"- `{tag}`: {count}" for tag, count in counter.most_common(top_n)]
    return "\n".join(lines) + "\n"


def build_report(manifest: dict[str, Any]) -> str:
    manifest_version = manifest.get("manifest_version", "unknown")
    generated_at = manifest.get("generated_at", "unknown")
    repository_root = manifest.get("repository_root", "unknown")
    inbox_path = manifest.get("inbox_path", "unknown")
    item_count = int(manifest.get("item_count", 0))
    items = safe_list(manifest.get("items"))

    summary = summarize_items(items)
    report_generated_at = datetime.now(timezone.utc).isoformat()

    lines: list[str] = []
    lines.append("# Inbox Review Report")
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- report_generated_at: `{report_generated_at}`")
    lines.append(f"- manifest_version: `{manifest_version}`")
    lines.append(f"- manifest_generated_at: `{generated_at}`")
    lines.append(f"- repository_root: `{repository_root}`")
    lines.append(f"- inbox_path: `{inbox_path}`")
    lines.append(f"- item_count: `{item_count}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- total_items: **{item_count}**")
    lines.append(f"- classified_items: **{sum(summary['domain_counter'].values())}**")
    lines.append(f"- unclassified_items: **{len(summary['unclassified_items'])}**")
    lines.append(f"- ambiguous_items: **{len(summary['ambiguous_items'])}**")
    lines.append("")
    lines.append("## By Candidate Domain")
    lines.append("")
    lines.append(format_counter_table(summary["domain_counter"], ("candidate_domain", "count")))
    lines.append("## By Extension")
    lines.append("")
    lines.append(format_counter_table(summary["extension_counter"], ("extension", "count")))
    lines.append("## By Confidence")
    lines.append("")
    lines.append(format_counter_table(summary["confidence_counter"], ("confidence", "count")))
    lines.append("## Top Tags")
    lines.append("")
    lines.append(format_top_tags(summary["tag_counter"]))
    lines.append("## Ambiguous Items")
    lines.append("")
    lines.append(format_item_list(summary["ambiguous_items"]))
    lines.append("## Unclassified Items")
    lines.append("")
    lines.append(format_item_list(summary["unclassified_items"]))
    lines.append("## Full Item Review")
    lines.append("")
    lines.append(format_item_list(items))
    return "\n".join(lines)


def save_report(report_text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(report_text)


def main() -> None:
    manifest = load_manifest(MANIFEST_PATH)
    report_text = build_report(manifest)
    save_report(report_text, REPORT_PATH)

    print("[OK] Review report generated")
    print(f" - Manifest path : {MANIFEST_PATH}")
    print(f" - Report path   : {REPORT_PATH}")


if __name__ == "__main__":
    main()