"""Dry-run command line entrypoint for ChantaPermaMemory."""

from __future__ import annotations

import argparse
from pathlib import Path

from chanta_perma_memory.config.settings import load_config
from chanta_perma_memory.policies.ingest import evaluate_inbox


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chanta-perma-memory",
        description="Dry-run repository ingest and policy checks.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional path to a JSON config file.",
    )
    parser.add_argument(
        "--inbox",
        type=Path,
        default=None,
        help="Override inbox path for this invocation.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Reserved for future use. Current version is dry-run only and "
            "will refuse to execute file operations."
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.execute:
        parser.error("Execution mode is not implemented. Use dry-run mode only.")

    config = load_config(args.config)
    inbox = args.inbox or config.repository.inbox_path
    decisions = evaluate_inbox(inbox)

    print("ChantaPermaMemory dry-run ingest")
    print(f"Repository root: {config.repository.root_path}")
    print(f"Inbox: {inbox}")
    print(f"Candidates discovered: {len(decisions)}")

    for decision in decisions:
        print(f"- {decision.source_path} -> {decision.suggested_bucket} ({decision.reason})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
