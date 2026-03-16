from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_VERSION = "0.7"


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "inbox_manifest.schema.json"
DOMAIN_RULES_PATH = PROJECT_ROOT / "policies" / "domain_rules.json"
TAG_RULES_PATH = PROJECT_ROOT / "policies" / "tag_rules.json"

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


@dataclass
class AppConfig:
    repository_root: Path
    inbox_path: Path
    shared_path: Path
    archive_path: Path
    dry_run: bool
    recursive_scan: bool
    output_path: Path
    enable_light_parsing: bool
    preview_char_limit: int


@dataclass
class DomainRule:
    domain: str
    confidence: str
    keywords: list[str]


@dataclass
class KeywordTagRule:
    keywords: list[str]
    tags: list[str]


@dataclass
class TagRules:
    extension_tags: dict[str, list[str]]
    keyword_tags: list[KeywordTagRule]
    domain_tags: dict[str, list[str]]


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
    content_preview: str | None
    content_preview_source: str | None


def load_config(config_path: Path) -> AppConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file does not exist: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return AppConfig(
        repository_root=Path(raw["repository_root"]),
        inbox_path=Path(raw["inbox_path"]),
        shared_path=Path(raw["shared_path"]),
        archive_path=Path(raw["archive_path"]),
        dry_run=bool(raw["dry_run"]),
        recursive_scan=bool(raw["recursive_scan"]),
        output_path=PROJECT_ROOT / raw["output_path"],
        enable_light_parsing=bool(raw.get("enable_light_parsing", False)),
        preview_char_limit=int(raw.get("preview_char_limit", 1200)),
    )


def load_domain_rules(rules_path: Path) -> list[DomainRule]:
    if not rules_path.exists():
        raise FileNotFoundError(f"Domain rules file does not exist: {rules_path}")

    with rules_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    rules: list[DomainRule] = []
    for item in raw.get("rules", []):
        rules.append(
            DomainRule(
                domain=item["domain"],
                confidence=item["confidence"],
                keywords=item["keywords"],
            )
        )
    return rules


def load_tag_rules(rules_path: Path) -> TagRules:
    if not rules_path.exists():
        raise FileNotFoundError(f"Tag rules file does not exist: {rules_path}")

    with rules_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    keyword_rules: list[KeywordTagRule] = []
    for item in raw.get("keyword_tags", []):
        keyword_rules.append(
            KeywordTagRule(
                keywords=item["keywords"],
                tags=item["tags"],
            )
        )

    return TagRules(
        extension_tags=raw.get("extension_tags", {}),
        keyword_tags=keyword_rules,
        domain_tags=raw.get("domain_tags", {}),
    )


def should_skip(path: Path) -> bool:
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
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def extract_text_preview(file_path: Path, char_limit: int) -> tuple[str | None, str | None]:
    """
    Light parsing only.
    Currently supports:
    - .txt
    - .md
    """
    extension = file_path.suffix.lower()

    if extension not in {".txt", ".md"}:
        return None, None

    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None, None

    preview = " ".join(text.split())
    preview = preview[:char_limit].strip()

    if not preview:
        return None, None

    return preview, "text_file"


def suggest_candidate_domain(
    file_path: Path,
    rules: list[DomainRule],
    content_preview: str | None = None,
) -> tuple[str | None, str | None]:
    """
    Suggest candidate domain based on filename/path keywords,
    optionally strengthened by light content preview.
    """
    haystack_parts = [str(file_path.name), str(file_path.stem), str(file_path)]
    if content_preview:
        haystack_parts.append(content_preview)

    haystack = " ".join(haystack_parts).lower()

    matched_rules: list[DomainRule] = []
    for rule in rules:
        for keyword in rule.keywords:
            if keyword.lower() in haystack:
                matched_rules.append(rule)
                break

    if len(matched_rules) == 1:
        confidence = matched_rules[0].confidence
        if content_preview:
            confidence = "high" if confidence == "medium" else confidence
        return matched_rules[0].domain, confidence

    if len(matched_rules) > 1:
        return None, "low"

    return None, None


