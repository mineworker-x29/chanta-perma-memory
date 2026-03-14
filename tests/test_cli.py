from pathlib import Path

from chanta_perma_memory.cli import build_parser


def test_cli_parser_rejects_execute_mode() -> None:
    parser = build_parser()
    args = parser.parse_args(["--inbox", str(Path("/tmp/inbox"))])

    assert args.execute is False
    assert args.inbox == Path("/tmp/inbox")
