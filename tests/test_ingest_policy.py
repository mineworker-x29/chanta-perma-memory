from pathlib import Path

from chanta_perma_memory.policies.ingest import evaluate_inbox


def test_evaluate_inbox_returns_dry_run_suggestions(tmp_path: Path) -> None:
    doc = tmp_path / "notes.md"
    unknown = tmp_path / "blob.bin"
    doc.write_text("hello", encoding="utf-8")
    unknown.write_bytes(b"data")

    decisions = evaluate_inbox(tmp_path)

    assert [d.source_path.name for d in decisions] == ["blob.bin", "notes.md"]
    by_name = {d.source_path.name: d for d in decisions}
    assert by_name["notes.md"].suggested_bucket == "90_Shared"
    assert by_name["blob.bin"].suggested_bucket == "00_Inbox"


def test_evaluate_inbox_missing_path_returns_empty(tmp_path: Path) -> None:
    decisions = evaluate_inbox(tmp_path / "missing")
    assert decisions == []