def suggest_tags(
    file_path: Path,
    candidate_domain: str | None,
    tag_rules: TagRules,
    content_preview: str | None = None,
) -> list[str]:
    """
    Suggest retrieval-oriented tags from:
    1. extension
    2. filename/path keywords
    3. candidate domain
    4. light content preview
    """
    haystack_parts = [str(file_path.name), str(file_path.stem), str(file_path)]
    if content_preview:
        haystack_parts.append(content_preview)

    haystack = " ".join(haystack_parts).lower()
    tags: list[str] = []

    extension = file_path.suffix.lower()
    tags.extend(tag_rules.extension_tags.get(extension, []))

    for rule in tag_rules.keyword_tags:
        for keyword in rule.keywords:
            if keyword.lower() in haystack:
                tags.extend(rule.tags)
                break

    if candidate_domain is not None:
        tags.extend(tag_rules.domain_tags.get(candidate_domain, []))

    unique_tags: list[str] = []
    seen: set[str] = set()
    for tag in tags:
        normalized = tag.strip().lower()
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_tags.append(normalized)

    return unique_tags


def extract_file_metadata(
    file_path: Path,
    inbox_root: Path,
    domain_rules: list[DomainRule],
    tag_rules: TagRules,
    config: AppConfig,
) -> RepositoryItem:
    stat = file_path.stat()

    try:
        relative_path = file_path.relative_to(inbox_root)
    except ValueError:
        relative_path = Path(file_path.name)

    content_preview = None
    content_preview_source = None

    if config.enable_light_parsing:
        content_preview, content_preview_source = extract_text_preview(
            file_path,
            config.preview_char_limit,
        )

    candidate_domain, confidence = suggest_candidate_domain(
        file_path,
        domain_rules,
        content_preview=content_preview,
    )

    tags = suggest_tags(
        file_path,
        candidate_domain,
        tag_rules,
        content_preview=content_preview,
    )

    return RepositoryItem(
        path=str(file_path),
        relative_path=str(relative_path),
        name=file_path.name,
        extension=file_path.suffix.lower(),
        size=stat.st_size,
        modified_time=to_iso_utc(stat.st_mtime),
        status="inbox",
        candidate_domain=candidate_domain,
        tags=tags,
        confidence=confidence,
        is_file=file_path.is_file(),
        content_preview=content_preview,
        content_preview_source=content_preview_source,
    )


def iter_candidate_files(inbox_path: Path, recursive_scan: bool) -> list[Path]:
    if recursive_scan:
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


def scan_inbox(
    inbox_path: Path,
    recursive_scan: bool,
    domain_rules: list[DomainRule],
    tag_rules: TagRules,
    config: AppConfig,
) -> list[RepositoryItem]:
    files = iter_candidate_files(inbox_path, recursive_scan)
    return [
        extract_file_metadata(file_path, inbox_path, domain_rules, tag_rules, config)
        for file_path in files
    ]


def build_manifest(items: list[RepositoryItem], config: AppConfig) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()

    return {
        "manifest_version": MANIFEST_VERSION,
        "generated_at": generated_at,
        "repository_root": str(config.repository_root),
        "inbox_path": str(config.inbox_path),
        "item_count": len(items),
        "items": [asdict(item) for item in items],
    }


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def main() -> None:
    config = load_config(CONFIG_PATH)
    domain_rules = load_domain_rules(DOMAIN_RULES_PATH)
    tag_rules = load_tag_rules(TAG_RULES_PATH)

    if not config.repository_root.exists():
        raise FileNotFoundError(
            f"Repository root does not exist: {config.repository_root}"
        )

    if not config.inbox_path.exists():
        raise FileNotFoundError(
            f"Inbox path does not exist: {config.inbox_path}"
        )

    if not config.inbox_path.is_dir():
        raise NotADirectoryError(
            f"Inbox path is not a directory: {config.inbox_path}"
        )

    items = scan_inbox(
        config.inbox_path,
        config.recursive_scan,
        domain_rules,
        tag_rules,
        config,
    )
    manifest = build_manifest(items, config)
    save_manifest(manifest, config.output_path)

    matched = sum(1 for item in items if item.candidate_domain is not None)
    ambiguous = sum(
        1 for item in items if item.candidate_domain is None and item.confidence == "low"
    )
    tagged = sum(1 for item in items if len(item.tags) > 0)
    parsed = sum(1 for item in items if item.content_preview is not None)

    print("[OK] Inbox scan complete")
    print(f" - Manifest ver : {MANIFEST_VERSION}")
    print(f" - Config path  : {CONFIG_PATH}")
    print(f" - Inbox path   : {config.inbox_path}")
    print(f" - Items found  : {len(items)}")
    print(f" - Matched      : {matched}")
    print(f" - Ambiguous    : {ambiguous}")
    print(f" - Tagged       : {tagged}")
    print(f" - Parsed       : {parsed}")
    print(f" - Output file  : {config.output_path}")
    print(f" - Schema path  : {SCHEMA_PATH}")
    print(f" - Dry run      : {config.dry_run}")


if __name__ == "__main__":
    main()